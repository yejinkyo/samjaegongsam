"""OCR 정확도 파일럿 평가 + 판독 신뢰도 임계값 결정.

라벨 형식 (JSONL, 줄 하나 = OCR 줄 하나)::

    {"doc_id": "scan01", "line_no": 3, "script": "typewriter",
     "ocr_text": "피고인은 2O19. 3. 5.", "gold_text": "피고인은 2019. 3. 5.",
     "ocr_confidence": 0.81, "min_word_confidence": 0.42}

판정 기준: '판독 가능'으로 표시한 줄 중 CER ≤ max_cer 인 비율(precision)이 목표 이상이 되는
가장 낮은 임계값을 고른다 — 낮을수록 사용자에게 되묻는 줄이 줄어든다.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from ..ingest.confidence import ReadabilityScorer, line_features
from ..ingest.ocr import OcrLine
from ..schema import Script
from .metrics import cer

# 파인튜닝 여부 판단용 초기 목표 CER (팀이 파일럿 전에 합의해 조정할 값)
DEFAULT_CER_TARGETS = {"printed": 0.03, "typewriter": 0.08, "handwritten": 0.15, "unknown": 0.08}


class LineLabel(BaseModel):
    doc_id: str = ""
    line_no: int | None = None
    script: Script = Script.UNKNOWN
    ocr_text: str
    gold_text: str
    ocr_confidence: float
    min_word_confidence: float | None = None


def load_line_labels(path: str | Path) -> list[LineLabel]:
    rows = Path(path).read_text(encoding="utf-8").splitlines()
    return [LineLabel.model_validate_json(r) for r in rows if r.strip()]


def features_for(label: LineLabel) -> dict[str, float]:
    feats = line_features(OcrLine(text=label.ocr_text, confidence=label.ocr_confidence), label.script)
    if label.min_word_confidence is not None:
        feats["min_word_conf"] = label.min_word_confidence
    return feats


def training_samples(labels: list[LineLabel], max_cer: float = 0.1) -> list[tuple[dict[str, float], int]]:
    return [(features_for(lb), int(cer(lb.ocr_text, lb.gold_text) <= max_cer)) for lb in labels]


def evaluate_ocr(
    labels: list[LineLabel],
    scorer: ReadabilityScorer | None = None,
    max_cer: float = 0.1,
    target_precision: float = 0.95,
    cer_targets: dict[str, float] | None = None,
) -> dict:
    scorer = scorer or ReadabilityScorer()
    targets = {**DEFAULT_CER_TARGETS, **(cer_targets or {})}
    rows = []
    for lb in labels:
        rows.append((lb, cer(lb.ocr_text, lb.gold_text), scorer.score(features_for(lb))))

    by_script: dict[str, dict] = {}
    for script in {lb.script.value for lb in labels}:
        sel = [(lb, c) for lb, c, _ in rows if lb.script.value == script]
        chars = sum(len(lb.gold_text.replace(" ", "")) for lb, _ in sel) or 1
        weighted = sum(c * len(lb.gold_text.replace(" ", "")) for lb, c in sel) / chars
        by_script[script] = {
            "lines": len(sel),
            "cer": round(weighted, 4),
            "target_cer": targets.get(script),
            "finetune_recommended": weighted > targets.get(script, 1.0),
        }

    sweep = []
    good_total = sum(1 for _, c, _ in rows if c <= max_cer)
    for i in range(1, 20):
        tau = i / 20
        readable = [(c, s) for _, c, s in rows if s >= tau]
        good = sum(1 for c, _ in readable if c <= max_cer)
        sweep.append({
            "threshold": tau,
            "coverage": round(len(readable) / len(rows), 4) if rows else 0.0,
            "precision": round(good / len(readable), 4) if readable else None,
            "recall": round(good / good_total, 4) if good_total else None,
        })
    ok = [r for r in sweep if r["precision"] is not None and r["precision"] >= target_precision]
    return {
        "lines": len(rows),
        "max_cer_for_readable": max_cer,
        "target_precision": target_precision,
        "by_script": by_script,
        "current_threshold": scorer.threshold,
        "recommended_threshold": ok[0]["threshold"] if ok else None,
        "threshold_sweep": sweep,
    }


def dump_report(report: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
