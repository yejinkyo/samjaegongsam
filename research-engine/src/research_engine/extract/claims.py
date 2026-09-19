"""Claim 태깅 (누가 무엇을 진술했는가) + 구조화 슬롯.

슬롯 값이 있는 주장은 4단계에서 규칙 NLI로 직접 비교되고, 슬롯이 없는 주장은
텍스트 NLI 모델(선택)을 거친다. 기록 문서(이체확인증·판결문)의 내용도 발급 주체의 '주장'으로
표현해 같은 틀에서 대조한다.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass

from ..schema import (
    Claim,
    ClaimSlot,
    DocumentType,
    EntityKind,
    EntityMention,
    Polarity,
    ProcessedDocument,
    Sourced,
    TextLine,
    TimeValue,
)
from . import patterns as P
from .events import STAGE_TRIGGERS, message_time_bound, pick_time
from .temporal import TimeMatch

S = ClaimSlot

# 계좌로 보낸 것만이 아니라 현금을 직접 건넨 경우도 돈이 오간 주장이다.
# 금액이 앞에 있을 때만 잡는다 — '서류를 건넸습니다'까지 끌어오면 안 된다.
TRANSFER_CUE = re.compile(
    r"송금|이체|입금|보냈|보내드렸|부쳤|"
    r"원\s*(?:을|를)?\s*(?:건네|건넸|건네주|지급|전달|주었|줬)"
)
TRANSFER_AMOUNT_LABEL = re.compile(r"(이체|송금|입금|거래)\s*금액")
TRANSFER_TIME_LABEL = re.compile(r"(이체|송금|거래)\s*(일시|일자|시각)")
RECEIPT_TIME_LABEL = re.compile(r"(접수|신고)\s*(일시|일자|일)")
HOLDER = re.compile(
    rf"(?P<label>예금주|받는\s*분|수취인|명의자)\s*(?:은|는|:|：)?\s*(?P<name>[가-힣][가-힣{P.MASK_CLASS}]{{1,4}})"
)
HOLDER_SELF = re.compile(r"(?P<self>제|저의|내|본인)\s*명의")
HOLDER_NAMED = re.compile(rf"(?P<name>[가-힣][가-힣{P.MASK_CLASS}]{{1,3}})\s*(?:씨\s*)?명의")
SHIP_CONTEXT = re.compile(r"택배|물건|상품|배송|발송|송장|출고|편의점\s*택배|반값\s*택배")
SHIP_AFFIRM = re.compile(r"발송\s*(?:했|하였|완료|됐|되었|해\s*드렸)|보냈|부쳤|출고\s*(?:했|됐|되었)")
SHIP_DENY = re.compile(r"발송\s*(?:하지|을\s*안|안\s*했)|안\s*보냈|보내지\s*않|안\s*부쳤")
RECEIVED = re.compile(
    r"(?:물건|상품|택배)\S*\s*(?:을|를|이|가)?\s*(?P<deny>받지\s*못|못\s*받|안\s*왔|오지\s*않|도착하지\s*않)"
    r"|(?:물건|상품|택배)\S*\s*(?:을|를|이|가)?\s*(?P<affirm>받았|도착했)"
)
INVESTIGATOR = re.compile(
    r"담당\s*(?:수사관|형사|경찰관|조사관)\s*(?:은|는|:|：)?\s*(?:경위|경사|경장|순경|경감|경정)?\s*(?P<name>[가-힣]{2,4})"
)
_POLICE_TITLE = r"(?:자|수사관|형사|경찰관|조사관)"
# "담당자 바뀌었다고 함", "담당 형사가 교체됐다"
INVESTIGATOR_CHANGE = re.compile(
    rf"담당\s*{_POLICE_TITLE}?\s*(?:이|가|은|는|도)?\s*(?:또\s*)?(?:바뀌|바꼈|변경|교체|새로\s*(?:왔|배정))"
)
# "새 담당 형사 이름 김영수" — 바뀐 뒤의 담당자
NEW_INVESTIGATOR = re.compile(
    rf"(?:새|새로운|바뀐)\s*담당\s*{_POLICE_TITLE}?\s*(?:이름|성명)?\s*(?:은|는|:|：)?\s*"
    r"(?:경위|경사|경장|순경|경감|경정)?\s*(?P<name>[가-힣]{2,4})"
)
POLICE_ROLES = P.ROLE_GROUPS["police"]
# "판매자는 물건을 보냈다고 하였으나" → 인용 구간의 화자는 판매자
REPORTED = re.compile(
    r"(?P<who>판매자|구매자|피고인|피고소인|피의자|피해자|고소인|상대방|[가-힣]{2,4}?)(?:은|는|이|가|측은)\s+"
    r"(?P<content>[^.。]+?)(?:다고|라고|자고|냐고)\s*(?:하였|했|말했|말하였|주장|진술|얘기|이야기|밝혔|밝히|전했|알렸|설명)"
)
SPEAKER_STOP = {"내용", "사실", "이것", "그것", "자료", "기록", "당시", "이후", "그날"}
LAST_SEEN = re.compile(r"(?:최종|마지막(?:으로)?)\s*(?:목격|찍|확인|모습|보)")
LAST_CONTACT = re.compile(r"연락\s*(?:두절|이?\s*끊|이\s*안\s*(?:되|됐|됨))|까지\s*(?:\S+\s+){0,2}?연락")
DECISION_TIME_LABEL = re.compile(r"(?:결정|처분|통지)\s*일\s*자?")
# 결정 문구. 장기·미제 사건 서류는 대부분 2021년 수사권 조정 전의 것이라 그때 말(기소중지 · 기소유예 ·
# 검사의 참고인중지 · 무혐의 · 송치)도 받는다. 같은 자리에서 여러 갈래가 맞으면 앞 갈래가 이기므로
# '불기소의견 송치'가 '불기소'로 잘리지 않게 송치 문구를 먼저 둔다.
DECISION_TYPE = re.compile(
    r"(?:불기소|기소)\s*의견\s*송치|검찰\s*송치|송치\s*결정|"
    r"수사\s*중지(?:\s*\([^)]*\))?|기소\s*중지|기소\s*유예|참고인\s*중지|피의자\s*중지|"
    r"불송치(?:\s*\([^)]*\))?|불기소(?:\s*\([^)]*\))?|혐의\s*없음|무혐의|내사\s*종결|각하|기각"
)
# 서식의 '죄명' 칸. 서술 속 '사기죄로 고소'는 잡지 않는다 — 칸으로 적힌 값만 죄명으로 쓴다.
OFFENCE_LABEL = re.compile(r"죄\s*명\s*[:：|ㅣ]?\s*(?P<name>[가-힣][가-힣·ㆍ.,\s()]*?)\s*(?:등)?\s*$")
ACCOUNT_IN = re.compile(r"입금|받는|수취|(?:로|으로)\s*(?:[\d,]+\s*만?\s*원\s*(?:을|를)?\s*)?(?:보내|송금|이체|입금)")
ACCOUNT_OUT = re.compile(r"출금|보내는|제\s*계좌에서|내\s*계좌에서")


def decision_base(value: str | None) -> str:
    """'수사중지(피의자중지)' → '수사중지'."""
    return re.sub(r"\(.*?\)|\s", "", value or "")


@dataclass
class Speaker:
    name: str
    basis: str
    mention_id: str | None = None


def document_speaker(doc: ProcessedDocument, mentions: list[EntityMention]) -> Speaker:
    persons = [m for m in mentions if m.kind is EntityKind.PERSON]
    t = doc.doc_type
    if t is DocumentType.STATEMENT:
        who = next((m for m in persons if m.role in ("진술인", None)), None)
        return Speaker(who.normalized, "document_author", who.mention_id) if who else Speaker("진술인", "document_author")
    if t is DocumentType.COMPLAINT:
        who = next((m for m in persons if m.role in ("고소인", "진정인", "고발인")), None)
        return Speaker(who.normalized, "document_author", who.mention_id) if who else Speaker("고소인", "document_author")
    if t is DocumentType.JUDGMENT:
        return Speaker("법원(판결문)", "document_issuer")
    if t in (DocumentType.RECEIPT, DocumentType.NOTICE):
        org = next((m for m in mentions if m.kind is EntityKind.ORGANIZATION), None)
        return Speaker(org.normalized if org else f"{doc.file_name} 발급처", "document_issuer",
                       org.mention_id if org else None)
    if t in (DocumentType.MEMO, DocumentType.USER_NOTE):
        return Speaker("나", "document_author")
    if t is DocumentType.NEWS:
        return Speaker("보도", "document_author")
    return Speaker("작성자 미상", "document_author")


def line_speaker(
    line: TextLine, doc: ProcessedDocument, default: Speaker, previous: Speaker | None, mentions: list[EntityMention]
) -> tuple[Speaker, int]:
    """(화자, 발화 본문 시작 오프셋)."""
    text = line.text
    if doc.doc_type is DocumentType.MESSENGER:
        m = P.MESSENGER_LINE.match(text)
        if m:
            name = m["speaker"].strip()
            mid = next((mm.mention_id for mm in mentions if mm.name.char_start == m.start("speaker")), None)
            return Speaker(name, "message_prefix", mid), m.start("msg")
        return (previous or default), 0
    if doc.doc_type is DocumentType.TRANSCRIPT:
        qa = P.TRANSCRIPT_QA.match(text)
        if qa:
            name = "질문자" if qa["qa"] in ("문", "질문") else default.name
            return Speaker(name, "transcript_prefix"), qa.start("msg")
        m = P.COLON_SPEAKER_LINE.match(text)
        if m:
            return Speaker(m["speaker"], "transcript_prefix"), m.start("msg")
        return (previous or default), 0
    return default, 0


def claims_from_line(
    line: TextLine,
    clause_start: int,
    speaker: Speaker,
    doc: ProcessedDocument,
    matches: list[TimeMatch],
    mentions: list[EntityMention],
    said_at: TimeMatch | None,
    ids: itertools.count,
) -> list[Claim]:
    text = line.text
    clause = text[clause_start:]
    is_question = clause.rstrip().endswith("?")
    is_request = bool(P.REQUEST_OR_FUTURE.search(clause))
    base = 0.9 if doc.evidence_level.value == "record" else 0.85
    out: list[Claim] = []
    reported = [
        (clause_start + m.start("content"), clause_start + m.end("content"), m["who"])
        for m in REPORTED.finditer(clause)
        if m["who"] not in SPEAKER_STOP
    ]

    def add(
        slot: ClaimSlot | None,
        s: int,
        e: int,
        value: str | None = None,
        slot_time: TimeValue | None = None,
        polarity: Polarity = Polarity.AFFIRM,
        self_value: bool = False,
        conf_factor: float = 1.0,
        subject: str | None = None,
    ) -> None:
        conf = round(base * conf_factor * line.span_confidence(s, e), 4)
        who = next((r for r in reported if r[0] <= s and e <= r[1]), None)
        name, basis, mention_id = (who[2], "reported_speech", None) if who else (
            speaker.name, speaker.basis, speaker.mention_id
        )
        if self_value:
            value = name
        out.append(
            Claim(
                claim_id=f"{doc.doc_id}:c{next(ids)}",
                doc_id=doc.doc_id,
                speaker=name,
                speaker_basis=basis,
                speaker_mention_id=mention_id,
                content=Sourced[str].at(line.ref(clause_start, len(text)), clause.strip(), conf),
                slot=slot,
                slot_value=value,
                slot_time=slot_time,
                value_is_speaker_self=self_value,
                subject=subject,
                polarity=polarity,
                said_at=said_at.value if said_at else None,
                evidence_level=doc.evidence_level,
            )
        )

    if is_question:
        return out

    transfer_cue = TRANSFER_CUE.search(clause) and not SHIP_CONTEXT.search(clause)
    amount_label = TRANSFER_AMOUNT_LABEL.search(clause)
    if (transfer_cue and not is_request) or amount_label:
        for m in P.MONEY.finditer(clause):
            value = P.parse_money(m["num"])
            if value:
                neg = Polarity.DENY if P.is_negated(clause[m.end():]) else Polarity.AFFIRM
                add(S.TRANSFER_AMOUNT, clause_start + m.start(), clause_start + m.end(), str(value), polarity=neg)

    time_label = TRANSFER_TIME_LABEL.search(clause)
    if (transfer_cue and not is_request and not P.is_negated(clause)) or time_label:
        tm = pick_time(matches, clause_start, len(text), clause_start)
        if tm is not None:
            add(S.TRANSFER_TIME, tm.start, tm.end, tm.value.iso(), slot_time=tm.value,
                conf_factor=tm.confidence / 0.95)
        elif said_at is not None and said_at.value.is_resolved and transfer_cue:
            add(S.TRANSFER_TIME, said_at.start, said_at.end, None, slot_time=message_time_bound(said_at.value),
                conf_factor=0.7)

    for mm in mentions:
        s, e = mm.name.char_start or 0, mm.name.char_end or 0
        if s < clause_start:
            continue
        if mm.kind is EntityKind.ACCOUNT:
            role = "deposit" if ACCOUNT_IN.search(clause) else "withdrawal" if ACCOUNT_OUT.search(clause) else None
            add(S.ACCOUNT_NUMBER, s, e, mm.normalized, subject=role)
        elif mm.kind is EntityKind.RECEIPT_NUMBER:
            add(S.RECEIPT_NUMBER, s, e, mm.normalized)
        elif mm.kind is EntityKind.CASE_NUMBER:
            add(S.CASE_NUMBER, s, e, mm.normalized)
        elif mm.kind is EntityKind.PERSON and mm.role and re.sub(r"\s", "", mm.role) in POLICE_ROLES:
            add(S.INVESTIGATOR, s, e, mm.normalized)

    for m in HOLDER.finditer(clause):
        name = P.strip_particles(m["name"])
        if name in P.NOT_NAMES:
            continue
        s = clause_start + m.start("name")
        neg = Polarity.DENY if P.is_negated(clause[m.end():]) else Polarity.AFFIRM
        add(S.ACCOUNT_HOLDER, s, s + len(name), P.normalize_mask(name), polarity=neg)
    if not any(c.slot is S.ACCOUNT_HOLDER for c in out):
        m = HOLDER_SELF.search(clause)
        if m:
            neg = Polarity.DENY if P.is_negated(clause[m.end():]) else Polarity.AFFIRM
            add(S.ACCOUNT_HOLDER, clause_start + m.start(), clause_start + m.end(), speaker.name,
                polarity=neg, self_value=True)
        else:
            for m in HOLDER_NAMED.finditer(clause):
                name = m["name"]
                if name in P.NOT_NAMES or name in ("제", "본인", "저의"):
                    continue
                neg = Polarity.DENY if P.is_negated(clause[m.end():]) else Polarity.AFFIRM
                add(S.ACCOUNT_HOLDER, clause_start + m.start("name"), clause_start + m.end("name"),
                    P.normalize_mask(name), polarity=neg)

    if SHIP_CONTEXT.search(clause) and not is_request:
        deny = SHIP_DENY.search(clause)
        affirm = SHIP_AFFIRM.search(clause)
        if deny:
            add(S.SHIPMENT_SENT, clause_start + deny.start(), clause_start + deny.end(), "true", polarity=Polarity.DENY)
        elif affirm:
            add(S.SHIPMENT_SENT, clause_start + affirm.start(), clause_start + affirm.end(), "true")
        for m in RECEIVED.finditer(clause):
            pol = Polarity.DENY if m["deny"] else Polarity.AFFIRM
            add(S.ITEM_RECEIVED, clause_start + m.start(), clause_start + m.end(), "true", polarity=pol)

    for m in P.TRACKING_NUMBER.finditer(clause):
        add(S.TRACKING_NUMBER, clause_start + m.start("no"), clause_start + m.end("no"), re.sub(r"\D", "", m["no"]))

    change = INVESTIGATOR_CHANGE.search(clause)
    if change and not is_request and not P.is_negated(clause[change.end():]):
        # 바뀐 사실 자체는 시각이 흐려도 유효하므로 시각 신뢰도로 깎지 않는다
        tm = pick_time(matches, clause_start, len(text), clause_start + change.start())
        add(S.INVESTIGATOR_CHANGE, clause_start + change.start(), clause_start + change.end(), "changed",
            slot_time=tm.value if tm else None)
    for m in NEW_INVESTIGATOR.finditer(clause):
        name = P.strip_particles(m["name"])
        if name not in P.NOT_NAMES and not any(c.slot is S.INVESTIGATOR for c in out):
            s = clause_start + m.start("name")
            add(S.INVESTIGATOR, s, s + len(name), name)
    for m in INVESTIGATOR.finditer(clause):
        if m["name"] not in P.NOT_NAMES and not any(c.slot is S.INVESTIGATOR for c in out):
            add(S.INVESTIGATOR, clause_start + m.start("name"), clause_start + m.end("name"), m["name"])

    def timed(slot: ClaimSlot, cue: re.Match[str] | None) -> None:
        if cue is None:
            return
        tm = pick_time(matches, clause_start, len(text), clause_start + cue.start())
        if tm is not None:
            add(slot, tm.start, tm.end, tm.value.iso(), slot_time=tm.value, conf_factor=tm.confidence / 0.95)

    if not is_request:
        timed(S.LAST_SEEN_TIME, LAST_SEEN.search(clause))
        timed(S.LAST_CONTACT_TIME, LAST_CONTACT.search(clause))
    decision_cue = DECISION_TIME_LABEL.search(clause) or (
        STAGE_TRIGGERS[0][1].search(clause) if doc.doc_type is DocumentType.NOTICE else None
    )
    timed(S.DECISION_TIME, decision_cue)
    if doc.doc_type is DocumentType.NOTICE or re.search(r"결정|처분|통지", clause):
        for m in DECISION_TYPE.finditer(clause):
            add(S.DECISION_TYPE, clause_start + m.start(), clause_start + m.end(), re.sub(r"\s", "", m.group(0)))
            break

    offence = OFFENCE_LABEL.search(clause)
    if offence:
        name = re.sub(r"\s+", " ", offence["name"]).strip(" ,.")
        s = clause_start + offence.start("name")
        add(S.OFFENCE, s, s + len(offence["name"]), name)

    receipt_label = RECEIPT_TIME_LABEL.search(clause)
    receipt_trigger = STAGE_TRIGGERS[1][1].search(clause)
    if receipt_label or (receipt_trigger and not is_request and not P.is_negated(clause)):
        tm = pick_time(matches, clause_start, len(text), clause_start)
        if tm is not None:
            add(S.RECEIPT_TIME, tm.start, tm.end, tm.value.iso(), slot_time=tm.value, conf_factor=tm.confidence / 0.95)

    occurrence = STAGE_TRIGGERS[-1][1].search(clause)
    if occurrence and not is_request:
        tm = pick_time(matches, clause_start, len(text), clause_start + occurrence.start())
        if tm is not None:
            add(S.INCIDENT_TIME, tm.start, tm.end, tm.value.iso(), slot_time=tm.value, conf_factor=tm.confidence / 0.95)

    if not out and doc.evidence_level.value != "record" and clause.strip() and not is_request:
        has_signal = any(p.search(clause) for _, p in STAGE_TRIGGERS) or any(
            (mm.name.char_start or 0) >= clause_start and mm.kind is not EntityKind.PERSON for mm in mentions
        )
        if has_signal or SHIP_CONTEXT.search(clause):
            add(None, clause_start, len(text))
    return out
