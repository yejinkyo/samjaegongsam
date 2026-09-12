"""KLUE NLI → 라벨 변환. 네트워크·모델 없이 도는 부분만 본다 (허브 접근은 CI에서 하지 않는다)."""

import json

import pytest

from research_engine.analysis import CombinedNli, SlotRuleNli
from research_engine.eval.klue import klue_nli_rows, load_klue_nli, write_labels
from research_engine.eval.nli_eval import load_pair_labels, tune_thresholds
from research_engine.schema import NliLabel

ROWS = [
    {"guid": "k1", "premise": "발코니가 있는 방에서는 흡연이 가능합니다.", "hypothesis": "어떤 방에서도 흡연은 금지됩니다.", "label": 2},
    {"guid": "k2", "premise": "10명이 함께 쓰기에 만족했다.", "hypothesis": "10명이 쓰기에 만족스러웠다.", "label": 0},
    {"guid": "k3", "premise": "10층에 수영장이 있습니다.", "hypothesis": "성인 10명이 이용했다.", "label": 1},
]


def test_정수_라벨과_문자열_라벨을_모두_받는다():
    golds = [r["gold"] for r in klue_nli_rows(ROWS)]
    assert golds == ["contradiction", "entailment", "neutral"]
    as_text = [dict(r, label={0: "entailment", 1: "neutral", 2: "contradiction"}[r["label"]]) for r in ROWS]
    assert [r["gold"] for r in klue_nli_rows(as_text)] == golds


def test_알_수_없는_라벨과_빈_문장은_건너뛴다():
    bad = [
        {"guid": "x1", "premise": "문장", "hypothesis": "문장", "label": 99},
        {"guid": "x2", "premise": "", "hypothesis": "문장", "label": 0},
        {"guid": "x3", "premise": "문장", "hypothesis": None, "label": 0},
    ]
    assert list(klue_nli_rows(bad)) == []


def test_변환_결과가_eval_nli_라벨로_그대로_읽힌다(tmp_path):
    out = write_labels(list(klue_nli_rows(ROWS)), tmp_path / "pairs.jsonl")
    labels = load_pair_labels(out)
    assert len(labels) == 3
    first = labels[0]
    assert first.gold is NliLabel.CONTRADICTION
    assert first.a is not None and first.b is not None
    # 출처 없는 문장은 이 파이프라인에 넣을 수 없다 — 데이터셋 행을 문서로 본다
    assert first.a.content.source_doc_id == "k1:a" and first.a.content.source_line == 1
    assert first.a.doc_id != first.b.doc_id  # 다른 문서여야 비교 대상으로 잡힌다


def test_슬롯_없는_주장은_규칙이_판단하지_않는다(tmp_path):
    """KLUE 라벨은 자유 서술이라 slot=None 이다. 규칙 NLI 는 점수를 내지 않아야 한다."""
    labels = load_pair_labels(write_labels(list(klue_nli_rows(ROWS)), tmp_path / "pairs.jsonl"))
    rule = SlotRuleNli()
    assert all(rule.score(lb.a, lb.b) is None for lb in labels)
    assert all(CombinedNli().score(lb.a, lb.b) is None for lb in labels)  # 텍스트 모델이 없으면 그대로 None


def test_텍스트_모델이_없으면_모순_recall이_0이다(tmp_path):
    """현재 기본 설정의 측정값. 텍스트 모델을 붙이기 전에는 자유 서술 모순을 못 잡는다."""
    report = tune_thresholds(load_pair_labels(write_labels(list(klue_nli_rows(ROWS)), tmp_path / "pairs.jsonl")))
    assert report["gold_contradictions"] == 1
    assert report["current_policy"]["contradiction"]["recall"] == 0.0
    assert report["recommended_policy"] is None


def test_파일에서_읽을_때_형식을_가린다(tmp_path):
    src = tmp_path / "klue.jsonl"
    src.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ROWS), encoding="utf-8")
    assert len(load_klue_nli(path=src)) == 3
    assert len(load_klue_nli(path=src, limit=2)) == 2
    with pytest.raises(ValueError, match="지원하지 않는 형식"):
        load_klue_nli(path=tmp_path / "klue.csv")


@pytest.mark.skipif(
    not __import__("os").environ.get("RESEARCH_ENGINE_NLI_MODEL"),
    reason="체크포인트를 내려받아야 한다. RESEARCH_ENGINE_NLI_MODEL=Huffon/klue-roberta-base-nli 로 실행",
)
def test_텍스트_모델을_붙이면_자유_서술도_점수가_나온다(tmp_path):
    """RoBERTa 본체 + BertTokenizer 조합에서 token_type_ids 로 죽지 않는지까지 확인한다."""
    import os

    from research_engine.analysis import HuggingFaceNli

    labels = load_pair_labels(write_labels(list(klue_nli_rows(ROWS)), tmp_path / "pairs.jsonl"))
    nli = CombinedNli(text=HuggingFaceNli(os.environ["RESEARCH_ENGINE_NLI_MODEL"]))
    scored = [nli.score(lb.a, lb.b) for lb in labels]
    assert all(s is not None for s in scored)
    contradiction, entailment, _ = scored
    assert contradiction.contradiction > contradiction.entailment
    assert entailment.entailment > entailment.contradiction


def _free_text_pair(tmp_path):
    labels = load_pair_labels(write_labels(list(klue_nli_rows(ROWS)), tmp_path / "pairs.jsonl"))
    return labels[0].a, labels[0].b  # gold=contradiction


def test_자유_서술은_텍스트_점수가_높아도_확정하지_않는다(tmp_path):
    """측정 precision(0.86~0.88)이 목표 0.95 에 못 미친다 — '차이 의심'까지만 올린다."""
    from research_engine.analysis import ConservativePolicy
    from research_engine.schema import NliScores

    a, b = _free_text_pair(tmp_path)
    scores = NliScores(entailment=0.01, contradiction=0.89, neutral=0.10)
    policy = ConservativePolicy()
    decision = policy.decide("p1", a, b, scores, "hf:test")
    assert decision.model_label is NliLabel.CONTRADICTION
    assert decision.label is NliLabel.NEUTRAL and decision.downgraded
    assert any("항목 값이 없어" in r for r in decision.reasons)
    assert policy.is_suspected(decision)  # 화면의 '차이가 있어 보입니다'로 올라간다


def test_항목_값이_있으면_확정_경로는_그대로다(tmp_path):
    """슬롯 있는 주장(금액·일시·계좌)은 값을 직접 비교하므로 기존 확정 경로를 막지 않는다."""
    from research_engine.analysis import ConservativePolicy
    from research_engine.schema import ClaimSlot, NliScores

    a, b = _free_text_pair(tmp_path)
    a = a.model_copy(update={"slot": ClaimSlot.TRANSFER_AMOUNT, "slot_value": "350000"})
    b = b.model_copy(update={"slot": ClaimSlot.TRANSFER_AMOUNT, "slot_value": "300000"})
    scores = NliScores(entailment=0.01, contradiction=0.89, neutral=0.10)
    decision = ConservativePolicy().decide("p2", a, b, scores, "slot-rule-v1")
    assert decision.label is NliLabel.CONTRADICTION and not decision.reasons


def test_켜면_자유_서술도_확정한다(tmp_path):
    """검증 데이터가 목표를 넘기면 이 값만 True 로 바꾼다."""
    from research_engine.analysis import ConservativePolicy
    from research_engine.schema import NliScores

    a, b = _free_text_pair(tmp_path)
    scores = NliScores(entailment=0.01, contradiction=0.89, neutral=0.10)
    decision = ConservativePolicy(confirm_free_text=True).decide("p3", a, b, scores, "hf:test")
    assert decision.label is NliLabel.CONTRADICTION
