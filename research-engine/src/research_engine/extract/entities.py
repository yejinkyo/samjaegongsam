"""Entity 태깅 (인물·닉네임·기관·장소·계좌·전화·사건번호·접수번호).

규칙 기반 기준선이다. 라벨링 파일럿에서 F1이 목표에 못 미치면 같은 ``EntityExtractor``
프로토콜로 파인튜닝 모델을 끼운다 (eval/ner_eval.py 참고).
"""

from __future__ import annotations

import itertools
import re
from typing import Protocol

from ..schema import DocumentType, EntityKind, EntityMention, Sourced, TextLine
from . import patterns as P


class EntityExtractor(Protocol):
    def extract_line(self, line: TextLine, doc_type: DocumentType, ids: itertools.count) -> list[EntityMention]: ...


class RuleBasedEntityExtractor:
    def extract_line(self, line: TextLine, doc_type: DocumentType, ids: itertools.count) -> list[EntityMention]:
        text = line.text
        taken: list[tuple[int, int]] = []
        out: list[EntityMention] = []

        def add(kind: EntityKind, s: int, e: int, base: float, normalized: str, role: str | None = None) -> None:
            if s >= e or any(s < te and ts < e for ts, te in taken):
                return
            taken.append((s, e))
            ref = line.ref(s, e)
            out.append(
                EntityMention(
                    mention_id=f"{line.doc_id}:m{next(ids)}",
                    doc_id=line.doc_id,
                    kind=kind,
                    name=Sourced[str].at(ref, text[s:e], round(base * line.span_confidence(s, e), 4)),
                    normalized=normalized,
                    role=role,
                )
            )

        if doc_type in (DocumentType.MESSENGER, DocumentType.TRANSCRIPT):
            m = P.MESSENGER_LINE.match(text) or (
                P.COLON_SPEAKER_LINE.match(text) if doc_type is DocumentType.TRANSCRIPT else None
            )
            if m and not P.TRANSCRIPT_QA.match(text):
                name = m["speaker"].strip()
                if name in ("나", "나 ", "me", "Me"):
                    add(EntityKind.PERSON, m.start("speaker"), m.end("speaker"), 0.9, "나", "사용자")
                else:
                    add(EntityKind.NICKNAME, m.start("speaker"), m.end("speaker"), 0.85, name, "대화 상대")

        for m in P.ACCOUNT.finditer(text):
            acct = m["acct"]
            if sum(ch.isdigit() for ch in acct) < 4 or P.PHONE.fullmatch(acct):
                continue
            add(EntityKind.ACCOUNT, m.start("acct"), m.end("acct"), 0.9, P.normalize_account(acct))
            if m["bank"]:
                add(EntityKind.ORGANIZATION, m.start("bank"), m.end("bank"), 0.8, _bank_name(m["bank"]))
        for m in P.BANK_LABEL.finditer(text):
            add(EntityKind.ORGANIZATION, m.start("bank"), m.end("bank"), 0.8, _bank_name(m["bank"]))
        for m in P.PHONE.finditer(text):
            add(EntityKind.PHONE, m.start("phone"), m.end("phone"), 0.9, P.normalize_account(m["phone"]))
        for pattern, kind, base in (
            (P.CASE_NUMBER, EntityKind.CASE_NUMBER, 0.9),
            (P.RECEIPT_NUMBER, EntityKind.RECEIPT_NUMBER, 0.85),
            (P.CASE_NUMBER_LABEL, EntityKind.CASE_NUMBER, 0.75),
        ):
            for m in pattern.finditer(text):
                add(kind, m.start("no"), m.end("no"), base, P.normalize_mask(re.sub(r"\s", "", m["no"])))
        for m in P.PLACE.finditer(text):
            add(EntityKind.PLACE, m.start("addr"), m.end("addr"), 0.7, re.sub(r"\s+", " ", m["addr"]))
        for m in P.ORG.finditer(text):
            s, name = m.start("name"), m["name"]
            for stop in P.ORG_PREFIX_STOP:
                if name.startswith(stop) and len(name) > len(stop) + 1:
                    s, name = s + len(stop), name[len(stop):]
                    break
            if name == "은행":  # '입금은행' 같은 서식 라벨
                continue
            add(EntityKind.ORGANIZATION, s, s + len(name), 0.75, _org_name(name))
        for m in P.NICKNAME.finditer(text):
            add(EntityKind.NICKNAME, m.start("nick"), m.end("nick"), 0.7, m["nick"])

        for m in P.PERSON_ROLE.finditer(text):
            name = P.strip_particles(m["name"])
            if name in P.NOT_NAMES or any(name.startswith(w) for w in P.NOT_NAMES if len(w) >= 2):
                continue
            role = re.sub(r"\s+", "", m["role"])
            role = None if role in ("성명", "이름") else role
            s = m.start("name")
            add(EntityKind.PERSON, s, s + len(name), 0.8, P.normalize_mask(name), role)
        for m in P.PERSON_AGE.finditer(text):
            add(EntityKind.PERSON, m.start("name"), m.end("name"), 0.7, m["name"])
        for m in P.PERSON_MASKED.finditer(text):
            add(EntityKind.PERSON, m.start("name"), m.end("name"), 0.6, P.normalize_mask(m["name"]))
        for m in P.PERSON_MO.finditer(text):
            add(EntityKind.PERSON, m.start(), m.end(), 0.55, f"{m['sur']}*")
        return out


def _bank_name(raw: str) -> str:
    name = raw.replace("KB", "").replace("NH", "").replace("IBK", "")
    if name in ("카카오뱅크", "토스뱅크", "케이뱅크", "새마을금고", "우체국", "신협", "수협"):
        return name
    return f"{name}은행"


def _org_name(raw: str) -> str:
    name = P.normalize_mask(re.sub(r"\s+", "", raw))
    for abbr, full in P.ORG_ABBREV.items():
        if name.endswith(abbr):
            return name[: -len(abbr)] + full
    return name
