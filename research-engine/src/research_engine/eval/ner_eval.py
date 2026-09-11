"""Entity·시간 표현 추출 정확도 파일럿 평가.

골드 형식 (JSONL, 줄 하나 = 문서 하나. ``doc``은 골드 파일 기준 상대 경로의 OCR JSON)::

    {"doc": "docs/judgment01.json", "doc_type": "judgment", "as_of": "2026-06-24",
     "entities": [{"line_no": 3, "text": "김○○", "kind": "person"}],
     "times": [{"line_no": 5, "text": "2019. 3. 5.", "start": "2019-03-05T00:00", "end": "2019-03-06T00:00"}]}

OCR 오류와 추출 오류를 분리해 보려면 ``doc``에 정답 전사로 만든 OCR JSON(신뢰도 1.0)을 넣는다.
엔티티 F1이 목표에 못 미치는 유형은 ``finetune_recommended``로 표시된다.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from ..extract.extractor import Extractor
from ..ingest import DocumentIngestor, load_ocr_document
from ..schema import DocumentType, EntityKind
from .metrics import PRF


class GoldEntity(BaseModel):
    line_no: int
    text: str
    kind: EntityKind


class GoldTime(BaseModel):
    line_no: int
    text: str
    start: datetime | None = None
    end: datetime | None = None


class GoldDocument(BaseModel):
    doc: str
    doc_type: DocumentType | None = None
    as_of: date | None = None
    entities: list[GoldEntity] = Field(default_factory=list)
    times: list[GoldTime] = Field(default_factory=list)


def _overlap(a: str, b: str) -> bool:
    a, b = a.replace(" ", ""), b.replace(" ", "")
    return bool(a) and bool(b) and (a in b or b in a)


def evaluate_extraction(gold_path: str | Path, target_f1: float = 0.85, default_as_of: date | None = None) -> dict:
    gold_path = Path(gold_path)
    golds = [GoldDocument.model_validate_json(r) for r in gold_path.read_text(encoding="utf-8").splitlines() if r.strip()]
    ingestor, extractor = DocumentIngestor(), Extractor()
    strict: dict[str, PRF] = {}
    partial: dict[str, PRF] = {}
    time_detect, time_norm_ok, time_norm_total = PRF(), 0, 0

    for gold in golds:
        ocr = load_ocr_document(gold_path.parent / gold.doc)
        if gold.doc_type is not None:
            ocr = ocr.model_copy(update={"doc_type_hint": gold.doc_type})
        doc = ingestor.ingest(ocr).document
        result = extractor.extract([doc], gold.as_of or default_as_of or date.today())

        predicted = [(m.name.source_line, m.kind.value, m.name.value) for m in result.mentions]
        for kind in {e.kind.value for e in gold.entities} | {p[1] for p in predicted}:
            g = [(e.line_no, e.text) for e in gold.entities if e.kind.value == kind]
            p = [(line, text) for line, k, text in predicted if k == kind]
            s, pa = strict.setdefault(kind, PRF()), partial.setdefault(kind, PRF())
            s_hit = {x for x in p if x in g}
            s.tp += len(s_hit)
            s.fp += len(p) - len(s_hit)
            s.fn += len([x for x in g if x not in p])
            used = set()
            for gl, gt in g:
                match = next((i for i, (pl, pt) in enumerate(p) if i not in used and pl == gl and _overlap(pt, gt)), None)
                if match is None:
                    pa.fn += 1
                else:
                    used.add(match)
                    pa.tp += 1
            pa.fp += len(p) - len(used)

        used = set()
        for gt in gold.times:
            match = next(
                (i for i, t in enumerate(result.times)
                 if i not in used and t.source_line == gt.line_no and _overlap(t.quote or "", gt.text)),
                None,
            )
            if match is None:
                time_detect.fn += 1
                continue
            used.add(match)
            time_detect.tp += 1
            if gt.start is not None:
                time_norm_total += 1
                v = result.times[match].value
                time_norm_ok += int(v.start == gt.start and v.end == gt.end)
        time_detect.fp += len(result.times) - len(used)

    return {
        "documents": len(golds),
        "target_f1": target_f1,
        "entities": {
            kind: {
                "strict": strict[kind].as_dict(),
                "partial": partial[kind].as_dict(),
                "finetune_recommended": strict[kind].f1 < target_f1,
            }
            for kind in sorted(strict)
        },
        "times": {
            "detection": time_detect.as_dict(),
            "normalization_accuracy": round(time_norm_ok / time_norm_total, 4) if time_norm_total else None,
            "normalization_evaluated": time_norm_total,
        },
    }


def dump_report(report: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
