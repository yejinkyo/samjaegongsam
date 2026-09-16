"""Event 태깅 (행위 + 시각)."""

from __future__ import annotations

import itertools
import re
from datetime import timedelta

from ..schema import (
    GRANULARITY_RANK,
    EntityMention,
    Event,
    EvidenceLevel,
    ProcessedDocument,
    Sourced,
    Stage,
    TextLine,
    TimeGranularity,
    TimeKind,
    TimeValue,
)
from . import patterns as P
from .temporal import TimeMatch

# 발생 단계 안의 행위 종류. 같은 종류끼리만 타임라인에서 합친다
OCCURRENCE_KINDS: list[tuple[str, re.Pattern[str]]] = [
    ("sighting", re.compile(r"목격|마지막(?:으로)?\s*(?:찍|보|확인)|(?:근처|부근|입구|앞|인근)에서\s*(?:보았|봤)")),
    ("contact_lost", re.compile(
        r"연락\s*(?:두절|이?\s*끊|이\s*안\s*(?:되|됐|됨))|전화\s*(?:를\s*)?(?:안\s*받|받지\s*않)")),
    ("disappearance", re.compile(r"실종|가출|행방\s*불명")),
    ("fraud", re.compile(r"사기|편취")),
    ("violence", re.compile(r"폭행|상해")),
    ("harm", re.compile(r"피해를?\s*(?:입|당)")),
    ("dealing", re.compile(r"거래\s*(?:대화|문의)|구매\s*문의|판매\s*중")),
]

# 우선순위 순서: 한 줄에 여러 단서가 있으면 절차상 더 뒤 단계를 택한다 ("신고 접수" → 접수)
STAGE_TRIGGERS: list[tuple[Stage, re.Pattern[str]]] = [
    (Stage.OUTCOME, re.compile(
        r"판결|선고|유죄|무죄|징역|벌금형|집행유예|기소(?!\s*중지)|불기소|불송치|무혐의|혐의\s*없음|각하|기각|"
        r"수사\s*중지|기소\s*중지|사건\s*종결")),
    (Stage.RECEIPT, re.compile(r"접수(?!\s*번호|\s*일시|\s*일자)")),
    (Stage.INVESTIGATION, re.compile(
        r"(?<!재)수사(?!\s*중지|관|팀|대|과|기관|\s*기록|\s*자료)|조사(?!관)|출석|소환|압수|수색|입건|송치|피의자\s*신문")),
    (Stage.REPORT, re.compile(r"신고(?!인|번호)|고소(?!인|장|\s*취지)|고발(?!인)|진정(?!인|서|\s*취지)|112에")),
    # 계좌로 보낸 것만이 아니라 현금을 직접 건넨 경우도 돈이 오간 일이다.
    # 금액이 앞에 있을 때만 잡는다 — '서류를 건넸습니다'까지 끌어오면 안 된다.
    (Stage.TRANSFER, re.compile(
        r"송금|이체(?!\s*금액|\s*일시|\s*확인증)|입금(?!\s*계좌|\s*은행)|"
        r"원\s*(?:을|를)?\s*(?:건네|건넸|건네주|지급|전달|주었|줬)")),
    (Stage.OCCURRENCE, re.compile("|".join(f"(?:{p.pattern})" for _, p in OCCURRENCE_KINDS))),
]
# 문서 자체가 하는 요청 ("재수사를 요청합니다") — 시각은 본문 속 과거 날짜가 아니라 문서 작성일
PETITION = re.compile(r"재수사\s*(?:를|을)?\s*(?:요청|신청)|이의\s*신청|재기\s*신청|(?:고소|고발|진정)\s*(?:합니다|하오니)")
FORMAL_PRESENT = re.compile(r"(?:합니다|하오니|바랍니다|청구함|요청함)\s*\.?\s*$")

RECORD_TITLES: list[tuple[Stage, re.Pattern[str]]] = [
    (Stage.TRANSFER, re.compile(r"이체\s*확인증|송금\s*확인증|거래\s*내역|입출금\s*내역")),
    (Stage.RECEIPT, re.compile(r"접\s*수\s*증|접수\s*확인")),
    (Stage.OUTCOME, re.compile(r"결\s*과\s*통\s*지|처분\s*결과|불송치\s*결정|수사\s*중지\s*결정")),
]
RECORD_TIME_LABEL = re.compile(r"(거래|이체|송금|접수|신고|발급|처리|결정|처분|통지)\s*(일시|일자|시각|일)|일\s*시")
RECORD_AMOUNT_LABEL = re.compile(r"(이체|거래|송금|입금|결제)\s*금액|합\s*계|총\s*액|금\s*액")


def occurrence_kind(clause: str) -> str | None:
    found = [(m.start(), kind) for kind, p in OCCURRENCE_KINDS if (m := p.search(clause))]
    return min(found)[1] if found else None


def find_trigger(clause: str) -> tuple[Stage, re.Match[str]] | None:
    petition = PETITION.search(clause)
    if petition:
        return Stage.REPORT, petition
    for stage, pattern in STAGE_TRIGGERS:
        m = pattern.search(clause)
        if m:
            return stage, m
    return None


PAST_TENSE = re.compile(r"었|았|였|했|됐|냈|봤|왔|갔|렸|쳤|셨|줬")


def message_time(said_at: TimeValue, clause: str) -> TimeValue:
    """시각 없이 말한 일의 시각. 과거형이면 메시지 시각 이전 구간, 아니면 메시지 시각 그대로."""
    return message_time_bound(said_at) if PAST_TENSE.search(clause) else said_at


def message_time_bound(said_at: TimeValue) -> TimeValue:
    """'송금했습니다'처럼 시각 없이 과거형으로 말한 일: 메시지 시각 이전 12시간 안에 일어났다고 본다."""
    return said_at.model_copy(
        update={
            "start": said_at.start - timedelta(hours=12) if said_at.start else None,
            "candidates": [],
            "kind": TimeKind.CONTEXTUAL,
            "approximate": True,
            "note": "메시지를 보낸 시각 이전에 일어난 일로 추정",
        }
    )


def pick_time(matches: list[TimeMatch], lo: int, hi: int, near: int) -> TimeMatch | None:
    inside = [m for m in matches if lo <= m.start and m.end <= hi and (m.value.is_resolved or m.value.candidates)]
    if not inside:
        return None
    # '지난해 10월 10일 밤 11시쯤'처럼 여러 표현이 있으면 하루 이하 입도를 우선, 그다음 가까운 것
    day = GRANULARITY_RANK[TimeGranularity.DAY]
    return min(inside, key=lambda m: (max(GRANULARITY_RANK[m.value.granularity], day), abs(m.start - near)))


def event_from_line(
    line: TextLine,
    clause_start: int,
    doc: ProcessedDocument,
    matches: list[TimeMatch],
    mentions: list[EntityMention],
    said_at: TimeMatch | None,
    ids: itertools.count,
    doc_date: Sourced[TimeValue] | None = None,
) -> Event | None:
    text = line.text
    clause = text[clause_start:]
    found = find_trigger(clause)
    if found is None:
        return None
    stage, trig = found
    after = clause[trig.end():]  # '전화 안받음'처럼 부정이 단서 자체에 들어 있는 경우는 제외하고 본다
    if P.REQUEST_OR_FUTURE.search(after) or P.is_negated(after) or clause.rstrip().endswith("?"):
        return None

    t_start, t_end = clause_start + trig.start(), clause_start + trig.end()
    base = 0.9 if doc.evidence_level is EvidenceLevel.RECORD else 0.8
    action = Sourced[str].at(
        line.ref(clause_start, len(text)), clause.strip(), round(base * line.span_confidence(t_start, t_end), 4)
    )

    time = None
    tm = pick_time(matches, clause_start, len(text), t_start)
    if PETITION.search(clause) and FORMAL_PRESENT.search(clause) and doc_date is not None:
        time = doc_date
    elif tm is not None:
        time = Sourced[TimeValue].at(line.ref(tm.start, tm.end), tm.value, round(tm.confidence * line.readability, 4))
    elif said_at is not None and said_at.value.is_resolved:
        time = Sourced[TimeValue].at(
            line.ref(said_at.start, said_at.end),
            message_time(said_at.value, clause),
            round(said_at.confidence * 0.8 * line.readability, 4),
        )

    amount = None
    for m in P.MONEY.finditer(clause):
        value = P.parse_money(m["num"])
        if value:
            s, e = clause_start + m.start(), clause_start + m.end()
            amount = Sourced[int].at(line.ref(s, e), value, round(0.9 * line.span_confidence(s, e), 4))
            break

    return Event(
        event_id=f"{doc.doc_id}:e{next(ids)}",
        doc_id=doc.doc_id,
        stage=stage,
        action=action,
        time=time,
        amount=amount,
        participant_mention_ids=[mm.mention_id for mm in mentions],
        evidence_level=doc.evidence_level,
        action_kind="petition" if PETITION.search(clause) else occurrence_kind(clause) if stage is Stage.OCCURRENCE else None,
    )


def record_event(
    doc: ProcessedDocument,
    matches_by_line: dict[int, list[TimeMatch]],
    mentions: list[EntityMention],
    ids: itertools.count,
) -> Event | None:
    """이체확인증·접수증 같은 기록 문서는 문서 전체가 하나의 사건이다 (제목=행위, 라벨 줄=시각·금액)."""
    lines = doc.readable_lines()
    title = None
    for ln in lines[:4]:
        for stage, pattern in RECORD_TITLES:
            if pattern.search(ln.text):
                title = (stage, ln)
                break
        if title:
            break
    if title is None:
        return None
    stage, title_line = title

    time = None
    for ln in lines:
        if RECORD_TIME_LABEL.search(ln.text):
            tm = next((m for m in matches_by_line.get(ln.line_no, []) if m.value.is_resolved or m.value.candidates), None)
            if tm is not None:
                time = Sourced[TimeValue].at(ln.ref(tm.start, tm.end), tm.value, round(tm.confidence * ln.readability, 4))
                break

    amount = None
    for ln in lines:
        if RECORD_AMOUNT_LABEL.search(ln.text):
            m = P.MONEY.search(ln.text)
            if m and (value := P.parse_money(m["num"])):
                amount = Sourced[int].at(
                    ln.ref(m.start(), m.end()), value, round(0.95 * ln.span_confidence(m.start(), m.end()), 4)
                )
                break

    return Event(
        event_id=f"{doc.doc_id}:e{next(ids)}",
        doc_id=doc.doc_id,
        stage=stage,
        action=Sourced[str].at(title_line.ref(), title_line.text.strip(), round(0.95 * title_line.readability, 4)),
        time=time,
        amount=amount,
        participant_mention_ids=[m.mention_id for m in mentions],
        evidence_level=doc.evidence_level,
    )
