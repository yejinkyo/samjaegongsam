# CLAUDE.md

이 파일은 Claude Code가 이 저장소에서 작업할 때 따르는 규칙이다.
2인 협업(바이브 코딩) 기준이며, Claude가 **Git 협업 흐름을 직접 관리**한다.

---

## 1. 프로젝트 개요

- **프로젝트명**: 삼재공삼 — 장기·미제 사건 정리 서비스
- **스택**: Python 3.11+ (백엔드 `research-engine` · `action-engine`), 프론트는 정적 HTML
- **패키지 매니저**: `uv`
- **테스트 실행**: `uv run pytest`
- **린트/포맷**: `uv run ruff check .` (line-length 140, target py311)
- **CLI 실행**: `uv run research-engine run <case.json> --out <out.json>`
- **카드 예제**: `uv run python examples/run_card.py` (`action-engine`)

> ⚠️ **위 명령은 모두 패키지 폴더(`research-engine/` 또는 `action-engine/`) 안에서 실행한다.**
> 저장소 루트에는 `pyproject.toml`이 없어서 `uv run`이 명령을 찾지 못한다.
> 두 패키지는 서로 import 하지 않으므로 **고친 패키지에서** 테스트·린트를 돌린다.
>
> ```bash
> cd research-engine   # 또는 cd action-engine
> uv sync
> uv run pytest
> ```

**폴더 구조**

```
2026 wanted/
├── CLAUDE.md            협업 규칙 (이 파일)
├── docs/proposal.md     서비스 기획서
├── mockups/             기능 1 HTML 목업
├── research-engine/     기능 1 · 사건 리서치·재구성 엔진 ("무엇이 비어 있는가")
│   ├── src/research_engine/
│   │   ├── ingest/      OCR · 레이아웃 · 판독 신뢰도
│   │   ├── extract/     Event · Entity · Claim · 시간 표현 정규화
│   │   ├── timeline/    coreference · 시간축 병합 · 기록 공백
│   │   ├── analysis/    Claim 쌍 NLI · 불일치/미확인/빠진 정보 판정
│   │   ├── eval/        OCR · NER · NLI 평가 (라벨링 파일럿)
│   │   ├── schema/      Pydantic 스키마 (provenance 포함)
│   │   └── requirements/ 사건 유형별 필요 자료 정의
│   └── tests/fixtures/  사건 예시 (인물·사건은 가상)
└── action-engine/       기능 2 · 다음 행동 강령 엔진 ("무엇을 해야 하는가")
    ├── src/action_engine/
    │   ├── mapping.py   research-engine 출력 → ST · INF 코드
    │   ├── rules.py     우선순위 규칙 평가 · 기한 계산
    │   ├── limitation.py 죄명별 공소시효
    │   ├── checklist.py 필요 서류 ↔ 자료함 대조
    │   ├── agencies.py  관할 경찰관서 조회
    │   └── data/        지식베이스 (rules · deadlines · documents · offences · agencies)
    ├── tools/           지식베이스 생성 스크립트
    └── tests/fixtures/  research-engine 실제 출력
```

---

## 2. 브랜치 전략

| 브랜치 | 용도 | 직접 커밋 |
|--------|------|-----------|
| `main` | 통합 브랜치. 모든 기능이 여기로 모임 | 금지 (PR 병합만) |
| `feature/*` | 기능 개발 | 자유 |
| `fix/*` | 버그 수정 | 자유 |
| `docs/*` | 문서 수정 | 자유 |

- 모든 작업 브랜치는 **`main`에서 분기**하고 **`main`으로 PR**한다.
- 브랜치 이름: `feature/research-pipeline`, `fix/날짜-파싱` 처럼 `타입/짧은-설명` (kebab-case, 한글/영문 무관).
- 한 브랜치 = 한 기능/한 관심사. 브랜치가 커지면 쪼갠다.

> `dev` 브랜치는 쓰지 않는다. 리모트에 남아 있는 `origin/dev`는 초기 커밋에서 멈춘 잔재이므로 무시하거나 삭제한다.

---

## 3. 작업 시작 전 (Claude가 자동 수행)

새 작업 요청을 받으면 코드를 건드리기 전에 아래를 순서대로 실행한다.

```bash
git status                      # 작업 중인 변경사항이 있는지 확인
git stash                       # (있으면) 임시 저장하고 사용자에게 알림
git checkout main
git pull origin main            # 최신 main 받기
git checkout -b feature/<설명>   # 새 작업 브랜치 생성
```

규칙:
- `git status`에 커밋되지 않은 변경사항이 있으면 **먼저 사용자에게 알리고** 어떻게 할지 확인한다(계속 / stash / 커밋).
- 이미 올바른 작업 브랜치에서 이어서 작업 중이면 새로 분기하지 않고, `git pull origin main` 후 필요 시 `git merge main` 또는 `git rebase main`으로 최신화만 한다.
- `main`에서 직접 코드를 수정하지 않는다. 실수로 그 위에 있으면 즉시 브랜치를 만든다.

---

## 4. 기능 구현 중

- 요청받은 범위만 구현한다. 관련 없는 리팩터링/포맷팅은 섞지 않는다.
- 주변 코드의 스타일(네이밍, 들여쓰기, 주석 밀도)을 그대로 따른다.
- 구현 후 **고친 패키지 폴더**에서 테스트와 린트를 돌려 통과를 확인하고, 결과를 사실대로 보고한다(실패하면 실패했다고 말한다).
  ```bash
  cd research-engine && uv run pytest && uv run ruff check .
  cd action-engine && uv run pytest && uv run ruff check .
  ```
- `research-engine` 출력 스키마를 바꾸면 `action-engine/tests/fixtures/`를 다시 만들고(방법은 `action-engine/README.md`) 양쪽 테스트를 모두 돌린다.
- 커밋은 **의미 단위로 작게** 나눈다. "일단 전부 한 커밋"은 피한다.

---

## 5. 변경사항 저장 (add / commit)

Claude가 자동으로 수행한다.

```bash
git add <관련 파일들>          # git add . 대신 관련 파일만 명시
git commit -m "<타입>: <설명>"
```

커밋 메시지 규칙 (Conventional Commits, 본문은 한국어 허용):
- `feat: 장기 미제 실종·수사중지 사건 유형 지원`
- `fix: 날짜 접미사·연도 추정·인물 오인식 수정`
- `refactor:`, `style:`, `docs:`, `test:`, `chore:`
- 제목은 50자 이내, 명령형 현재시제. 필요하면 본문에 "왜"를 적는다.
- 커밋 메시지 마지막 줄:
  ```
  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
  ```

---

## 6. 푸시 & PR

- **push 전에는 항상 사용자에게 한 번 확인**받는다(무엇을, 어느 브랜치로). 확인 후:

```bash
git push -u origin feature/<설명>
```

- 그다음 `main`을 base로 하는 PR을 생성한다(`gh pr create`, 없으면 push 결과에 뜨는 링크 전달). PR 본문에:
  - 무엇을 왜 바꿨는지 요약
  - 테스트 방법 / 확인한 것
  - 관련 이슈 번호
  - 마지막 줄: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
- PR 생성 후 링크를 사용자에게 전달한다. **병합은 사람이 리뷰 후 직접** 한다.

---

## 7. 팀원과의 동기화 / 충돌 처리

- 작업 중 팀원이 `main`을 업데이트했을 수 있으므로, 오래 걸린 브랜치는 push 전에 `main`을 다시 받아 최신화한다:
  ```bash
  git fetch origin
  git rebase origin/main        # 히스토리 깔끔하게 (또는 git merge origin/main)
  ```
- **충돌이 나면 자동으로 임의 해결하지 않는다.** 충돌 파일 목록과 각 충돌 지점을 사용자에게 보여주고, 어느 쪽을 택할지 확인한 뒤 해결한다.
- 이미 push해서 팀원이 받았을 수 있는 브랜치는 **force push 하지 않는다**(꼭 필요하면 사용자 승인 후 `--force-with-lease`).

---

## 8. Claude 행동 규칙 요약

| 상황 | 동작 |
|------|------|
| 새 작업 시작 | 브랜치 상태 확인 → `main` pull → `feature/*` 분기 (자동) |
| 코드 구현 | 요청 범위만, 스타일 준수, 테스트/린트 확인 |
| 변경 저장 | 관련 파일만 `add`, 의미 단위 `commit` (자동) |
| `push` | **사용자 확인 후** 실행 |
| PR 생성 | push 후 자동 생성, 링크 전달, 병합은 사람이 |
| 충돌 | 자동 해결 금지, 사용자에게 보고 후 처리 |
| `main` 직접 수정 | 금지 |
| force push | 금지 (승인 시 `--force-with-lease`만) |

---

## 9. 커밋 전 체크리스트

- [ ] `feature/*` · `fix/*` · `docs/*` 브랜치에 있다 (`main` 아님)
- [ ] 요청 범위 외 변경이 섞이지 않았다
- [ ] `uv run pytest` 통과 (또는 실패를 사용자에게 보고했다)
- [ ] `uv run ruff check .` 통과
- [ ] 커밋이 의미 단위로 나뉘어 있다
- [ ] 커밋 메시지가 컨벤션을 따른다
