import json
from datetime import date

from research_engine.analysis import ConservativePolicy
from research_engine.eval import cer, levenshtein
from research_engine.eval.ner_eval import evaluate_extraction
from research_engine.eval.nli_eval import load_pair_labels, tune_thresholds
from research_engine.eval.ocr_eval import evaluate_ocr, load_line_labels, training_samples
from research_engine.ingest import ReadabilityScorer

from .conftest import FIXTURES

PILOT = FIXTURES / "pilot"


def test_cer_ignores_spaces():
    assert levenshtein("2O19", "2019") == 1
    assert cer("피고인은 2O19", "피고인은2019") == 1 / 8


def test_ocr_eval_reports_cer_by_script_and_threshold():
    labels = load_line_labels(PILOT / "ocr_lines.jsonl")
    report = evaluate_ocr(labels, target_precision=0.95)
    assert set(report["by_script"]) == {"printed", "typewriter", "handwritten"}
    assert report["by_script"]["typewriter"]["finetune_recommended"] is True
    chosen = report["recommended_threshold"]
    row = next(r for r in report["threshold_sweep"] if r["threshold"] == chosen)
    assert row["precision"] >= 0.95


def test_readability_training_roundtrip(tmp_path):
    labels = load_line_labels(PILOT / "ocr_lines.jsonl")
    scorer = ReadabilityScorer().fit(training_samples(labels))
    scorer.to_json(tmp_path / "scorer.json")
    loaded = ReadabilityScorer.from_json(tmp_path / "scorer.json")
    assert loaded.weights == scorer.weights and loaded.threshold == scorer.threshold


def test_extraction_eval_on_gold():
    report = evaluate_extraction(PILOT / "ner_gold.jsonl", default_as_of=date(2026, 6, 24))
    assert report["entities"]["account"]["strict"]["f1"] == 1.0
    assert report["times"]["normalization_accuracy"] == 1.0
    assert all("finetune_recommended" in v for v in report["entities"].values())


def test_nli_threshold_tuning_meets_target_precision(tmp_path):
    labels = load_pair_labels(PILOT / "nli_pairs.jsonl")
    report = tune_thresholds(labels, target_precision=0.9)
    rec = report["recommended_policy"]
    assert rec["contradiction"]["precision"] >= 0.9
    assert report["current_policy"]["contradiction"]["precision"] < 0.9
    path = tmp_path / "policy.json"
    path.write_text(json.dumps({k: v for k, v in rec.items() if k != "contradiction"}), encoding="utf-8")
    assert ConservativePolicy.from_json(path).contradiction_min == rec["contradiction_min"]


def test_nli_tuning_reports_when_target_is_unreachable():
    labels = load_pair_labels(PILOT / "nli_pairs.jsonl")
    # 모든 모순 예측에 오답이 섞이도록 뒤집으면 목표를 만족하는 임계값이 없다
    flipped = [lb.model_copy(update={"gold": "neutral" if lb.gold.value == "contradiction" else lb.gold}) for lb in labels]
    report = tune_thresholds(flipped, target_precision=0.9)
    assert report["recommended_policy"] is None and report["note"]
