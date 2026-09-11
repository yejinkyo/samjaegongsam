"""2단계 오케스트레이션: 문서별 기준일 결정 → 줄 단위 시간·엔티티·이벤트·주장 추출."""

from __future__ import annotations

import itertools
import re
from datetime import date

from ..schema import (
    ClaimSlot,
    ClarificationKind,
    ClarificationRequest,
    DocumentType,
    EntityKind,
    ExtractionResult,
    ProcessedDocument,
    Sourced,
    TimeKind,
    TimeValue,
)
from .claims import claims_from_line, document_speaker, line_speaker
from .entities import EntityExtractor, RuleBasedEntityExtractor
from .events import event_from_line, record_event
from .temporal import Anchor, TemporalNormalizer, TimeMatch

DOC_DATE_LABEL = re.compile(
    r"판결\s*선고|선\s*고\s*일?|작성\s*일자?|거래\s*일시|이체\s*일시|거래\s*일자|접수\s*일시|접수\s*일자?|"
    r"발급\s*일자?|발행\s*일자?|신고\s*일시|녹취\s*일시|녹음\s*일시|입력\s*[:：]?"
)
ANCHOR_KINDS = (TimeKind.ABSOLUTE, TimeKind.PARTIAL, TimeKind.RELATIVE, TimeKind.LUNAR)


class Extractor:
    def __init__(
        self,
        normalizer: TemporalNormalizer | None = None,
        entity_extractor: EntityExtractor | None = None,
    ):
        self.normalizer = normalizer
        self.entity_extractor = entity_extractor or RuleBasedEntityExtractor()

    def extract(self, docs: list[ProcessedDocument], as_of: date) -> ExtractionResult:
        normalizer = self.normalizer or TemporalNormalizer(today=as_of)
        result = ExtractionResult()
        for doc in docs:
            self._extract_doc(doc, as_of, normalizer, result)
        return result

    def _document_anchor(
        self, doc: ProcessedDocument, as_of: date, normalizer: TemporalNormalizer
    ) -> tuple[Anchor, Sourced[TimeValue] | None]:
        fallback = (
            Anchor(doc.captured_at.date(), "capture_date") if doc.captured_at else Anchor(as_of, "as_of")
        )
        lines = doc.readable_lines()

        def absolute(ln):
            for m in normalizer.extract(ln.text, fallback):
                if m.value.kind is TimeKind.ABSOLUTE and m.day and not m.value.needs_confirmation:
                    return m
            return None

        candidates = [ln for ln in lines if DOC_DATE_LABEL.search(ln.text)]
        if doc.doc_type in (DocumentType.STATEMENT, DocumentType.COMPLAINT):
            candidates += list(reversed(lines[-5:]))
        for ln in candidates:
            m = absolute(ln)
            if m is not None:
                ref = ln.ref(m.start, m.end)
                return Anchor(m.day, "document_date"), Sourced[TimeValue].at(
                    ref, m.value, round(m.confidence * ln.readability, 4)
                )
        return fallback, None

    def _extract_doc(
        self, doc: ProcessedDocument, as_of: date, normalizer: TemporalNormalizer, result: ExtractionResult
    ) -> None:
        ids = itertools.count(1)
        lines = doc.readable_lines()
        mentions_by_line = {ln.line_no: self.entity_extractor.extract_line(ln, doc.doc_type, ids) for ln in lines}
        all_mentions = [m for ms in mentions_by_line.values() for m in ms]
        result.mentions.extend(all_mentions)

        doc_anchor, doc_date = self._document_anchor(doc, as_of, normalizer)
        if doc_date is not None:
            result.document_dates[doc.doc_id] = doc_date

        default_speaker = document_speaker(doc, all_mentions)
        previous_speaker = None
        message_anchor: Anchor | None = None
        mentioned: Anchor | None = None
        matches_by_line: dict[int, list[TimeMatch]] = {}
        line_events = []
        is_record = doc.doc_type is DocumentType.RECEIPT

        for ln in lines:
            if doc.doc_type is DocumentType.MESSENGER:
                date_line = normalizer.is_date_line(ln.text)
                if date_line is not None:
                    message_anchor = mentioned = Anchor(date_line.day, "message_date")
                    continue
            deictic = message_anchor or doc_anchor
            matches = normalizer.extract(ln.text, deictic, mentioned)
            matches_by_line[ln.line_no] = matches
            result.times.extend(
                Sourced[TimeValue].at(ln.ref(m.start, m.end), m.value, round(m.confidence * ln.readability, 4))
                for m in matches
            )
            for m in matches:
                if m.day and m.value.kind in ANCHOR_KINDS and not m.value.needs_confirmation:
                    mentioned = Anchor(m.day, "mentioned_date")

            speaker, clause_start = line_speaker(ln, doc, default_speaker, previous_speaker, all_mentions)
            previous_speaker = speaker
            said_at = next((m for m in matches if m.end <= clause_start), None) if clause_start else None
            mentions = mentions_by_line[ln.line_no]

            if not is_record:
                ev = event_from_line(ln, clause_start, doc, matches, mentions, said_at, ids)
                if ev is not None:
                    line_events.append(ev)
            claims = claims_from_line(ln, clause_start, speaker, doc, matches, mentions, said_at, ids)
            result.claims.extend(claims)
            self._date_questions(doc, ln.line_no, matches, bool(claims), result)

        if is_record:
            ev = record_event(doc, matches_by_line, all_mentions, ids)
            if ev is not None:
                line_events.append(ev)
        result.events.extend(line_events)
        self._link_subjects(doc.doc_id, result)

    @staticmethod
    def _date_questions(
        doc: ProcessedDocument, line_no: int, matches: list[TimeMatch], used: bool, result: ExtractionResult
    ) -> None:
        """오탈자로 보이는 날짜만 되묻는다 (기준일이 약한 상대 날짜는 고를 보기가 없으므로 제외)."""
        for m in matches:
            v = m.value
            if v.kind not in (TimeKind.CORRECTED, TimeKind.UNRESOLVED) or not (used or doc.doc_type is DocumentType.RECEIPT):
                continue
            options = [c.start.date().isoformat() for c in v.candidates]
            if v.is_resolved and not v.candidates:
                options = [v.start.date().isoformat()]  # type: ignore[union-attr]
            result.clarifications.append(
                ClarificationRequest(
                    request_id=f"{doc.doc_id}:q-date{line_no}-{m.start}",
                    kind=ClarificationKind.AMBIGUOUS_DATE,
                    question=f"'{v.raw}' 이 날짜가 맞나요? 원본 사진을 보고 골라주세요." + (f" ({v.note})" if v.note else ""),
                    doc_id=doc.doc_id,
                    page=doc.line(line_no).page if doc.line(line_no) else 1,  # type: ignore[union-attr]
                    line_no=line_no,
                    bbox=doc.line(line_no).bbox if doc.line(line_no) else None,  # type: ignore[union-attr]
                    options=options + ["모르겠어요"],
                    context=[v.raw],
                    priority=30,
                )
            )

    @staticmethod
    def _link_subjects(doc_id: str, result: ExtractionResult) -> None:
        """같은 문서 안에서 대상이 하나뿐이면 슬롯 주장에 대상(계좌·금액)을 붙여 비교 범위를 좁힌다."""
        claims = [c for c in result.claims if c.doc_id == doc_id]
        account_claims = [c for c in claims if c.slot is ClaimSlot.ACCOUNT_NUMBER]
        deposit = [c for c in account_claims if c.subject == "deposit"]
        accounts = {c.slot_value for c in (deposit or account_claims)}
        if not accounts:
            accounts = {
                m.normalized for m in result.mentions if m.doc_id == doc_id and m.kind is EntityKind.ACCOUNT
            }
        amounts = {c.slot_value for c in claims if c.slot is ClaimSlot.TRANSFER_AMOUNT}
        for c in claims:
            if c.slot is ClaimSlot.ACCOUNT_HOLDER and len(accounts) == 1:
                c.subject = next(iter(accounts))
            elif c.slot is ClaimSlot.TRANSFER_TIME and len(amounts) == 1:
                c.subject = next(iter(amounts))
