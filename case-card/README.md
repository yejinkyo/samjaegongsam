# case-card

기능 2 **나의 사건 카드** 화면. `research-engine`(기능 1)의 출력을 그대로 받아 렌더한다.

```
research-engine  ──PipelineResult(JSON)──▶  case-card/index.html
```

의존성 없는 단일 HTML이다. 브라우저로 `index.html`을 열면 바로 뜬다.

## 실제 데이터 연결

1. 파이프라인을 돌려 결과 JSON을 만든다 (명령은 `research-engine/` 안에서).

   ```bash
   cd research-engine
   uv sync
   uv run research-engine run tests/fixtures/long_unsolved_missing/case.json --out out/long.json
   ```

2. `index.html`을 열고 우상단 **결과 JSON 불러오기** 로 `out/long.json`을 선택한다.

`PipelineResult` 전체와 `CaseAnalysis` 단독 둘 다 받는다. 파일을 불러오기 전에는 `tests/fixtures/long_unsolved_missing` 기준의 **예시 데이터**가 떠 있고, 상단에 예시임을 알리는 띠가 보인다.

## 예시 데이터 갱신

`index.html`은 의존성 없는 단일 파일로 유지한다. 그래서 예시 데이터도 파일 안
`/* SAMPLE:BEGIN */ … /* SAMPLE:END */` 구간에 박아 두고, 아래 명령으로 덮어쓴다.

```bash
cd research-engine
uv run research-engine run tests/fixtures/long_unsolved_missing/case.json --out out/long.json
uv run python ../case-card/make-sample.py out/long.json
```

카드가 쓰는 필드만 추려 넣으므로 결과 JSON 전체(180KB 남짓)가 그대로 들어가지는 않는다.
**이 구간은 손으로 고치지 않는다.**

## 화면 구성

카드와 타임라인은 같은 데이터의 두 배율이다. 카드 위 스테퍼를 누르면 해당 단계의 타임라인 항목으로 이동한다.

| 영역 | 소비하는 필드 |
|---|---|
| 되묻기 (상단) | `clarifications[]` — `status: "pending"` 인 것만 |
| 자료함 (좌) | `documents[]` — `file_name` · `doc_type` · `evidence_level` |
| 사건 카드 | `analysis.case_card` — `case_type_label` · `stages[]` · `current_stage` · `evidence_doc_count` · `slots_done`/`slots_total` · `needs_confirmation_count` · `next_trigger` |
| 타임라인 | `timeline.events[]` · `timeline.gaps[]` |
| 확인이 필요해요 (우) | `analysis.issues[]` — `category`별로 묶어 표시 |

## 되묻기

`ClarificationRequest` 주석대로 **한 화면에 하나만 묻는다.** `priority` 순으로 하나씩 보여주고, `context`(앞뒤로 읽힌 줄)를 판독 보조로 함께 띄운다. `options`가 있으면 버튼으로, 없으면 직접 입력한다.

우측 `확인이 필요해요` 항목에 `clarification_request_ids`가 있으면 **이 부분 답하러 가기** 버튼이 붙고, 누르면 해당 질문으로 이동한다.

받은 답은 **화면에만 쌓인다.** 정적 HTML이라 파이프라인을 다시 돌릴 수 없기 때문이다. 답을 다 하면 아래 형태로 모아 주고, 이걸 넣어 다시 분석해야 카드와 타임라인에 반영된다.

```json
[{"request_id": "mother_memo:u5:q", "answer": "새 담당 형사 김영수"}]
```

```python
for a in answers:
    result = pipeline.answer(result, a["request_id"], a["answer"])
```

숫자를 임의로 깎지 않는다 — 답변했다고 `확인 필요 10건`을 화면에서 줄이면 실제 재분석 결과와 어긋나기 때문이다.

## 스키마 대응

`index.html` 상단의 상수 세 개가 `research-engine/src/research_engine/schema/`와 1:1로 대응한다. **엔진 쪽 enum이 바뀌면 여기만 고치면 된다.**

| 상수 | 대응 |
|---|---|
| `STAGE_LABELS` | `schema/extraction.py` `STAGE_LABELS` |
| `EVIDENCE` | `schema/document.py` `EvidenceLevel` → 배지 `확인됨` / `주장·미확인` / `내가 입력` |
| `CATEGORY` | `schema/analysis.py` `ISSUE_CATEGORY_LABELS` |
| `CONDITION` | `schema/analysis.py` `GapCondition` |

`StageState`는 CSS에서 직접 받는다 — `done` · `current`(지금 여기) · `pending` · `skipped`.

## 절차 안내를 만들지 않는 이유

`ActionTrigger`에는 절차 문구가 없다. 엔진 주석대로다.

> 절차(무엇을·어디에·어떻게·언제까지)는 이 엔진이 만들지 않는다 — 검증된 지식베이스의 몫.

그래서 **다음 행동** 칸에는 트리거의 조건 이름(`GapCondition`)과 근거만 보여주고, 서식명·제출처·기한은 비워 둔다. 검증된 절차 지식베이스가 붙기 전까지 이 자리는 "아직 연결되지 않았습니다"로 남는다. 화면이 법적 절차를 지어내지 않게 하는 장치다.
