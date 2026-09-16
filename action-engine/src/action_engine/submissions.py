"""무엇을 언제 내고 어떤 답을 받았는가.

엔진은 사용자가 무엇을 냈는지 모른다. 그래서 이의제기서를 이미 냈어도 그 행동이
계속 다음 행동으로 뜨고, 낸 뒤 답이 없다는 사실은 어디에도 남지 않는다.
장기 미제 사건에서 **'냈는데 답이 없다'는 그 자체로 다음 행동의 근거**다.

이 모듈이 다루는 것은 날짜와 '자료가 남아 있느냐' 둘뿐이다.

- **며칠이면 늦은 것인지 판단하지 않는다.** 회신 처리기한은 지식베이스에 없다.
  기다린 날수를 세어 그대로 보여줄 뿐, '늦었습니다'라고 쓰지 않는다.
- **낸 사실을 자료로 승격시키지 않는다.** 접수증이 없으면 본인 말뿐이고,
  그건 INF-041(원본 출처 누락)로 남는다. 다른 진술을 다루는 방식과 같다.

판정 규칙은 새로 만들지 않고 이미 있는 INF 코드를 재사용한다. 규칙 평가(``decide``)가
끝난 뒤에 붙이는 뒷단계라서, 여기서 켠 코드가 규칙을 다시 돌리지는 않는다.
회신 통지서를 **자료로 올리면** 그건 기존 파이프라인이 읽어 ST 를 다시 판정한다.
"""

from __future__ import annotations

from datetime import date

from .codes import INF
from .schema import CaseCardOut, CodeHit, Confidence, Submission

SUBMITTED = "제출함"
ANSWERED = "회신옴"


def status_of(sub: Submission) -> str:
    """낸 것 하나의 상태. 답이 왔으면 회신옴, 아니면 제출함."""
    return ANSWERED if sub.response else SUBMITTED


def waiting_days(sub: Submission, as_of: date) -> int | None:
    """낸 날부터 며칠 기다렸는가. 답이 왔으면 세지 않는다(None).

    이 숫자는 사실이지 판단이 아니다. 며칠이 지나야 늦은 것인지는 여기서 정하지 않는다.
    """
    if sub.response:
        return None
    return max((as_of - sub.submitted_at).days, 0)


def _label_of(sub: Submission) -> str:
    """사람이 읽을 이름이 없으면 행동 키를 그대로 쓴다 — 문구를 지어내지 않는다."""
    return sub.action


def apply(card: CaseCardOut, submissions: list[Submission], as_of: date) -> CaseCardOut:
    """낸 기록을 카드에 반영한다. 원본은 건드리지 않고 새 카드를 돌려준다.

    1. 이미 낸 행동은 다음 행동에서 내린다. 참고사항에는 남겨 둔다 — 없앴다가는
       무엇을 냈는지가 화면에서 사라진다. (기한이 지났더라도 마찬가지다.
       낸 뒤에 기한이 지난 것과 안 내고 기한이 지난 것은 다른 상황이다.)
    2. 접수증 없는 제출은 INF-041 로 남긴다.
    3. 답을 기다리는 중이면 INF-042 로 기다린 날수를 남긴다.
    """
    if not submissions:
        return card

    out = card.model_copy(deep=True)
    out.submissions = list(submissions)

    done = {s.action for s in submissions}
    if out.next_action and out.next_action.action in done:
        moved = out.next_action
        nxt = [a for a in out.also if a.action not in done]
        out.next_action = nxt[0] if nxt else None
        # 내린 행동은 참고사항 맨 앞에 둔다 — 방금 낸 것이라 사용자가 제일 먼저 찾는다
        out.also = [moved] + [a for a in out.also if a is not out.next_action]

    for sub in submissions:
        if sub.evidence_doc_id is None:
            out.inf.append(CodeHit(
                code=INF.SOURCE_MISSING,
                label="원본 출처 누락",
                confidence=Confidence.PRESUMED,   # 낸 사실 자체가 사용자의 말이다
                reason=f"{_label_of(sub)} 을(를) {sub.submitted_at:%Y-%m-%d} 에 냈다고 기록했지만, 접수증이 자료함에 없습니다.",
            ))

        days = waiting_days(sub, as_of)
        if days is not None and days > 0:
            out.inf.append(CodeHit(
                code=INF.RECORD_UNCHECKED,
                label="수사 기록 미확인",
                confidence=Confidence.CONFIRMED,   # 날수는 기록에서 바로 나온다
                reason=f"{_label_of(sub)} 을(를) 낸 뒤 {days}일째 회신 자료가 없습니다.",
            ))

    return out
