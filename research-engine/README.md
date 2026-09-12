# research-engine

기능 1 **사건 리서치·재구성 엔진**의 백엔드 파이프라인 ([docs/proposal.md](../docs/proposal.md), [목업](../mockups/research-engine.html)).
사진·스캔 자료를 받아 타임라인과 "확인이 필요해요" 목록, 그리고 행동 강령 매칭용 트리거를 만든다.

```
1 ingest    사진/스캔 → OCR·레이아웃 → 판독 신뢰도 → 읽히지 않은 줄은 되묻기
2 extract   Event · Entity · Claim · Source 태깅 + 시간 표현 정규화
3 timeline  coreference로 엔티티 통합 → 이벤트를 시간축에 병합 → 단계 상태·기록 공백
4 analysis  Claim 쌍 NLI → 보수적 판정 → 불일치 / 확인되지 않음 / 빠진 정보 / 행동 강령 트리거
```

## 실행

명령은 모두 `research-engine/` 폴더 안에서 실행한다 (저장소 루트에는 `pyproject.toml`이 없어 `uv run`이 명령을 찾지 못한다).

```bash
cd research-engine
uv sync
uv run pytest
uv run research-engine run tests/fixtures/used_goods_fraud/case.json --out out/result.json
uv run research-engine schema --out-dir out/schemas
```

예시 사례 세 개가 OCR 결과 형태로 들어 있다 (인물·사건은 가상).

| 픽스처 | 사건 유형 | 자료 |
|---|---|---|
| `tests/fixtures/used_goods_fraud/` | `used_goods_fraud` | 목업의 중고거래 사기 — 메신저 캡처, 이체확인증, 접수증, 손글씨 메모, 진술서 |
| `tests/fixtures/long_unsolved_missing/` | `missing_person_suspended` | 장기 미제 실종 — 2015 실종신고 접수증, 2016 보도, 2019 목격자 진술서, 2022 수사중지 결정 통지서, 2023 진정서, 가족 손글씨 메모 |
| `tests/fixtures/investigation_suspended/` | `investigation_suspended` | 수사중지 — 2021 고소장·접수증, 2023 참고인중지 결정 통지서, 2025 목격 진술서 (실종 서식이 없는 일반 수사중지 유형) |

```bash
uv run research-engine run tests/fixtures/long_unsolved_missing/case.json --out out/long.json
uv run research-engine run tests/fixtures/investigation_suspended/case.json --out out/suspended.json
```

## 원칙이 코드에 들어간 자리

| 원칙 (proposal.md) | 구현 |
|---|---|
| 출처 없는 문장을 쓰지 않는다 (§7) | `schema/provenance.py` `Sourced[T]` = `{value, source_doc_id, source_line/bbox, confidence}`. 위치가 없으면 생성 자체가 실패한다. 모든 Event·Entity·Claim이 이걸 쓴다 |
| 원문 좌표 ↔ 텍스트 매핑 | `TextLine`이 문서 전체 줄 번호 + 페이지 + bbox + 문자 구간을 유지. 사용자 답변으로 고친 줄도 번호·bbox를 그대로 둔다 |
| 읽히지 않은 부분만 되묻는다 (§5 기능1, §6) | `ingest/confidence.py` 판독 점수 < 임계값 → `UnreadableRegion` + `ClarificationRequest`. OCR 추정 문자열은 하위 단계 입력에서 제외 |
| AI가 아는 척하지 않는다 (§7) | `analysis/policy.py` 불일치는 5가지 조건을 모두 통과해야 확정, 아니면 Neutral(확인 필요). 점수는 추출 신뢰도로 중립 쪽으로 수축 |
| 절차를 지어내지 않는다 (§3, §7) | 엔진은 `ActionTrigger.key`(`{사건유형}/{단계}/{항목}/{상태}`)까지만 만든다. 무엇을·어디에·어떻게·언제까지는 검증된 지식베이스의 몫 |

## 단계별 핵심

**1단계** — `OcrEngine` 프로토콜(Tesseract 어댑터, 외부 OCR JSON 로더). 문서 유형은 서식 키워드 분류기가 기준선이고, 라벨이 생기면 나이브 베이즈(`train-doc-classifier`)를 앙상블한다. 판독 신뢰도는 엔진 신뢰도·최저 단어 신뢰도·깨진 글자 비율·낱자모 비율·필체를 피처로 한 로지스틱 모델이며 `train-readability`로 보정한다.

**2단계** — `extract/temporal.py`가 정확도 병목이 될 가능성이 커서 규칙을 명시적으로 뒀다.
- 발화 기준(어제·지난주 금요일·3일 전)은 메신저 날짜 줄 → 문서 작성일 → 촬영일 순으로 기준일을 잡고, 문맥 기준(그날·다음날·3일 후)은 직전에 언급된 날짜를 쓴다
- 음력(윤달 포함)은 양력으로 변환, `단기` 연도 지원
- `2O26`처럼 글자가 섞이면 교정하되 확인 필요로 표시하고, 달력에 없는 날짜·요일 불일치는 **후보만** 내고 되묻는다
- 기준일이 촬영일/분석일뿐이면 확인 필요

Claim은 화자(메신저 접두어, 문/답, 진술서 작성자, 인용 "판매자는 ~했다고 하였으나", 기록 문서 발급처)를 붙이고, 비교 가능한 값은 슬롯(`transfer_amount`, `account_holder` …)으로 구조화한다.

**3단계** — 계좌 마스킹(`940*-**-****21`)은 보이는 자리가 4개 이상 겹칠 때만 병합, 이름은 역할 묶음(피고인≈피고소인≈피의자)이 같을 때만 병합하고 나머지는 `possible_same_as` 링크로 남긴다. 이벤트는 같은 단계 + (금액 일치 / 식별자 공유 / 하루 이하 입도 시각 겹침)일 때만 합치고, 금액이 다르면 합치지 않는다.

**4단계** — 서로 다른 문서의 같은 슬롯 Claim 쌍만 비교한다. 대상이 같은지 불확실하면(계좌가 입금/출금 중 무엇인지 모름, 금액이 다른 두 송금) 모순 판정을 막는다. 출력 스키마:

- `Issue` — 목업 "확인이 필요해요" 한 줄. `category`(자료끼리 어긋남/확인되지 않음/빠진 정보/읽히지 않은 부분), 근거 `sources` 또는 '없음' 판단 시 `checked_doc_ids`
- `ActionTrigger` — 행동 강령 매칭 엔진 입력. `since`·`elapsed_days`로 "접수 후 3주 경과" 같은 기한 계산이 가능
- `CaseCard` — 기능 2 카드 (단계 진행, 확보 자료 수, 확인 필요 수, 완료 n/m, 다음 트리거)

한 항목에 기록 자료가 여러 줄 걸리면 **더 구체적인 값**을 대표로 세운다. 통지서는 제목(`수사중지 결정 통지서`)과 결정내용란(`수사중지(참고인중지)`)에 같은 결정을 다르게 적는데, 앞줄이 대표가 되면 중지 사유가 사라져 행동 강령 엔진이 피의자중지·참고인중지를 가르지 못한다. 한 값이 다른 값을 그대로 품고 있을 때만 순서를 바꾸고, 서로 다른 값이면 모순 판정에 맡긴다.

사건 유형별 추적 항목은 `requirements/*.json`에 데이터로 둔다. 현재 `used_goods_fraud`, `investigation_suspended`, `missing_person_suspended` 모두 `draft_unverified` — 법률 전문가 검수 전 초안이다.

장기 미제 유형(`flag_unrecorded_facts`, `stall_after_final_stage`)에서는 두 가지를 더 본다.
- **기록에서 확인되지 않는 사건 이후 사실** — 첫 발생 이후의 목격·제보 같은 진술 중 통지서·접수증 같은 기록 자료로 뒷받침되지 않는 것. 마지막 결정보다 앞선 내용인지 뒤의 내용인지 함께 적는다. proposal.md 사례 B("2019년 목격 진술이 기존 수사 기록에 포함되어 있지 않습니다")의 트리거(`…/occurrence/new_fact/unrecorded_fact`)다. 엔진은 수사 기록 원본을 보지 못하므로 "포함되지 않았다"고 단정하지 않고 "반영 여부 확인 필요"로만 올린다
- **결정 이후 경과** — 수사중지 같은 마지막 단계도 멈춘 상태로 보고 결정일부터 경과일을 센다

시간이 지나며 바뀌는 값(현재는 담당 수사관)은 `analysis/changes.py`가 다룬다. "담당자 바뀌었다고 함" 같은 변경 주장이 있으면 그 이전의 기록 값은 **틀린 게 아니라 낡았을 수 있는 값**이 된다. 변경 이후의 값이 없으면 `possibly_outdated`(현재 담당자 확인 필요)로 올리고, 변경 전후 값끼리는 모순으로 비교하지 않는다.

## 먼저 검증할 것: 라벨링 파일럿

기성 규칙·모델로 충분한지 먼저 재고, 부족한 곳만 파인튜닝한다. 라벨 형식은 각 모듈 docstring에 있고 `tests/fixtures/pilot/`에 예시가 있다.

```bash
# OCR: 필체별 CER, 목표 precision을 만족하는 판독 임계값
uv run research-engine eval-ocr pilot/ocr_lines.jsonl
uv run research-engine train-readability pilot/ocr_lines.jsonl --out models/scorer.json

# 엔티티·시간: 유형별 P/R/F1, 목표 F1 미달이면 finetune_recommended
uv run research-engine eval-ner pilot/ner_gold.jsonl --target-f1 0.85

# NLI: precision ≥ 목표를 지키면서 Contradiction recall 최대인 임계값 → 정책 JSON
uv run research-engine eval-nli pilot/nli_pairs.jsonl --target-precision 0.95 --out models/policy.json

uv run research-engine run case.json --scorer models/scorer.json --policy models/policy.json
```

모델 교체 지점: `OcrEngine`, `DocumentClassifier`, `EntityExtractor`, `NliModel`(슬롯 없는 자유 서술은 `HuggingFaceNli`로 한국어 NLI 체크포인트 연결).

## 현재 한계

- 판결문·녹취록·손글씨 학습 데이터가 없어 **추출기는 규칙 기반 기준선**이다. 실제 자료에서의 정확도는 파일럿으로 측정해야 한다
- `TesseractOcrEngine`(`[ocr]`), `HuggingFaceNli`(`[nli]`)는 선택 의존성이며 이 환경에서 실행 검증하지 않았다
- 텍스트 NLI 쌍은 대상 동일성을 확신할 수 없어 현재 정책상 불일치로 확정되지 않는다 (확인 필요로만 올라감)
- 목업은 판매자의 "택배 보냈어요"를 '불일치'로 표시하지만, 반대 기록이 없는 진술은 이 엔진에서 '확인되지 않음'으로 분류된다
