"""출처(provenance) 모델.

proposal.md §7 "출처 없는 문장을 쓰지 않는다"를 데이터 모델 수준에서 강제한다.
모든 추출 값은 ``Sourced[T]``로 감싸며, 문서 id와 (줄 번호 또는 bbox) 없이는 생성 자체가 실패한다.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

T = TypeVar("T")


class BBox(BaseModel):
    """원문 이미지 픽셀 좌표 (좌상단 원점)."""

    model_config = ConfigDict(frozen=True)

    x0: float
    y0: float
    x1: float
    y1: float

    @model_validator(mode="before")
    @classmethod
    def _from_sequence(cls, data):
        """OCR 엔진들이 흔히 쓰는 [x0, y0, x1, y1] 형식도 받는다."""
        if isinstance(data, (list, tuple)) and len(data) == 4:
            return dict(zip(("x0", "y0", "x1", "y1"), data, strict=True))
        return data

    @model_validator(mode="after")
    def _check_order(self) -> BBox:
        if self.x1 < self.x0 or self.y1 < self.y0:
            raise ValueError(f"잘못된 bbox: {self}")
        return self

    @classmethod
    def from_list(cls, v: list[float] | tuple[float, float, float, float]) -> BBox:
        return cls(x0=v[0], y0=v[1], x1=v[2], y1=v[3])

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2

    def union(self, other: BBox) -> BBox:
        return BBox(
            x0=min(self.x0, other.x0),
            y0=min(self.y0, other.y0),
            x1=max(self.x1, other.x1),
            y1=max(self.y1, other.y1),
        )

    def vertical_overlap(self, other: BBox) -> float:
        """두 박스의 세로 겹침 비율 (작은 쪽 높이 기준, 0~1)."""
        overlap = min(self.y1, other.y1) - max(self.y0, other.y0)
        base = min(self.height, other.height) or 1.0
        return max(0.0, overlap) / base


class SourceRef(BaseModel):
    """원문 위치. "어느 문서 몇 번째 줄(또는 어느 영역)에서 왔는가"."""

    source_doc_id: str = Field(min_length=1)
    page: int = Field(default=1, ge=1)
    source_line: int | None = Field(default=None, ge=1, description="문서 전체 기준 줄 번호 (1부터)")
    source_line_end: int | None = Field(default=None, ge=1)
    source_bbox: BBox | None = None
    char_start: int | None = Field(default=None, ge=0)
    char_end: int | None = Field(default=None, ge=0)
    quote: str | None = Field(default=None, description="원문 발췌 (OCR 원문 그대로)")

    @model_validator(mode="after")
    def _require_location(self) -> SourceRef:
        if self.source_line is None and self.source_bbox is None:
            raise ValueError("출처 위치가 없습니다: source_line 또는 source_bbox 중 하나는 반드시 있어야 합니다")
        if (
            self.source_line is not None
            and self.source_line_end is not None
            and self.source_line_end < self.source_line
        ):
            raise ValueError("source_line_end가 source_line보다 앞설 수 없습니다")
        return self

    def ref(self) -> SourceRef:
        """위치 정보만 떼어낸 SourceRef."""
        return SourceRef.model_validate(self.model_dump(include=set(SourceRef.model_fields)))

    def cite(self) -> str:
        if self.source_line is None:
            return self.source_doc_id
        if self.source_line_end and self.source_line_end != self.source_line:
            return f"{self.source_doc_id} · {self.source_line}–{self.source_line_end}줄"
        return f"{self.source_doc_id} · {self.source_line}줄"


class Sourced(SourceRef, Generic[T]):
    """출처와 신뢰도가 붙은 값: ``{value, source_doc_id, source_line/bbox, confidence}``."""

    value: T
    confidence: float = Field(ge=0.0, le=1.0)

    @classmethod
    def at(cls, ref: SourceRef, value: T, confidence: float) -> Sourced[T]:
        return cls(**ref.model_dump(), value=value, confidence=confidence)
