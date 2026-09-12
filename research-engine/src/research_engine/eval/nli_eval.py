"""NLI 임계값 튜닝: 목표 precision을 지키는 범위에서 Contradiction recall 최대화.

라벨 형식 (JSONL, 줄 하나 = Claim 쌍 하나). 둘 중 하나:

1. 모델 점수를 이미 뽑아 둔 경우 (어떤 모델이든)::

    {"scores": {"entailment": 0.05, "contradiction": 0.81, "neutral": 0.14},
     "min_confidence": 0.88, "subject_certain": true, "gold": "contradiction"}

2. Claim 두 개를 넣고 이 패키지의 NLI로 점수를 매기는 경우::

    {"a": {...Claim JSON...}, "b": {...Claim JSON...}, "subject_certain": true, "gold": "neutral"}

gold는 사람이 두 원문을 보고 판단한 값이다. 결과 JSON은 ``ConservativePolicy.from_json``으로 바로 불러 쓴다.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from ..analysis.nli import CombinedNli, NliModel
from ..analysis.policy import ConservativePolicy
from ..schema import Claim, NliLabel, NliScores
from .metrics import PRF


class PairLabel(BaseModel):
    gold: NliLabel
    scores: NliScores | None = None
    min_confidence: float = 1.0
    subject_certain: bool = True
    a: Claim | None = None
    b: Claim | None = None


def load_pair_labels(path: str | Path) -> list[PairLabel]:
    return [PairLabel.model_validate_json(r) for r in Path(path).read_text(encoding="utf-8").splitlines() if r.strip()]


def _materialize(labels: list[PairLabel], nli: NliModel) -> list[tuple[NliScores, float, bool, NliLabel]]:
    rows = []
    for lb in labels:
        scores, conf = lb.scores, lb.min_confidence
        if scores is None:
            if lb.a is None or lb.b is None:
                raise ValueError("scores 또는 a/b 중 하나는 있어야 합니다")
            scores = nli.score(lb.a, lb.b)
            conf = min(lb.a.content.confidence, lb.b.content.confidence)
            if scores is None:
                scores = NliScores(entailment=0.0, contradiction=0.0, neutral=1.0)
        rows.append((scores, conf, lb.subject_certain, lb.gold))
    return rows


def score_labels(labels: list[PairLabel], nli: NliModel) -> list[PairLabel]:
    """모델을 한 번만 돌려 점수를 채운 라벨을 돌려준다.

    임계값 스윕은 점수만 있으면 되는데 모델 추론이 가장 비싸다. 점수를 저장해 두면
    임계값·목표 precision 을 바꿔 다시 재는 일이 모델 없이 즉시 끝난다.
    """
    out: list[PairLabel] = []
    for lb, (scores, conf, certain, gold) in zip(labels, _materialize(labels, nli), strict=True):
        out.append(PairLabel(gold=gold, scores=scores, min_confidence=conf, subject_certain=certain,
                             a=lb.a, b=lb.b))
    return out


def _predict(scores: NliScores, conf: float, subject_certain: bool, policy: ConservativePolicy) -> bool:
    margin = scores.contradiction - max(scores.entailment, scores.neutral)
    return (
        scores.contradiction >= policy.contradiction_min
        and margin >= policy.contradiction_margin
        and conf >= policy.min_claim_confidence
        and subject_certain
    )


def tune_thresholds(
    labels: list[PairLabel],
    target_precision: float = 0.95,
    base: ConservativePolicy | None = None,
    nli: NliModel | None = None,
) -> dict:
    base = base or ConservativePolicy()
    rows = _materialize(labels, nli or CombinedNli())
    grid = []
    for ci in range(6, 20):
        for mi in range(0, 7):
            policy = base.model_copy(update={"contradiction_min": ci / 20, "contradiction_margin": mi / 10})
            prf = PRF()
            for scores, conf, certain, gold in rows:
                pred = _predict(scores, conf, certain, policy)
                is_gold = gold is NliLabel.CONTRADICTION
                prf.tp += pred and is_gold
                prf.fp += pred and not is_gold
                prf.fn += (not pred) and is_gold
            grid.append((policy, prf))

    feasible = [(p, m) for p, m in grid if m.tp + m.fp > 0 and m.precision >= target_precision]
    # recall이 같으면 더 엄격한(높은) 임계값을 택한다
    chosen = (
        max(feasible, key=lambda pm: (pm[1].recall, pm[0].contradiction_min, pm[0].contradiction_margin))
        if feasible
        else None
    )
    base_prf = PRF()
    for scores, conf, certain, gold in rows:
        pred = _predict(scores, conf, certain, base)
        base_prf.tp += pred and gold is NliLabel.CONTRADICTION
        base_prf.fp += pred and gold is not NliLabel.CONTRADICTION
        base_prf.fn += (not pred) and gold is NliLabel.CONTRADICTION
    return {
        "pairs": len(rows),
        "gold_contradictions": sum(1 for r in rows if r[3] is NliLabel.CONTRADICTION),
        "target_precision": target_precision,
        "current_policy": {**base.model_dump(), "contradiction": base_prf.as_dict()},
        "recommended_policy": (
            {**chosen[0].model_dump(), "contradiction": chosen[1].as_dict()} if chosen else None
        ),
        "note": None if chosen else "목표 precision을 만족하는 임계값이 없습니다 — 모델 개선 또는 라벨 추가가 필요합니다",
    }
