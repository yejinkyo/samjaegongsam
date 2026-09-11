"""추출기들이 공유하는 한국어 법률·금융 문서 패턴."""

from __future__ import annotations

import re

BANKS = (
    "NH농협|농협|KB국민|국민|신한|우리|하나|IBK기업|기업|카카오뱅크|토스뱅크|케이뱅크|SC제일|씨티|"
    "대구|부산|경남|광주|전북|제주|수협|신협|새마을금고|우체국"
)
MASK_CHARS = "○●◯*＊Xx"
MASK_CLASS = "○●◯*＊Xx"

# 이름 뒤에 붙는 조사·호칭·서술격 (길이 긴 것부터)
LONG_PARTICLES = (
    "이에요", "입니다", "에게서", "로부터", "이라고", "께서", "에게", "한테", "라고", "으로", "씨는", "씨가",
    "씨의", "입니", "이며", "이고", "이다", "예요",
)
SHORT_PARTICLES = ("은", "는", "이", "가", "을", "를", "의", "와", "과", "도", "씨", "님")
NOT_NAMES = {
    "측", "본인", "서명", "날인", "주소", "성명", "연락처", "인적사항", "명의", "계좌", "진술", "주장", "등",
    "들", "에게", "관할", "담당", "측에서", "사건", "배정", "관서", "부서", "확인", "미상", "불상", "없음",
    "사람", "친구", "가족", "타인", "다른", "누구", "그분", "상대", "상대방", "정보", "표시",
    "물건", "상품", "택배", "금액", "연락", "전화", "문자", "사실", "내용", "경찰", "수사", "조사", "송금", "입금",
    "이체", "거래", "대화", "판매", "구매", "피해", "계좌로", "측은", "메모", "통장", "은행",
}

ROLE_WORDS = (
    "피고소인|피고인|피의자|피해자|고소인|고발인|신고인|진정인|진술인|참고인|증인|원고|피고|판매자|구매자|"
    "예금주|수취인|담당\\s*수사관|수사관|조사관|경위|경사|경장|순경|경감|경정|검사|판사|재판장"
)
# 같은 당사자를 절차 단계마다 다르게 부르는 역할 묶음 (coreference 근거)
ROLE_GROUPS = {
    "accused": {"피고소인", "피고인", "피의자", "피고", "판매자"},
    "victim": {"피해자", "고소인", "신고인", "진정인", "원고", "구매자"},
    "police": {"수사관", "담당수사관", "조사관", "경위", "경사", "경장", "순경", "경감", "경정"},
}

PERSON_ROLE = re.compile(
    rf"(?P<role>{ROLE_WORDS}|성명|이름)\s*(?:[:：]\s*|\s+)(?P<name>[가-힣][가-힣{MASK_CLASS}]{{1,4}})"
)
PERSON_MASKED = re.compile(rf"(?<![가-힣])(?P<name>[가-힣][{MASK_CLASS}]{{1,2}})(?![가-힣{MASK_CLASS}])")
PERSON_MO = re.compile(r"(?<![가-힣])(?P<sur>[가-힣])모\s*(?:씨|군|양)")
PERSON_AGE = re.compile(r"(?<![가-힣])(?P<name>[가-힣]{2,4})\s*\(\s*(?:남|여)?\s*,?\s*\d{2}\s*세\s*\)")

ORG_SUFFIX = (
    "지방법원|고등법원|가정법원|행정법원|대법원|법원|지방검찰청|고등검찰청|대검찰청|검찰청|지청|"
    "경찰서|경찰청|지구대|파출소|사이버수사대|사이버수사팀|사이버팀|수사과|형사과|은행|구청|시청|군청|"
    "주민센터|행정복지센터|우체국|금융감독원|국민권익위원회|법률구조공단|지법|고법|지검|고검|대검"
)
ORG = re.compile(rf"(?P<name>[가-힣{MASK_CLASS}]{{0,12}}?(?:{ORG_SUFFIX}))(?!원|장님)")
ORG_PREFIX_STOP = (
    "주거래", "보내는", "관할", "담당", "해당", "인근", "가까운", "입금", "출금", "거래", "받는",
)
ORG_ABBREV = {
    "지법": "지방법원", "고법": "고등법원", "지검": "지방검찰청", "고검": "고등검찰청", "대검": "대검찰청",
}

ACCOUNT = re.compile(
    rf"(?:(?P<bank>{BANKS})(?:은행)?\s*[:：]?\s*|(?:입금|출금|받는|보내는)?\s*계좌(?:번호)?\s*[:：]?\s*)"
    r"(?P<acct>[0-9*＊][0-9*＊\-]{7,}[0-9*＊])"
)
BANK_LABEL = re.compile(rf"(?:입금|출금|받는|보내는)\s*은행\s*[:：]?\s*(?P<bank>{BANKS})(?:은행)?")
PHONE = re.compile(r"(?<![0-9])(?P<phone>01[016789]-?[0-9*]{3,4}-?[0-9*]{4}|0[2-6][0-9]?-[0-9]{3,4}-[0-9]{4})(?![0-9])")
CASE_NUMBER = re.compile(
    r"(?<![0-9])(?P<no>(?:19|20)\d{2}\s?(?:고단|고합|고정|고약|재고단|노|도|가단|가합|가소|나|다|형제|진정|내사|"
    r"초재|카단|카합|머|드단|드합|느단|느합|구단|구합|누|두)\s?\d{1,7})(?![0-9])"
)
CASE_NUMBER_LABEL = re.compile(r"사건\s*번호\s*[:：]?\s*(?P<no>[0-9A-Za-z가-힣*\-]{4,})")
RECEIPT_NUMBER = re.compile(
    r"(?:접수|신고|민원|사건접수)\s*번호\s*[:：]?\s*(?P<no>[0-9A-Za-z][0-9A-Za-z*＊\-]{3,})"
)
TRACKING_NUMBER = re.compile(r"(?:운?송장|등기)\s*번호\s*[:：]?\s*(?P<no>[0-9][0-9\-]{7,})")
NICKNAME = re.compile(r"(?:닉네임|아이디|대화명|계정명?)\s*[:：]?\s*[\"“'‘]?(?P<nick>[^\s\"”'’,]{1,20})")
PLACE = re.compile(
    r"(?P<addr>(?:서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|충청북|충청남|전북|전남|전라북|전라남|"
    r"경북|경남|경상북|경상남|제주)[가-힣]*\s+[가-힣]+(?:시|군|구)(?:\s+[가-힣]+(?:구|시|군))?"
    r"(?:\s+[가-힣0-9]+(?:동|읍|면|리|로|길))?(?:\s*[0-9\-]+(?:번지)?)?)"
)

MONEY = re.compile(
    r"(?<![0-9,])(?:금\s*)?(?P<num>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\s*(?:억|천|백|십|만)(?:\s*\d+)?)*)\s*원"
)

MESSENGER_LINE = re.compile(
    r"^\s*\[(?!오전|오후)(?P<speaker>[^\]\d][^\]]{0,19})\]\s*(?:\[(?P<ts>(?:오전|오후)\s*\d{1,2}:\d{2})\])?\s*(?P<msg>.*)$"
)
COLON_SPEAKER_LINE = re.compile(r"^\s*(?P<speaker>[가-힣A-Za-z0-9_]{1,15})\s*[:：]\s*(?P<msg>.+)$")
TRANSCRIPT_QA = re.compile(r"^\s*(?P<qa>문|답|질문|답변)\s*[:：.]\s*(?P<msg>.+)$")

NEGATION = re.compile(r"(않|안\s*(?:했|보냈|받|왔|됐|되)|못\s*(?:했|받|보)|없(?:었|습|어|음|다|는)|아니|아닙|아녜)")
REQUEST_OR_FUTURE = re.compile(r"(주세요|줘요|주시|할\s*예정|하겠|할게|할께|하려|해야|드릴게|드리겠|될\s*예정|됩니다\s*$)")


def strip_particles(name: str) -> str:
    """'김철수는'→'김철수', '홍길동입니'→'홍길동'. 한 글자 조사는 4자 이상일 때만 뗀다 ('이가은' 보호)."""
    for p in LONG_PARTICLES:
        if name.endswith(p) and len(name) - len(p) >= 2:
            return name[: -len(p)]
    if len(name) >= 4 and name.endswith(SHORT_PARTICLES):
        return name[:-1]
    return name


def normalize_mask(text: str) -> str:
    return re.sub(f"[{MASK_CLASS}]", "*", text)


def normalize_account(text: str) -> str:
    return normalize_mask(re.sub(r"[\s\-]", "", text))


def parse_money(raw: str) -> int | None:
    """'350,000' '35만' '1억 2천만' '3만 5천' → 정수 원."""
    s = raw.replace(",", "").replace(" ", "")
    if s.isdigit():
        return int(s)
    total, rest = 0, s
    for unit, mult in (("억", 100_000_000), ("만", 10_000)):
        if unit in rest:
            head, rest = rest.split(unit, 1)
            total += _small_korean_number(head or "1") * mult
    if rest:
        total += _small_korean_number(rest)
    return total or None


def _small_korean_number(s: str) -> int:
    """'2천5백30' → 2530."""
    total, num = 0, ""
    for ch in s:
        if ch.isdigit():
            num += ch
        elif ch in "천백십":
            total += int(num or "1") * {"천": 1000, "백": 100, "십": 10}[ch]
            num = ""
    return total + int(num or "0")


def is_negated(clause: str) -> bool:
    return bool(NEGATION.search(clause))
