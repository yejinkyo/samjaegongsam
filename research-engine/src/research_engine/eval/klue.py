"""공개 데이터셋 → 이 저장소의 라벨 형식 변환.

파이프라인의 NLI는 직접 만든 픽스처로만 확인해 왔고 수치가 없었다. KLUE NLI(25K/3K)를
`eval-nli`가 읽는 Claim 쌍 라벨로 옮겨 **자유 서술 주장의 모순 감지**를 측정 가능하게 한다.

두 가지를 구분해서 봐야 한다.

- **슬롯 있는 주장**(금액·일시·계좌·이름·결정내용)은 `SlotRuleNli`가 값을 직접 비교한다.
  여기에 텍스트 모델은 쓰지 않는다 — 값 비교가 더 정확하고 근거를 댈 수 있다.
- **슬롯 없는 자유 서술**은 규칙이 판단하지 못한다(`SlotRuleNli.score`가 None).
  `CombinedNli(text=None)`이 기본값이라 현재는 **비교 자체를 하지 않는다.** KLUE NLI는
  이 경로를 재는 데이터다. 그래서 변환 결과의 Claim 은 `slot=None` 이다.

한계를 적어 둔다. KLUE NLI 는 숙박 후기·위키·뉴스 문장이고 우리 입력은 수사 서류다.
여기서 나온 수치는 **"한국어 문장 쌍 판정 능력"의 상한 추정**이지 사건 자료에서의 성능이
아니다. 실제 성능은 사건 자료 라벨(`tests/fixtures/pilot/`)로만 알 수 있다.

라이선스: KLUE 는 CC BY-SA 4.0 이다. 파생물에 같은 조건이 붙으므로, 이 데이터로 학습한
모델을 배포할 때 조건을 확인해야 한다. 변환 결과를 저장소에 커밋하지 않는 이유이기도 하다
(``--out`` 기본 경로는 gitignore 대상인 작업 폴더로 둔다).
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from ..schema import Claim, EvidenceLevel, NliLabel, Sourced, SourceRef

# KLUE NLI 의 ClassLabel 순서. 정수로도 문자열로도 올 수 있어 둘 다 받는다.
KLUE_LABELS: dict[str, NliLabel] = {
    "0": NliLabel.ENTAILMENT,
    "1": NliLabel.NEUTRAL,
    "2": NliLabel.CONTRADICTION,
    "entailment": NliLabel.ENTAILMENT,
    "neutral": NliLabel.NEUTRAL,
    "contradiction": NliLabel.CONTRADICTION,
}


def _claim(guid: str, side: str, text: str, confidence: float) -> Claim:
    """문장 하나를 Claim 으로 감싼다.

    출처가 없는 문장은 이 파이프라인에 넣을 수 없다(`SourceRef` 가 위치를 요구한다).
    데이터셋 행 자체를 문서로 보고 `guid` 를 doc_id, premise/hypothesis 를 1·2줄로 둔다.
    두 Claim 의 doc_id 가 달라야 `candidate_pairs` 가 비교 대상으로 잡는다.
    """
    ref = SourceRef(source_doc_id=f"{guid}:{side}", source_line=1, quote=text)
    return Claim(
        claim_id=f"{guid}:{side}",
        doc_id=f"{guid}:{side}",
        speaker=f"화자{side.upper()}",
        speaker_basis="document_author",
        content=Sourced[str].at(ref, text, confidence),
        slot=None,  # 규칙이 비교하지 못하는 자유 서술 경로를 재기 위해서다
        evidence_level=EvidenceLevel.STATEMENT,
    )


def klue_nli_rows(rows: Iterable[dict[str, Any]], confidence: float = 0.9) -> Iterator[dict[str, Any]]:
    """KLUE NLI 행 → `eval-nli` 라벨(JSON dict). 알 수 없는 라벨은 건너뛴다."""
    for row in rows:
        label = KLUE_LABELS.get(str(row.get("label")).strip().lower())
        premise, hypothesis = row.get("premise"), row.get("hypothesis")
        if label is None or not premise or not hypothesis:
            continue
        guid = row.get("guid") or f"klue-nli-{abs(hash((premise, hypothesis))):x}"
        yield {
            "gold": label.value,
            "min_confidence": confidence,
            "subject_certain": True,  # 같은 문장 쌍을 비교하므로 대상 불확실은 없다
            "a": json.loads(_claim(guid, "a", premise, confidence).model_dump_json()),
            "b": json.loads(_claim(guid, "b", hypothesis, confidence).model_dump_json()),
        }


def load_klue_nli(split: str = "validation", limit: int | None = None, path: str | Path | None = None) -> list[dict[str, Any]]:
    """KLUE NLI 를 읽는다. ``path`` 가 있으면 내려받은 파일(JSONL·Parquet)을, 없으면 허브에서.

    허브에서 받을 때는 ``datasets`` 가 필요하다 (``uv sync --extra data``).
    """
    if path is not None:
        rows = _rows_from_file(Path(path))
    else:
        from datasets import load_dataset

        rows = load_dataset("klue/klue", "nli", split=split)
    out: list[dict[str, Any]] = []
    for row in klue_nli_rows(rows):
        out.append(row)
        if limit is not None and len(out) >= limit:
            break
    return out


def _rows_from_file(path: Path) -> Iterable[dict[str, Any]]:
    if path.suffix in (".jsonl", ".json"):
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            data = json.loads(text)
            return data if isinstance(data, list) else data.get("data", [])
        return [json.loads(r) for r in text.splitlines() if r.strip()]
    if path.suffix == ".parquet":
        import pyarrow.parquet as pq

        return pq.read_table(path).to_pylist()
    raise ValueError(f"지원하지 않는 형식입니다: {path.suffix} (.jsonl · .json · .parquet)")


def write_labels(rows: list[dict[str, Any]], out: str | Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return out
