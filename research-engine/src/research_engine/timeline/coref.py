"""엔티티 coreference: 여러 자료의 같은 인물·계좌·기관을 하나로 묶는다.

잘못 합치면 없는 모순이 생긴다. 그래서 확실한 경우(정규화 값 일치, 충분히 겹치는 마스킹 계좌,
역할 묶음이 같은 마스킹 이름)만 병합하고, 애매하면 ``possible_same_as`` 링크로만 남겨
'동일인 여부 확인 필요'로 흘려보낸다.
"""

from __future__ import annotations

import re

from ..extract.patterns import ROLE_GROUPS, normalize_mask
from ..schema import EntityKind, EntityLink, EntityMention, ResolvedEntity

GENERIC_ORGS = {"경찰서", "법원", "검찰청", "지구대", "파출소", "은행", "구청", "시청", "사이버수사대", "사이버수사팀"}


def mask_compatible(a: str, b: str, min_known: int = 4) -> tuple[bool, int]:
    """같은 길이의 마스킹 문자열이 모순 없이 겹치는가, 그리고 둘 다 보이는 자리가 몇 개인가."""
    if len(a) != len(b):
        return False, 0
    known = 0
    for x, y in zip(a, b, strict=True):
        if x == "*" or y == "*":
            continue
        if x != y:
            return False, 0
        known += 1
    return known >= min_known, known


def role_group(role: str | None) -> str | None:
    if not role:
        return None
    role = re.sub(r"\s", "", role)
    return next((g for g, members in ROLE_GROUPS.items() if role in members), None)


def name_compatible(a: str, b: str) -> str | None:
    """'exact' | 'masked' | None."""
    if a == b:
        return "exact" if "*" not in a else "masked"
    if "*" not in a and "*" not in b:
        return None
    if a.endswith("*") and len(a) == 2 and b[:1] == a[:1]:  # '이모씨' → '이*'
        return "masked"
    ok, _ = mask_compatible(a, b, min_known=1)
    return "masked" if ok else None


class _UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.conf = [1.0] * n

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, i: int, j: int, conf: float) -> None:
        ri, rj = self.find(i), self.find(j)
        if ri != rj:
            self.parent[rj] = ri
            self.conf[ri] = min(self.conf[ri], self.conf[rj], conf)


class CoreferenceResolver:
    def resolve(self, mentions: list[EntityMention]) -> tuple[list[ResolvedEntity], dict[str, str]]:
        uf = _UnionFind(len(mentions))
        links: list[tuple[int, int, float, str]] = []

        for i, a in enumerate(mentions):
            for j in range(i + 1, len(mentions)):
                b = mentions[j]
                if not self._same_family(a.kind, b.kind):
                    continue
                decision = self._compare(a, b)
                if decision is None:
                    continue
                kind, conf, reason = decision
                if kind == "merge":
                    uf.union(i, j, conf)
                else:
                    links.append((i, j, conf, reason))

        clusters: dict[int, list[int]] = {}
        for i in range(len(mentions)):
            clusters.setdefault(uf.find(i), []).append(i)

        entities: list[ResolvedEntity] = []
        mention_to_entity: dict[str, str] = {}
        root_to_entity: dict[int, str] = {}
        for n, (root, members) in enumerate(sorted(clusters.items(), key=lambda kv: kv[1][0]), start=1):
            ms = [mentions[k] for k in members]
            entity_id = f"ent{n}"
            root_to_entity[root] = entity_id
            canonical = max(ms, key=lambda m: (m.normalized.count("*") == 0, len(m.normalized), m.name.confidence))
            entities.append(
                ResolvedEntity(
                    entity_id=entity_id,
                    kind=canonical.kind,
                    canonical_name=canonical.normalized,
                    aliases=sorted({m.name.value for m in ms}),
                    roles=sorted({m.role for m in ms if m.role}),
                    mention_ids=[m.mention_id for m in ms],
                    sources=[m.name.ref() for m in ms],
                    merge_confidence=round(uf.conf[root], 4),
                )
            )
            for m in ms:
                mention_to_entity[m.mention_id] = entity_id

        by_id = {e.entity_id: e for e in entities}
        seen: set[tuple[str, str]] = set()
        for i, j, conf, reason in sorted(links, key=lambda x: -x[2]):  # 같은 엔티티 쌍이면 가장 강한 근거만
            ea, eb = root_to_entity[uf.find(i)], root_to_entity[uf.find(j)]
            pair = (min(ea, eb), max(ea, eb))
            if ea == eb or pair in seen:
                continue
            seen.add(pair)
            by_id[ea].possible_same_as.append(EntityLink(other_entity_id=eb, confidence=conf, reason=reason))
            by_id[eb].possible_same_as.append(EntityLink(other_entity_id=ea, confidence=conf, reason=reason))
        return entities, mention_to_entity

    @staticmethod
    def _same_family(a: EntityKind, b: EntityKind) -> bool:
        people = {EntityKind.PERSON, EntityKind.NICKNAME}
        return a == b or (a in people and b in people)

    def _compare(self, a: EntityMention, b: EntityMention) -> tuple[str, float, str] | None:
        if a.kind is EntityKind.ACCOUNT or a.kind is EntityKind.PHONE:
            if a.normalized == b.normalized:
                return "merge", 0.95, "번호 일치"
            ok, known = mask_compatible(a.normalized, b.normalized)
            if ok:
                return "merge", 0.85, f"마스킹 번호 {known}자리 일치"
            if mask_compatible(a.normalized, b.normalized, min_known=1)[0]:
                return "link", 0.4, "보이는 자리가 적어 같은 번호인지 확인되지 않음"
            return None

        if a.kind in (EntityKind.CASE_NUMBER, EntityKind.RECEIPT_NUMBER):
            if a.normalized == b.normalized and "*" not in a.normalized:
                return "merge", 0.95, "번호 일치"
            if mask_compatible(a.normalized, b.normalized, min_known=4)[0]:
                return "link", 0.6, "마스킹된 번호라 같은 사건인지 확인되지 않음"
            return None

        if a.kind is EntityKind.ORGANIZATION:
            if a.normalized == b.normalized and a.normalized not in GENERIC_ORGS:
                return "merge", 0.9, "기관명 일치"
            for generic, specific in ((a.normalized, b.normalized), (b.normalized, a.normalized)):
                if generic in GENERIC_ORGS and specific != generic and specific.endswith(generic):
                    return "link", 0.4, "일반 명칭이라 같은 기관인지 확인되지 않음"
            masked = "*" in a.normalized or "*" in b.normalized
            if masked and mask_compatible(normalize_mask(a.normalized), normalize_mask(b.normalized), 2)[0]:
                return "link", 0.5, "마스킹된 기관명"
            return None

        if a.kind is EntityKind.PLACE:
            return ("merge", 0.85, "주소 일치") if a.normalized == b.normalized else None

        # 인물·닉네임
        if a.kind is EntityKind.NICKNAME or b.kind is EntityKind.NICKNAME:
            if a.kind == b.kind and a.normalized == b.normalized:
                return "merge", 0.9, "같은 닉네임"
            if a.kind != b.kind and role_group(a.role) and role_group(a.role) == role_group(b.role):
                return "link", 0.4, "닉네임과 실명이 같은 사람인지 확인되지 않음"
            return None
        match = name_compatible(a.normalized, b.normalized)
        ga, gb = role_group(a.role), role_group(b.role)
        if match == "exact":
            if ga and gb and ga != gb:
                return "link", 0.5, "이름은 같지만 역할이 달라 동명이인일 수 있음"
            return "merge", 0.9, "이름 일치"
        if match == "masked":
            if ga and ga == gb:
                return "merge", 0.75, "마스킹된 이름과 역할이 일치"
            return "link", 0.45, "마스킹된 이름이라 같은 사람인지 확인되지 않음"
        return None
