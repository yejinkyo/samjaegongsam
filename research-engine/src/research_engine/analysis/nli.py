"""Claim 쌍 NLI 모델.

- ``SlotRuleNli``      : 슬롯 값이 구조화된 주장끼리 값 자체를 비교 (금액·일시·계좌·이름·여부)
- ``HuggingFaceNli``   : 슬롯이 없는 자유 서술 주장용. 한국어 NLI로 파인튜닝된 체크포인트를 넣는다
                         (예: KLUE-NLI 학습 모델). ``pip install research-engine[nli]`` 필요. 이 저장소에서는 미검증.
- ``CombinedNli``      : 규칙 우선, 판단 불가일 때만 텍스트 모델

모든 모델 점수는 두 주장의 추출 신뢰도로 중립 쪽으로 수축시킨다 — 흐릿한 글자에서 나온 모순은 모순이 아니다.
"""

from __future__ import annotations

from typing import Protocol

from ..schema import Claim, ClaimSlot, NliScores, Polarity
from ..timeline.coref import mask_compatible

S = ClaimSlot
AMOUNT_SLOTS = {S.TRANSFER_AMOUNT}
TIME_SLOTS = {S.TRANSFER_TIME, S.RECEIPT_TIME, S.INCIDENT_TIME}
ID_SLOTS = {S.ACCOUNT_NUMBER, S.TRACKING_NUMBER, S.RECEIPT_NUMBER, S.CASE_NUMBER}
NAME_SLOTS = {S.ACCOUNT_HOLDER, S.INVESTIGATOR}
BOOL_SLOTS = {S.SHIPMENT_SENT, S.ITEM_RECEIVED}


class NliModel(Protocol):
    name: str

    def score(self, a: Claim, b: Claim) -> NliScores | None: ...


def _scores(e: float, c: float) -> NliScores:
    return NliScores(entailment=round(e, 4), contradiction=round(c, 4), neutral=round(max(0.0, 1 - e - c), 4))


def shrink_by_confidence(scores: NliScores, a: Claim, b: Claim) -> NliScores:
    w = min(a.content.confidence, b.content.confidence)
    return _scores(scores.entailment * w, scores.contradiction * w)


class SlotRuleNli:
    name = "slot-rule-v1"

    def score(self, a: Claim, b: Claim) -> NliScores | None:
        if a.slot is None or a.slot is not b.slot:
            return None
        raw = self._compare(a, b)
        return shrink_by_confidence(raw, a, b) if raw is not None else None

    def _compare(self, a: Claim, b: Claim) -> NliScores | None:
        slot = a.slot
        opposite = a.polarity is not b.polarity
        if slot in BOOL_SLOTS:
            return _scores(0.02, 0.85) if opposite else _scores(0.8, 0.02)

        if slot in TIME_SLOTS:
            ta, tb = a.slot_time, b.slot_time
            if ta is None or tb is None:
                return None
            if ta.needs_confirmation or tb.needs_confirmation:
                return _scores(0.1, 0.1)
            compatible = ta.compatible(tb)
            if compatible is None:
                return None
            if compatible:
                precise = all(t.granularity.value in ("minute", "hour", "day") and not t.approximate for t in (ta, tb))
                return _scores(0.85, 0.02) if precise else _scores(0.35, 0.02)
            # 겹치지 않음: 가까운 어긋남은 기억 오차일 수 있어 약하게
            gap = ta.gap_seconds(tb) or 0
            return _scores(0.02, 0.9) if gap >= 6 * 3600 else _scores(0.05, 0.45)

        if a.slot_value is None or b.slot_value is None:
            return None
        if opposite:
            return _scores(0.02, 0.8) if a.slot_value == b.slot_value else _scores(0.05, 0.05)

        if slot in AMOUNT_SLOTS:
            return _scores(0.95, 0.02) if a.slot_value == b.slot_value else _scores(0.02, 0.93)

        if slot in ID_SLOTS:
            va, vb = a.slot_value, b.slot_value
            if va == vb and "*" not in va:
                return _scores(0.95, 0.02)
            if va == vb or mask_compatible(va, vb, min_known=1)[0]:
                return _scores(0.4, 0.02)  # 마스킹 때문에 확정 못 함
            if len(va) == len(vb) or ("*" not in va and "*" not in vb):
                return _scores(0.02, 0.88)
            return _scores(0.05, 0.3)

        if slot in NAME_SLOTS:
            if a.value_is_speaker_self or b.value_is_speaker_self:
                # "제 명의예요" — 화자가 닉네임이면 실명과 비교할 수 없다
                if a.slot_value == b.slot_value:
                    return _scores(0.5, 0.02)
                return _scores(0.05, 0.05)
            va, vb = a.slot_value, b.slot_value
            if va == vb and "*" not in va:
                return _scores(0.9, 0.02)
            if "*" in va or "*" in vb:
                ok = mask_compatible(va, vb, min_known=1)[0]
                return _scores(0.35, 0.02) if ok else _scores(0.02, 0.7)
            return _scores(0.02, 0.85)
        return None


class HuggingFaceNli:
    """premise=a.content, hypothesis=b.content. label_map으로 체크포인트 라벨명을 맞춘다."""

    def __init__(self, model_name: str, label_map: dict[str, str] | None = None, device: int | str | None = None):
        from transformers import pipeline

        self.name = f"hf:{model_name}"
        self._pipe = pipeline("text-classification", model=model_name, top_k=None, device=device)
        self.label_map = label_map or {"entailment": "entailment", "contradiction": "contradiction", "neutral": "neutral"}

    def score(self, a: Claim, b: Claim) -> NliScores | None:
        out = self._pipe({"text": a.content.value, "text_pair": b.content.value})
        rows = out[0] if out and isinstance(out[0], list) else out
        probs = {"entailment": 0.0, "contradiction": 0.0, "neutral": 0.0}
        for row in rows:
            key = self.label_map.get(row["label"]) or self.label_map.get(row["label"].lower())
            if key in probs:
                probs[key] = float(row["score"])
        return shrink_by_confidence(_scores(probs["entailment"], probs["contradiction"]), a, b)


class CombinedNli:
    def __init__(self, rule: NliModel | None = None, text: NliModel | None = None):
        self.rule = rule or SlotRuleNli()
        self.text = text
        self.name = self.rule.name + (f"+{self.text.name}" if self.text else "")

    def score(self, a: Claim, b: Claim) -> NliScores | None:
        scores = self.rule.score(a, b)
        if scores is None and self.text is not None and a.slot is None and b.slot is None:
            scores = self.text.score(a, b)
        return scores

    def model_for(self, a: Claim, b: Claim) -> str:
        return self.rule.name if a.slot is not None else (self.text.name if self.text else self.rule.name)


__all__ = ["CombinedNli", "HuggingFaceNli", "NliModel", "Polarity", "SlotRuleNli", "shrink_by_confidence"]
