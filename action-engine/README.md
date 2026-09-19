# action-engine

기능 2 **다음 행동 강령**의 백엔드. `research-engine`(기능 1)이 "무엇이 비어 있는가"까지 하고 멈춘 자리에서 이어받는다.

```
research-engine ──ActionTrigger──▶ action-engine ──ActionDecision──▶ case-card
  무엇이 비어 있는가                 무엇을 해야 하는가                  화면
```

`research-engine`을 import 하지 않는다. 출력 JSON(dict)만 받는다. 두 패키지를 따로 설치·테스트할 수 있고, 저쪽 스키마가 바뀌어도 `mapping.py` 한 곳만 고치면 된다.

## 실행

```bash
cd action-engine
uv sync
uv run pytest
```

```python
import json
from action_engine import build_card

result = json.load(open("result.json", encoding="utf-8"))   # research-engine 출력
card = build_card(result)

print(card.case_type_label)          # 실종 사건 · 수사중지
print(card.st.code)                  # ST-201
print(card.next_action.rule_no)      # 5
print(card.next_action.action)       # ACT-신규정보제출
print(card.next_action.why)          # 새 정보는 중지·종결된 절차를 되살릴 수 있다
print(card.procedure)                # None — 지식베이스가 붙기 전까지
```

## 연동 계약

`research-engine`이 `schema/analysis.py`에 선언한 두 창구를 그대로 씁니다.

> 이 스키마는 기능 2(나의 사건 카드)와 행동 강령 매칭 엔진이 **그대로 소비하도록** 설계했다.

### `CaseCard` → `CaseCardOut`

`build_card()`는 `CaseCard`를 **손대지 않고 통과시키고** 기능 2가 판정한 값을 덧붙입니다. 화면은 이 객체 하나만 읽으면 되고 `research-engine` 출력을 따로 뒤지지 않습니다.

```
research-engine ──CaseCard + ActionTrigger[]──▶ action-engine ──CaseCardOut──▶ 화면
```

| 통과시키는 것 | 덧붙이는 것 |
|---|---|
| `case_type_label` · `stages` · `current_stage` | `st` · `inf` · `tim` |
| `evidence_doc_count` · `slots_done`/`slots_total` | `next_action` · `also` |
| `requirements_status` · `needs_confirmation_count` | `procedure` (항상 `None`) |

`research-engine`이 고른 `next_trigger`는 `source_trigger`에 원본 그대로 남깁니다. 우리 판정과 대조할 수 있게 하기 위해서입니다.

### `ActionTrigger`를 1급 입력으로

`inf_from_triggers()`는 `action_triggers[]`만 받아 INF를 판정합니다. `issues[]` 전체를 뒤지지 않아도 되고, 트리거에 판정에 필요한 것이 다 들어 있습니다(`condition` · `stage` · `slot` · `since` · `elapsed_days` · `evidence`).

`basis_from_triggers()`는 `since`("기한 계산용"으로 선언된 필드)로 기산일을 채웁니다.

다만 트리거에는 사람이 읽을 메시지와 화자 정보가 없어서, 화면 문장까지 필요하면 `resolve_inf()`를 씁니다. 두 경로가 같은 코드를 내는지는 `test_트리거_판정은_issues_판정과_어긋나지_않는다`가 확인합니다.

## 세 단계

### 1. 매핑 — `mapping.py`

두 코드 체계가 다르다. `research-engine`은 `Stage` 6종(발생·송금·신고·접수·수사·결과)까지만 알고, 그 "결과"가 불송치인지 수사중지인지는 구분하지 않는다. 대신 **`decision_type` 슬롯에 결정 내용을 문자열로 뽑아 준다** — 그 값으로 ST를 가른다.

| research-engine | → | action-engine |
|---|---|---|
| `decision_type` 값 | | `ST` 12종 |
| `GapCondition` 12종 | | `INF` 10종 |
| `doc_type` | | `INF-01*` (신규 정보 유입) |

`identity_unconfirmed`처럼 대응 코드가 없는 조건은 **억지로 옮기지 않는다.** 판정할 수 없으면 `ST-UNKNOWN`을 내보내고 사용자에게 되묻는다.

### 2. 규칙 — `data/rules.json`

조합표(if-else 나열)나 가중치를 쓰지 않는다. 경우의 수가 **1,572,864개**(ST 12 × INF 2¹⁰ × TIM 2⁷)라 나열이 불가능하다. 우선순위 13줄(0~12번)로 덮는다.

순서는 하나의 원칙에서 도출된다.

> **놓치면 영원히 못 하는 것 → 시간이 걸리는 것 → 나중에도 할 수 있는 것**

그래서 방어할 것이 열 개가 아니라 원칙 하나다. 새 코드가 생기면 줄을 하나 추가하고, 생각이 바뀌면 줄 순서만 바꾼다.

평가기가 하는 일은 셋뿐이다 — 규칙을 순서대로 훑고, 먼저 맞는 하나를 메인으로 고르고, **발화한 규칙 번호를 결과에 같이 실어 보낸다.** 세 번째가 설명 가능성의 전부다.

단계 전용 줄이 둘 있다.

- **0번 — 재판 · 확정 · 재심(ST-401 · 402 · 403)은 범위 밖이다.** 재판이 시작되면 절차는 법원이 진행한다. `stop` 이 붙어 있어 이 줄이 맞으면 뒤의 규칙을 보지 않는다 — 새 정보가 있어도 '수사기관에 제출'을 참고사항으로 띄우지 않는다. 화면에는 범위 밖이라는 사실과 피해자가 쓸 수 있는 법원 · 검찰 경로(공판기록 열람·등사 제294조의4, 진술 신청 제294조의2, 확정기록 열람 제59조의2)만 알린다. 재심은 피해자에게 청구권이 없다(제424조). 수사 단계의 기한(TIM-021 · 031 · 041 · 042)도 붙이지 않는다(`except_st`) — 공소가 제기되면 시효가 정지된다(제253조 제1항).
- **11번 — 수사 중(ST-101 · 102 · 103)이면 진행상황 확인.** 아직 불복할 결정이 없다. 경찰 수사 중이면 수사 진행상황 통지 요청(경찰수사규칙 제11조), 검찰 수사 중이면 형사사법포털 조회(수사준칙 제12조), 입건 전이면 고소(형사소송법 제237조)와 불입건 통지(수사준칙 제16조)를 안내한다. 새 정보 · 모순이 있으면 6~10번이 먼저다 — 수사 중인 사건에 자료·의견을 내는 것(수사준칙 제25조)은 맞는 경로다.

### 3. 기한 — `data/deadlines.json` · `data/offences.json`

법령 원문에서 확인한 값을 채웠다. 파일 상태는 `draft_unverified` — **법률 전문가 검수 전**이다.

| 코드 | 기한 | 근거 |
|---|---|---|
| `TIM-011` 불송치 이의신청 | **법정 기한 없음** (`no_statutory_limit`) | 형사소송법 제245조의7 |
| `TIM-012` 항고 (검사의 불기소 · 기소중지 · 참고인중지) | 30일 | 검찰청법 제10조 · 검찰사건사무규칙 제147조 |
| `TIM-013` 재정신청 | 10일 | 형사소송법 제260조 제3항 |
| `TIM-014` 수사중지 이의제기 (사법경찰관의 결정) | 30일 | 경찰수사규칙 제101조 |
| `TIM-021` 공소시효 | 가장 최근 통지서의 죄명 · 범행 종료일로 계산 (`limitation.py`) — 초일 산입 | 형사소송법 제249조 · 제66조 |
| `TIM-031` 디지털 데이터 보존 | 90일 — 메신저 대화 · 마지막 연락 가운데 **다음으로 사라질 기록**의 날부터 | 통신비밀보호법 시행령 제41조 |
| `TIM-041` · `TIM-042` 상시 진정·자료 제출 / 정보공개청구 | 기한 없음 | — / 정보공개법 |

지키는 원칙은 네 가지다. 각각 테스트가 고정한다.

- **값이 `null`이면 D-day를 만들지 않고** `unresolved`에 이유를 적는다 — `test_기한값이_비어있으면_Dday를_만들지_않는다`
- **"법정 기한 없음"과 "아직 못 채움"을 구별한다.** 앞의 것은 사용자에게 필요한 정보이고 뒤의 것은 화면에 띄우면 안 된다 — `test_기한없음과_못채움을_구별한다`
- **값을 넣으면 `statute`와 `source`를 반드시 함께 적는다** — `test_기한에는_반드시_출처가_붙는다`
- **이미 지난 기한은 다음 행동이 되지 않는다.** 장기·미제 사건은 결정이 몇 년 전이라 대부분 만료돼 있다 — `test_이미_지난_기한은_다음_행동이_되지_않는다`

> 잘못된 기한 한 줄이 들어가면 파이프라인 전체가 그 값을 신뢰하고 끝까지 통과시킨다. 피해자가 불복 기한을 놓치면 사건이 그대로 끝난다. **추측으로 채우지 않는다.** 수집 자료를 고친 곳은 `corrections`에 근거와 함께 남긴다(예: 수사중지 '재수사 요청 · 제108조' → '이의제기 · 제101조').

**결정을 낸 기관을 본다.** '혐의없음'은 경찰 불송치와 검찰 불기소에 함께 쓰는 사유이고, '기소중지'는 검사의 결정이라 이의제기가 아니라 항고 대상이다. `mapping.decision_issuer`가 결정 문구 → 통지서 발급 기관 → 결정일(2021-01-01 수사권 조정 전이면 검찰) 순으로 기관을 정하고, 끝내 모르면 단계를 고르지 않고(ST-UNKNOWN) 사용자에게 묻는다. 기한 행에 `issuer`가 있으면 그 기관의 결정에만 붙는다.

`TIM-021`(공소시효)은 **죄명과 범행일이 있어야** 계산된다. `offences.json`에 10개 죄명을 채웠고, 살인은 2015년 시효가 폐지되었으며 2007년 개정 전후로 기간이 갈린다. 성폭력범죄(기산점·배제 특례), 이득액에 따라 달라지는 특정경제범죄 사기, 국외이송 목적 약취·유인은 **지금 표 구조로 넣으면 틀린 값이 나와** `not_filled`에 이유와 함께 남겼다.

### 4. 제출 서류 — `data/documents.json`

행동마다 서식 · 제출처 · 근거 조문 · 준비물을 둔다. 서식 번호 · 제출처 · 조문을 **현행 법령 원문(국가법령정보센터 공개 API)과 대조해** `status: verified`로 올렸다. 대조한 법령과 시행일자는 `verified_laws`, 행동마다 무엇을 대조했는지는 `verified`에 있다. **법률 전문가 검토는 아니다**(`verified_scope`). 법령에 없는 것(전화번호, 관서별 접수 방법, 수수료)은 `known_gaps`에 남겼다.

- 법정 서식이 있는 것만 서식 번호를 적는다(불송치 이의신청서 별지 제125호, 수사중지 이의제기서 별지 제110호, 정보공개 청구서 별지 제1호의2, 사건기록 열람·등사 신청서 별지 제5호). 항고장 · 재정신청서는 법정 서식이 없다.
- 신규정보제출 · 모순확인 · 공소시효 · 증거보존은 수사준칙 제25조의 **자료·의견 제출서**로 낸다. 초안의 두 번째 칸은 '이의 사유'가 아니라 '요청 사항'이다(`reason_heading`).
- 근거보완 · 공백보완은 낼 서류가 아니라 자료를 얻는 일이라 `no_submission`으로 두고, 공식 경로(정보공개 청구 · 개인정보 열람 요구 · 수사서류 열람·복사)를 `routes`에 적었다.
- 같은 단계라도 기관에 따라 서류가 다르면 `by_stage`에 `"ST-201/prosecution"`처럼 기관을 붙인 키를 먼저 찾는다.

## 절차 문구를 만들지 않는 이유

`ActionDecision.main.action`은 `ACT-기록열람` 같은 **지식베이스 조회 키**일 뿐이다. 무엇을·어디에·어떻게·언제까지는 검증된 지식베이스에서만 온다. 비어 있으면 화면은 빈칸으로 둔다. `research-engine` 쪽 주석과 같은 원칙이다.

> 절차는 이 엔진이 만들지 않는다 — 검증된 지식베이스의 몫.

## 범위

29개를 쓰고 8개를 뺐다. 제외 근거는 `codes.EXCLUDED`에 있다. 구현 여력이 아니라 **자동 판정이 원리적으로 불가능하거나 사용자가 자료를 구할 수 없는 경우**를 기준으로 했다.

| 코드 | 근거 |
|---|---|
| `ST-203` `ST-204` | 경찰 내부 이관·분류라 사용자 문서에 드러나지 않음 |
| `INF-022` | 진술 vs 영상·통신기록 비교가 필요한 멀티모달 문제 |
| `INF-031` `INF-032` `INF-033` | 기준 타임라인 선행 필요 · 내부자료 · 일반화 어려움 |
| `TIM-022` | "손해를 안 날"이 판례마다 갈리는 법적 쟁점 |
| `TIM-032` `TIM-033` | 사건 서류 밖 정보(목격자 신상 · 지자체 행정데이터) |

`INF-03`은 하위 셋이 다 빠졌지만 **상위 코드로는 남긴다.** `INF-031`이 요구하는 "사건의 완전한 기준 타임라인"이 아니라 **확보된 자료들의 날짜 사이 간격**만 보면 되기 때문이다 — `research-engine`의 `time_gap`이 이미 그 계산을 해서 준다.

## 테스트 픽스처

`research-engine`의 실제 출력을 저장해 쓴다. 다시 만들려면:

```bash
cd research-engine
uv run research-engine run tests/fixtures/long_unsolved_missing/case.json \
    --out ../action-engine/tests/fixtures/long_unsolved_missing.json
uv run research-engine run tests/fixtures/used_goods_fraud/case.json \
    --out ../action-engine/tests/fixtures/used_goods_fraud.json
uv run research-engine run tests/fixtures/investigation_suspended/case.json \
    --out ../action-engine/tests/fixtures/investigation_suspended.json
uv run research-engine run tests/fixtures/suspension_recent/case.json \
    --out ../action-engine/tests/fixtures/suspension_recent.json
```
