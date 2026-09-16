// 자동 생성 파일 — action-engine/tools/export_web.py 로 다시 만든다. 직접 고치지 않는다.
window.TARAE_CASES = [
  {
    "id": "used_goods_fraud",
    "title": "중고거래 사기 피해",
    "type_label": "중고거래 사기",
    "as_of": "2026.06.24",
    "period": "2026.06.01 – 06.03",
    "doc_count": 5,
    "need_count": 8,
    "stages": [
      {
        "label": "발생",
        "state": "done"
      },
      {
        "label": "송금",
        "state": "done"
      },
      {
        "label": "신고",
        "state": "done"
      },
      {
        "label": "접수",
        "state": "current"
      },
      {
        "label": "수사",
        "state": "todo"
      },
      {
        "label": "결과",
        "state": "todo"
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "카톡_0601.png"
      },
      {
        "kind": "PDF",
        "name": "이체확인증.pdf"
      },
      {
        "kind": "PDF",
        "name": "ECRM_접수증.pdf"
      },
      {
        "kind": "IMG",
        "name": "메모.jpg"
      },
      {
        "kind": "IMG",
        "name": "진술서.jpg"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "06/01 10:22",
        "title": "네 판매 중입니다. 미개봉 새 상품이에요",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  카톡_0601.png · 3줄 외 1곳"
      },
      {
        "type": "event",
        "time": "06/01 13~16시경",
        "title": "300,000원 송금",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": true,
        "needs_date": false,
        "source": "출처 ⑤  진술서.jpg · 3줄 외 2곳"
      },
      {
        "type": "event",
        "time": "06/01 14:05",
        "title": "350,000원 송금",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": true,
        "needs_date": false,
        "source": "출처 ②  이체확인증.pdf · 1줄 외 4곳"
      },
      {
        "type": "event",
        "time": "06/02 17~22시경",
        "title": "6/2 저녁 전화 안받음",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": true,
        "source": "출처 ④  메모.jpg · 1줄 외 1곳"
      },
      {
        "type": "event",
        "time": "06/03",
        "title": "6/3 사이버수사대 신고함",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": true,
        "source": "출처 ④  메모.jpg · 2줄"
      },
      {
        "type": "event",
        "time": "06/03 09:12",
        "title": "사이버범죄 신고 접수증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  ECRM_접수증.pdf · 1줄 외 1곳"
      }
    ],
    "issues": [
      {
        "label": "자료끼리 어긋남",
        "severity": "conflict",
        "items": [
          {
            "text": "송금 금액: 자료마다 다르게 적혀 있습니다 — ‘350,000원’(transfer_receipt · 6줄) / ‘300,000원’(statement · 3줄)",
            "how": "근거 · 이체확인증.pdf 6줄"
          }
        ]
      },
      {
        "label": "확인되지 않음",
        "severity": "unknown",
        "items": [
          {
            "text": "입금 계좌 예금주 명의: 찬찬의 말만 있고 이를 뒷받침하는 기록 자료가 없습니다 — ‘계좌는 제 명의예요’(kakao_0601 · 5줄)",
            "how": "근거 · 카톡_0601.png 5줄"
          },
          {
            "text": "판매자 발송 여부: 찬찬, 판매자의 말만 있고 이를 뒷받침하는 기록 자료가 없습니다 — ‘택배 보냈어요, 내일 도착합니다’(kakao_0601 · 8줄) / ‘판매자는 물건을 보냈다고 하였으나 물건을 받지 못하였습니다.’(statement · 4줄)",
            "how": "근거 · 카톡_0601.png 8줄"
          }
        ]
      },
      {
        "label": "빠진 정보",
        "severity": "gap",
        "items": [
          {
            "text": "‘사이버범죄 신고 접수증’(2026-06-03 09:12) 이후 기관의 진행 기록이 없습니다 (21일 경과)",
            "how": "근거 · ECRM_접수증.pdf 1줄"
          },
          {
            "text": "담당 수사관: 올린 자료에서 찾지 못했습니다",
            "how": "확인한 자료 6개에서 찾지 못함"
          },
          {
            "text": "사건번호: 올린 자료에서 찾지 못했습니다",
            "how": "확인한 자료 6개에서 찾지 못함"
          }
        ]
      },
      {
        "label": "읽히지 않은 부분",
        "severity": "gap",
        "items": [
          {
            "text": "이체확인증.pdf에서 읽히지 않은 부분이 1곳 있습니다 (7줄). 사진을 보고 알려주세요",
            "how": "근거 · 이체확인증.pdf 7줄"
          },
          {
            "text": "메모.jpg에서 읽히지 않은 부분이 1곳 있습니다 (4줄). 사진을 보고 알려주세요",
            "how": "근거 · 메모.jpg 4줄"
          }
        ]
      }
    ],
    "next_action": {
      "rule_no": 6,
      "action": "ACT-모순확인",
      "label": "자료끼리 어긋난 부분 확인 요청",
      "why": "송금 금액: 자료마다 다르게 적혀 있습니다 — ‘350,000원’(transfer_receipt · 6줄) / ‘300,000원’(statement · 3줄)",
      "rule_why": "진술 모순은 재수사 사유가 된다",
      "due": null,
      "state": "unresolved",
      "rows": [],
      "prepare": null,
      "note": null,
      "unverified": true,
      "also": [
        {
          "rule_no": 7,
          "label": "수사 기록 열람 신청",
          "why": "수사 기록 없이는 다른 판단이 불가능하다"
        },
        {
          "rule_no": 8,
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        }
      ]
    }
  },
  {
    "id": "long_unsolved_missing",
    "title": "2015년 실종 사건",
    "type_label": "실종 사건 · 수사중지",
    "as_of": "2026.09.11",
    "period": "2015.10 – 2023.04",
    "doc_count": 6,
    "need_count": 10,
    "stages": [
      {
        "label": "발생",
        "state": "done"
      },
      {
        "label": "신고",
        "state": "done"
      },
      {
        "label": "접수",
        "state": "done"
      },
      {
        "label": "수사",
        "state": "todo"
      },
      {
        "label": "결과",
        "state": "current"
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "실종신고_접수증_2015.jpg"
      },
      {
        "kind": "IMG",
        "name": "기사캡처_2016.png"
      },
      {
        "kind": "IMG",
        "name": "최영호_진술서.jpg"
      },
      {
        "kind": "IMG",
        "name": "수사중지_결정통지서.jpg"
      },
      {
        "kind": "IMG",
        "name": "진정서_2023.jpg"
      },
      {
        "kind": "IMG",
        "name": "엄마_메모.jpg"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "2015.10.10\n20~24시경",
        "title": "15년 10월 10일 밤 연락 끊김",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑥  엄마_메모.jpg · 2줄"
      },
      {
        "type": "event",
        "time": "2015.10.10\n22시~익일 1시경",
        "title": "경찰은 김씨가 지난해 10월 10일 밤 11시쯤 ○○역 인근 CCTV에…",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  기사캡처_2016.png · 3줄 외 3곳"
      },
      {
        "type": "event",
        "time": "2015.10.12",
        "title": "10월 12일 경찰서 실종신고",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑥  엄마_메모.jpg · 3줄"
      },
      {
        "type": "event",
        "time": "2015.10.12\n21:30",
        "title": "실종신고 접수증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  실종신고_접수증_2015.jpg · 1줄 외 1곳"
      },
      {
        "type": "gap",
        "range": "2016.02.03 – 2019.02.14",
        "text": "이 기간의 기록이 없어요 (약 3.0년)"
      },
      {
        "type": "event",
        "time": "2019.03",
        "title": "본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남…",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  최영호_진술서.jpg · 3줄 외 2곳"
      },
      {
        "type": "gap",
        "range": "2019.04.16 – 2022.03.15",
        "text": "이 기간의 기록이 없어요 (약 2.9년)"
      },
      {
        "type": "event",
        "time": "2022.03.15",
        "title": "수사결과 통지서",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ④  수사중지_결정통지서.jpg · 1줄 외 1곳"
      },
      {
        "type": "gap",
        "range": "2022.03.16 – 2023.04.02",
        "text": "이 기간의 기록이 없어요 (약 1.0년)"
      },
      {
        "type": "event",
        "time": "2023.04.02",
        "title": "2015. 10. 10. 실종된 아들 김민수 사건(2016형제12345…",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑤  진정서_2023.jpg · 4줄 외 1곳"
      },
      {
        "type": "event",
        "time": "시각 미상",
        "title": "○○시 20대 남성 실종 넉 달째 행방 묘연",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  기사캡처_2016.png · 1줄"
      }
    ],
    "issues": [
      {
        "label": "확인되지 않음",
        "severity": "unknown",
        "items": [
          {
            "text": "‘본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남…’(2019-03-01~03-10, witness_statement_2019 · 3줄, petition_2023 · 6줄) — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2022-03-15)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
            "how": "근거 · 최영호_진술서.jpg 3줄"
          },
          {
            "text": "담당 수사관: 기록상 ‘박정호’(suspension_notice_2022 · 8줄, 2022-03-15)이지만, 이후 바뀌었다는 내용이 있습니다 — ‘작년 추석 무렵 수사관한테 전화 → 담당자 바뀌었다고 함’(mother_memo · 4줄, 2025-10-04~10-08). 현재 담당 수사관 확인이 필요합니다 (바뀐 정보가 있을 수 있는 부분이 읽히지 않았습니다: mother_memo · 5줄)",
            "how": "근거 · 수사중지_결정통지서.jpg 8줄"
          },
          {
            "text": "마지막 연락 시점: ‘2015-10-11 00~06시’(news_2016 · 4줄) / ‘2015-10-10 20~24시’(mother_memo · 2줄) — 자료에서 읽어낸 값의 신뢰도가 낮아 확인이 필요합니다",
            "how": "근거 · 기사캡처_2016.png 4줄"
          }
        ]
      },
      {
        "label": "빠진 정보",
        "severity": "gap",
        "items": [
          {
            "text": "‘수사결과 통지서’(2022-03-15) 이후 기관의 진행 기록이 없습니다 (1641일 경과)",
            "how": "근거 · 수사중지_결정통지서.jpg 1줄"
          },
          {
            "text": "‘수사’ 단계에 해당하는 자료가 없습니다",
            "how": "확인한 자료 7개에서 찾지 못함"
          },
          {
            "text": "2016-02-03 ~ 2019-02-14 사이의 기록이 없습니다 (약 3.0년)",
            "how": "근거 · 기사캡처_2016.png 2줄"
          },
          {
            "text": "2019-04-16 ~ 2022-03-15 사이의 기록이 없습니다 (약 2.9년)",
            "how": "근거 · 최영호_진술서.jpg 3줄"
          },
          {
            "text": "2022-03-16 ~ 2023-04-02 사이의 기록이 없습니다 (약 1.0년)",
            "how": "근거 · 수사중지_결정통지서.jpg 1줄"
          }
        ]
      },
      {
        "label": "읽히지 않은 부분",
        "severity": "gap",
        "items": [
          {
            "text": "실종신고_접수증_2015.jpg에서 읽히지 않은 부분이 1곳 있습니다 (8줄). 사진을 보고 알려주세요",
            "how": "근거 · 실종신고_접수증_2015.jpg 8줄"
          },
          {
            "text": "엄마_메모.jpg에서 읽히지 않은 부분이 1곳 있습니다 (5줄). 사진을 보고 알려주세요",
            "how": "근거 · 엄마_메모.jpg 5줄"
          }
        ]
      }
    ],
    "next_action": {
      "rule_no": 5,
      "action": "ACT-신규정보제출",
      "label": "새로 확인된 정보를 수사기관에 제출",
      "why": "최영호_진술서.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
      "rule_why": "새 정보는 중지·종결된 절차를 되살릴 수 있다",
      "due": null,
      "state": "unresolved",
      "rows": [],
      "prepare": null,
      "note": null,
      "unverified": true,
      "also": [
        {
          "rule_no": 7,
          "label": "수사 기록 열람 신청",
          "why": "수사 기록 없이는 다른 판단이 불가능하다"
        },
        {
          "rule_no": 8,
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        },
        {
          "rule_no": 9,
          "label": "기록이 빈 기간의 자료 확보",
          "why": "기록 공백은 반박 여지를 남긴다"
        }
      ]
    }
  },
  {
    "id": "suspension_recent",
    "title": "고소 사건 (수사중지)",
    "type_label": "수사중지 사건",
    "as_of": "2026.09.12",
    "period": "2021.05 – 2026.08",
    "doc_count": 4,
    "need_count": 5,
    "stages": [
      {
        "label": "발생",
        "state": "done"
      },
      {
        "label": "신고",
        "state": "done"
      },
      {
        "label": "접수",
        "state": "done"
      },
      {
        "label": "수사",
        "state": "todo"
      },
      {
        "label": "결과",
        "state": "current"
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "고소장_2021.jpg"
      },
      {
        "kind": "IMG",
        "name": "접수증_2021.jpg"
      },
      {
        "kind": "IMG",
        "name": "수사중지_결정통지서.jpg"
      },
      {
        "kind": "IMG",
        "name": "조미래_진술서.jpg"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "2021.05.18",
        "title": "18,000,000원 발생",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2021.jpg · 5줄 외 1곳"
      },
      {
        "type": "event",
        "time": "2021.05.25",
        "title": "2021. 5. 25. ○○경찰서에 고소하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2021.jpg · 7줄"
      },
      {
        "type": "event",
        "time": "2021.05.25\n14:20",
        "title": "접 수 증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  접수증_2021.jpg · 1줄 외 1곳"
      },
      {
        "type": "gap",
        "range": "2021.05.26 – 2025.06.03",
        "text": "이 기간의 기록이 없어요 (약 4.0년)"
      },
      {
        "type": "event",
        "time": "2025.06.03",
        "title": "2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ④  조미래_진술서.jpg · 3줄"
      },
      {
        "type": "gap",
        "range": "2025.06.11 – 2026.08.18",
        "text": "이 기간의 기록이 없어요 (약 1.2년)"
      },
      {
        "type": "event",
        "time": "2026.08.18",
        "title": "수사결과 통지서",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  수사중지_결정통지서.jpg · 1줄 외 1곳"
      }
    ],
    "issues": [
      {
        "label": "확인되지 않음",
        "severity": "unknown",
        "items": [
          {
            "text": "‘2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.’(2025-06-03, witness_statement_2025 · 3줄) — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2026-08-18)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
            "how": "근거 · 조미래_진술서.jpg 3줄"
          },
          {
            "text": "사건 발생 시점: 정하늘, 조미래의 말만 있고 이를 뒷받침하는 기록 자료가 없습니다 — ‘2021. 5. 18. 인테리어 공사대금 명목으로 1,800만원을 편취당하는 사기 피해를 입었습니다.’(complaint_2021 · 5줄) / ‘2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.’(witness_statement_2025 · 3줄)",
            "how": "근거 · 고소장_2021.jpg 5줄"
          }
        ]
      },
      {
        "label": "빠진 정보",
        "severity": "gap",
        "items": [
          {
            "text": "‘수사’ 단계에 해당하는 자료가 없습니다",
            "how": "확인한 자료 5개에서 찾지 못함"
          },
          {
            "text": "2021-05-26 ~ 2025-06-03 사이의 기록이 없습니다 (약 4.0년)",
            "how": "근거 · 고소장_2021.jpg 7줄"
          },
          {
            "text": "2025-06-11 ~ 2026-08-18 사이의 기록이 없습니다 (약 1.2년)",
            "how": "근거 · 조미래_진술서.jpg 6줄"
          }
        ]
      }
    ],
    "next_action": {
      "rule_no": 2,
      "action": "ACT-불복기한",
      "label": "기한 안에 결정에 대한 불복 절차 진행",
      "why": "기한이 지나면 그 불복 경로가 소멸한다",
      "rule_why": "기한이 지나면 그 불복 경로가 소멸한다",
      "due": {
        "label": "D-5",
        "text": "2026.09.17까지 (수사중지 이의제기 기한)",
        "severity": "critical"
      },
      "state": "filled",
      "rows": [
        {
          "k": "무엇을",
          "v": "수사중지 결정 이의제기서"
        },
        {
          "k": "어디에",
          "v": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 송부된다)"
        },
        {
          "k": "언제까지",
          "v": "2026.09.17까지 (수사중지 이의제기 기한)"
        },
        {
          "k": "근거",
          "v": "경찰수사규칙 제101조"
        }
      ],
      "prepare": {
        "done": 1,
        "total": 2,
        "items": [
          {
            "label": "수사중지 결정 이의제기서",
            "state": "생성가능",
            "required": true
          },
          {
            "label": "수사결과 통지서 (수사중지 결정)",
            "state": "보유",
            "required": false
          }
        ]
      },
      "note": "이의제기(30일) 말고 두 번째 경로가 있다. 수사준칙 제54조 제3항 — 수사중지 결정이 법령위반·인권침해·현저한 수사권 남용으로 의심되면 검사에게 신고할 수 있고, 여기에는 기한 제한이 없다. 경찰수사규칙 제97조 제8항이 이 사실을 통지서에 적도록 하고 있어서, 사용자가 받은 통지서에 이미 안내가 들어 있다",
      "unverified": true,
      "also": [
        {
          "rule_no": 5,
          "label": "새로 확인된 정보를 수사기관에 제출",
          "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
        },
        {
          "rule_no": 7,
          "label": "수사 기록 열람 신청",
          "why": "수사 기록 없이는 다른 판단이 불가능하다"
        },
        {
          "rule_no": 8,
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        },
        {
          "rule_no": 9,
          "label": "기록이 빈 기간의 자료 확보",
          "why": "기록 공백은 반박 여지를 남긴다"
        }
      ]
    }
  }
];
