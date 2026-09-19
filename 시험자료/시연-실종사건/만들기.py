"""해커톤 시연 사건 — 2017년 실종, 9년째 미제. 인물·사건·서류는 전부 지어낸 것이다.

한 사건 안에서 여러 서류를 시간축으로 잇기 · 자료끼리 모순 · 기록 공백 · 흐린 판독 · 본인 말뿐인 날짜 ·
새 제보가 함께 보이도록 짰다. 카드는 손으로 쓰지 않는다 — 엔진이 이 서류를 읽고 만든다.

    py 시험자료/시연-실종사건/만들기.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent


def doc(doc_id, file_name, captured_at, lines, script="typewriter"):
    """lines: 문자열 또는 (문자열, 신뢰도)."""
    out, y = [], 40
    for ln in lines:
        text, conf = (ln, 0.94) if isinstance(ln, str) else ln
        out.append({"text": text, "bbox": [40, y, 40 + 22 * len(text), y + 44], "confidence": conf})
        y += 60
    return {"doc_id": doc_id, "file_name": file_name, "captured_at": captured_at,
            "pages": [{"page_no": 1, "width": 1080, "height": y + 40, "script_hint": script, "lines": out}]}


DOCS = [
    doc("missing_report_2017", "실종신고_접수증_2017.jpg", "2026-09-15T10:00:00", [
        "실종신고 접수증", "접수번호 2017-00481", "접수일시 2017. 11. 4. 09:20",
        "실종자 정하윤 (여, 21세)", "신고인 정미경 (모)",
        "최종 목격 2017. 11. 2. 22시경 ○○역 3번 출구 부근", "접수관서 ○○경찰서 여성청소년과"]),
    doc("witness_station_2017", "진술서_편의점직원.jpg", "2026-09-15T10:02:00", [
        "진 술 서", "성명: 강태오",
        "본인은 2017. 11. 2. 22시경 ○○역 3번 출구 편의점에서 정하윤으로 보이는 여성을 보았습니다.",
        "검은색 코트를 입고 혼자였습니다.", "2017. 11. 6.", "진술인 강태오 (서명)"]),
    doc("witness_market_2017", "진술서_시장상인.jpg", "2026-09-15T10:03:00", [
        "진 술 서", "성명: 오미란",
        "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을 목격하였습니다.",
        "누군가와 통화하며 버스정류장 쪽으로 걸어갔습니다.", "2017. 11. 8.", "진술인 오미란 (서명)"],
        script="handwritten"),
    doc("family_statement_2017", "가족_진술서.jpg", "2026-09-15T10:05:00", [
        "진 술 서", "진술인 정미경",
        "딸은 11월 2일 밤 11시쯤 마지막으로 저에게 문자를 보냈습니다.",
        "그 뒤로 휴대전화가 꺼져 있었습니다.",
        "2017. 11. 3. 밤 112에 신고하였습니다.",
        "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다."], script="handwritten"),
    doc("news_2018", "기사_2018.jpg", "2026-09-15T10:06:00", [
        "○○시 20대 여성 석 달째 행방 묘연", "입력 2018.02.05 08:30  이○○ 기자",
        "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 마지막으로 찍혔다고 밝혔다.",
        "무단전재 및 재배포 금지"]),
    doc("suspension_notice_2019", "수사중지_통지서_2019.jpg", "2026-09-15T10:08:00", [
        "수사결과 통지서", "사건번호 2017형제30918", "피의자 성명불상", "죄명 약취유인",
        "결정일자 2019. 6. 17.", "결정내용 수사중지(피의자중지)",
        ("이유 피의자를 특정할 수 ▒▒ 수사를 중▒함", 0.46), "담당 수사관 경위 한상우", "○○경찰서장"]),
    doc("tip_statement_2025", "진술서_2025.jpg", "2026-09-15T10:10:00", [
        "진 술 서", "성명: 배수진",
        "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤으로 보이는 여성을 목격하였습니다.",
        "회색 모자를 쓰고 있었고 왼손에 흉터가 있었습니다.", "2025. 9. 1.", "진술인 배수진 (서명)"],
        script="handwritten"),
]

CASE = {
    "case_id": "demo-missing-2017",
    "case_type": "missing_person_suspended",
    "as_of": "2026-09-19",
    "documents": [f"{d['doc_id']}.json" for d in DOCS],
    "user_notes": [
        {"note_id": "note_no_contact", "text": "2019년 통지서를 받은 뒤로 경찰에서 연락 온 적이 없습니다.",
         "created_at": "2026-09-15T11:00:00"},
        {"note_id": "note_tip", "text": "2025년 9월 목격 제보를 전화로 알렸지만 담당자가 바뀌었다고만 들었습니다.",
         "created_at": "2026-09-15T11:05:00"},
    ],
}

if __name__ == "__main__":
    for d in DOCS:
        (HERE / f"{d['doc_id']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "case.json").write_text(json.dumps(CASE, ensure_ascii=False, indent=2), encoding="utf-8")
    print("서류", len(DOCS), "장을 썼습니다")
