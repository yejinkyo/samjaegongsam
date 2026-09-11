"""사건 리서치·재구성 엔진 (proposal.md 기능 1).

1단계 ingest   : 사진·스캔 → OCR/레이아웃 → 신뢰도 스코어링 → 읽히지 않은 부분 되묻기
2단계 extract  : Event · Entity · Claim · Source 태깅 + 시간 표현 정규화
3단계 timeline : coreference로 엔티티 통합, 이벤트를 시간축에 병합
4단계 analysis : Claim 쌍 NLI(보수적 판정) → 자료 간 불일치 / 확인 필요 / 행동 강령 트리거
"""

__version__ = "0.1.0"
