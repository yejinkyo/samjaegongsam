// 자동 생성 파일 — action-engine/tools/export_web.py 로 다시 만든다. 직접 고치지 않는다.
window.TARAE_CASES = [
  {
    "id": "demo_missing_2017",
    "title": "2017년 실종, 9년째 미제",
    "type": "missing_person_suspended",
    "type_label": "실종 사건 · 수사중지",
    "as_of": "2026.09.19",
    "period": "2017.11 – 2025.09",
    "doc_count": 7,
    "need_count": 10,
    "stages": [
      {
        "label": "발생",
        "state": "done",
        "noted": false
      },
      {
        "label": "신고",
        "state": "done",
        "noted": false
      },
      {
        "label": "수사",
        "state": "done",
        "noted": false
      },
      {
        "label": "중지",
        "state": "current",
        "noted": false
      },
      {
        "label": "재수사",
        "state": "todo",
        "noted": false
      }
    ],
    "sources": [
      {
        "kind": "IMG",
        "name": "실종신고_접수증_2017.jpg",
        "doc_id": "missing_report_2017"
      },
      {
        "kind": "IMG",
        "name": "진술서_편의점직원.jpg",
        "doc_id": "witness_station_2017"
      },
      {
        "kind": "IMG",
        "name": "진술서_시장상인.jpg",
        "doc_id": "witness_market_2017"
      },
      {
        "kind": "IMG",
        "name": "가족_진술서.jpg",
        "doc_id": "family_statement_2017"
      },
      {
        "kind": "IMG",
        "name": "기사_2018.jpg",
        "doc_id": "news_2018"
      },
      {
        "kind": "IMG",
        "name": "수사중지_통지서_2019.jpg",
        "doc_id": "suspension_notice_2019"
      },
      {
        "kind": "IMG",
        "name": "진술서_2025.jpg",
        "doc_id": "tip_statement_2025"
      }
    ],
    "timeline": [
      {
        "type": "event",
        "at": "2017-11-01",
        "time": "2017.11.01\n22시~익일 1시경",
        "title": "마지막 목격 · ○○역 인근",
        "full": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 마지막으로 찍혔다고 밝혔다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑤  기사_2018.jpg · 3줄 외 1곳",
        "sources": [
          {
            "name": "기사_2018.jpg",
            "doc_id": "news_2018",
            "line": 3,
            "quote": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 마지막으로 찍혔다고 밝혔다."
          },
          {
            "name": "기사_2018.jpg",
            "doc_id": "news_2018",
            "line": 3,
            "quote": "11월 1일 밤 11시쯤"
          }
        ]
      },
      {
        "type": "event",
        "at": "2017-11-02",
        "time": "2017.11.02\n21~24시경",
        "title": "목격 · ○○시 중앙시장 앞",
        "full": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을 목격하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ③  진술서_시장상인.jpg · 3줄 외 1곳",
        "sources": [
          {
            "name": "진술서_시장상인.jpg",
            "doc_id": "witness_market_2017",
            "line": 3,
            "quote": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을 목격하였습니다."
          },
          {
            "name": "진술서_시장상인.jpg",
            "doc_id": "witness_market_2017",
            "line": 3,
            "quote": "2017. 11. 2. 22시경"
          }
        ]
      },
      {
        "type": "event",
        "at": "2017-11-03",
        "time": "2017.11.03",
        "title": "112 신고",
        "full": "2017. 11. 3. 밤 112에 신고하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ④  가족_진술서.jpg · 5줄",
        "sources": [
          {
            "name": "가족_진술서.jpg",
            "doc_id": "family_statement_2017",
            "line": 5,
            "quote": "2017. 11. 3. 밤 112에 신고하였습니다."
          }
        ]
      },
      {
        "type": "event",
        "at": "2017-11-04",
        "time": "2017.11.04\n09:20",
        "title": "실종신고 접수",
        "full": "실종신고 접수증",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  실종신고_접수증_2017.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "실종신고_접수증_2017.jpg",
            "doc_id": "missing_report_2017",
            "line": 1,
            "quote": "실종신고 접수증"
          },
          {
            "name": "실종신고_접수증_2017.jpg",
            "doc_id": "missing_report_2017",
            "line": 3,
            "quote": "2017. 11. 4. 09:20"
          }
        ]
      },
      {
        "type": "event",
        "at": "2017-11-10",
        "time": "2017.11.10",
        "title": "출석 조사",
        "full": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ④  가족_진술서.jpg · 6줄",
        "sources": [
          {
            "name": "가족_진술서.jpg",
            "doc_id": "family_statement_2017",
            "line": 6,
            "quote": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다."
          }
        ]
      },
      {
        "type": "gap",
        "at": "2018-02-05",
        "range": "2018.02.05 – 2019.06.17",
        "text": "이 기간의 기록이 없어요 (약 1.4년)"
      },
      {
        "type": "event",
        "at": "2019-01-01",
        "time": "2019",
        "title": "2019년 통지서를 받은 뒤로 경찰에서 연락 온 적이 없습니다",
        "full": "2019년 통지서를 받은 뒤로 경찰에서 연락 온 적이 없습니다.",
        "kind": "mine",
        "badge": "내가 입력",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  직접 입력 · 1줄",
        "sources": [
          {
            "name": "직접 입력",
            "doc_id": "note_no_contact",
            "line": 1,
            "quote": "2019년 통지서를 받은 뒤로 경찰에서 연락 온 적이 없습니다."
          }
        ]
      },
      {
        "type": "event",
        "at": "2019-06-17",
        "time": "2019.06.17",
        "title": "수사결과 통지 — 수사중지(피의자중지)",
        "full": "수사결과 통지서",
        "kind": "verified",
        "badge": "확인됨",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑥  수사중지_통지서_2019.jpg · 1줄 외 1곳",
        "sources": [
          {
            "name": "수사중지_통지서_2019.jpg",
            "doc_id": "suspension_notice_2019",
            "line": 1,
            "quote": "수사결과 통지서"
          },
          {
            "name": "수사중지_통지서_2019.jpg",
            "doc_id": "suspension_notice_2019",
            "line": 5,
            "quote": "2019. 6. 17."
          }
        ]
      },
      {
        "type": "gap",
        "at": "2019-06-18",
        "range": "2019.06.18 – 2025.08.14",
        "text": "이 기간의 기록이 없어요 (약 6.2년)"
      },
      {
        "type": "event",
        "at": "2025-08-14",
        "time": "2025.08.14\n12~18시경",
        "title": "목격 · ○○시 버스터미널",
        "full": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤으로 보이는 여성을 목격하였습니다.",
        "kind": "claim",
        "badge": "주장 · 미확인",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ⑦  진술서_2025.jpg · 3줄 외 1곳",
        "sources": [
          {
            "name": "진술서_2025.jpg",
            "doc_id": "tip_statement_2025",
            "line": 3,
            "quote": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤으로 보이는 여성을 목격하였습니다."
          },
          {
            "name": "진술서_2025.jpg",
            "doc_id": "tip_statement_2025",
            "line": 3,
            "quote": "2025. 8. 14. 오후"
          }
        ]
      },
      {
        "type": "event",
        "at": "2025-09-01",
        "time": "2025.09",
        "title": "2025년 9월 목격 제보를 전화로 알렸지만 담당자가 바뀌었다고만 들었습니다",
        "full": "2025년 9월 목격 제보를 전화로 알렸지만 담당자가 바뀌었다고만 들었습니다.",
        "kind": "mine",
        "badge": "내가 입력",
        "conflict": false,
        "needs_date": false,
        "source": "출처 ①  직접 입력 · 1줄",
        "sources": [
          {
            "name": "직접 입력",
            "doc_id": "note_tip",
            "line": 1,
            "quote": "2025년 9월 목격 제보를 전화로 알렸지만 담당자가 바뀌었다고만 들었습니다."
          }
        ]
      }
    ],
    "people": [
      {
        "label": "사람",
        "items": [
          {
            "name": "정하윤",
            "roles": [
              "실종자"
            ],
            "docs": [
              "실종신고_접수증_2017.jpg"
            ],
            "same_as": []
          },
          {
            "name": "정미경",
            "roles": [
              "신고인",
              "진술인"
            ],
            "docs": [
              "실종신고_접수증_2017.jpg"
            ],
            "same_as": []
          },
          {
            "name": "강태오",
            "roles": [
              "진술인"
            ],
            "docs": [],
            "same_as": []
          },
          {
            "name": "오미란",
            "roles": [
              "진술인"
            ],
            "docs": [],
            "same_as": []
          },
          {
            "name": "한상우",
            "roles": [
              "담당수사관"
            ],
            "docs": [
              "수사중지_통지서_2019.jpg"
            ],
            "same_as": []
          },
          {
            "name": "배수진",
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
              "가족_진술서.jpg",
              "수사중지_통지서_2019.jpg",
              "실종신고_접수증_2017.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "사건번호",
        "items": [
          {
            "name": "2017형제30918",
            "roles": [],
            "docs": [
              "수사중지_통지서_2019.jpg"
            ],
            "same_as": []
          }
        ]
      },
      {
        "label": "접수번호",
        "items": [
          {
            "name": "2017-00481",
            "roles": [],
            "docs": [
              "실종신고_접수증_2017.jpg"
            ],
            "same_as": []
          }
        ]
      }
    ],
    "slots": [
      {
        "slot": "마지막 목격 시점",
        "value": "2017-11-02 21~24시",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2017-11-02 21~24시",
            "doc": "실종신고_접수증_2017.jpg",
            "speaker": "**경찰서",
            "record": true
          },
          {
            "value": "2017-11-01 22시~01시",
            "doc": "기사_2018.jpg",
            "speaker": "경찰",
            "record": false
          }
        ]
      },
      {
        "slot": "마지막 연락 시점",
        "value": null,
        "state": "자료에 없음",
        "severity": "unverified",
        "said": []
      },
      {
        "slot": "접수번호",
        "value": "2017-00481",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2017-00481",
            "doc": "실종신고_접수증_2017.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "접수일시",
        "value": "2017-11-04 09:20",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2017-11-04 09:20",
            "doc": "실종신고_접수증_2017.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "죄명",
        "value": "약취유인",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "약취유인",
            "doc": "수사중지_통지서_2019.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "사건번호",
        "value": "2017형제30918",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2017형제30918",
            "doc": "수사중지_통지서_2019.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "담당 수사관",
        "value": "한상우",
        "state": "낡았을 수 있음",
        "severity": "unverified",
        "said": [
          {
            "value": "한상우",
            "doc": "수사중지_통지서_2019.jpg",
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
            "doc": "수사중지_통지서_2019.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      },
      {
        "slot": "결정일",
        "value": "2019-06-17",
        "state": "기록으로 확인",
        "severity": "verified",
        "said": [
          {
            "value": "2019-06-17",
            "doc": "수사중지_통지서_2019.jpg",
            "speaker": "**경찰서",
            "record": true
          }
        ]
      }
    ],
    "issues": [
      {
        "label": "자료끼리 어긋남",
        "severity": "conflict",
        "items": [
          {
            "text": "최종 목격 일시: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — ‘2017-11-02 21~24시’(실종신고_접수증_2017.jpg · 6줄) / ‘2017-11-01 22시~01시’(기사_2018.jpg · 3줄)",
            "how": "근거 · 실종신고_접수증_2017.jpg 6줄",
            "kind": "suspected_conflict"
          }
        ]
      },
      {
        "label": "확인되지 않음",
        "severity": "unknown",
        "items": [
          {
            "text": "‘본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
            "how": "근거 · 진술서_시장상인.jpg 3줄",
            "kind": "unrecorded_fact"
          },
          {
            "text": "‘2019년 통지서를 받은 뒤로 경찰에서 연락 온 적이 없습니다.’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17) 이후에 나온 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
            "how": "근거 · 직접 입력 1줄",
            "kind": "unrecorded_fact"
          },
          {
            "text": "‘본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17) 이후에 나온 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
            "how": "근거 · 진술서_2025.jpg 3줄",
            "kind": "unrecorded_fact"
          },
          {
            "text": "‘2025년 9월 목격 제보를 전화로 알렸지만 담당자가 바뀌었다고만 들었…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17) 이후에 나온 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
            "how": "근거 · 직접 입력 1줄",
            "kind": "unrecorded_fact"
          },
          {
            "text": "담당 수사관: 기록상 ‘한상우’(수사중지_통지서_2019.jpg · 8줄, 2019-06-17)이지만, 이후 바뀌었다는 내용이 있습니다 — ‘2025년 9월 목격 제보를 전화로 알렸지만 담당자가 바뀌었다고만 들었습니다.’(직접 입력 · 1줄, 2025-09). 현재 담당 수사관 확인이 필요합니다",
            "how": "근거 · 수사중지_통지서_2019.jpg 8줄",
            "kind": "possibly_outdated"
          }
        ]
      },
      {
        "label": "빠진 정보",
        "severity": "gap",
        "items": [
          {
            "text": "‘수사결과 통지서’(2019-06-17) 이후 기관의 진행 기록이 없습니다 (2651일 경과)",
            "how": "근거 · 수사중지_통지서_2019.jpg 1줄",
            "kind": "stage_stalled"
          },
          {
            "text": "2018-02-05 ~ 2019-06-17 사이의 기록이 없습니다 (약 1.4년)",
            "how": "근거 · 기사_2018.jpg 2줄",
            "kind": "time_gap"
          },
          {
            "text": "2019-06-18 ~ 2025-08-14 사이의 기록이 없습니다 (약 6.2년)",
            "how": "근거 · 수사중지_통지서_2019.jpg 1줄",
            "kind": "time_gap"
          }
        ]
      },
      {
        "label": "읽히지 않은 부분",
        "severity": "gap",
        "items": [
          {
            "text": "수사중지_통지서_2019.jpg에서 읽히지 않은 부분이 1곳 있습니다 (7줄). 사진을 보고 알려주세요",
            "how": "근거 · 수사중지_통지서_2019.jpg 7줄",
            "kind": "unreadable"
          }
        ]
      }
    ],
    "next_action": {
      "rule_no": 6,
      "action": "ACT-신규정보제출",
      "label": "새로 확인된 정보를 수사기관에 제출",
      "why": "진술서_2025.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
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
          "rule_no": 7,
          "action": "ACT-모순확인",
          "label": "자료끼리 어긋난 부분 확인 요청",
          "why": "진술 모순은 재수사 사유가 된다"
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
            "value": "2017형제30918",
            "from": "case_record"
          },
          {
            "label": "접수번호",
            "value": "2017-00481",
            "from": "case_record"
          },
          {
            "label": "결정 내용",
            "value": "수사중지(피의자중지)",
            "from": "case_record"
          },
          {
            "label": "결정일",
            "value": "2019-06-17",
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
            "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                "date": "2017. 11. 1.",
                "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                "level": "statement",
                "source": "기사_2018.jpg 3줄"
              },
              {
                "date": "2017. 11. 2.",
                "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                "level": "statement",
                "source": "진술서_시장상인.jpg 3줄"
              },
              {
                "date": "2017. 11. 3.",
                "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                "level": "statement",
                "source": "가족_진술서.jpg 5줄"
              },
              {
                "date": "2017. 11. 4.",
                "text": "실종신고 접수증",
                "level": "record",
                "source": "실종신고_접수증_2017.jpg 1줄"
              },
              {
                "date": "2017. 11. 10.",
                "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                "level": "statement",
                "source": "가족_진술서.jpg 6줄"
              },
              {
                "date": "2019. 6. 17.",
                "text": "수사결과 통지서",
                "level": "record",
                "source": "수사중지_통지서_2019.jpg 1줄"
              },
              {
                "date": "2025. 8. 14.",
                "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                "level": "statement",
                "source": "진술서_2025.jpg 3줄"
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
        "why": "진술서_2025.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
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
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "진술 모순은 재수사 사유가 된다"
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
              "value": "2017형제30918",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2017-00481",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2019-06-17",
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
              "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                  "date": "2017. 11. 1.",
                  "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                  "level": "statement",
                  "source": "기사_2018.jpg 3줄"
                },
                {
                  "date": "2017. 11. 2.",
                  "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                  "level": "statement",
                  "source": "진술서_시장상인.jpg 3줄"
                },
                {
                  "date": "2017. 11. 3.",
                  "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                  "level": "statement",
                  "source": "가족_진술서.jpg 5줄"
                },
                {
                  "date": "2017. 11. 4.",
                  "text": "실종신고 접수증",
                  "level": "record",
                  "source": "실종신고_접수증_2017.jpg 1줄"
                },
                {
                  "date": "2017. 11. 10.",
                  "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                  "level": "statement",
                  "source": "가족_진술서.jpg 6줄"
                },
                {
                  "date": "2019. 6. 17.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_통지서_2019.jpg 1줄"
                },
                {
                  "date": "2025. 8. 14.",
                  "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                  "level": "statement",
                  "source": "진술서_2025.jpg 3줄"
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
        "rule_no": 7,
        "action": "ACT-모순확인",
        "label": "자료끼리 어긋난 부분 확인 요청",
        "why": "최종 목격 일시: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — ‘2017-11-02 21~24시’(실종신고_접수증_2017.jpg · 6줄) / ‘2017-11-01 22시~01시’(기사_2018.jpg · 3줄)",
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
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "진술 모순은 재수사 사유가 된다"
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
              "value": "2017형제30918",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2017-00481",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2019-06-17",
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
              "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                  "date": "2017. 11. 1.",
                  "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                  "level": "statement",
                  "source": "기사_2018.jpg 3줄"
                },
                {
                  "date": "2017. 11. 2.",
                  "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                  "level": "statement",
                  "source": "진술서_시장상인.jpg 3줄"
                },
                {
                  "date": "2017. 11. 3.",
                  "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                  "level": "statement",
                  "source": "가족_진술서.jpg 5줄"
                },
                {
                  "date": "2017. 11. 4.",
                  "text": "실종신고 접수증",
                  "level": "record",
                  "source": "실종신고_접수증_2017.jpg 1줄"
                },
                {
                  "date": "2017. 11. 10.",
                  "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                  "level": "statement",
                  "source": "가족_진술서.jpg 6줄"
                },
                {
                  "date": "2019. 6. 17.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_통지서_2019.jpg 1줄"
                },
                {
                  "date": "2025. 8. 14.",
                  "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                  "level": "statement",
                  "source": "진술서_2025.jpg 3줄"
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
        "why": "‘본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
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
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "진술 모순은 재수사 사유가 된다"
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
              "value": "2017형제30918",
              "from": "case_record"
            },
            {
              "label": "접수번호",
              "value": "2017-00481",
              "from": "case_record"
            },
            {
              "label": "결정 내용",
              "value": "수사중지(피의자중지)",
              "from": "case_record"
            },
            {
              "label": "결정일",
              "value": "2019-06-17",
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
              "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                  "date": "2017. 11. 1.",
                  "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                  "level": "statement",
                  "source": "기사_2018.jpg 3줄"
                },
                {
                  "date": "2017. 11. 2.",
                  "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                  "level": "statement",
                  "source": "진술서_시장상인.jpg 3줄"
                },
                {
                  "date": "2017. 11. 3.",
                  "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                  "level": "statement",
                  "source": "가족_진술서.jpg 5줄"
                },
                {
                  "date": "2017. 11. 4.",
                  "text": "실종신고 접수증",
                  "level": "record",
                  "source": "실종신고_접수증_2017.jpg 1줄"
                },
                {
                  "date": "2017. 11. 10.",
                  "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                  "level": "statement",
                  "source": "가족_진술서.jpg 6줄"
                },
                {
                  "date": "2019. 6. 17.",
                  "text": "수사결과 통지서",
                  "level": "record",
                  "source": "수사중지_통지서_2019.jpg 1줄"
                },
                {
                  "date": "2025. 8. 14.",
                  "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                  "level": "statement",
                  "source": "진술서_2025.jpg 3줄"
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
        "why": "수사중지_통지서_2019.jpg에서 읽히지 않은 부분이 1곳 있습니다 (7줄). 사진을 보고 알려주세요",
        "rule_why": "근거 없는 주장은 판단 대상이 되지 않는다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "원본 출처나 감정 결과를 확보하는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "진술 모순은 재수사 사유가 된다"
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
        "why": "2018-02-05 ~ 2019-06-17 사이의 기록이 없습니다 (약 1.4년)",
        "rule_why": "기록 공백은 반박 여지를 남긴다",
        "due": null,
        "state": "no_submission",
        "rows": [],
        "prepare": null,
        "note": "기록이 비어 있는 기간의 자료를 모으는 단계라 수사기관에 낼 서류가 아직 없다. 자료를 확보한 뒤에는 새 정보 제출(ACT-신규정보제출) 경로를 쓴다",
        "unverified": true,
        "also": [
          {
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "진술 모순은 재수사 사유가 된다"
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
    "severity_days": {
      "critical": 7,
      "soon": 30
    },
    "outcomes": {
      "불송치": {
        "st": "경찰 불송치",
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
              "done": 1,
              "total": 3,
              "items": [
                {
                  "label": "불송치 결정 이의신청서",
                  "state": "생성가능",
                  "required": true
                },
                {
                  "label": "수사결과 통지서 (불송치 결정)",
                  "state": "미보유",
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
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "label": "담당 수사관",
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "진술서_2025.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
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
              "done": 1,
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
                  "state": "미보유",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "최종 목격 일시: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — ‘2017-11-02 21~24시’(실종신고_접수증_2017.jpg · 6줄) / ‘2017-11-01 22시~01시’(기사_2018.jpg · 3줄)",
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
              "done": 1,
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
                  "state": "미보유",
                  "required": false
                }
              ]
            },
            "note": "어긋난 부분을 자료 이름과 줄로 짚고 사실관계 확인을 요청한다(수사준칙 제25조). 누가 틀렸는지 단정하지 않는다. 본인이 한 진술은 열람·복사를 신청해 확인할 수 있다(수사준칙 제69조 제1항).",
            "unverified": true,
            "also": [
              {
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "‘본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "ACT-회신 을(를) 2026-09-19 에 냈다고 기록했지만, 접수증이 자료함에 없습니다.",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "2018-02-05 ~ 2019-06-17 사이의 기록이 없습니다 (약 1.4년)",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          }
        ],
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": []
      },
      "불기소": {
        "st": "검찰 불기소",
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
                "v": "항고장"
              },
              {
                "k": "어디에",
                "v": "불기소 처분을 한 검사가 속한 지방검찰청·지청을 거쳐 관할 고등검찰청 검사장"
              },
              {
                "k": "근거",
                "v": "검찰청법 제10조"
              }
            ],
            "prepare": {
              "done": 0,
              "total": 2,
              "items": [
                {
                  "label": "항고장",
                  "state": "생성가능",
                  "required": true
                },
                {
                  "label": "불기소 이유 통지서",
                  "state": "미보유",
                  "required": false
                }
              ]
            },
            "note": "항고는 불기소 통지를 받은 날부터 30일 이내다(검찰청법 제10조 제4항). 기간이 지났어도 중요한 증거가 새로 발견된 경우 그 사유를 소명하면 항고할 수 있다(같은 조 제7항). 검사의 기소중지·참고인중지 결정도 항고 대상이다(검찰사건사무규칙 제147조 제1항).",
            "unverified": true,
            "also": [
              {
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "submit_to": "불기소 처분을 한 검사가 속한 지방검찰청·지청을 거쳐 관할 고등검찰청 검사장",
            "form_name": "항고장",
            "draft": {
              "is_draft": true,
              "prose": null,
              "form_name": "항고장",
              "form_source": "법정 서식 없음 — 검찰청법 제10조 제1항: 서면으로 항고한다",
              "form_url": null,
              "fields": [
                {
                  "label": "사건번호",
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
                  "from": "case_record"
                },
                {
                  "label": "서식",
                  "value": "항고장",
                  "from": "knowledge_base"
                },
                {
                  "label": "제출처",
                  "value": "불기소 처분을 한 검사가 속한 지방검찰청·지청을 거쳐 관할 고등검찰청 검사장",
                  "from": "knowledge_base"
                },
                {
                  "label": "근거 법령",
                  "value": "검찰청법 제10조",
                  "from": "knowledge_base"
                }
              ],
              "unfilled": [
                {
                  "label": "담당 수사관",
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": {
              "label": "검찰 항고 기한",
              "period_days": 30
            }
          },
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "진술서_2025.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
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
              "done": 1,
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
                  "state": "미보유",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "최종 목격 일시: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — ‘2017-11-02 21~24시’(실종신고_접수증_2017.jpg · 6줄) / ‘2017-11-01 22시~01시’(기사_2018.jpg · 3줄)",
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
              "done": 1,
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
                  "state": "미보유",
                  "required": false
                }
              ]
            },
            "note": "어긋난 부분을 자료 이름과 줄로 짚고 사실관계 확인을 요청한다(수사준칙 제25조). 누가 틀렸는지 단정하지 않는다. 본인이 한 진술은 열람·복사를 신청해 확인할 수 있다(수사준칙 제69조 제1항).",
            "unverified": true,
            "also": [
              {
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "‘본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "ACT-회신 을(를) 2026-09-19 에 냈다고 기록했지만, 접수증이 자료함에 없습니다.",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "2018-02-05 ~ 2019-06-17 사이의 기록이 없습니다 (약 1.4년)",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          }
        ],
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "검찰 항고 기한",
            "period_days": 30,
            "statute": "검찰청법 제10조",
            "submit_to": "불기소 처분을 한 검사가 속한 지방검찰청 또는 지청을 거쳐 관할 고등검찰청 검사장"
          }
        ]
      },
      "항고 기각": {
        "st": "이의신청/항고 중",
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
                "v": "재정신청서"
              },
              {
                "k": "어디에",
                "v": "지방검찰청 검사장 또는 지청장"
              },
              {
                "k": "근거",
                "v": "형사소송법 제260조"
              }
            ],
            "prepare": {
              "done": 0,
              "total": 2,
              "items": [
                {
                  "label": "재정신청서",
                  "state": "생성가능",
                  "required": true
                },
                {
                  "label": "항고기각 결정 통지서",
                  "state": "미보유",
                  "required": true
                }
              ]
            },
            "note": "고소를 한 사람만 할 수 있다(형사소송법 제260조 제1항 — 고발인은 형법 제123조~제126조의 죄만).",
            "unverified": true,
            "also": [
              {
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "submit_to": "지방검찰청 검사장 또는 지청장",
            "form_name": "재정신청서",
            "draft": {
              "is_draft": true,
              "prose": null,
              "form_name": "재정신청서",
              "form_source": "법정 서식 없음 — 형사소송법 제260조 제4항: 범죄사실 및 증거 등 재정신청을 이유 있게 하는 사유를 적는다",
              "form_url": null,
              "fields": [
                {
                  "label": "사건번호",
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
                  "from": "case_record"
                },
                {
                  "label": "서식",
                  "value": "재정신청서",
                  "from": "knowledge_base"
                },
                {
                  "label": "제출처",
                  "value": "지방검찰청 검사장 또는 지청장",
                  "from": "knowledge_base"
                },
                {
                  "label": "근거 법령",
                  "value": "형사소송법 제260조",
                  "from": "knowledge_base"
                }
              ],
              "unfilled": [
                {
                  "label": "담당 수사관",
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": {
              "label": "법원 재정신청 기한",
              "period_days": 10
            }
          },
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "진술서_2025.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
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
              "done": 1,
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
                  "state": "미보유",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "최종 목격 일시: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — ‘2017-11-02 21~24시’(실종신고_접수증_2017.jpg · 6줄) / ‘2017-11-01 22시~01시’(기사_2018.jpg · 3줄)",
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
              "done": 1,
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
                  "state": "미보유",
                  "required": false
                }
              ]
            },
            "note": "어긋난 부분을 자료 이름과 줄로 짚고 사실관계 확인을 요청한다(수사준칙 제25조). 누가 틀렸는지 단정하지 않는다. 본인이 한 진술은 열람·복사를 신청해 확인할 수 있다(수사준칙 제69조 제1항).",
            "unverified": true,
            "also": [
              {
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "‘본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "ACT-회신 을(를) 2026-09-19 에 냈다고 기록했지만, 접수증이 자료함에 없습니다.",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "2018-02-05 ~ 2019-06-17 사이의 기록이 없습니다 (약 1.4년)",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          }
        ],
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "법원 재정신청 기한",
            "period_days": 10,
            "statute": "형사소송법 제260조 제3항",
            "submit_to": "지방검찰청 검사장 또는 지청장"
          }
        ]
      },
      "피의자중지": {
        "st": "피의자 중지",
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
                "v": "수사중지 결정 이의제기서"
              },
              {
                "k": "어디에",
                "v": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 송부된다)"
              },
              {
                "k": "근거",
                "v": "경찰수사규칙 제101조"
              }
            ],
            "prepare": {
              "done": 0,
              "total": 2,
              "items": [
                {
                  "label": "수사중지 결정 이의제기서",
                  "state": "생성가능",
                  "required": true
                },
                {
                  "label": "수사결과 통지서 (수사중지 결정)",
                  "state": "미보유",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "label": "담당 수사관",
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": {
              "label": "수사중지 이의제기 기한",
              "period_days": 30
            }
          },
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "진술서_2025.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
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
              "done": 1,
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
                  "state": "미보유",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "최종 목격 일시: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — ‘2017-11-02 21~24시’(실종신고_접수증_2017.jpg · 6줄) / ‘2017-11-01 22시~01시’(기사_2018.jpg · 3줄)",
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
              "done": 1,
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
                  "state": "미보유",
                  "required": false
                }
              ]
            },
            "note": "어긋난 부분을 자료 이름과 줄로 짚고 사실관계 확인을 요청한다(수사준칙 제25조). 누가 틀렸는지 단정하지 않는다. 본인이 한 진술은 열람·복사를 신청해 확인할 수 있다(수사준칙 제69조 제1항).",
            "unverified": true,
            "also": [
              {
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "‘본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "ACT-회신 을(를) 2026-09-19 에 냈다고 기록했지만, 접수증이 자료함에 없습니다.",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "2018-02-05 ~ 2019-06-17 사이의 기록이 없습니다 (약 1.4년)",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          }
        ],
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          }
        ]
      },
      "참고인중지": {
        "st": "참고인 중지",
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
                "v": "수사중지 결정 이의제기서"
              },
              {
                "k": "어디에",
                "v": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 송부된다)"
              },
              {
                "k": "근거",
                "v": "경찰수사규칙 제101조"
              }
            ],
            "prepare": {
              "done": 0,
              "total": 2,
              "items": [
                {
                  "label": "수사중지 결정 이의제기서",
                  "state": "생성가능",
                  "required": true
                },
                {
                  "label": "수사결과 통지서 (수사중지 결정)",
                  "state": "미보유",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "label": "담당 수사관",
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": {
              "label": "수사중지 이의제기 기한",
              "period_days": 30
            }
          },
          {
            "rule_no": 6,
            "action": "ACT-신규정보제출",
            "label": "새로 확인된 정보를 수사기관에 제출",
            "why": "진술서_2025.jpg 의 내용이 기록 자료에서 확인되지 않습니다",
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
              "done": 1,
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
                  "state": "미보유",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 7,
            "action": "ACT-모순확인",
            "label": "자료끼리 어긋난 부분 확인 요청",
            "why": "최종 목격 일시: 자료 사이에 차이가 있어 보이지만 판단 근거가 부족합니다 — ‘2017-11-02 21~24시’(실종신고_접수증_2017.jpg · 6줄) / ‘2017-11-01 22시~01시’(기사_2018.jpg · 3줄)",
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
              "done": 1,
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
                  "state": "미보유",
                  "required": false
                }
              ]
            },
            "note": "어긋난 부분을 자료 이름과 줄로 짚고 사실관계 확인을 요청한다(수사준칙 제25조). 누가 틀렸는지 단정하지 않는다. 본인이 한 진술은 열람·복사를 신청해 확인할 수 있다(수사준칙 제69조 제1항).",
            "unverified": true,
            "also": [
              {
                "rule_no": 6,
                "action": "ACT-신규정보제출",
                "label": "새로 확인된 정보를 수사기관에 제출",
                "why": "새 정보는 중지·종결된 절차를 되살릴 수 있다"
              },
              {
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 8,
            "action": "ACT-기록열람",
            "label": "수사 기록 열람 신청",
            "why": "‘본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…’ — 기록 자료(통지서·접수증 등)에서는 확인되지 않는 진술입니다. ‘수사결과 통지서’(2019-06-17)보다 앞선 내용입니다. 수사 기록에 반영됐는지 확인이 필요합니다",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
                  "value": "2017형제30918",
                  "from": "case_record"
                },
                {
                  "label": "접수번호",
                  "value": "2017-00481",
                  "from": "case_record"
                },
                {
                  "label": "결정 내용",
                  "value": "수사중지(피의자중지)",
                  "from": "case_record"
                },
                {
                  "label": "결정일",
                  "value": "2019-06-17",
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
                  "reason": "자료에 '한상우' 로 적혀 있지만 기록으로 확인되지 않았습니다. 확인 후 적어 주세요."
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
                      "date": "2017. 11. 1.",
                      "text": "경찰은 정씨가 지난해 11월 1일 밤 11시쯤 ○○역 인근 CCTV에 …",
                      "level": "statement",
                      "source": "기사_2018.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 2.",
                      "text": "본인은 2017. 11. 2. 22시경 ○○시 중앙시장 앞에서 정하윤을…",
                      "level": "statement",
                      "source": "진술서_시장상인.jpg 3줄"
                    },
                    {
                      "date": "2017. 11. 3.",
                      "text": "2017. 11. 3. 밤 112에 신고하였습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 5줄"
                    },
                    {
                      "date": "2017. 11. 4.",
                      "text": "실종신고 접수증",
                      "level": "record",
                      "source": "실종신고_접수증_2017.jpg 1줄"
                    },
                    {
                      "date": "2017. 11. 10.",
                      "text": "2017. 11. 10. ○○경찰서에 출석하여 참고인 조사를 받았습니다.",
                      "level": "statement",
                      "source": "가족_진술서.jpg 6줄"
                    },
                    {
                      "date": "2019. 6. 17.",
                      "text": "수사결과 통지서",
                      "level": "record",
                      "source": "수사중지_통지서_2019.jpg 1줄"
                    },
                    {
                      "date": "2025. 8. 14.",
                      "text": "본인은 2025. 8. 14. 오후 ○○시 버스터미널 대합실에서 정하윤…",
                      "level": "statement",
                      "source": "진술서_2025.jpg 3줄"
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
            },
            "due_rule": null
          },
          {
            "rule_no": 9,
            "action": "ACT-근거보완",
            "label": "주장을 뒷받침할 근거 자료 보완",
            "why": "ACT-회신 을(를) 2026-09-19 에 냈다고 기록했지만, 접수증이 자료함에 없습니다.",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          },
          {
            "rule_no": 10,
            "action": "ACT-공백보완",
            "label": "기록이 빈 기간의 자료 확보",
            "why": "2018-02-05 ~ 2019-06-17 사이의 기록이 없습니다 (약 1.4년)",
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
                "rule_no": 7,
                "action": "ACT-모순확인",
                "label": "자료끼리 어긋난 부분 확인 요청",
                "why": "진술 모순은 재수사 사유가 된다"
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
            "draft": null,
            "due_rule": null
          }
        ],
        "next": "기한 안에 결정에 대한 불복 절차 진행",
        "next_key": "ACT-불복기한",
        "deadlines": [
          {
            "label": "수사중지 이의제기 기한",
            "period_days": 30,
            "statute": "경찰수사규칙 제101조 (검사와 사법경찰관의 상호협력과 일반적 수사준칙에 관한 규정 제54조 제1항)",
            "submit_to": "해당 사법경찰관이 소속된 바로 위 상급경찰관서의 장 (소속 경찰관서에 제출하면 상급관서로 송부된다)"
          }
        ]
      },
      "기소": {
        "st": "재판 진행 중",
        "actions": [
          {
            "rule_no": 0,
            "action": "ACT-재판단계",
            "label": "재판 단계 — 이 서비스의 안내 범위 밖",
            "why": "재판이 시작되면 절차는 법원이 진행한다. 수사기관에 새 정보를 내라고 안내하면 엉뚱한 곳에 내게 된다",
            "rule_why": "재판이 시작되면 절차는 법원이 진행한다. 수사기관에 새 정보를 내라고 안내하면 엉뚱한 곳에 내게 된다",
            "due": null,
            "state": "no_submission",
            "rows": [],
            "prepare": null,
            "note": "재판이 시작된 사건입니다. 이제 절차는 법원이 진행해 이 서비스의 안내 범위 밖입니다 — 수사기관에 새 정보를 내는 대신 법원 절차를 쓰세요. 피해자는 재판장에게 공판기록 열람·등사를 신청할 수 있고(형사소송법 제294조의4), 법원에 증인으로 진술하겠다고 신청할 수 있습니다(제294조의2).",
            "unverified": true,
            "also": [],
            "submit_to": null,
            "form_name": null,
            "draft": null,
            "due_rule": null
          }
        ],
        "next": "재판 단계 — 이 서비스의 안내 범위 밖",
        "next_key": "ACT-재판단계",
        "deadlines": []
      }
    },
    "guide": true
  }
];
