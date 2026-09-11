"""보수적 판정 정책: recall보다 precision.

Contradiction을 과탐지하면 사용자가 신뢰를 잃는다 (proposal.md §7 'AI가 아는 척하는 것').
아래 조건을 모두 통과해야만 '자료 간 불일치'로 확정하고, 하나라도 걸리면 Neutral(확인 필요)로 내린다.

1. 모순 점수 ≥ contradiction_min
2. 모순 점수 − max(일치, 중립) ≥ contradiction_margin
3. 두 주장의 추출 신뢰도 ≥ min_claim_confidence
4. 같은 대상(같은 계좌·같은 송금)에 대한 주장임이 확실
5. 비교한 시각이 '확인 필요' 상태가 아님

기본값은 튜닝 전 초기값이다. 라벨링 파일럿 후 ``eval/nli_eval.py``가 목표 precision을 만족하는
임계값을 찾아 JSON으로 내보내고, ``ConservativePolicy.from_json``으로 불러 쓴다.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from ..schema import Claim, NliLabel, NliScores, PairDecision


class ConservativePolicy(BaseModel):
    contradiction_min: float = Field(default=0.70, ge=0.0, le=1.0)
    contradiction_margin: float = Field(default=0.40, ge=0.0, le=1.0)
    entailment_min: float = Field(default=0.70, ge=0.0, le=1.0)
    min_claim_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    suspect_min: float = Field(default=0.35, ge=0.0, le=1.0, description="이 이상이면 '차이 의심'으로 확인 필요에 올림")

    def decide(
        self,
        pair_id: str,
        a: Claim,
        b: Claim,
        scores: NliScores,
        model_name: str,
        subject_certain: bool = True,
    ) -> PairDecision:
        model_label = scores.argmax()
        label = model_label
        reasons: list[str] = []
        low = [c for c in (a, b) if c.content.confidence < self.min_claim_confidence]
        unsure_time = any(c.slot_time is not None and c.slot_time.needs_confirmation for c in (a, b))

        if model_label is NliLabel.CONTRADICTION or scores.contradiction >= self.suspect_min:
            if scores.contradiction < self.contradiction_min:
                reasons.append(f"모순 점수 {scores.contradiction:.2f} < 기준 {self.contradiction_min:.2f}")
            margin = scores.contradiction - max(scores.entailment, scores.neutral)
            if margin < self.contradiction_margin:
                reasons.append(f"다른 해석과의 차이 {margin:.2f} < 기준 {self.contradiction_margin:.2f}")
            for c in low:
                reasons.append(f"추출 신뢰도 낮음: {c.content.cite()} ({c.content.confidence:.2f})")
            if not subject_certain:
                reasons.append("같은 대상에 대한 주장인지 확실하지 않음")
            if unsure_time:
                reasons.append("비교한 날짜·시각 자체가 확인 필요 상태")
            label = NliLabel.NEUTRAL if reasons else NliLabel.CONTRADICTION
        elif model_label is NliLabel.ENTAILMENT:
            if scores.entailment < self.entailment_min:
                reasons.append(f"일치 점수 {scores.entailment:.2f} < 기준 {self.entailment_min:.2f}")
            for c in low:
                reasons.append(f"추출 신뢰도 낮음: {c.content.cite()} ({c.content.confidence:.2f})")
            if unsure_time:
                reasons.append("비교한 날짜·시각 자체가 확인 필요 상태")
            label = NliLabel.NEUTRAL if reasons else NliLabel.ENTAILMENT

        return PairDecision(
            pair_id=pair_id,
            claim_a_id=a.claim_id,
            claim_b_id=b.claim_id,
            slot=a.slot,
            scores=scores,
            model_label=model_label,
            label=label,
            downgraded=label is not model_label or (label is NliLabel.NEUTRAL and bool(reasons)),
            reasons=reasons,
            model_name=model_name,
        )

    def is_suspected(self, decision: PairDecision) -> bool:
        return decision.label is NliLabel.NEUTRAL and decision.scores.contradiction >= self.suspect_min

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> ConservativePolicy:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate({k: v for k, v in data.items() if k in cls.model_fields})
