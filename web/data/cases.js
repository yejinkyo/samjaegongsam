// 자동 생성 파일 — action-engine/tools/export_web.py 로 다시 만든다. 직접 고치지 않는다.
window.TARAE_CASES = [
  {
    "id": "used_goods_fraud",
    "title": "중고거래 사기 피해",
    "type": "used_goods_fraud",
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
        "name": "카톡_0601.png",
        "doc_id": "kakao_0601"
      },
      {
        "kind": "PDF",
        "name": "이체확인증.pdf",
        "doc_id": "transfer_receipt"
      },
      {
        "kind": "PDF",
        "name": "ECRM_접수증.pdf",
        "doc_id": "ecrm_receipt"
      },
      {
        "kind": "IMG",
        "name": "메모.jpg",
        "doc_id": "memo_handwritten"
      },
      {
        "kind": "IMG",
        "name": "진술서.jpg",
        "doc_id": "statement"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "06/01 10:22",
        "title": "거래 대화",
        "full": "네 판매 중입니다. 미개봉 새 상품이에요",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  카톡_0601.png · 3줄 외 1곳",
        "sources": [
          {
            "name": "카톡_0601.png",
            "doc_id": "kakao_0601",
            "line": 3,
            "quote": "네 판매 중입니다. 미개봉 새 상품이에요"
          },
          {
            "name": "카톡_0601.png",
            "doc_id": "kakao_0601",
            "line": 3,
            "quote": "오전 10:22"
          }
        ]
      },
      {
        "type": "event",
        "time": "06/01 13~16시경",
        "title": "300,000원 송금",
        "full": "300,000원 송금",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": true,
        "needs_date": false,
        "source": "출처 ⑤  진술서.jpg · 3줄 외 2곳",
        "sources": [
          {
            "name": "진술서.jpg",
            "doc_id": "statement",
            "line": 3,
            "quote": "위 진술인은 2026년 6월 1일 오후 2시경 판매자 계좌로 30만원을 송금하였습니다."
          },
          {
            "name": "진술서.jpg",
            "doc_id": "statement",
            "line": 3,
            "quote": "2026년 6월 1일 오후 2시경"
          },
          {
            "name": "진술서.jpg",
            "doc_id": "statement",
            "line": 3,
            "quote": "30만원"
          }
        ]
      },
      {
        "type": "event",
        "time": "06/01 14:05",
        "title": "350,000원 송금",
        "full": "350,000원 송금",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": true,
        "needs_date": false,
        "source": "출처 ②  이체확인증.pdf · 1줄 외 4곳",
        "sources": [
          {
            "name": "이체확인증.pdf",
            "doc_id": "transfer_receipt",
            "line": 1,
            "quote": "이체확인증"
          },
          {
            "name": "이체확인증.pdf",
            "doc_id": "transfer_receipt",
            "line": 2,
            "quote": "2026-06-01 14:05"
          },
          {
            "name": "이체확인증.pdf",
            "doc_id": "transfer_receipt",
            "line": 6,
            "quote": "350,000원"
          },
          {
            "name": "카톡_0601.png",
            "doc_id": "kakao_0601",
            "line": 6,
            "quote": "송금했습니다"
          },
          {
            "name": "카톡_0601.png",
            "doc_id": "kakao_0601",
            "line": 6,
            "quote": "오후 2:05"
          }
        ]
      },
      {
        "type": "event",
        "time": "06/02 17~22시경",
        "title": "연락 두절",
        "full": "6/2 저녁 전화 안받음",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": true,
        "source": "출처 ④  메모.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "메모.jpg",
            "doc_id": "memo_handwritten",
            "line": 1,
            "quote": "6/2 저녁 전화 안받음"
          },
          {
            "name": "직접 입력",
            "doc_id": "note_0602",
            "line": 1,
            "quote": "6월 2일 하루 종일 연락이 안 됐습니다."
          }
        ]
      },
      {
        "type": "event",
        "time": "06/03",
        "title": "사이버수사대 신고",
        "full": "6/3 사이버수사대 신고함",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": true,
        "source": "출처 ④  메모.jpg · 2줄",
        "sources": [
          {
            "name": "메모.jpg",
            "doc_id": "memo_handwritten",
            "line": 2,
            "quote": "6/3 사이버수사대 신고함"
          }
        ]
      },
      {
        "type": "event",
        "time": "06/03 09:12",
        "title": "사이버범죄 신고 접수",
        "full": "사이버범죄 신고 접수증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  ECRM_접수증.pdf · 1줄 외 1곳",
        "sources": [
          {
            "name": "ECRM_접수증.pdf",
            "doc_id": "ecrm_receipt",
            "line": 1,
            "quote": "사이버범죄 신고 접수증"
          },
          {
            "name": "ECRM_접수증.pdf",
            "doc_id": "ecrm_receipt",
            "line": 3,
            "quote": "2026.06.03 09:12"
          }
        ]
      }
    ],
    "people": [
      {
        "label": "사람",
        "items": [
          {
            "name": "나",
            "roles": [
              "사용자"
            ],
            "docs": [
              "이체확인증.pdf",
              "카톡_0601.png"
            ],
            "same_as": []
          },
          {
            "name": "홍길동",
            "roles": [
              "진술인"
            ],
            "docs": [],
            "same_as": []
          }
        ]
      },
      {
        "label": "기관",
        "items": [
          {
            "name": "국민은행",
            "roles": [],
            "docs": [
              "이체확인증.pdf",
              "카톡_0601.png"
            ],
            "same_as": []
          },
          {
            "name": "신한은행",
            "roles": [],
            "docs": [
              "이체확인증.pdf",
              "카톡_0601.png"
            ],
            "same_as": []
          },
          {
            "name": "사이버수사대",
            "roles": [],
            "docs": [
              "메모.jpg"
            ],
            "same_as": []
          },
          {
            "name": "경찰서",
            "roles": [],
            "docs": [],
            "same_as": []
          }
        ]
      },
      {
        "label": "계좌",
        "items": [
          {
            "name": "940*******21",
            "roles": [],
            "docs": [
              "이체확인증.pdf",
              "카톡_0601.png"
            ],
            "same_as": []
          },
          {
            "name": "110*******88",
            "roles": [],
            "docs": [
              "이체확인증.pdf",
              "카톡_0601.png"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "접수번호",
        "items": [
          {
            "name": "2026-0603-***",
            "roles": [],
            "docs": [
              "ECRM_접수증.pdf"
            ],
            "same_as": []
          }
        ]
      }
    ],
    "slots": [
      {
        "slot": "송금 금액",
        "value": null,
        "state": "자료마다 다름",
        "severity": "conflict",
        "said": [
          {
            "value": "350,000",
            "doc": "이체확인증.pdf",
            "speaker": "신한은행",
            "record": true
          },
          {
            "value": "300,000",
            "doc": "진술서.jpg",
            "speaker": "홍길동",
            "record": false
          }
        ]
      },
      {
        "slot": "송금 시점",
        "value": "2026-06-01 14:05",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2026-06-01 14:05",
            "doc": "이체확인증.pdf",
            "speaker": "신한은행",
            "record": true
          },
          {
            "value": "2026-06-01 13~16시",
            "doc": "진술서.jpg",
            "speaker": "홍길동",
            "record": false
          }
        ]
      },
      {
        "slot": "계좌번호",
        "value": "940*******21",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "940*******21",
            "doc": "카톡_0601.png",
            "speaker": "찬찬",
            "record": false
          },
          {
            "value": "110*******88",
            "doc": "이체확인증.pdf",
            "speaker": "신한은행",
            "record": true
          },
          {
            "value": "940*******21",
            "doc": "이체확인증.pdf",
            "speaker": "신한은행",
            "record": true
          }
        ]
      },
      {
        "slot": "예금주",
        "value": null,
        "state": "말만 있고 기록 없음",
        "severity": "unverified",
        "said": [
          {
            "value": "찬찬",
            "doc": "카톡_0601.png",
            "speaker": "찬찬",
            "record": false
          }
        ]
      },
      {
        "slot": "발송 여부",
        "value": null,
        "state": "말만 있고 기록 없음",
        "severity": "unverified",
        "said": [
          {
            "value": "예",
            "doc": "카톡_0601.png",
            "speaker": "찬찬",
            "record": false
          },
          {
            "value": "예",
            "doc": "진술서.jpg",
            "speaker": "판매자",
            "record": false
          }
        ]
      },
      {
        "slot": "송장번호",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
      },
      {
        "slot": "접수번호",
        "value": "2026-0603-***",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2026-0603-***",
            "doc": "ECRM_접수증.pdf",
            "speaker": "ECRM_접수증.pdf 발급처",
            "record": true
          }
        ]
      },
      {
        "slot": "접수일시",
        "value": "2026-06-03 09:12",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2026-06-03 09:12",
            "doc": "ECRM_접수증.pdf",
            "speaker": "ECRM_접수증.pdf 발급처",
            "record": true
          }
        ]
      },
      {
        "slot": "담당 수사관",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
      },
      {
        "slot": "offence",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
      },
      {
        "slot": "사건번호",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
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
      "rule_no": 7,
      "action": "ACT-모순확인",
      "label": "자료끼리 어긋난 부분 확인 요청",
      "why": "송금 금액: 자료마다 다르게 적혀 있습니다 — ‘350,000원’(transfer_receipt · 6줄) / ‘300,000원’(statement · 3줄)",
      "rule_why": "진술 모순은 재수사 사유가 된다",
      "due": null,
      "state": "filled",
      "rows": [
        {
          "k": "무엇을",
          "v": "자료·의견 제출서"
        },
        {
          "k": "어디에",
          "v": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다"
        },
        {
          "k": "근거",
          "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조"
        }
      ],
      "prepare": {
        "done": 2,
        "total": 3,
        "items": [
          {
            "label": "자료·의견 제출서",
            "state": "생성가능",
            "required": true
          },
          {
            "label": "서로 어긋난 내용이 적힌 자료 (사본)",
            "state": "보유",
            "required": true
          },
          {
            "label": "수사결과 통지서 또는 접수증 (사건번호 확인용)",
            "state": "보유",
            "required": false
          }
        ]
      },
      "note": "어긋난 부분을 자료 이름과 줄로 짚고 사실관계 확인을 요청한다(수사준칙 제25조). 누가 틀렸는지 단정하지 않는다. 본인이 한 진술은 열람·복사를 신청해 확인할 수 있다(수사준칙 제69조 제1항).",
      "unverified": true,
      "also": [
        {
          "rule_no": 8,
          "action": "ACT-기록열람",
          "label": "수사 기록 열람 신청",
          "why": "수사 기록 없이는 다른 판단이 불가능하다"
        },
        {
          "rule_no": 9,
          "action": "ACT-근거보완",
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        }
      ],
      "submit_to": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
      "form_name": "자료·의견 제출서",
      "draft": {
        "is_draft": true,
        "prose": null,
        "form_name": "자료·의견 제출서",
        "form_source": "법정 서식 없음 — 수사준칙 제25조(자료·의견의 제출기회 보장)에 따라 서면으로 낸다",
        "form_url": null,
        "fields": [
          {
            "label": "접수번호",
            "value": "2026-0603-***",
            "from": "case_record"
          },
          {
            "label": "서식",
            "value": "자료·의견 제출서",
            "from": "knowledge_base"
          },
          {
            "label": "제출처",
            "value": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
            "from": "knowledge_base"
          },
          {
            "label": "근거 법령",
            "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조",
            "from": "knowledge_base"
          }
        ],
        "unfilled": [
          {
            "label": "사건번호",
            "reason": "자료에서 찾지 못했습니다."
          },
          {
            "label": "담당 수사관",
            "reason": "자료에서 찾지 못했습니다."
          },
          {
            "label": "결정 내용",
            "reason": "자료에서 찾지 못했습니다."
          },
          {
            "label": "결정일",
            "reason": "자료에서 찾지 못했습니다."
          },
          {
            "label": "신청인 성명",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 연락처",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 주소",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          }
        ],
        "sections": [
          {
            "heading": "사건 경위",
            "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
            "lines": [
              {
                "date": "2026. 6. 1.",
                "text": "네 판매 중입니다. 미개봉 새 상품이에요",
                "level": "statement",
                "source": "카톡_0601.png 3줄"
              },
              {
                "date": "2026. 6. 1.",
                "text": "300,000원 송금",
                "level": "statement",
                "source": "진술서.jpg 3줄"
              },
              {
                "date": "2026. 6. 1.",
                "text": "350,000원 송금",
                "level": "record",
                "source": "이체확인증.pdf 1줄"
              },
              {
                "date": "2026. 6. 2.",
                "text": "6/2 저녁 전화 안받음",
                "level": "statement",
                "source": "메모.jpg 1줄"
              },
              {
                "date": "2026. 6. 3.",
                "text": "6/3 사이버수사대 신고함",
                "level": "statement",
                "source": "메모.jpg 2줄"
              },
              {
                "date": "2026. 6. 3.",
                "text": "사이버범죄 신고 접수증",
                "level": "record",
                "source": "ECRM_접수증.pdf 1줄"
              }
            ]
          },
          {
            "heading": "요청 사항",
            "note": "어긋난 부분을 어떻게 확인해 달라는지 직접 적어 주세요. 타래는 이 칸을 대신 쓰지 않습니다.",
            "lines": []
          }
        ],
        "dropped": 0
      }
    },
    "actions": [
      {
        "rule_no": 7,
        "action": "ACT-모순확인",
        "label": "자료끼리 어긋난 부분 확인 요청",
        "why": "송금 금액: 자료마다 다르게 적혀 있습니다 — ‘350,000원’(transfer_receipt · 6줄) / ‘300,000원’(statement · 3줄)",
        "rule_why": "진술 모순은 재수사 사유가 된다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "자료·의견 제출서"
          },
          {
            "k": "어디에",
            "v": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다"
          },
          {
            "k": "근거",
            "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조"
          }
        ],
        "prepare": {
          "done": 2,
          "total": 3,
          "items": [
            {
              "label": "자료·의견 제출서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "서로 어긋난 내용이 적힌 자료 (사본)",
              "state": "보유",
              "required": true
            },
            {
              "label": "수사결과 통지서 또는 접수증 (사건번호 확인용)",
              "state": "보유",
              "required": false
            }
          ]
        },
        "note": "어긋난 부분을 자료 이름과 줄로 짚고 사실관계 확인을 요청한다(수사준칙 제25조). 누가 틀렸는지 단정하지 않는다. 본인이 한 진술은 열람·복사를 신청해 확인할 수 있다(수사준칙 제69조 제1항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          }
        ],
        "submit_to": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
        "form_name": "자료·의견 제출서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "자료·의견 제출서",
          "form_source": "법정 서식 없음 — 수사준칙 제25조(자료·의견의 제출기회 보장)에 따라 서면으로 낸다",
          "form_url": null,
          "fields": [
            {
              "label": "접수번호",
              "value": "2026-0603-***",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "자료·의견 제출서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "사건번호",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "담당 수사관",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "결정 내용",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "결정일",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2026. 6. 1.",
                  "text": "네 판매 중입니다. 미개봉 새 상품이에요",
                  "level": "statement",
                  "source": "카톡_0601.png 3줄"
                },
                {
                  "date": "2026. 6. 1.",
                  "text": "300,000원 송금",
                  "level": "statement",
                  "source": "진술서.jpg 3줄"
                },
                {
                  "date": "2026. 6. 1.",
                  "text": "350,000원 송금",
                  "level": "record",
                  "source": "이체확인증.pdf 1줄"
                },
                {
                  "date": "2026. 6. 2.",
                  "text": "6/2 저녁 전화 안받음",
                  "level": "statement",
                  "source": "메모.jpg 1줄"
                },
                {
                  "date": "2026. 6. 3.",
                  "text": "6/3 사이버수사대 신고함",
                  "level": "statement",
                  "source": "메모.jpg 2줄"
                },
                {
                  "date": "2026. 6. 3.",
                  "text": "사이버범죄 신고 접수증",
                  "level": "record",
                  "source": "ECRM_접수증.pdf 1줄"
                }
              ]
            },
            {
              "heading": "요청 사항",
              "note": "어긋난 부분을 어떻게 확인해 달라는지 직접 적어 주세요. 타래는 이 칸을 대신 쓰지 않습니다.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 8,
        "action": "ACT-기록열람",
        "label": "수사 기록 열람 신청",
        "why": "‘사이버범죄 신고 접수증’(2026-06-03 09:12) 이후 기관의 진행 기록이 없습니다 (21일 경과)",
        "rule_why": "수사 기록 없이는 다른 판단이 불가능하다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "수사기록 열람·등사 신청서"
          },
          {
            "k": "어디에",
            "v": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청"
          },
          {
            "k": "근거",
            "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침"
          }
        ],
        "prepare": {
          "done": 0,
          "total": 2,
          "items": [
            {
              "label": "수사기록 열람·등사 신청서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "신청인 신분 확인 서류",
              "state": "미보유",
              "required": true
            }
          ]
        },
        "note": "불송치·불기소로 끝난 사건은 정보공개청구가 거부되는 일이 잦다. 거부를 전제로 다음 경로(이의신청·행정소송)까지 함께 안내해야 한다. 수사 중인 사건은 본인 진술과 본인이 낸 서류만(수사준칙 제69조 제1항), 불송치·불기소 사건은 기록의 전부 또는 일부를(제2항) 신청할 수 있다. 가족은 위임장과 신분관계 증명서를 내고 신청할 수 있다(제5항). 경찰관서는 신청을 받은 날부터 10일 이내에 공개 여부를 결정한다(경찰수사규칙 제87조 제2항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          }
        ],
        "submit_to": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
        "form_name": "수사기록 열람·등사 신청서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "수사기록 열람·등사 신청서",
          "form_source": "검찰보존사무규칙 별지 제5호서식 「사건기록 열람·등사 신청서」(제20조의2·제20조의3). 경찰관서 신청 서식은 경찰청장이 따로 정한다(경찰수사규칙 제87조 제6항)",
          "form_url": "https://law.go.kr/flDownload.do?gubun=&flSeq=132313759",
          "fields": [
            {
              "label": "접수번호",
              "value": "2026-0603-***",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "수사기록 열람·등사 신청서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "사건번호",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "담당 수사관",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "결정 내용",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "결정일",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2026. 6. 1.",
                  "text": "네 판매 중입니다. 미개봉 새 상품이에요",
                  "level": "statement",
                  "source": "카톡_0601.png 3줄"
                },
                {
                  "date": "2026. 6. 1.",
                  "text": "300,000원 송금",
                  "level": "statement",
                  "source": "진술서.jpg 3줄"
                },
                {
                  "date": "2026. 6. 1.",
                  "text": "350,000원 송금",
                  "level": "record",
                  "source": "이체확인증.pdf 1줄"
                },
                {
                  "date": "2026. 6. 2.",
                  "text": "6/2 저녁 전화 안받음",
                  "level": "statement",
                  "source": "메모.jpg 1줄"
                },
                {
                  "date": "2026. 6. 3.",
                  "text": "6/3 사이버수사대 신고함",
                  "level": "statement",
                  "source": "메모.jpg 2줄"
                },
                {
                  "date": "2026. 6. 3.",
                  "text": "사이버범죄 신고 접수증",
                  "level": "record",
                  "source": "ECRM_접수증.pdf 1줄"
                }
              ]
            },
            {
              "heading": "이의 사유",
              "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 9,
        "action": "ACT-근거보완",
        "label": "주장을 뒷받침할 근거 자료 보완",
        "why": "이체확인증.pdf에서 읽히지 않은 부분이 1곳 있습니다 (7줄). 사진을 보고 알려주세요",
        "rule_why": "근거 없는 주장은 판단 대상이 되지 않는다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "원본 출처나 감정 결과를 확보하는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      }
    ],
    "response_choices": [
      "불송치",
      "불기소",
      "항고 기각",
      "피의자중지",
      "참고인중지",
      "기소"
    ],
    "outcomes": {
      "불송치": {
        "st": "경찰 불송치",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "불기소": {
        "st": "검찰 불기소",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "검찰 항고 기한",
            "period_days": 30,
            "statute": "검찰청법 제10조",
            "submit_to": "불기소 처분을 한 검사가 속한 지방검찰청 또는 지청을 거쳐 관할 고등검찰청 검사장"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "항고 기각": {
        "st": "이의신청/항고 중",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "법원 재정신청 기한",
            "period_days": 10,
            "statute": "형사소송법 제260조 제3항",
            "submit_to": "지방검찰청 검사장 또는 지청장"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "피의자중지": {
        "st": "피의자 중지",
        "next": "자료끼리 어긋난 부분 확인 요청",
        "next_key": "ACT-모순확인",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "참고인중지": {
        "st": "참고인 중지",
        "next": "자료끼리 어긋난 부분 확인 요청",
        "next_key": "ACT-모순확인",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "기소": {
        "st": "재판 진행 중",
        "next": "자료끼리 어긋난 부분 확인 요청",
        "next_key": "ACT-모순확인",
        "deadlines": [
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      }
    }
  },
  {
    "id": "long_unsolved_missing",
    "title": "2015년 실종 사건",
    "type": "missing_person_suspended",
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
        "label": "수사",
        "state": "todo"
      },
      {
        "label": "중지",
        "state": "current"
      },
      {
        "label": "재수사",
        "state": "todo"
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "실종신고_접수증_2015.jpg",
        "doc_id": "missing_report_2015"
      },
      {
        "kind": "IMG",
        "name": "기사캡처_2016.png",
        "doc_id": "news_2016"
      },
      {
        "kind": "IMG",
        "name": "최영호_진술서.jpg",
        "doc_id": "witness_statement_2019"
      },
      {
        "kind": "IMG",
        "name": "수사중지_결정통지서.jpg",
        "doc_id": "suspension_notice_2022"
      },
      {
        "kind": "IMG",
        "name": "진정서_2023.jpg",
        "doc_id": "petition_2023"
      },
      {
        "kind": "IMG",
        "name": "엄마_메모.jpg",
        "doc_id": "mother_memo"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "2015.10.10\n20~24시경",
        "title": "연락 두절",
        "full": "15년 10월 10일 밤 연락 끊김",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑥  엄마_메모.jpg · 2줄",
        "sources": [
          {
            "name": "엄마_메모.jpg",
            "doc_id": "mother_memo",
            "line": 2,
            "quote": "15년 10월 10일 밤 연락 끊김"
          }
        ]
      },
      {
        "type": "event",
        "time": "2015.10.10\n22시~익일 1시경",
        "title": "마지막 목격 · ○○역 인근",
        "full": "경찰은 김씨가 지난해 10월 10일 밤 11시쯤 ○○역 인근 CCTV에 마지막으로 찍혔다고 밝혔다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  기사캡처_2016.png · 3줄 외 3곳",
        "sources": [
          {
            "name": "기사캡처_2016.png",
            "doc_id": "news_2016",
            "line": 3,
            "quote": "경찰은 김씨가 지난해 10월 10일 밤 11시쯤 ○○역 인근 CCTV에 마지막으로 찍혔다고 밝혔다."
          },
          {
            "name": "기사캡처_2016.png",
            "doc_id": "news_2016",
            "line": 3,
            "quote": "10월 10일 밤 11시쯤"
          },
          {
            "name": "진정서_2023.jpg",
            "doc_id": "petition_2023",
            "line": 5,
            "quote": "아들은 10월 10일 밤 11시경 ○○역 부근에서 마지막으로 목격되었습니다."
          },
          {
            "name": "진정서_2023.jpg",
            "doc_id": "petition_2023",
            "line": 5,
            "quote": "10월 10일 밤 11시경"
          }
        ]
      },
      {
        "type": "event",
        "time": "2015.10.12",
        "title": "실종신고",
        "full": "10월 12일 경찰서 실종신고",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑥  엄마_메모.jpg · 3줄",
        "sources": [
          {
            "name": "엄마_메모.jpg",
            "doc_id": "mother_memo",
            "line": 3,
            "quote": "10월 12일 경찰서 실종신고"
          }
        ]
      },
      {
        "type": "event",
        "time": "2015.10.12\n21:30",
        "title": "실종신고 접수",
        "full": "실종신고 접수증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  실종신고_접수증_2015.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "실종신고_접수증_2015.jpg",
            "doc_id": "missing_report_2015",
            "line": 1,
            "quote": "실종신고 접수증"
          },
          {
            "name": "실종신고_접수증_2015.jpg",
            "doc_id": "missing_report_2015",
            "line": 3,
            "quote": "2015. 10. 12. 21:30"
          }
        ]
      },
      {
        "type": "gap",
        "range": "2016.02.03 – 2019.02.14",
        "text": "이 기간의 기록이 없어요 (약 3.0년)"
      },
      {
        "type": "event",
        "time": "2019.03",
        "title": "목격 · ○○시장 입구",
        "full": "본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남성을 목격하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  최영호_진술서.jpg · 3줄 외 2곳",
        "sources": [
          {
            "name": "최영호_진술서.jpg",
            "doc_id": "witness_statement_2019",
            "line": 3,
            "quote": "본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남성을 목격하였습니다."
          },
          {
            "name": "최영호_진술서.jpg",
            "doc_id": "witness_statement_2019",
            "line": 3,
            "quote": "2019년 3월 초순"
          },
          {
            "name": "진정서_2023.jpg",
            "doc_id": "petition_2023",
            "line": 6,
            "quote": "2019년 3월경 이웃 주민 최영호가 아들을 ○○시장 근처에서 보았다고 말했습니다."
          }
        ]
      },
      {
        "type": "gap",
        "range": "2019.04.16 – 2022.03.15",
        "text": "이 기간의 기록이 없어요 (약 2.9년)"
      },
      {
        "type": "event",
        "time": "2022.03.15",
        "title": "수사결과 통지 — 수사중지(피의자중지)",
        "full": "수사결과 통지서",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ④  수사중지_결정통지서.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "수사중지_결정통지서.jpg",
            "doc_id": "suspension_notice_2022",
            "line": 1,
            "quote": "수사결과 통지서"
          },
          {
            "name": "수사중지_결정통지서.jpg",
            "doc_id": "suspension_notice_2022",
            "line": 5,
            "quote": "2022. 3. 15."
          }
        ]
      },
      {
        "type": "gap",
        "range": "2022.03.16 – 2023.04.02",
        "text": "이 기간의 기록이 없어요 (약 1.0년)"
      },
      {
        "type": "event",
        "time": "2023.04.02",
        "title": "재수사 요청",
        "full": "2015. 10. 10. 실종된 아들 김민수 사건(2016형제12345)의 재수사를 요청합니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑤  진정서_2023.jpg · 4줄 외 1곳",
        "sources": [
          {
            "name": "진정서_2023.jpg",
            "doc_id": "petition_2023",
            "line": 4,
            "quote": "2015. 10. 10. 실종된 아들 김민수 사건(2016형제12345)의 재수사를 요청합니다."
          },
          {
            "name": "진정서_2023.jpg",
            "doc_id": "petition_2023",
            "line": 8,
            "quote": "2023. 4. 2."
          }
        ]
      },
      {
        "type": "event",
        "time": "시각 미상",
        "title": "실종",
        "full": "○○시 20대 남성 실종 넉 달째 행방 묘연",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  기사캡처_2016.png · 1줄",
        "sources": [
          {
            "name": "기사캡처_2016.png",
            "doc_id": "news_2016",
            "line": 1,
            "quote": "○○시 20대 남성 실종 넉 달째 행방 묘연"
          }
        ]
      },
      {
        "type": "event",
        "time": "시각 미상",
        "title": "결정 통지서를 받은 뒤로 경찰에서 따로 연락 온 적이 없습니다",
        "full": "결정 통지서를 받은 뒤로 경찰에서 따로 연락 온 적이 없습니다.",
        "kind": "mine",
        "badge": "내가 입력",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  직접 입력 · 1줄",
        "sources": [
          {
            "name": "직접 입력",
            "doc_id": "note_family",
            "line": 1,
            "quote": "결정 통지서를 받은 뒤로 경찰에서 따로 연락 온 적이 없습니다."
          }
        ]
      }
    ],
    "people": [
      {
        "label": "사람",
        "items": [
          {
            "name": "김민수",
            "roles": [
              "실종자",
              "아들"
            ],
            "docs": [
              "실종신고_접수증_2015.jpg",
              "진정서_2023.jpg"
            ],
            "same_as": []
          },
          {
            "name": "이순자",
            "roles": [
              "신고인",
              "진정인"
            ],
            "docs": [
              "실종신고_접수증_2015.jpg"
            ],
            "same_as": []
          },
          {
            "name": "최영호",
            "roles": [
              "진술인"
            ],
            "docs": [],
            "same_as": []
          },
          {
            "name": "박정호",
            "roles": [
              "담당수사관"
            ],
            "docs": [
              "수사중지_결정통지서.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "기관",
        "items": [
          {
            "name": "**경찰서",
            "roles": [],
            "docs": [
              "수사중지_결정통지서.jpg",
              "실종신고_접수증_2015.jpg"
            ],
            "same_as": [
              {
                "name": "경찰서",
                "reason": "일반 명칭이라 같은 기관인지 확인되지 않음"
              }
            ]
          },
          {
            "name": "경찰서",
            "roles": [],
            "docs": [
              "엄마_메모.jpg"
            ],
            "same_as": [
              {
                "name": "**경찰서",
                "reason": "일반 명칭이라 같은 기관인지 확인되지 않음"
              }
            ]
          }
        ]
      },
      {
        "label": "사건번호",
        "items": [
          {
            "name": "2016형제12345",
            "roles": [],
            "docs": [
              "수사중지_결정통지서.jpg",
              "진정서_2023.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "접수번호",
        "items": [
          {
            "name": "2015-00123",
            "roles": [],
            "docs": [
              "실종신고_접수증_2015.jpg"
            ],
            "same_as": []
          }
        ]
      }
    ],
    "slots": [
      {
        "slot": "마지막 목격 시점",
        "value": "2015-10-10 22시~01시",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2015-10-10 22시~01시",
            "doc": "실종신고_접수증_2015.jpg",
            "speaker": "**경찰서",
            "record": true
          },
          {
            "value": "2015-10-10 22시~01시",
            "doc": "기사캡처_2016.png",
            "speaker": "경찰",
            "record": false
          },
          {
            "value": "2015-10-10 22시~01시",
            "doc": "진정서_2023.jpg",
            "speaker": "이순자",
            "record": false
          }
        ]
      },
      {
        "slot": "마지막 연락 시점",
        "value": null,
        "state": "판독 신뢰도 낮음",
        "severity": "unverified",
        "said": [
          {
            "value": "2015-10-11 00~06시",
            "doc": "기사캡처_2016.png",
            "speaker": "가족",
            "record": false
          },
          {
            "value": "2015-10-10 20~24시",
            "doc": "엄마_메모.jpg",
            "speaker": "나",
            "record": false
          }
        ]
      },
      {
        "slot": "접수번호",
        "value": "2015-00123",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2015-00123",
            "doc": "실종신고_접수증_2015.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "접수일시",
        "value": "2015-10-12 21:30",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2015-10-12 21:30",
            "doc": "실종신고_접수증_2015.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "offence",
        "value": "약취유인",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "약취유인",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "사건번호",
        "value": "2016형제12345",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2016형제12345",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          },
          {
            "value": "2016형제12345",
            "doc": "진정서_2023.jpg",
            "speaker": "이순자",
            "record": false
          }
        ]
      },
      {
        "slot": "담당 수사관",
        "value": "박정호",
        "state": "낡았을 수 있음",
        "severity": "unverified",
        "said": [
          {
            "value": "박정호",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "결정 내용",
        "value": "수사중지(피의자중지)",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "수사중지(피의자중지)",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "결정일",
        "value": "2022-03-15",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2022-03-15",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
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
      "rule_no": 6,
      "action": "ACT-신규정보제출",
      "label": "새로 확인된 정보를 수사기관에 제출",
      "why": "최영호_진술서.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
      "rule_why": "새 정보는 중지·종결된 절차를 되살릴 수 있다",
      "due": null,
      "state": "filled",
      "rows": [
        {
          "k": "무엇을",
          "v": "자료·의견 제출서"
        },
        {
          "k": "어디에",
          "v": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다"
        },
        {
          "k": "근거",
          "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조"
        }
      ],
      "prepare": {
        "done": 2,
        "total": 3,
        "items": [
          {
            "label": "자료·의견 제출서",
            "state": "생성가능",
            "required": true
          },
          {
            "label": "새로 확인한 자료 (원본 또는 사본)",
            "state": "보유",
            "required": true
          },
          {
            "label": "수사결과 통지서 또는 접수증 (사건번호 확인용)",
            "state": "보유",
            "required": false
          }
        ]
      },
      "note": "사건관계인이 사실관계 확인을 위해 낸 자료는 수사기록에 편철된다(수사준칙 제25조). 수사중지 사건은 피의자·참고인의 소재 등 중지 사유가 풀리면 사법경찰관이 즉시 수사를 재개해야 한다(경찰수사규칙 제102조) — 새 자료가 중지 사유를 푸는 내용인지 적어 낸다. 검찰 불기소 사건은 항고 기간이 지났어도 중요한 증거가 새로 발견되면 항고할 수 있다(검찰청법 제10조 제7항).",
      "unverified": true,
      "also": [
        {
          "rule_no": 8,
          "action": "ACT-기록열람",
          "label": "수사 기록 열람 신청",
          "why": "수사 기록 없이는 다른 판단이 불가능하다"
        },
        {
          "rule_no": 9,
          "action": "ACT-근거보완",
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        },
        {
          "rule_no": 10,
          "action": "ACT-공백보완",
          "label": "기록이 빈 기간의 자료 확보",
          "why": "기록 공백은 반박 여지를 남긴다"
        }
      ],
      "submit_to": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
      "form_name": "자료·의견 제출서",
      "draft": {
        "is_draft": true,
        "prose": null,
        "form_name": "자료·의견 제출서",
        "form_source": "법정 서식 없음 — 수사준칙 제25조(자료·의견의 제출기회 보장)에 따라 서면으로 낸다",
        "form_url": null,
        "fields": [
          {
            "label": "사건번호",
            "value": "2016형제12345",
            "from": "case_record"
          },
          {
            "label": "접수번호",
            "value": "2015-00123",
            "from": "case_record"
          },
          {
            "label": "결정 내용",
            "value": "수사중지(피의자중지)",
            "from": "case_record"
          },
          {
            "label": "결정일",
            "value": "2022-03-15",
            "from": "case_record"
          },
          {
            "label": "서식",
            "value": "자료·의견 제출서",
            "from": "knowledge_base"
          },
          {
            "label": "제출처",
            "value": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
            "from": "knowledge_base"
          },
          {
            "label": "근거 법령",
            "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조",
            "from": "knowledge_base"
          }
        ],
        "unfilled": [
          {
            "label": "담당 수사관",
            "reason": "자료에 '박정호' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
          },
          {
            "label": "신청인 성명",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 연락처",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 주소",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          }
        ],
        "sections": [
          {
            "heading": "사건 경위",
            "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
            "lines": [
              {
                "date": "2015. 10. 10.",
                "text": "15년 10월 10일 밤 연락 끊김",
                "level": "statement",
                "source": "엄마_메모.jpg 2줄"
              },
              {
                "date": "2015. 10. 10.",
                "text": "경찰은 김씨가 지난해 10월 10일 밤 11시쯤 ○○역 인근 CCTV에…",
                "level": "statement",
                "source": "기사캡처_2016.png 3줄"
              },
              {
                "date": "2015. 10. 12.",
                "text": "10월 12일 경찰서 실종신고",
                "level": "statement",
                "source": "엄마_메모.jpg 3줄"
              },
              {
                "date": "2015. 10. 12.",
                "text": "실종신고 접수증",
                "level": "record",
                "source": "실종신고_접수증_2015.jpg 1줄"
              },
              {
                "date": "2019. 3.",
                "text": "본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남…",
                "level": "statement",
                "source": "최영호_진술서.jpg 3줄"
              },
              {
                "date": "2022. 3. 15.",
                "text": "수사결과 통지서",
                "level": "record",
                "source": "수사중지_결정통지서.jpg 1줄"
              },
              {
                "date": "2023. 4. 2.",
                "text": "2015. 10. 10. 실종된 아들 김민수 사건(2016형제12345…",
                "level": "statement",
                "source": "진정서_2023.jpg 4줄"
              },
              {
                "date": null,
                "text": "○○시 20대 남성 실종 넉 달째 행방 묘연",
                "level": "statement",
                "source": "기사캡처_2016.png 1줄"
              }
            ]
          },
          {
            "heading": "요청 사항",
            "note": "무엇을 확인해 달라는지 직접 적어 주세요 — 예: 새 자료의 사실관계 확인, 수사 재개 검토. 타래는 이 칸을 대신 쓰지 않습니다.",
            "lines": []
          }
        ],
        "dropped": 0
      }
    },
    "actions": [
      {
        "rule_no": 6,
        "action": "ACT-신규정보제출",
        "label": "새로 확인된 정보를 수사기관에 제출",
        "why": "최영호_진술서.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
        "rule_why": "새 정보는 중지·종결된 절차를 되살릴 수 있다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "자료·의견 제출서"
          },
          {
            "k": "어디에",
            "v": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다"
          },
          {
            "k": "근거",
            "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조"
          }
        ],
        "prepare": {
          "done": 2,
          "total": 3,
          "items": [
            {
              "label": "자료·의견 제출서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "새로 확인한 자료 (원본 또는 사본)",
              "state": "보유",
              "required": true
            },
            {
              "label": "수사결과 통지서 또는 접수증 (사건번호 확인용)",
              "state": "보유",
              "required": false
            }
          ]
        },
        "note": "사건관계인이 사실관계 확인을 위해 낸 자료는 수사기록에 편철된다(수사준칙 제25조). 수사중지 사건은 피의자·참고인의 소재 등 중지 사유가 풀리면 사법경찰관이 즉시 수사를 재개해야 한다(경찰수사규칙 제102조) — 새 자료가 중지 사유를 푸는 내용인지 적어 낸다. 검찰 불기소 사건은 항고 기간이 지났어도 중요한 증거가 새로 발견되면 항고할 수 있다(검찰청법 제10조 제7항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
        "form_name": "자료·의견 제출서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "자료·의견 제출서",
          "form_source": "법정 서식 없음 — 수사준칙 제25조(자료·의견의 제출기회 보장)에 따라 서면으로 낸다",
          "form_url": null,
          "fields": [
            {
              "label": "사건번호",
              "value": "2016형제12345",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2015-00123",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2022-03-15",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "자료·의견 제출서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "담당 수사관",
              "reason": "자료에 '박정호' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
            },
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2015. 10. 10.",
                  "text": "15년 10월 10일 밤 연락 끊김",
                  "level": "statement",
                  "source": "엄마_메모.jpg 2줄"
                },
                {
                  "date": "2015. 10. 10.",
                  "text": "경찰은 김씨가 지난해 10월 10일 밤 11시쯤 ○○역 인근 CCTV에…",
                  "level": "statement",
                  "source": "기사캡처_2016.png 3줄"
                },
                {
                  "date": "2015. 10. 12.",
                  "text": "10월 12일 경찰서 실종신고",
                  "level": "statement",
                  "source": "엄마_메모.jpg 3줄"
                },
                {
                  "date": "2015. 10. 12.",
                  "text": "실종신고 접수증",
                  "level": "record",
                  "source": "실종신고_접수증_2015.jpg 1줄"
                },
                {
                  "date": "2019. 3.",
                  "text": "본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남…",
                  "level": "statement",
                  "source": "최영호_진술서.jpg 3줄"
                },
                {
                  "date": "2022. 3. 15.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_결정통지서.jpg 1줄"
                },
                {
                  "date": "2023. 4. 2.",
                  "text": "2015. 10. 10. 실종된 아들 김민수 사건(2016형제12345…",
                  "level": "statement",
                  "source": "진정서_2023.jpg 4줄"
                },
                {
                  "date": null,
                  "text": "○○시 20대 남성 실종 넉 달째 행방 묘연",
                  "level": "statement",
                  "source": "기사캡처_2016.png 1줄"
                }
              ]
            },
            {
              "heading": "요청 사항",
              "note": "무엇을 확인해 달라는지 직접 적어 주세요 — 예: 새 자료의 사실관계 확인, 수사 재개 검토. 타래는 이 칸을 대신 쓰지 않습니다.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 8,
        "action": "ACT-기록열람",
        "label": "수사 기록 열람 신청",
        "why": "‘본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남…’(2019-03-01~03-10, witness_statement_2019 · 3줄, petition_2023 · 6줄) — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2022-03-15)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
        "rule_why": "수사 기록 없이는 다른 판단이 불가능하다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "수사기록 열람·등사 신청서"
          },
          {
            "k": "어디에",
            "v": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청"
          },
          {
            "k": "근거",
            "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침"
          }
        ],
        "prepare": {
          "done": 0,
          "total": 2,
          "items": [
            {
              "label": "수사기록 열람·등사 신청서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "신청인 신분 확인 서류",
              "state": "미보유",
              "required": true
            }
          ]
        },
        "note": "불송치·불기소로 끝난 사건은 정보공개청구가 거부되는 일이 잦다. 거부를 전제로 다음 경로(이의신청·행정소송)까지 함께 안내해야 한다. 수사 중인 사건은 본인 진술과 본인이 낸 서류만(수사준칙 제69조 제1항), 불송치·불기소 사건은 기록의 전부 또는 일부를(제2항) 신청할 수 있다. 가족은 위임장과 신분관계 증명서를 내고 신청할 수 있다(제5항). 경찰관서는 신청을 받은 날부터 10일 이내에 공개 여부를 결정한다(경찰수사규칙 제87조 제2항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
        "form_name": "수사기록 열람·등사 신청서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "수사기록 열람·등사 신청서",
          "form_source": "검찰보존사무규칙 별지 제5호서식 「사건기록 열람·등사 신청서」(제20조의2·제20조의3). 경찰관서 신청 서식은 경찰청장이 따로 정한다(경찰수사규칙 제87조 제6항)",
          "form_url": "https://law.go.kr/flDownload.do?gubun=&flSeq=132313759",
          "fields": [
            {
              "label": "사건번호",
              "value": "2016형제12345",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2015-00123",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2022-03-15",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "수사기록 열람·등사 신청서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "담당 수사관",
              "reason": "자료에 '박정호' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
            },
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2015. 10. 10.",
                  "text": "15년 10월 10일 밤 연락 끊김",
                  "level": "statement",
                  "source": "엄마_메모.jpg 2줄"
                },
                {
                  "date": "2015. 10. 10.",
                  "text": "경찰은 김씨가 지난해 10월 10일 밤 11시쯤 ○○역 인근 CCTV에…",
                  "level": "statement",
                  "source": "기사캡처_2016.png 3줄"
                },
                {
                  "date": "2015. 10. 12.",
                  "text": "10월 12일 경찰서 실종신고",
                  "level": "statement",
                  "source": "엄마_메모.jpg 3줄"
                },
                {
                  "date": "2015. 10. 12.",
                  "text": "실종신고 접수증",
                  "level": "record",
                  "source": "실종신고_접수증_2015.jpg 1줄"
                },
                {
                  "date": "2019. 3.",
                  "text": "본인은 2019년 3월 초순 오후 ○○시장 입구에서 김민수로 보이는 남…",
                  "level": "statement",
                  "source": "최영호_진술서.jpg 3줄"
                },
                {
                  "date": "2022. 3. 15.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_결정통지서.jpg 1줄"
                },
                {
                  "date": "2023. 4. 2.",
                  "text": "2015. 10. 10. 실종된 아들 김민수 사건(2016형제12345…",
                  "level": "statement",
                  "source": "진정서_2023.jpg 4줄"
                },
                {
                  "date": null,
                  "text": "○○시 20대 남성 실종 넉 달째 행방 묘연",
                  "level": "statement",
                  "source": "기사캡처_2016.png 1줄"
                }
              ]
            },
            {
              "heading": "이의 사유",
              "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 9,
        "action": "ACT-근거보완",
        "label": "주장을 뒷받침할 근거 자료 보완",
        "why": "실종신고_접수증_2015.jpg에서 읽히지 않은 부분이 1곳 있습니다 (8줄). 사진을 보고 알려주세요",
        "rule_why": "근거 없는 주장은 판단 대상이 되지 않는다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "원본 출처나 감정 결과를 확보하는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      },
      {
        "rule_no": 10,
        "action": "ACT-공백보완",
        "label": "기록이 빈 기간의 자료 확보",
        "why": "‘수사’ 단계에 해당하는 자료가 없습니다",
        "rule_why": "기록 공백은 반박 여지를 남긴다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "기록이 비어 있는 기간의 자료를 모으는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      }
    ],
    "response_choices": [
      "불송치",
      "불기소",
      "항고 기각",
      "피의자중지",
      "참고인중지",
      "기소"
    ],
    "outcomes": {
      "불송치": {
        "st": "경찰 불송치",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "불기소": {
        "st": "검찰 불기소",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "검찰 항고 기한",
            "period_days": 30,
            "statute": "검찰청법 제10조",
            "submit_to": "불기소 처분을 한 검사가 속한 지방검찰청 또는 지청을 거쳐 관할 고등검찰청 검사장"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "항고 기각": {
        "st": "이의신청/항고 중",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "법원 재정신청 기한",
            "period_days": 10,
            "statute": "형사소송법 제260조 제3항",
            "submit_to": "지방검찰청 검사장 또는 지청장"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "피의자중지": {
        "st": "피의자 중지",
        "next": "새로 확인된 정보를 수사기관에 제출",
        "next_key": "ACT-신규정보제출",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "참고인중지": {
        "st": "참고인 중지",
        "next": "새로 확인된 정보를 수사기관에 제출",
        "next_key": "ACT-신규정보제출",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      },
      "기소": {
        "st": "재판 진행 중",
        "next": "새로 확인된 정보를 수사기관에 제출",
        "next_key": "ACT-신규정보제출",
        "deadlines": [
          {
            "label": "디지털 데이터 보존 기한",
            "period_days": 90,
            "statute": "통신비밀보호법 시행령 제41조",
            "submit_to": null
          }
        ]
      }
    }
  },
  {
    "id": "suspension_recent",
    "title": "고소 사건 (수사중지)",
    "type": "investigation_suspended",
    "type_label": "수사중지 사건",
    "as_of": "2026.09.12",
    "period": "2021.05 – 2026.08",
    "doc_count": 4,
    "need_count": 5,
    "stages": [
      {
        "label": "고소",
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
        "label": "중지",
        "state": "current"
      },
      {
        "label": "재개",
        "state": "todo"
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "고소장_2021.jpg",
        "doc_id": "complaint_2021"
      },
      {
        "kind": "IMG",
        "name": "접수증_2021.jpg",
        "doc_id": "receipt_2021"
      },
      {
        "kind": "IMG",
        "name": "수사중지_결정통지서.jpg",
        "doc_id": "suspension_notice_2026"
      },
      {
        "kind": "IMG",
        "name": "조미래_진술서.jpg",
        "doc_id": "witness_statement_2025"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "2021.05.18",
        "title": "18,000,000원 사기 피해",
        "full": "18,000,000원 발생",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2021.jpg · 5줄 외 1곳",
        "sources": [
          {
            "name": "고소장_2021.jpg",
            "doc_id": "complaint_2021",
            "line": 5,
            "quote": "2021. 5. 18. 인테리어 공사대금 명목으로 1,800만원을 편취당하는 사기 피해를 입었습니다."
          },
          {
            "name": "고소장_2021.jpg",
            "doc_id": "complaint_2021",
            "line": 5,
            "quote": "1,800만원"
          }
        ]
      },
      {
        "type": "event",
        "time": "2021.05.25",
        "title": "○○경찰서 고소",
        "full": "2021. 5. 25. ○○경찰서에 고소하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2021.jpg · 7줄",
        "sources": [
          {
            "name": "고소장_2021.jpg",
            "doc_id": "complaint_2021",
            "line": 7,
            "quote": "2021. 5. 25. ○○경찰서에 고소하였습니다."
          }
        ]
      },
      {
        "type": "event",
        "time": "2021.05.25\n14:20",
        "title": "사건 접수",
        "full": "접 수 증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  접수증_2021.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "접수증_2021.jpg",
            "doc_id": "receipt_2021",
            "line": 1,
            "quote": "접 수 증"
          },
          {
            "name": "접수증_2021.jpg",
            "doc_id": "receipt_2021",
            "line": 3,
            "quote": "2021. 5. 25. 14:20"
          }
        ]
      },
      {
        "type": "gap",
        "range": "2021.05.26 – 2025.06.03",
        "text": "이 기간의 기록이 없어요 (약 4.0년)"
      },
      {
        "type": "event",
        "time": "2025.06.03",
        "title": "목격 · ○○시 중앙시장 앞",
        "full": "2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ④  조미래_진술서.jpg · 3줄",
        "sources": [
          {
            "name": "조미래_진술서.jpg",
            "doc_id": "witness_statement_2025",
            "line": 3,
            "quote": "2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다."
          }
        ]
      },
      {
        "type": "gap",
        "range": "2025.06.11 – 2026.08.18",
        "text": "이 기간의 기록이 없어요 (약 1.2년)"
      },
      {
        "type": "event",
        "time": "2026.08.18",
        "title": "수사결과 통지 — 수사중지(피의자중지)",
        "full": "수사결과 통지서",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  수사중지_결정통지서.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "수사중지_결정통지서.jpg",
            "doc_id": "suspension_notice_2026",
            "line": 1,
            "quote": "수사결과 통지서"
          },
          {
            "name": "수사중지_결정통지서.jpg",
            "doc_id": "suspension_notice_2026",
            "line": 6,
            "quote": "2026. 8. 18."
          }
        ]
      },
      {
        "type": "event",
        "time": "시각 미상",
        "title": "결정 통지서를 받은 뒤로 경찰에서 따로 연락이 온 적이 없습니다",
        "full": "결정 통지서를 받은 뒤로 경찰에서 따로 연락이 온 적이 없습니다.",
        "kind": "mine",
        "badge": "내가 입력",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  직접 입력 · 1줄",
        "sources": [
          {
            "name": "직접 입력",
            "doc_id": "note_victim",
            "line": 1,
            "quote": "결정 통지서를 받은 뒤로 경찰에서 따로 연락이 온 적이 없습니다."
          }
        ]
      }
    ],
    "people": [
      {
        "label": "사람",
        "items": [
          {
            "name": "정하늘",
            "roles": [
              "고소인",
              "신고인"
            ],
            "docs": [
              "수사중지_결정통지서.jpg",
              "접수증_2021.jpg"
            ],
            "same_as": []
          },
          {
            "name": "한지훈",
            "roles": [
              "담당수사관"
            ],
            "docs": [
              "수사중지_결정통지서.jpg"
            ],
            "same_as": []
          },
          {
            "name": "조미래",
            "roles": [
              "진술인"
            ],
            "docs": [],
            "same_as": []
          }
        ]
      },
      {
        "label": "기관",
        "items": [
          {
            "name": "**경찰서",
            "roles": [],
            "docs": [
              "고소장_2021.jpg",
              "수사중지_결정통지서.jpg",
              "접수증_2021.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "사건번호",
        "items": [
          {
            "name": "2021형제45678",
            "roles": [],
            "docs": [
              "수사중지_결정통지서.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "접수번호",
        "items": [
          {
            "name": "2021-005821",
            "roles": [],
            "docs": [
              "접수증_2021.jpg"
            ],
            "same_as": []
          }
        ]
      }
    ],
    "slots": [
      {
        "slot": "사건 발생 시점",
        "value": null,
        "state": "말만 있고 기록 없음",
        "severity": "unverified",
        "said": [
          {
            "value": "2021-05-18",
            "doc": "고소장_2021.jpg",
            "speaker": "정하늘",
            "record": false
          },
          {
            "value": "2025-06-03",
            "doc": "조미래_진술서.jpg",
            "speaker": "조미래",
            "record": false
          }
        ]
      },
      {
        "slot": "접수번호",
        "value": "2021-005821",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2021-005821",
            "doc": "접수증_2021.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "offence",
        "value": "사기",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "사기",
            "doc": "접수증_2021.jpg",
            "speaker": "**경찰서",
            "record": true
          },
          {
            "value": "사기",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "사건번호",
        "value": "2021형제45678",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2021형제45678",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "담당 수사관",
        "value": "한지훈",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "한지훈",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "결정 내용",
        "value": "수사중지(피의자중지)",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "수사중지(피의자중지)",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "결정일",
        "value": "2026-08-18",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2026-08-18",
            "doc": "수사중지_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
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
      "note": "이의제기(30일) 말고 두 번째 경로가 있다. 수사준칙 제54조 제3항 — 수사중지 결정이 법령위반·인권침해·현저한 수사권 남용으로 의심되면 검사에게 신고할 수 있고, 여기에는 기한 제한이 없다. 경찰수사규칙 제97조 제8항이 이 사실을 통지서에 적도록 하고 있어서, 사용자가 받은 통지서에 이미 안내가 들어 있다 이의제기를 받은 상급경찰관서장은 30일 이내에 결정하고, 결정한 날부터 7일 이내에 결과를 통지한다(경찰수사규칙 제101조 제3항·제5항).",
      "unverified": true,
      "also": [
        {
          "rule_no": 6,
          "action": "ACT-신규정보제출",
          "label": "새로 확인된 정보를 수사기관에 제출",
          "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
        },
        {
          "rule_no": 8,
          "action": "ACT-기록열람",
          "label": "수사 기록 열람 신청",
          "why": "수사 기록 없이는 다른 판단이 불가능하다"
        },
        {
          "rule_no": 9,
          "action": "ACT-근거보완",
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        },
        {
          "rule_no": 10,
          "action": "ACT-공백보완",
          "label": "기록이 빈 기간의 자료 확보",
          "why": "기록 공백은 반박 여지를 남긴다"
        }
      ],
      "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 송부된다)",
      "form_name": "수사중지 결정 이의제기서",
      "draft": {
        "is_draft": true,
        "prose": null,
        "form_name": "수사중지 결정 이의제기서",
        "form_source": "경찰수사규칙 별지 제110호서식",
        "form_url": "https://law.go.kr/flDownload.do?gubun=&flSeq=111544061&bylClsCd=110202",
        "fields": [
          {
            "label": "사건번호",
            "value": "2021형제45678",
            "from": "case_record"
          },
          {
            "label": "접수번호",
            "value": "2021-005821",
            "from": "case_record"
          },
          {
            "label": "담당 수사관",
            "value": "한지훈",
            "from": "case_record"
          },
          {
            "label": "결정 내용",
            "value": "수사중지(피의자중지)",
            "from": "case_record"
          },
          {
            "label": "결정일",
            "value": "2026-08-18",
            "from": "case_record"
          },
          {
            "label": "서식",
            "value": "수사중지 결정 이의제기서",
            "from": "knowledge_base"
          },
          {
            "label": "제출처",
            "value": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 송부된다)",
            "from": "knowledge_base"
          },
          {
            "label": "근거 법령",
            "value": "경찰수사규칙 제101조",
            "from": "knowledge_base"
          }
        ],
        "unfilled": [
          {
            "label": "신청인 성명",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 연락처",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 주소",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          }
        ],
        "sections": [
          {
            "heading": "사건 경위",
            "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
            "lines": [
              {
                "date": "2021. 5. 18.",
                "text": "18,000,000원 발생",
                "level": "statement",
                "source": "고소장_2021.jpg 5줄"
              },
              {
                "date": "2021. 5. 25.",
                "text": "2021. 5. 25. ○○경찰서에 고소하였습니다.",
                "level": "statement",
                "source": "고소장_2021.jpg 7줄"
              },
              {
                "date": "2021. 5. 25.",
                "text": "접 수 증",
                "level": "record",
                "source": "접수증_2021.jpg 1줄"
              },
              {
                "date": "2025. 6. 3.",
                "text": "2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.",
                "level": "statement",
                "source": "조미래_진술서.jpg 3줄"
              },
              {
                "date": "2026. 8. 18.",
                "text": "수사결과 통지서",
                "level": "record",
                "source": "수사중지_결정통지서.jpg 1줄"
              }
            ]
          },
          {
            "heading": "이의 사유",
            "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
            "lines": []
          }
        ],
        "dropped": 0
      }
    },
    "actions": [
      {
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
        "note": "이의제기(30일) 말고 두 번째 경로가 있다. 수사준칙 제54조 제3항 — 수사중지 결정이 법령위반·인권침해·현저한 수사권 남용으로 의심되면 검사에게 신고할 수 있고, 여기에는 기한 제한이 없다. 경찰수사규칙 제97조 제8항이 이 사실을 통지서에 적도록 하고 있어서, 사용자가 받은 통지서에 이미 안내가 들어 있다 이의제기를 받은 상급경찰관서장은 30일 이내에 결정하고, 결정한 날부터 7일 이내에 결과를 통지한다(경찰수사규칙 제101조 제3항·제5항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 송부된다)",
        "form_name": "수사중지 결정 이의제기서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "수사중지 결정 이의제기서",
          "form_source": "경찰수사규칙 별지 제110호서식",
          "form_url": "https://law.go.kr/flDownload.do?gubun=&flSeq=111544061&bylClsCd=110202",
          "fields": [
            {
              "label": "사건번호",
              "value": "2021형제45678",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2021-005821",
              "from": "case_record"
            },
            {
              "label": "담당 수사관",
              "value": "한지훈",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2026-08-18",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "수사중지 결정 이의제기서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 송부된다)",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "경찰수사규칙 제101조",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2021. 5. 18.",
                  "text": "18,000,000원 발생",
                  "level": "statement",
                  "source": "고소장_2021.jpg 5줄"
                },
                {
                  "date": "2021. 5. 25.",
                  "text": "2021. 5. 25. ○○경찰서에 고소하였습니다.",
                  "level": "statement",
                  "source": "고소장_2021.jpg 7줄"
                },
                {
                  "date": "2021. 5. 25.",
                  "text": "접 수 증",
                  "level": "record",
                  "source": "접수증_2021.jpg 1줄"
                },
                {
                  "date": "2025. 6. 3.",
                  "text": "2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.",
                  "level": "statement",
                  "source": "조미래_진술서.jpg 3줄"
                },
                {
                  "date": "2026. 8. 18.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_결정통지서.jpg 1줄"
                }
              ]
            },
            {
              "heading": "이의 사유",
              "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 6,
        "action": "ACT-신규정보제출",
        "label": "새로 확인된 정보를 수사기관에 제출",
        "why": "조미래_진술서.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
        "rule_why": "새 정보는 중지·종결된 절차를 되살릴 수 있다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "자료·의견 제출서"
          },
          {
            "k": "어디에",
            "v": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다"
          },
          {
            "k": "근거",
            "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조"
          }
        ],
        "prepare": {
          "done": 2,
          "total": 3,
          "items": [
            {
              "label": "자료·의견 제출서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "새로 확인한 자료 (원본 또는 사본)",
              "state": "보유",
              "required": true
            },
            {
              "label": "수사결과 통지서 또는 접수증 (사건번호 확인용)",
              "state": "보유",
              "required": false
            }
          ]
        },
        "note": "사건관계인이 사실관계 확인을 위해 낸 자료는 수사기록에 편철된다(수사준칙 제25조). 수사중지 사건은 피의자·참고인의 소재 등 중지 사유가 풀리면 사법경찰관이 즉시 수사를 재개해야 한다(경찰수사규칙 제102조) — 새 자료가 중지 사유를 푸는 내용인지 적어 낸다. 검찰 불기소 사건은 항고 기간이 지났어도 중요한 증거가 새로 발견되면 항고할 수 있다(검찰청법 제10조 제7항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
        "form_name": "자료·의견 제출서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "자료·의견 제출서",
          "form_source": "법정 서식 없음 — 수사준칙 제25조(자료·의견의 제출기회 보장)에 따라 서면으로 낸다",
          "form_url": null,
          "fields": [
            {
              "label": "사건번호",
              "value": "2021형제45678",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2021-005821",
              "from": "case_record"
            },
            {
              "label": "담당 수사관",
              "value": "한지훈",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2026-08-18",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "자료·의견 제출서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "사건을 담당하는 사법경찰관 또는 검사 — 수사중지·불송치 사건은 그 결정을 한 경찰관서, 검찰로 넘어간 사건은 그 검찰청. 사건번호를 적어 낸다",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제25조",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2021. 5. 18.",
                  "text": "18,000,000원 발생",
                  "level": "statement",
                  "source": "고소장_2021.jpg 5줄"
                },
                {
                  "date": "2021. 5. 25.",
                  "text": "2021. 5. 25. ○○경찰서에 고소하였습니다.",
                  "level": "statement",
                  "source": "고소장_2021.jpg 7줄"
                },
                {
                  "date": "2021. 5. 25.",
                  "text": "접 수 증",
                  "level": "record",
                  "source": "접수증_2021.jpg 1줄"
                },
                {
                  "date": "2025. 6. 3.",
                  "text": "2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.",
                  "level": "statement",
                  "source": "조미래_진술서.jpg 3줄"
                },
                {
                  "date": "2026. 8. 18.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_결정통지서.jpg 1줄"
                }
              ]
            },
            {
              "heading": "요청 사항",
              "note": "무엇을 확인해 달라는지 직접 적어 주세요 — 예: 새 자료의 사실관계 확인, 수사 재개 검토. 타래는 이 칸을 대신 쓰지 않습니다.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 8,
        "action": "ACT-기록열람",
        "label": "수사 기록 열람 신청",
        "why": "‘2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.’(2025-06-03, witness_statement_2025 · 3줄) — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2026-08-18)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
        "rule_why": "수사 기록 없이는 다른 판단이 불가능하다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "수사기록 열람·등사 신청서"
          },
          {
            "k": "어디에",
            "v": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청"
          },
          {
            "k": "근거",
            "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침"
          }
        ],
        "prepare": {
          "done": 0,
          "total": 2,
          "items": [
            {
              "label": "수사기록 열람·등사 신청서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "신청인 신분 확인 서류",
              "state": "미보유",
              "required": true
            }
          ]
        },
        "note": "불송치·불기소로 끝난 사건은 정보공개청구가 거부되는 일이 잦다. 거부를 전제로 다음 경로(이의신청·행정소송)까지 함께 안내해야 한다. 수사 중인 사건은 본인 진술과 본인이 낸 서류만(수사준칙 제69조 제1항), 불송치·불기소 사건은 기록의 전부 또는 일부를(제2항) 신청할 수 있다. 가족은 위임장과 신분관계 증명서를 내고 신청할 수 있다(제5항). 경찰관서는 신청을 받은 날부터 10일 이내에 공개 여부를 결정한다(경찰수사규칙 제87조 제2항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
        "form_name": "수사기록 열람·등사 신청서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "수사기록 열람·등사 신청서",
          "form_source": "검찰보존사무규칙 별지 제5호서식 「사건기록 열람·등사 신청서」(제20조의2·제20조의3). 경찰관서 신청 서식은 경찰청장이 따로 정한다(경찰수사규칙 제87조 제6항)",
          "form_url": "https://law.go.kr/flDownload.do?gubun=&flSeq=132313759",
          "fields": [
            {
              "label": "사건번호",
              "value": "2021형제45678",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2021-005821",
              "from": "case_record"
            },
            {
              "label": "담당 수사관",
              "value": "한지훈",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2026-08-18",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "수사기록 열람·등사 신청서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2021. 5. 18.",
                  "text": "18,000,000원 발생",
                  "level": "statement",
                  "source": "고소장_2021.jpg 5줄"
                },
                {
                  "date": "2021. 5. 25.",
                  "text": "2021. 5. 25. ○○경찰서에 고소하였습니다.",
                  "level": "statement",
                  "source": "고소장_2021.jpg 7줄"
                },
                {
                  "date": "2021. 5. 25.",
                  "text": "접 수 증",
                  "level": "record",
                  "source": "접수증_2021.jpg 1줄"
                },
                {
                  "date": "2025. 6. 3.",
                  "text": "2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.",
                  "level": "statement",
                  "source": "조미래_진술서.jpg 3줄"
                },
                {
                  "date": "2026. 8. 18.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_결정통지서.jpg 1줄"
                }
              ]
            },
            {
              "heading": "이의 사유",
              "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 9,
        "action": "ACT-근거보완",
        "label": "주장을 뒷받침할 근거 자료 보완",
        "why": "사건 발생 시점: 정하늘, 조미래의 말만 있고 이를 뒷받침하는 기록 자료가 없습니다 — ‘2021. 5. 18. 인테리어 공사대금 명목으로 1,800만원을 편취당하는 사기 피해를 입었습니다.’(complaint_2021 · 5줄) / ‘2025. 6. 3. ○○시 중앙시장 앞에서 박현수를 목격하였습니다.’(witness_statement_2025 · 3줄)",
        "rule_why": "근거 없는 주장은 판단 대상이 되지 않는다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "원본 출처나 감정 결과를 확보하는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      },
      {
        "rule_no": 10,
        "action": "ACT-공백보완",
        "label": "기록이 빈 기간의 자료 확보",
        "why": "‘수사’ 단계에 해당하는 자료가 없습니다",
        "rule_why": "기록 공백은 반박 여지를 남긴다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "기록이 비어 있는 기간의 자료를 모으는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      }
    ],
    "response_choices": [
      "불송치",
      "불기소",
      "항고 기각",
      "피의자중지",
      "참고인중지",
      "기소"
    ],
    "outcomes": {
      "불송치": {
        "st": "경찰 불송치",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "불기소": {
        "st": "검찰 불기소",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "검찰 항고 기한",
            "period_days": 30,
            "statute": "검찰청법 제10조",
            "submit_to": "불기소 처분을 한 검사가 속한 지방검찰청 또는 지청을 거쳐 관할 고등검찰청 검사장"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "항고 기각": {
        "st": "이의신청/항고 중",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "법원 재정신청 기한",
            "period_days": 10,
            "statute": "형사소송법 제260조 제3항",
            "submit_to": "지방검찰청 검사장 또는 지청장"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "피의자중지": {
        "st": "피의자 중지",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "참고인중지": {
        "st": "참고인 중지",
        "next": "새로 확인된 정보를 수사기관에 제출",
        "next_key": "ACT-신규정보제출",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "기소": {
        "st": "재판 진행 중",
        "next": "새로 확인된 정보를 수사기관에 제출",
        "next_key": "ACT-신규정보제출",
        "deadlines": [
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      }
    }
  },
  {
    "id": "no_referral_test",
    "title": "불송치 사건 (시험)",
    "type": "investigation_suspended",
    "type_label": "수사중지 사건",
    "as_of": "2026.09.16",
    "period": "2024.03 – 2026.08",
    "doc_count": 4,
    "need_count": 4,
    "stages": [
      {
        "label": "고소",
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
        "label": "중지",
        "state": "current"
      },
      {
        "label": "재개",
        "state": "todo"
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "고소장_2024.jpg",
        "doc_id": "complaint_2024"
      },
      {
        "kind": "IMG",
        "name": "접수증_2024.jpg",
        "doc_id": "receipt_2024"
      },
      {
        "kind": "IMG",
        "name": "불송치_결정통지서.jpg",
        "doc_id": "no_referral_notice_2026"
      },
      {
        "kind": "IMG",
        "name": "계좌거래내역_2026.png",
        "doc_id": "bank_2026"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "2024.03.12",
        "title": "8,500,000원 송금",
        "full": "8,500,000원 송금",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2024.jpg · 5줄 외 2곳",
        "sources": [
          {
            "name": "고소장_2024.jpg",
            "doc_id": "complaint_2024",
            "line": 5,
            "quote": "2024. 3. 12. 중고 노트북 거래를 명목으로 8,500,000원을 송금하였습니다."
          },
          {
            "name": "고소장_2024.jpg",
            "doc_id": "complaint_2024",
            "line": 5,
            "quote": "8,500,000원"
          },
          {
            "name": "계좌거래내역_2026.png",
            "doc_id": "bank_2026",
            "line": 3,
            "quote": "2024. 3. 12. 같은 계좌에서 타인 3명에게 분산 이체됨"
          }
        ]
      },
      {
        "type": "event",
        "time": "2024.03.20\n11:05",
        "title": "사건 접수",
        "full": "접 수 증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  접수증_2024.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "접수증_2024.jpg",
            "doc_id": "receipt_2024",
            "line": 1,
            "quote": "접 수 증"
          },
          {
            "name": "접수증_2024.jpg",
            "doc_id": "receipt_2024",
            "line": 3,
            "quote": "2024. 3. 20. 11:05"
          }
        ]
      },
      {
        "type": "gap",
        "range": "2024.03.20 – 2026.08.25",
        "text": "이 기간의 기록이 없어요 (약 2.4년)"
      },
      {
        "type": "event",
        "time": "2026.08.25",
        "title": "수사결과 통지 — 불송치",
        "full": "수사결과 통지서",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  불송치_결정통지서.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "불송치_결정통지서.jpg",
            "doc_id": "no_referral_notice_2026",
            "line": 1,
            "quote": "수사결과 통지서"
          },
          {
            "name": "불송치_결정통지서.jpg",
            "doc_id": "no_referral_notice_2026",
            "line": 6,
            "quote": "2026. 8. 25."
          }
        ]
      },
      {
        "type": "event",
        "time": "시각 미상",
        "title": "사기 피해",
        "full": "죄명 사기",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2024.jpg · 4줄",
        "sources": [
          {
            "name": "고소장_2024.jpg",
            "doc_id": "complaint_2024",
            "line": 4,
            "quote": "죄명 사기"
          }
        ]
      },
      {
        "type": "event",
        "time": "시각 미상",
        "title": "통지서를 받고 은행에서 거래내역을 떼어 보니 제가 보낸 돈이 바로 다른 사람들에게 나뉘어 갔습니다",
        "full": "통지서를 받고 은행에서 거래내역을 떼어 보니 제가 보낸 돈이 바로 다른 사람들에게 나뉘어 갔습니다.",
        "kind": "mine",
        "badge": "내가 입력",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  직접 입력 · 1줄",
        "sources": [
          {
            "name": "직접 입력",
            "doc_id": "note_yoon",
            "line": 1,
            "quote": "통지서를 받고 은행에서 거래내역을 떼어 보니 제가 보낸 돈이 바로 다른 사람들에게 나뉘어 갔습니다."
          }
        ]
      }
    ],
    "people": [
      {
        "label": "사람",
        "items": [
          {
            "name": "윤서진",
            "roles": [
              "고소인",
              "신고인"
            ],
            "docs": [
              "불송치_결정통지서.jpg",
              "접수증_2024.jpg"
            ],
            "same_as": []
          },
          {
            "name": "박성우",
            "roles": [
              "피고소인"
            ],
            "docs": [
              "불송치_결정통지서.jpg"
            ],
            "same_as": []
          },
          {
            "name": "김도현",
            "roles": [
              "담당수사관"
            ],
            "docs": [
              "불송치_결정통지서.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "기관",
        "items": [
          {
            "name": "**경찰서",
            "roles": [],
            "docs": [
              "불송치_결정통지서.jpg",
              "접수증_2024.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "사건번호",
        "items": [
          {
            "name": "2024형제33210",
            "roles": [],
            "docs": [
              "불송치_결정통지서.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "접수번호",
        "items": [
          {
            "name": "2024-011234",
            "roles": [],
            "docs": [
              "접수증_2024.jpg"
            ],
            "same_as": []
          }
        ]
      }
    ],
    "slots": [
      {
        "slot": "사건 발생 시점",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
      },
      {
        "slot": "접수번호",
        "value": "2024-011234",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2024-011234",
            "doc": "접수증_2024.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "offence",
        "value": "사기",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "사기",
            "doc": "고소장_2024.jpg",
            "speaker": "윤서진",
            "record": false
          },
          {
            "value": "사기",
            "doc": "접수증_2024.jpg",
            "speaker": "**경찰서",
            "record": true
          },
          {
            "value": "사기",
            "doc": "불송치_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "사건번호",
        "value": "2024형제33210",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2024형제33210",
            "doc": "불송치_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "담당 수사관",
        "value": "김도현",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "김도현",
            "doc": "불송치_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "결정 내용",
        "value": "불송치(혐의없음)",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "불송치(혐의없음)",
            "doc": "불송치_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "결정일",
        "value": "2026-08-25",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2026-08-25",
            "doc": "불송치_결정통지서.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      }
    ],
    "issues": [
      {
        "label": "빠진 정보",
        "severity": "gap",
        "items": [
          {
            "text": "사건 발생 시점: 올린 자료에서 찾지 못했습니다",
            "how": "확인한 자료 5개에서 찾지 못함"
          },
          {
            "text": "‘신고’ 단계에 해당하는 자료가 없습니다",
            "how": "확인한 자료 5개에서 찾지 못함"
          },
          {
            "text": "‘수사’ 단계에 해당하는 자료가 없습니다",
            "how": "확인한 자료 5개에서 찾지 못함"
          },
          {
            "text": "2024-03-20 ~ 2026-08-25 사이의 기록이 없습니다 (약 2.4년)",
            "how": "근거 · 접수증_2024.jpg 1줄"
          }
        ]
      }
    ],
    "next_action": {
      "rule_no": 5,
      "action": "ACT-불복기한",
      "label": "기한 안에 결정에 대한 불복 절차 진행",
      "why": "불복할 수 있는 결정을 받은 상태다. 기한이 급하지 않아도 이 경로를 먼저 알려야 한다",
      "rule_why": "불복할 수 있는 결정을 받은 상태다. 기한이 급하지 않아도 이 경로를 먼저 알려야 한다",
      "due": null,
      "state": "filled",
      "rows": [
        {
          "k": "무엇을",
          "v": "불송치 결정 이의신청서"
        },
        {
          "k": "어디에",
          "v": "불송치 결정을 한 사법경찰관의 소속 관서의 장"
        },
        {
          "k": "근거",
          "v": "형사소송법 제245조의7"
        }
      ],
      "prepare": {
        "done": 2,
        "total": 3,
        "items": [
          {
            "label": "불송치 결정 이의신청서",
            "state": "생성가능",
            "required": true
          },
          {
            "label": "수사결과 통지서 (불송치 결정)",
            "state": "보유",
            "required": false
          },
          {
            "label": "이의신청 사유를 뒷받침하는 증거자료",
            "state": "보유",
            "required": false
          }
        ]
      },
      "note": null,
      "unverified": true,
      "also": [
        {
          "rule_no": 9,
          "action": "ACT-근거보완",
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        },
        {
          "rule_no": 10,
          "action": "ACT-공백보완",
          "label": "기록이 빈 기간의 자료 확보",
          "why": "기록 공백은 반박 여지를 남긴다"
        }
      ],
      "submit_to": "불송치 결정을 한 사법경찰관의 소속 관서의 장",
      "form_name": "불송치 결정 이의신청서",
      "draft": {
        "is_draft": true,
        "prose": null,
        "form_name": "불송치 결정 이의신청서",
        "form_source": "경찰수사규칙 별지 제125호 서식",
        "form_url": "https://www.law.go.kr/LSW//flDownload.do?flSeq=111544157&bylClsCd=110202",
        "fields": [
          {
            "label": "사건번호",
            "value": "2024형제33210",
            "from": "case_record"
          },
          {
            "label": "접수번호",
            "value": "2024-011234",
            "from": "case_record"
          },
          {
            "label": "담당 수사관",
            "value": "김도현",
            "from": "case_record"
          },
          {
            "label": "결정 내용",
            "value": "불송치(혐의없음)",
            "from": "case_record"
          },
          {
            "label": "결정일",
            "value": "2026-08-25",
            "from": "case_record"
          },
          {
            "label": "서식",
            "value": "불송치 결정 이의신청서",
            "from": "knowledge_base"
          },
          {
            "label": "제출처",
            "value": "불송치 결정을 한 사법경찰관의 소속 관서의 장",
            "from": "knowledge_base"
          },
          {
            "label": "근거 법령",
            "value": "형사소송법 제245조의7",
            "from": "knowledge_base"
          }
        ],
        "unfilled": [
          {
            "label": "신청인 성명",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 연락처",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          },
          {
            "label": "신청인 주소",
            "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
          }
        ],
        "sections": [
          {
            "heading": "사건 경위",
            "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
            "lines": [
              {
                "date": "2024. 3. 12.",
                "text": "8,500,000원 송금",
                "level": "statement",
                "source": "고소장_2024.jpg 5줄"
              },
              {
                "date": "2024. 3. 20.",
                "text": "접 수 증",
                "level": "record",
                "source": "접수증_2024.jpg 1줄"
              },
              {
                "date": "2026. 8. 25.",
                "text": "수사결과 통지서",
                "level": "record",
                "source": "불송치_결정통지서.jpg 1줄"
              },
              {
                "date": null,
                "text": "죄명 사기",
                "level": "statement",
                "source": "고소장_2024.jpg 4줄"
              }
            ]
          },
          {
            "heading": "이의 사유",
            "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
            "lines": []
          }
        ],
        "dropped": 0
      }
    },
    "actions": [
      {
        "rule_no": 5,
        "action": "ACT-불복기한",
        "label": "기한 안에 결정에 대한 불복 절차 진행",
        "why": "불복할 수 있는 결정을 받은 상태다. 기한이 급하지 않아도 이 경로를 먼저 알려야 한다",
        "rule_why": "불복할 수 있는 결정을 받은 상태다. 기한이 급하지 않아도 이 경로를 먼저 알려야 한다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "불송치 결정 이의신청서"
          },
          {
            "k": "어디에",
            "v": "불송치 결정을 한 사법경찰관의 소속 관서의 장"
          },
          {
            "k": "근거",
            "v": "형사소송법 제245조의7"
          }
        ],
        "prepare": {
          "done": 2,
          "total": 3,
          "items": [
            {
              "label": "불송치 결정 이의신청서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "수사결과 통지서 (불송치 결정)",
              "state": "보유",
              "required": false
            },
            {
              "label": "이의신청 사유를 뒷받침하는 증거자료",
              "state": "보유",
              "required": false
            }
          ]
        },
        "note": null,
        "unverified": true,
        "also": [
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "불송치 결정을 한 사법경찰관의 소속 관서의 장",
        "form_name": "불송치 결정 이의신청서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "불송치 결정 이의신청서",
          "form_source": "경찰수사규칙 별지 제125호 서식",
          "form_url": "https://www.law.go.kr/LSW//flDownload.do?flSeq=111544157&bylClsCd=110202",
          "fields": [
            {
              "label": "사건번호",
              "value": "2024형제33210",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2024-011234",
              "from": "case_record"
            },
            {
              "label": "담당 수사관",
              "value": "김도현",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "불송치(혐의없음)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2026-08-25",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "불송치 결정 이의신청서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "불송치 결정을 한 사법경찰관의 소속 관서의 장",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "형사소송법 제245조의7",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2024. 3. 12.",
                  "text": "8,500,000원 송금",
                  "level": "statement",
                  "source": "고소장_2024.jpg 5줄"
                },
                {
                  "date": "2024. 3. 20.",
                  "text": "접 수 증",
                  "level": "record",
                  "source": "접수증_2024.jpg 1줄"
                },
                {
                  "date": "2026. 8. 25.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "불송치_결정통지서.jpg 1줄"
                },
                {
                  "date": null,
                  "text": "죄명 사기",
                  "level": "statement",
                  "source": "고소장_2024.jpg 4줄"
                }
              ]
            },
            {
              "heading": "이의 사유",
              "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 9,
        "action": "ACT-근거보완",
        "label": "주장을 뒷받침할 근거 자료 보완",
        "why": "사건 발생 시점: 올린 자료에서 찾지 못했습니다",
        "rule_why": "근거 없는 주장은 판단 대상이 되지 않는다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "원본 출처나 감정 결과를 확보하는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      },
      {
        "rule_no": 10,
        "action": "ACT-공백보완",
        "label": "기록이 빈 기간의 자료 확보",
        "why": "‘신고’ 단계에 해당하는 자료가 없습니다",
        "rule_why": "기록 공백은 반박 여지를 남긴다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "기록이 비어 있는 기간의 자료를 모으는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      }
    ],
    "response_choices": [
      "불송치",
      "불기소",
      "항고 기각",
      "피의자중지",
      "참고인중지",
      "기소"
    ],
    "outcomes": {
      "불송치": {
        "st": "경찰 불송치",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "불기소": {
        "st": "검찰 불기소",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "검찰 항고 기한",
            "period_days": 30,
            "statute": "검찰청법 제10조",
            "submit_to": "불기소 처분을 한 검사가 속한 지방검찰청 또는 지청을 거쳐 관할 고등검찰청 검사장"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "항고 기각": {
        "st": "이의신청/항고 중",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "법원 재정신청 기한",
            "period_days": 10,
            "statute": "형사소송법 제260조 제3항",
            "submit_to": "지방검찰청 검사장 또는 지청장"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "피의자중지": {
        "st": "피의자 중지",
        "next": "주장을 뒷받침할 근거 자료 보완",
        "next_key": "ACT-근거보완",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "참고인중지": {
        "st": "참고인 중지",
        "next": "주장을 뒷받침할 근거 자료 보완",
        "next_key": "ACT-근거보완",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "기소": {
        "st": "재판 진행 중",
        "next": "주장을 뒷받침할 근거 자료 보완",
        "next_key": "ACT-근거보완",
        "deadlines": [
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      }
    }
  },
  {
    "id": "blurred_test",
    "title": "흐린 통지서 (시험)",
    "type": "investigation_suspended",
    "type_label": "수사중지 사건",
    "as_of": "2026.09.16",
    "period": "2022.02 – 2024.05",
    "doc_count": 3,
    "need_count": 7,
    "stages": [
      {
        "label": "고소",
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
        "label": "중지",
        "state": "current"
      },
      {
        "label": "재개",
        "state": "todo"
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "고소장_2022.jpg",
        "doc_id": "complaint_2022"
      },
      {
        "kind": "IMG",
        "name": "접수증_2022.jpg",
        "doc_id": "receipt_2022"
      },
      {
        "kind": "IMG",
        "name": "수사결과_통지서_흐림.jpg",
        "doc_id": "blurred_notice_2024"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "time": "2022.02.14",
        "title": "2,300,000원 송금",
        "full": "2,300,000원 송금",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2022.jpg · 4줄 외 1곳",
        "sources": [
          {
            "name": "고소장_2022.jpg",
            "doc_id": "complaint_2022",
            "line": 4,
            "quote": "2022. 2. 14. 중고 카메라 대금으로 2,300,000원을 송금하였습니다."
          },
          {
            "name": "고소장_2022.jpg",
            "doc_id": "complaint_2022",
            "line": 4,
            "quote": "2,300,000원"
          }
        ]
      },
      {
        "type": "event",
        "time": "2022.03.02",
        "title": "○○경찰서 고소",
        "full": "2022. 3. 2. ○○경찰서에 고소하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  고소장_2022.jpg · 5줄",
        "sources": [
          {
            "name": "고소장_2022.jpg",
            "doc_id": "complaint_2022",
            "line": 5,
            "quote": "2022. 3. 2. ○○경찰서에 고소하였습니다."
          }
        ]
      },
      {
        "type": "event",
        "time": "2022.03.02\n09:40",
        "title": "사건 접수",
        "full": "접 수 증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ②  접수증_2022.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "접수증_2022.jpg",
            "doc_id": "receipt_2022",
            "line": 1,
            "quote": "접 수 증"
          },
          {
            "name": "접수증_2022.jpg",
            "doc_id": "receipt_2022",
            "line": 3,
            "quote": "2022. 3. 2. 09:40"
          }
        ]
      },
      {
        "type": "gap",
        "range": "2022.03.03 – 2024.05.30",
        "text": "이 기간의 기록이 없어요 (약 2.2년)"
      },
      {
        "type": "event",
        "time": "2024.05.30",
        "title": "수사결과 통지",
        "full": "수사결과 통지서",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  수사결과_통지서_흐림.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "수사결과_통지서_흐림.jpg",
            "doc_id": "blurred_notice_2024",
            "line": 1,
            "quote": "수사결과 통지서"
          },
          {
            "name": "수사결과_통지서_흐림.jpg",
            "doc_id": "blurred_notice_2024",
            "line": 5,
            "quote": "2024. 5. 30."
          }
        ]
      },
      {
        "type": "event",
        "time": "시각 미상",
        "title": "통지서를 받았는데 비에 젖어서 결정 부분이 번졌습니다",
        "full": "통지서를 받았는데 비에 젖어서 결정 부분이 번졌습니다. 무슨 결정인지 모르겠어요.",
        "kind": "mine",
        "badge": "내가 입력",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  직접 입력 · 1줄",
        "sources": [
          {
            "name": "직접 입력",
            "doc_id": "note_kang",
            "line": 1,
            "quote": "통지서를 받았는데 비에 젖어서 결정 부분이 번졌습니다. 무슨 결정인지 모르겠어요."
          }
        ]
      }
    ],
    "people": [
      {
        "label": "사람",
        "items": [
          {
            "name": "강태오",
            "roles": [
              "고소인",
              "신고인"
            ],
            "docs": [
              "수사결과_통지서_흐림.jpg",
              "접수증_2022.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "기관",
        "items": [
          {
            "name": "**경찰서",
            "roles": [],
            "docs": [
              "고소장_2022.jpg",
              "수사결과_통지서_흐림.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "사건번호",
        "items": [
          {
            "name": "2022형제1077",
            "roles": [],
            "docs": [
              "수사결과_통지서_흐림.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "접수번호",
        "items": [
          {
            "name": "2022-003318",
            "roles": [],
            "docs": [
              "접수증_2022.jpg"
            ],
            "same_as": []
          }
        ]
      }
    ],
    "slots": [
      {
        "slot": "사건 발생 시점",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
      },
      {
        "slot": "접수번호",
        "value": "2022-003318",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2022-003318",
            "doc": "접수증_2022.jpg",
            "speaker": "접수증_2022.jpg 발급처",
            "record": true
          }
        ]
      },
      {
        "slot": "offence",
        "value": "사기",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "사기",
            "doc": "접수증_2022.jpg",
            "speaker": "접수증_2022.jpg 발급처",
            "record": true
          },
          {
            "value": "사기",
            "doc": "수사결과_통지서_흐림.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "사건번호",
        "value": "2022형제1077",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2022형제1077",
            "doc": "수사결과_통지서_흐림.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "담당 수사관",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
      },
      {
        "slot": "결정 내용",
        "value": null,
        "state": "unreadable",
        "severity": "unknown",
        "said": []
      },
      {
        "slot": "결정일",
        "value": "2024-05-30",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2024-05-30",
            "doc": "수사결과_통지서_흐림.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      }
    ],
    "issues": [
      {
        "label": "빠진 정보",
        "severity": "gap",
        "items": [
          {
            "text": "사건 발생 시점: 올린 자료에서 찾지 못했습니다",
            "how": "확인한 자료 4개에서 찾지 못함"
          },
          {
            "text": "‘수사결과 통지서’(2024-05-30) 이후 기관의 진행 기록이 없습니다 (839일 경과)",
            "how": "근거 · 수사결과_통지서_흐림.jpg 1줄"
          },
          {
            "text": "‘발생’ 단계에 해당하는 자료가 없습니다",
            "how": "확인한 자료 4개에서 찾지 못함"
          },
          {
            "text": "‘수사’ 단계에 해당하는 자료가 없습니다",
            "how": "확인한 자료 4개에서 찾지 못함"
          },
          {
            "text": "2022-03-03 ~ 2024-05-30 사이의 기록이 없습니다 (약 2.2년)",
            "how": "근거 · 고소장_2022.jpg 5줄"
          }
        ]
      },
      {
        "label": "읽히지 않은 부분",
        "severity": "gap",
        "items": [
          {
            "text": "결정 내용: 올린 자료에서 찾지 못했고, 해당 내용이 있을 수 있는 부분이 읽히지 않았습니다",
            "how": "근거 · 수사결과_통지서_흐림.jpg 6줄"
          },
          {
            "text": "수사결과_통지서_흐림.jpg에서 읽히지 않은 부분이 2곳 있습니다 (6, 7줄). 사진을 보고 알려주세요",
            "how": "근거 · 수사결과_통지서_흐림.jpg 6줄"
          }
        ]
      }
    ],
    "next_action": {
      "rule_no": 4,
      "action": "ACT-단계확인",
      "label": "지금 사건이 어느 단계인지 확인",
      "why": "단계를 모르면 나머지 판단이 전부 무의미하다",
      "rule_why": "단계를 모르면 나머지 판단이 전부 무의미하다",
      "due": null,
      "state": "filled",
      "rows": [
        {
          "k": "무엇을",
          "v": "형사사법포털 사건조회 (온라인)"
        },
        {
          "k": "어디에",
          "v": "형사사법포털 www.kics.go.kr — 형사사법공통시스템운영단 1588-4771"
        }
      ],
      "prepare": {
        "done": 1,
        "total": 2,
        "items": [
          {
            "label": "인증서 (형사사법포털 로그인용)",
            "state": "미보유",
            "required": true
          },
          {
            "label": "사건 접수증 또는 통지서",
            "state": "보유",
            "required": false
          }
        ]
      },
      "note": "고소사건은 고소인·피고소인·피해자, 고발사건은 고발인·피고발인·피해자, 인지사건은 피의자·피해자가 조회할 수 있다. 회원가입 후 인증서로 로그인해야 한다",
      "unverified": true,
      "also": [
        {
          "rule_no": 8,
          "action": "ACT-기록열람",
          "label": "수사 기록 열람 신청",
          "why": "수사 기록 없이는 다른 판단이 불가능하다"
        },
        {
          "rule_no": 9,
          "action": "ACT-근거보완",
          "label": "주장을 뒷받침할 근거 자료 보완",
          "why": "근거 없는 주장은 판단 대상이 되지 않는다"
        },
        {
          "rule_no": 10,
          "action": "ACT-공백보완",
          "label": "기록이 빈 기간의 자료 확보",
          "why": "기록 공백은 반박 여지를 남긴다"
        }
      ],
      "submit_to": "형사사법포털 www.kics.go.kr — 형사사법공통시스템운영단 1588-4771",
      "form_name": "형사사법포털 사건조회 (온라인)",
      "draft": null
    },
    "actions": [
      {
        "rule_no": 4,
        "action": "ACT-단계확인",
        "label": "지금 사건이 어느 단계인지 확인",
        "why": "단계를 모르면 나머지 판단이 전부 무의미하다",
        "rule_why": "단계를 모르면 나머지 판단이 전부 무의미하다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "형사사법포털 사건조회 (온라인)"
          },
          {
            "k": "어디에",
            "v": "형사사법포털 www.kics.go.kr — 형사사법공통시스템운영단 1588-4771"
          }
        ],
        "prepare": {
          "done": 1,
          "total": 2,
          "items": [
            {
              "label": "인증서 (형사사법포털 로그인용)",
              "state": "미보유",
              "required": true
            },
            {
              "label": "사건 접수증 또는 통지서",
              "state": "보유",
              "required": false
            }
          ]
        },
        "note": "고소사건은 고소인·피고소인·피해자, 고발사건은 고발인·피고발인·피해자, 인지사건은 피의자·피해자가 조회할 수 있다. 회원가입 후 인증서로 로그인해야 한다",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "형사사법포털 www.kics.go.kr — 형사사법공통시스템운영단 1588-4771",
        "form_name": "형사사법포털 사건조회 (온라인)",
        "draft": null
      },
      {
        "rule_no": 8,
        "action": "ACT-기록열람",
        "label": "수사 기록 열람 신청",
        "why": "‘수사결과 통지서’(2024-05-30) 이후 기관의 진행 기록이 없습니다 (839일 경과)",
        "rule_why": "수사 기록 없이는 다른 판단이 불가능하다",
        "due": null,
        "state": "filled",
        "rows": [
          {
            "k": "무엇을",
            "v": "수사기록 열람·등사 신청서"
          },
          {
            "k": "어디에",
            "v": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청"
          },
          {
            "k": "근거",
            "v": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침"
          }
        ],
        "prepare": {
          "done": 0,
          "total": 2,
          "items": [
            {
              "label": "수사기록 열람·등사 신청서",
              "state": "생성가능",
              "required": true
            },
            {
              "label": "신청인 신분 확인 서류",
              "state": "미보유",
              "required": true
            }
          ]
        },
        "note": "불송치·불기소로 끝난 사건은 정보공개청구가 거부되는 일이 잦다. 거부를 전제로 다음 경로(이의신청·행정소송)까지 함께 안내해야 한다. 수사 중인 사건은 본인 진술과 본인이 낸 서류만(수사준칙 제69조 제1항), 불송치·불기소 사건은 기록의 전부 또는 일부를(제2항) 신청할 수 있다. 가족은 위임장과 신분관계 증명서를 내고 신청할 수 있다(제5항). 경찰관서는 신청을 받은 날부터 10일 이내에 공개 여부를 결정한다(경찰수사규칙 제87조 제2항).",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
        "form_name": "수사기록 열람·등사 신청서",
        "draft": {
          "is_draft": true,
          "prose": null,
          "form_name": "수사기록 열람·등사 신청서",
          "form_source": "검찰보존사무규칙 별지 제5호서식 「사건기록 열람·등사 신청서」(제20조의2·제20조의3). 경찰관서 신청 서식은 경찰청장이 따로 정한다(경찰수사규칙 제87조 제6항)",
          "form_url": "https://law.go.kr/flDownload.do?gubun=&flSeq=132313759",
          "fields": [
            {
              "label": "사건번호",
              "value": "2022형제1077",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2022-003318",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2024-05-30",
              "from": "case_record"
            },
            {
              "label": "서식",
              "value": "수사기록 열람·등사 신청서",
              "from": "knowledge_base"
            },
            {
              "label": "제출처",
              "value": "경찰이 가진 수사서류는 그 서류를 보유·관리하는 경찰관서의 장(경찰수사규칙 제87조 제1항), 검찰이 가진 기록은 그 기록을 보관하는 검찰청",
              "from": "knowledge_base"
            },
            {
              "label": "근거 법령",
              "value": "검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제69조 · 사건기록 열람·등사에 관한 업무처리 지침",
              "from": "knowledge_base"
            }
          ],
          "unfilled": [
            {
              "label": "담당 수사관",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "결정 내용",
              "reason": "자료에서 찾지 못했습니다."
            },
            {
              "label": "신청인 성명",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 연락처",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            },
            {
              "label": "신청인 주소",
              "reason": "자료에 있을 수 없는 항목입니다. 직접 적어 주세요."
            }
          ],
          "sections": [
            {
              "heading": "사건 경위",
              "note": "자료에 적힌 날짜와 문구를 시간순으로 옮긴 것입니다. 문장을 다듬어 쓰세요.",
              "lines": [
                {
                  "date": "2022. 2. 14.",
                  "text": "2,300,000원 송금",
                  "level": "statement",
                  "source": "고소장_2022.jpg 4줄"
                },
                {
                  "date": "2022. 3. 2.",
                  "text": "2022. 3. 2. ○○경찰서에 고소하였습니다.",
                  "level": "statement",
                  "source": "고소장_2022.jpg 5줄"
                },
                {
                  "date": "2022. 3. 2.",
                  "text": "접 수 증",
                  "level": "record",
                  "source": "접수증_2022.jpg 1줄"
                },
                {
                  "date": "2024. 5. 30.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사결과_통지서_흐림.jpg 1줄"
                }
              ]
            },
            {
              "heading": "이의 사유",
              "note": "타래는 이 칸을 대신 쓰지 않습니다. 왜 결정에 동의할 수 없는지는 직접 적어 주세요.",
              "lines": []
            }
          ],
          "dropped": 0
        }
      },
      {
        "rule_no": 9,
        "action": "ACT-근거보완",
        "label": "주장을 뒷받침할 근거 자료 보완",
        "why": "결정 내용: 올린 자료에서 찾지 못했고, 해당 내용이 있을 수 있는 부분이 읽히지 않았습니다",
        "rule_why": "근거 없는 주장은 판단 대상이 되지 않는다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "원본 출처나 감정 결과를 확보하는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      },
      {
        "rule_no": 10,
        "action": "ACT-공백보완",
        "label": "기록이 빈 기간의 자료 확보",
        "why": "‘발생’ 단계에 해당하는 자료가 없습니다",
        "rule_why": "기록 공백은 반박 여지를 남긴다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "기록이 비어 있는 기간의 자료를 모으는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "수사 기록 없이는 다른 판단이 불가능하다"
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "근거 없는 주장은 판단 대상이 되지 않는다"
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "기록 공백은 반박 여지를 남긴다"
          }
        ],
        "submit_to": null,
        "form_name": null,
        "draft": null
      }
    ],
    "response_choices": [
      "불송치",
      "불기소",
      "항고 기각",
      "피의자중지",
      "참고인중지",
      "기소"
    ],
    "outcomes": {
      "불송치": {
        "st": "경찰 불송치",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "불기소": {
        "st": "검찰 불기소",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "검찰 항고 기한",
            "period_days": 30,
            "statute": "검찰청법 제10조",
            "submit_to": "불기소 처분을 한 검사가 속한 지방검찰청 또는 지청을 거쳐 관할 고등검찰청 검사장"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "항고 기각": {
        "st": "이의신청/항고 중",
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "법원 재정신청 기한",
            "period_days": 10,
            "statute": "형사소송법 제260조 제3항",
            "submit_to": "지방검찰청 검사장 또는 지청장"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "피의자중지": {
        "st": "피의자 중지",
        "next": "수사 기록 열람 신청",
        "next_key": "ACT-기록열람",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "참고인중지": {
        "st": "참고인 중지",
        "next": "수사 기록 열람 신청",
        "next_key": "ACT-기록열람",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          },
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      },
      "기소": {
        "st": "재판 진행 중",
        "next": "수사 기록 열람 신청",
        "next_key": "ACT-기록열람",
        "deadlines": [
          {
            "label": "형사 공소시효 임박",
            "period_days": 3650,
            "statute": "형법 제347조 제1항",
            "submit_to": null
          }
        ]
      }
    }
  }
];
