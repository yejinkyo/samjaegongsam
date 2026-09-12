"""사건 상태 코드 29개.

세 축은 성격이 다르다.
- ``ST``  절차적 단계. 상호배타 — 하나만 참이다.
- ``INF`` 정보 결합 상태. 여러 개가 동시에 참일 수 있다.
- ``TIM`` 기한/임계 상태. ST와 날짜에서 계산된다.

제외한 8개(ST-203·204, INF-022·031·032·033, TIM-022·032·033)는 자동 판정이
원리적으로 불가능하거나 사용자가 자료를 구할 수 없어서 뺐다. 되살릴 때는
여기에 코드를 추가하고 rules.json 에 줄을 하나 넣으면 된다.
"""

from __future__ import annotations

from enum import StrEnum


class ST(StrEnum):
    """절차적 단계."""

    # ST-100 입건 전 및 수사 진행
    PRE_INVESTIGATION = "ST-101"  # 입건 전 조사
    POLICE_INVESTIGATING = "ST-102"  # 경찰 수사 중
    PROSECUTION_INVESTIGATING = "ST-103"  # 검찰 수사 중
    # ST-200 수사 중지 및 미제 전환
    SUSPENDED_SUSPECT = "ST-201"  # 피의자 중지
    SUSPENDED_WITNESS = "ST-202"  # 참고인 중지
    # ST-300 수사 종결 및 불복
    POLICE_NO_REFERRAL = "ST-301"  # 경찰 불송치
    PROSECUTION_NO_CHARGE = "ST-302"  # 검찰 불기소
    APPEAL_PENDING = "ST-303"  # 이의신청/항고 중
    ADJUDICATION_REQUEST = "ST-304"  # 재정신청 단계
    # ST-400 재판 및 판결 확정
    TRIAL_ONGOING = "ST-401"  # 재판 진행 중
    JUDGMENT_FINAL = "ST-402"  # 판결 확정
    RETRIAL_PREP = "ST-403"  # 재심 준비/청구
    # 판정 불가
    UNKNOWN = "ST-UNKNOWN"


class INF(StrEnum):
    """정보 결합 상태."""

    NEW_STATEMENT = "INF-011"  # 신규 인적 진술
    NEW_PHYSICAL = "INF-012"  # 신규 디지털/물적 증거
    NEW_FORENSIC = "INF-013"  # 신규 감정 결과
    NEW_MEDIA = "INF-014"  # 외부 매체 정보
    CONTRADICTION_ACROSS = "INF-021"  # 진술 간 시공간 모순
    CONTRADICTION_SELF = "INF-023"  # 동일인 진술 번복
    RECORD_GAP = "INF-03"  # 기록 및 동선 공백 (하위 코드 없이 상위로만 쓴다)
    SOURCE_MISSING = "INF-041"  # 원본 출처 누락
    RECORD_UNCHECKED = "INF-042"  # 수사 기록 미확인
    ANALYSIS_NOT_DONE = "INF-043"  # 전문 분석 미실시


class TIM(StrEnum):
    """기한/임계 상태."""

    APPEAL_NO_REFERRAL = "TIM-011"  # 불송치 이의신청
    APPEAL_PROSECUTION = "TIM-012"  # 검찰 항고 기한
    ADJUDICATION = "TIM-013"  # 법원 재정신청 기한
    STATUTE_LIMITATION = "TIM-021"  # 형사 공소시효 임박
    DIGITAL_RETENTION = "TIM-031"  # 디지털 데이터 보존 기한
    ALWAYS_REINVESTIGATION = "TIM-041"  # 상시 재수사 요청
    ALWAYS_DISCLOSURE = "TIM-042"  # 상시 정보공개청구


LABELS: dict[str, str] = {
    ST.PRE_INVESTIGATION: "입건 전 조사",
    ST.POLICE_INVESTIGATING: "경찰 수사 중",
    ST.PROSECUTION_INVESTIGATING: "검찰 수사 중",
    ST.SUSPENDED_SUSPECT: "피의자 중지",
    ST.SUSPENDED_WITNESS: "참고인 중지",
    ST.POLICE_NO_REFERRAL: "경찰 불송치",
    ST.PROSECUTION_NO_CHARGE: "검찰 불기소",
    ST.APPEAL_PENDING: "이의신청/항고 중",
    ST.ADJUDICATION_REQUEST: "재정신청 단계",
    ST.TRIAL_ONGOING: "재판 진행 중",
    ST.JUDGMENT_FINAL: "판결 확정",
    ST.RETRIAL_PREP: "재심 준비/청구",
    ST.UNKNOWN: "단계 미확정",
    INF.NEW_STATEMENT: "신규 인적 진술",
    INF.NEW_PHYSICAL: "신규 디지털/물적 증거",
    INF.NEW_FORENSIC: "신규 감정 결과",
    INF.NEW_MEDIA: "외부 매체 정보",
    INF.CONTRADICTION_ACROSS: "진술 간 시공간 모순",
    INF.CONTRADICTION_SELF: "동일인 진술 번복",
    INF.RECORD_GAP: "기록 및 동선 공백",
    INF.SOURCE_MISSING: "원본 출처 누락",
    INF.RECORD_UNCHECKED: "수사 기록 미확인",
    INF.ANALYSIS_NOT_DONE: "전문 분석 미실시",
    TIM.APPEAL_NO_REFERRAL: "불송치 이의신청",
    TIM.APPEAL_PROSECUTION: "검찰 항고 기한",
    TIM.ADJUDICATION: "법원 재정신청 기한",
    TIM.STATUTE_LIMITATION: "형사 공소시효 임박",
    TIM.DIGITAL_RETENTION: "디지털 데이터 보존 기한",
    TIM.ALWAYS_REINVESTIGATION: "상시 재수사 요청",
    TIM.ALWAYS_DISCLOSURE: "상시 정보공개청구",
}

# 범위에서 뺀 코드와 근거. 발표·문서에서 "무엇을 다루지 않는가"로 쓴다.
EXCLUDED: dict[str, str] = {
    "ST-203": "경찰이 내부적으로 이관·분류한 상태라 사용자 문서에 드러나지 않는 경우가 많음",
    "ST-204": "경찰이 내부적으로 이관·분류한 상태라 사용자 문서에 드러나지 않는 경우가 많음",
    "INF-022": "진술 vs 영상·통신기록 비교가 필요한 멀티모달 문제. 텍스트 기반 모순탐지 범위 밖",
    "INF-031": "빈 시간대를 찾으려면 완전한 기준 타임라인이 먼저 필요해 근본적으로 더 어려움",
    "INF-032": "누가 공식조사를 받았는지는 수사기관 내부자료라 사용자가 구하기 어려움",
    "INF-033": "도메인이 좁아 참고할 데이터가 사실상 없고 케이스마다 표현이 달라 일반화 어려움",
    "TIM-022": "'손해 및 가해자를 안 날'이 판례마다 다르게 해석되는 법적 쟁점이라 자동 특정 어려움",
    "TIM-032": "목격자의 나이·건강·이민계획은 사건 서류에 거의 기재되지 않음",
    "TIM-033": "재개발·철거 여부는 문서 밖 지자체 행정데이터 조회가 필요한 별도 문제",
}


def label(code: str) -> str:
    return LABELS.get(code, code)
