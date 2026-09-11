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
from action_engine import run

result = json.load(open("result.json", encoding="utf-8"))   # research-engine 출력
decision = run(result)

print(decision.state.st.code)        # ST-201
print(decision.main.rule_no)         # 5
print(decision.main.action)          # ACT-신규정보제출
print(decision.main.why)             # 새 정보는 중지·종결된 절차를 되살릴 수 있다
```

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

조합표(if-else 나열)나 가중치를 쓰지 않는다. 경우의 수가 **1,572,864개**(ST 12 × INF 2¹⁰ × TIM 2⁷)라 나열이 불가능하다. 우선순위 10줄로 덮는다.

순서는 하나의 원칙에서 도출된다.

> **놓치면 영원히 못 하는 것 → 시간이 걸리는 것 → 나중에도 할 수 있는 것**

그래서 방어할 것이 열 개가 아니라 원칙 하나다. 새 코드가 생기면 줄을 하나 추가하고, 생각이 바뀌면 줄 순서만 바꾼다.

평가기가 하는 일은 셋뿐이다 — 규칙을 순서대로 훑고, 먼저 맞는 하나를 메인으로 고르고, **발화한 규칙 번호를 결과에 같이 실어 보낸다.** 세 번째가 설명 가능성의 전부다.

### 3. 기한 — `data/deadlines.json`

**값이 비어 있다.** `period_days`와 `statute`가 전부 `null`이다.

```json
{"code": "TIM-011", "applies_to_st": ["ST-301"], "period_days": null, "statute": null,
 "check": "기간의 유무와 길이, 기산점이 처분일인지 통지 수령일인지, 초일 산입 여부"}
```

값이 없으면 엔진은 **D-day를 만들지 않고** `unresolved`에 이유를 적는다. 지금은 대부분 여기로 떨어지는 것이 정상이다.

> 잘못된 기한 한 줄이 들어가면 파이프라인 전체가 그 값을 신뢰하고 끝까지 통과시킨다. 피해자가 불복 기한을 놓치면 사건이 그대로 끝난다. **추측으로 채우지 않는다.** `test_기한값은_전부_미검증_표시다` 가 이 상태를 고정한다.

`TIM-021`(공소시효)은 **죄명이 있어야** 계산된다. 죄명별 시효표가 먼저 필요하고, 살인은 2015년 폐지되었으며 다른 죄명은 개정 전후로 적용이 갈린다.

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
```
