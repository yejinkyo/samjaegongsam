/* 타래 화면 렌더링.
 *
 * 데이터는 data/cases.js 의 window.TARAE_CASES 에서만 읽는다(action-engine/tools/export_web.py 가 만든다).
 * 화면 문장을 여기서 지어내지 않는다 — 비어 있는 값은 비어 있다고 보여준다.
 * 사용자·엔진 문자열이 섞이므로 innerHTML 을 쓰지 않고 textContent 로만 넣는다.
 */
(function () {
  "use strict";

  var CASES = window.TARAE_CASES || [];

  function h(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        var value = attrs[key];
        if (value == null || value === false) return;
        if (key === "class") node.className = value;
        else if (key === "text") node.textContent = value;
        else if (key.indexOf("on") === 0) node.addEventListener(key.slice(2), value);
        else node.setAttribute(key, value === true ? "" : value);
      });
    }
    (children || []).forEach(function (child) {
      if (child == null) return;
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  function icon(name, size) {
    return h("span", { class: "icon" + (size ? " icon--" + size : ""), "aria-hidden": "true" }, [
      h("img", { src: "assets/icons/" + name + ".svg", alt: "", width: "24", height: "24" }),
    ]);
  }

  function caseHref(id) { return "case.html?id=" + encodeURIComponent(id); }

  // ── 공통 ────────────────────────────────────────────────
  function nav() {
    return h("header", { class: "nav" }, [
      // 브랜드를 누르면 시작 화면으로 나간다. 사건 목록은 옆의 '내 사건'
      h("a", { class: "nav__brand", href: "index.html" }, [
        h("span", { class: "nav__logo", "aria-hidden": "true" }),
        h("span", { class: "nav__name t-heading c-primary", text: "타래" }),
      ]),
      h("nav", { class: "nav__right", "aria-label": "주 메뉴" }, [
        h("a", { class: "t-body-m-strong c-primary", href: "cases.html", text: "내 사건" }),
        h("a", { class: "t-body-m c-secondary", href: "#", text: "도움말" }),
        h("span", { class: "nav__avatar", "aria-label": "내 정보" }, [h("span", { class: "t-label c-brand", text: "나" })]),
      ]),
    ]);
  }

  function backLink() {
    return h("a", { class: "back", href: "cases.html" }, [icon("arrow-left", 20), h("span", { class: "t-body-m c-secondary", text: "내 사건" })]);
  }

  function track(stages, fixed) {
    return h("div", { class: "track" + (fixed ? " track--fixed" : ""), role: "list", "aria-label": "진행 단계" },
      stages.map(function (s) {
        return h("div", { class: "step step--" + s.state, role: "listitem", "aria-current": s.state === "current" ? "step" : null }, [
          h("div", { class: "step__rail", "aria-hidden": "true" }, [h("span", { class: "step__line" }), h("span", { class: "step__dot" }), h("span", { class: "step__line" })]),
          h("span", { class: "step__label", text: s.label }),
        ]);
      }));
  }

  function badge(kind, label) {
    return h("span", { class: "badge badge--" + kind + " t-caption", text: label });
  }

  // ── 01 내 사건 ──────────────────────────────────────────

  /** 폴더 앞면에 적는 한 줄. 엔진이 준 단계 값에서만 만든다. */
  function caseStatus(c) {
    var current = (c.stages || []).filter(function (s) { return s.state === "current"; })[0];
    if (!current) return "진행 상태 확인 필요";
    // 마지막 단계에 멈춘 중지 사건은 '결과 단계'가 아니라 멈춰 있다는 것이 핵심이다
    if (current.label === "결과" && c.type_label.indexOf("중지") >= 0) return "중지";
    return current.label + " 단계";
  }

  /** 목록에서 그 사건이 가졌던 폴더 색. 상세 화면도 같은 색을 써서 '그 폴더를 열었다'가 보이게 한다. */
  function toneOf(c) {
    var i = CASES.indexOf(c);
    return ((i < 0 ? 0 : i) % 3) + 1;
  }

  function folder(c, tone) {
    var next = c.next_action;
    var due = next && next.due;

    return h("a", { class: "folder folder--tone" + tone, href: caseHref(c.id) }, [
      h("span", { class: "folder__tab", "aria-hidden": "true" }),
      h("span", { class: "folder__sheet", "aria-hidden": "true" }),
      h("div", { class: "folder__body" }, [
        // 기한은 놓치면 되돌릴 수 없어서 마우스를 올리기 전에도 보이게 둔다
        due ? h("span", { class: "folder__due t-label", text: due.label }) : null,
        h("p", { class: "folder__title t-title", text: c.title }),
        h("p", { class: "folder__status t-body-l", text: caseStatus(c) }),
        h("div", { class: "folder__peek" }, [
          h("p", { class: "folder__meta t-body-s", text: "확인 필요 " + c.need_count + " · 자료 " + c.doc_count + "개" }),
          h("p", { class: "folder__next t-body-m-strong", text: next ? next.label : "판단할 수 있는 행동이 아직 없어요" }),
          h("span", { class: "folder__more t-body-m-strong" }, [
            h("span", { text: "자세히 보기" }),
            icon("chevron-right", 20),
          ]),
        ]),
      ]),
    ]);
  }

  function renderHome(root) {
    var grid = h("div", { class: "folder-grid" });
    CASES.forEach(function (c) { grid.appendChild(folder(c, toneOf(c))); });

    grid.appendChild(h("a", { class: "folder folder--new", href: "new.html" }, [
      h("span", { class: "folder__tab", "aria-hidden": "true" }),
      h("div", { class: "folder__body" }, [
        h("span", { class: "circle-56" }, [icon("plus")]),
        h("p", { class: "t-heading c-secondary", text: "사건 등록" }),
        h("p", { class: "t-body-s c-tertiary", text: "유형을 고르고 자료를 올리면 정리가 시작돼요" }),
      ]),
    ]));

    root.appendChild(h("main", { class: "page page--home" }, [
      // 새 사건 등록은 그리드 끝의 점선 폴더가 맡는다 — 머리말에 같은 버튼을 두지 않는다
      h("div", { class: "page-head" }, [
        h("div", { class: "page-head__title" }, [
          h("h1", { class: "t-display c-primary", text: "내 사건" }),
          h("p", { class: "t-body-l c-secondary", text: "사건 카드를 선택하면 정리된 타임라인을 볼 수 있어요." }),
        ]),
      ]),
      grid,
    ]));
  }

  // ── 02 새 사건 등록 ─────────────────────────────────────
  var CATEGORIES = ["중고거래 사기", "온라인 괴롭힘", "폭행 · 상해", "금전 피해", "실종 · 미제", "수사중지"];

  function fileKind(name) {
    var ext = (name.split(".").pop() || "").toLowerCase();
    if (ext === "pdf") return "PDF";
    if (["png", "jpg", "jpeg", "heic", "webp", "gif"].indexOf(ext) >= 0) return "IMG";
    if (["m4a", "mp3", "wav", "aac"].indexOf(ext) >= 0) return "음성";
    return "문서";
  }

  function renderNew(root) {
    var files = [];
    var list = h("div", { class: "file-list" });
    var count = h("span", { class: "t-label c-brand", text: "0" });

    function chip(label, unsure) {
      var node = h("button", { type: "button", class: "chip" + (unsure ? " chip--unsure" : ""), "aria-pressed": "false", text: label });
      node.addEventListener("click", function () {
        chips.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
        node.setAttribute("aria-pressed", "true");
      });
      return node;
    }
    var chips = h("div", { class: "chips", role: "group", "aria-label": "사건 유형" },
      CATEGORIES.map(function (c) { return chip(c, false); }).concat([chip("잘 모르겠어요", true)]));
    chips.firstChild.setAttribute("aria-pressed", "true");

    function drawList() {
      list.textContent = "";
      count.textContent = String(files.length);
      if (!files.length) {
        list.appendChild(h("p", { class: "empty-files t-body-s c-tertiary", text: "아직 올린 자료가 없어요. 사진 한 장부터 시작해도 괜찮아요." }));
        return;
      }
      files.forEach(function (f) {
        list.appendChild(h("div", { class: "file-row" }, [
          h("span", { class: "file-row__kind t-caption", text: f.kind }),
          h("div", { class: "file-row__texts" }, [
            h("p", { class: "t-body-m-strong c-primary", text: f.name, title: f.name }),
            h("p", { class: "t-body-s c-tertiary", text: f.meta }),
          ]),
          f.link ? badge("unverified", "언제인가요?") : badge("unverified", "날짜 읽기 전"),
        ]));
      });
    }

    var picker = h("input", { type: "file", multiple: true, accept: "image/*,application/pdf,audio/*", hidden: true });
    var camera = h("input", { type: "file", accept: "image/*", capture: "environment", hidden: true });
    function addFiles(fileList) {
      Array.prototype.forEach.call(fileList, function (f) {
        files.push({ kind: fileKind(f.name), name: f.name, meta: "방금 추가 · 정리를 시작하면 날짜를 읽어요" });
      });
      drawList();
    }
    picker.addEventListener("change", function () { addFiles(picker.files); picker.value = ""; });
    camera.addEventListener("change", function () { addFiles(camera.files); camera.value = ""; });

    var dropzone = h("div", { class: "dropzone" }, [
      h("span", { class: "circle-56" }, [icon("upload")]),
      h("p", { class: "t-heading c-primary", text: "여기에 끌어다 놓거나, 휴대폰으로 찍어 올려주세요" }),
      h("p", { class: "dropzone__hint t-body-s c-tertiary", text: "이미지 · PDF · 음성 · 문서  |  여러 장을 한 번에 올릴 수 있어요" }),
      h("div", { class: "dropzone__actions" }, [
        h("button", { type: "button", class: "btn btn--primary t-body-m-strong", text: "파일 선택", onclick: function () { picker.click(); } }),
        h("button", { type: "button", class: "btn btn--secondary t-body-m-strong", text: "사진 찍기", onclick: function () { camera.click(); } }),
      ]),
      picker, camera,
    ]);
    ["dragenter", "dragover"].forEach(function (type) {
      dropzone.addEventListener(type, function (e) { e.preventDefault(); dropzone.classList.add("is-over"); });
    });
    ["dragleave", "drop"].forEach(function (type) {
      dropzone.addEventListener(type, function () { dropzone.classList.remove("is-over"); });
    });
    dropzone.addEventListener("drop", function (e) { e.preventDefault(); addFiles(e.dataTransfer.files); });

    var url = h("input", { type: "url", placeholder: "글 주소 붙여넣기 (삭제된 글도 찾아봅니다)", "aria-label": "글 주소" });
    function addUrl() {
      var value = url.value.trim();
      if (!value) return;
      files.push({ kind: "LINK", name: value, meta: "글 주소 · 올린 날짜를 알려주세요", link: true });
      url.value = "";
      drawList();
    }
    url.addEventListener("keydown", function (e) { if (e.key === "Enter") addUrl(); });

    drawList();
    // 빈 서류철을 하나 새로 만들어 채우는 화면 — 목록의 점선 폴더가 여기서 이어진다
    var folderBody = h("div", { class: "new-folder__body" }, [
      h("div", { class: "page-head page-head--stack" }, [
        h("h1", { class: "t-display c-primary", text: "새 사건 등록" }),
        h("p", { class: "t-body-l c-secondary", text: "사건 유형을 고르고 가진 자료를 올려주세요. 자료가 적어도 시작할 수 있어요." }),
      ]),
      h("section", { class: "card section", "aria-labelledby": "s1" }, [
        h("div", { class: "section__head" }, [h("span", { class: "section__num t-label", text: "1" }), h("h2", { id: "s1", class: "t-heading c-primary", text: "어떤 일에 가까운가요?" })]),
        chips,
        h("p", { class: "t-body-s c-tertiary", text: "유형에 따라 확인할 항목과 다음 행동이 달라져요. 잘 모르겠다면 자료를 보고 제안해 드려요." }),
      ]),
      h("section", { class: "card section", "aria-labelledby": "s2" }, [
        h("div", { class: "section__head" }, [
          h("span", { class: "section__num t-label", text: "2" }),
          h("h2", { id: "s2", class: "t-heading c-primary", text: "가진 자료를 올려주세요" }),
          h("span", { class: "t-body-s c-tertiary", text: "캡처 · 사진 · 접수증 무엇이든" }),
        ]),
        dropzone,
        h("div", { class: "url-row" }, [
          h("label", { class: "input" }, [icon("link", 20), url]),
          h("button", { type: "button", class: "btn btn--secondary t-body-m-strong", text: "추가", onclick: addUrl }),
        ]),
        h("div", { class: "list-head" }, [h("span", { class: "t-label c-secondary", text: "올린 자료" }), count]),
        list,
        h("p", { class: "note t-body-s c-secondary", text: "날짜가 정리의 뼈대가 됩니다. 날짜를 모르는 자료는 “언제인가요?”를 눌러 알려주세요." }),
        h("button", { type: "button", class: "add-event t-body-m-strong c-brand", text: "+  기억나는 내용을 직접 적기 (선택)", style: "padding:0" }),
      ]),
      h("div", { class: "cta" }, [
        // 서버가 없어 올린 파일을 실제로 정리하지 않는다. 예시 사건의 결과 화면으로 이동한다.
        h("a", { class: "btn btn--primary t-body-m-strong", href: CASES.length ? caseHref(CASES[0].id) : "cases.html", text: "정리 시작하기" }),
        h("a", { class: "btn btn--secondary t-body-m-strong", href: "cases.html", text: "자료는 나중에 더 추가할게요" }),
      ]),
    ]);

    root.appendChild(h("main", { class: "page page--new" }, [
      backLink(),
      h("div", { class: "new-folder" }, [
        h("span", { class: "new-folder__tab" }, [h("span", { class: "t-label c-tertiary", text: "새 서류철" })]),
        folderBody,
      ]),
    ]));
  }

  // ── 03 사건 상세 ────────────────────────────────────────

  /** 팝업. 자료 목록·행동 설명처럼 평소엔 접어 두는 것을 담는다. */
  function openModal(title, body) {
    // 닫힌 팝업이 남아 있으면 먼저 치운다 — close 이벤트가 늦게 오는 브라우저가 있다
    document.querySelectorAll("dialog.modal").forEach(function (old) { old.remove(); });

    var dialog = h("dialog", { class: "modal" }, [
      h("div", { class: "modal__head" }, [
        h("h2", { class: "t-heading c-primary", text: title }),
        h("button", { type: "button", class: "modal__close", "aria-label": "닫기", text: "✕" }),
      ]),
      h("div", { class: "modal__body" }, [body]),
    ]);
    dialog.querySelector(".modal__close").addEventListener("click", function () { dialog.close(); });
    // 바깥을 누르면 닫는다
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog) dialog.close();
    });
    dialog.addEventListener("close", function () { dialog.remove(); });
    document.body.appendChild(dialog);
    dialog.showModal();
  }

  /** '06/01 13~16시경' 처럼 두 줄로 오던 시각을 날짜와 시각으로 가른다.
      사건이 여러 해에 걸치면 엔진이 '2021.05.25 14:20' 처럼 연도까지 준다. */
  function splitTime(text) {
    var clean = String(text || "").replace(/\s+/g, " ").trim();
    var m = clean.match(/^(\d{4}\.\d{2}\.\d{2}|\d{2}\/\d{2})\s*(.*)$/);
    return m ? { day: m[1], time: m[2] } : { day: clean, time: "" };
  }

  // 뜻이 하나인 색만 위에 적는다. 노란색은 줄마다 이유가 조금씩 달라 그 자리에 적는다
  // (마우스를 올려야 보이는 설명은 손가락으로 쓰는 사람이 못 본다).
  var KIND_LEGEND = [
    ["verified", "확인완료"],
    ["mine", "내가 적음"],
  ];

  function timelineCard(c) {
    var wrap = h("div", { class: "card tl" });
    var rows = c.timeline;
    var lastEvent = -1;
    rows.forEach(function (row, i) { if (row.type === "event") lastEvent = i; });

    var used = {};
    rows.forEach(function (row) { if (row.type === "event") used[row.kind] = true; });
    wrap.appendChild(h("div", { class: "tl__legend" }, KIND_LEGEND.filter(function (k) { return used[k[0]]; }).map(function (k) {
      return h("span", { class: "tl__legend-item" }, [
        h("span", { class: "tl__dot tl__dot--" + k[0], "aria-hidden": "true" }),
        h("span", { text: k[1] }),
      ]);
    })));

    var lastDay = null;
    rows.forEach(function (row, i) {
      if (row.type === "gap") {
        lastDay = null;
        wrap.appendChild(h("div", { class: "tl__gap" }, [
          h("span", { class: "t-label", text: row.range }),
          h("span", { class: "t-body-s", text: row.text }),
        ]));
        return;
      }

      var t = splitTime(row.time);
      var sameDay = t.day === lastDay;
      lastDay = t.day;

      // 뜻이 있는 것만 뱃지로 남긴다 — 나머지는 점 색과 작은 글씨가 말해 준다
      var flags = [];
      if (row.conflict) flags.push(badge("conflict", "불일치"));
      if (row.needs_date) flags.push(badge("unverified", "날짜 확인 필요"));

      wrap.appendChild(h("div", { class: "tl__row" + (row.conflict ? " tl__row--flag" : "") + (i === lastEvent ? " tl__row--last" : "") }, [
        h("div", { class: "tl__when" }, [
          h("span", { class: "tl__day t-label" + (sameDay ? " tl__day--same" : ""), text: sameDay ? "" : t.day }),
          h("span", { class: "tl__time t-caption", text: t.time }),
        ]),
        h("div", { class: "tl__rail", "aria-hidden": "true" }, [
          h("span", { class: "tl__dot tl__dot--" + row.kind }),
          h("span", { class: "tl__line" }),
        ]),
        h("div", { class: "tl__body" }, [
          h("p", { class: "tl__title", text: row.title }),
          h("div", { class: "tl__meta" }, [
            // 기록으로 확인되지 않은 줄만 왜 그런지 적는다
            row.kind === "claim" ? h("span", { class: "tl__kind", text: row.badge }) : null,
            h("span", { class: "tl__source", text: row.source }),
          ].concat(flags)),
        ]),
      ]));
    });

    wrap.appendChild(h("button", { type: "button", class: "tl__add t-body-m-strong c-brand", text: "+  기억나는 일을 직접 추가" }));
    return wrap;
  }

  /** 인물 · 관계 — 사건을 뿌리로 두고 갈래마다 뻗는 나무로 그린다. */
  function peopleCard(c) {
    var groups = c.people || [];
    if (!groups.length) return h("div", { class: "card tab-empty" }, [h("p", { class: "t-body-m c-tertiary", text: "자료에서 찾은 인물이 아직 없어요." })]);

    var branches = h("ul", { class: "tree__branches" }, groups.map(function (g) {
      var leaves = h("ul", { class: "tree__leaves" }, g.items.map(function (p) {
        var node = h("div", { class: "tnode" }, [
          h("div", { class: "tnode__head" }, [h("span", { class: "tnode__name", text: p.name })].concat(
            p.roles.map(function (r) { return h("span", { class: "tnode__role", text: r }); }))),
        ]);
        if (p.docs.length) {
          node.appendChild(h("p", { class: "tnode__docs", text: p.docs.length + "개 자료에 나옴" }));
        }
        // 엔진이 합치지 못하고 남긴 링크 — 단정하지 않는다
        p.same_as.forEach(function (link) {
          node.appendChild(h("p", { class: "tnode__same" }, [
            h("span", { class: "tnode__same-mark", text: "≈" }),
            h("span", { text: link.name + " 과 같은 대상일 수 있음 — " + link.reason }),
          ]));
        });
        return h("li", { class: "tree__leaf" }, [node]);
      }));

      return h("li", { class: "tree__branch" }, [
        h("span", { class: "tree__group" }, [
          h("span", { text: g.label }),
          h("span", { class: "tree__group-count", text: String(g.items.length) }),
        ]),
        leaves,
      ]);
    }));

    return h("div", { class: "card tree" }, [
      h("div", { class: "tree__rootwrap" }, [h("span", { class: "tree__root", text: c.title })]),
      branches,
    ]);
  }

  var SLOT_ORDER = { conflict: 0, unverified: 1, verified: 2 };

  /** 주장 대조 — 볼 것이 있는 항목을 위로 올리고, 자료마다 적은 값을 나란히 놓는다. */
  function slotsCard(c) {
    function rank(row) { return row.severity in SLOT_ORDER ? SLOT_ORDER[row.severity] : 3; }
    var rows = (c.slots || []).slice().sort(function (a, b) { return rank(a) - rank(b); });
    if (!rows.length) return h("div", { class: "card tab-empty" }, [h("p", { class: "t-body-m c-tertiary", text: "비교할 항목이 아직 없어요." })]);

    var wrap = h("div", { class: "card slots" }, [
      h("p", { class: "slots__lead", text: "같은 항목을 자료마다 뭐라고 적었는지 나란히 놓았어요. 확인이 필요한 항목이 위에 옵니다." }),
    ]);

    rows.forEach(function (row) {
      var item = h("section", { class: "slot slot--" + row.severity }, [
        h("div", { class: "slot__head" }, [
          h("span", { class: "slot__name", text: row.slot }),
          h("span", { class: "slot__state", text: row.state }),
        ]),
      ]);

      if (!row.said.length) {
        item.appendChild(h("p", { class: "slot__empty", text: "이 항목을 적은 자료가 없어요." }));
      } else {
        row.said.forEach(function (s) {
          var chosen = row.value !== null && s.value === row.value;
          item.appendChild(h("div", { class: "slot__said" + (chosen ? " slot__said--chosen" : "") }, [
            h("div", { class: "slot__valwrap" }, [
              h("span", { class: "slot__value", text: s.value }),
              chosen ? h("span", { class: "slot__pick", text: "대표" }) : null,
            ]),
            h("p", { class: "slot__from" }, [
              h("span", { class: "slot__src slot__src--" + (s.record ? "record" : "said"), text: s.record ? "기록" : "말" }),
              h("span", { text: (s.speaker || "화자 미상") + " · " + s.doc }),
            ]),
          ]));
        });
      }
      wrap.appendChild(item);
    });
    return wrap;
  }

  function nextActionCard(next) {
    if (!next) return null;
    var details;
    if (next.state === "filled") {
      details = h("div", { class: "next-action__details" }, next.rows.map(function (r) {
        return h("div", { class: "next-action__row" }, [
          h("span", { class: "next-action__key t-caption", text: r.k }),
          h("span", { class: "next-action__val t-body-s", text: r.v }),
        ]);
      }));
      if (next.prepare) {
        details.appendChild(h("div", { class: "next-action__row" }, [
          h("span", { class: "next-action__key t-caption", text: "준비물" }),
          h("div", { class: "next-action__val" }, [
            h("span", { class: "t-body-s", text: next.prepare.done + " / " + next.prepare.total + " 확보" }),
            h("ul", { class: "next-action__prepare t-body-s" }, next.prepare.items.map(function (it) {
              var mark = it.state === "보유" ? "✓ " : "· ";
              return h("li", { text: mark + it.label + " — " + it.state + (it.required ? " (필수)" : "") });
            })),
          ]),
        ]));
      }
    } else {
      var message = next.state === "no_submission"
        ? next.note
        : "무엇을·어디에·어떻게·언제까지는 검수된 절차 데이터에서만 안내해요. 이 행동의 절차는 아직 확인 중이에요.";
      details = h("div", { class: "next-action__details" }, [h("p", { class: "t-body-s", text: message })]);
    }

    // 자세한 것은 평소엔 접어 두고 팝업에서만 보여 준다 — 카드에는 할 일만 크게 남긴다
    function detailBody() {
      var body = h("div", { class: "na-detail" }, [details]);
      if (next.state === "filled" && next.note) {
        body.appendChild(h("p", { class: "t-body-s c-secondary", text: next.note }));
      }
      body.appendChild(h("p", { class: "na-detail__why t-body-m c-secondary", text: "왜 필요한가요? " + next.why }));
      if (next.also.length) {
        body.appendChild(h("p", { class: "t-label c-secondary na-detail__also-label", text: "함께 볼 것" }));
        body.appendChild(h("ul", { class: "na-detail__also t-body-s c-secondary" }, next.also.map(function (a) {
          return h("li", { text: a.label + " — " + a.why });
        })));
      }
      return body;
    }

    var more = h("button", { type: "button", class: "na__more t-body-m-strong", text: "자세히 보기" });
    more.addEventListener("click", function () { openModal(next.label, detailBody()); });

    return h("section", { class: "next-action", "aria-labelledby": "na-title" }, [
      h("div", { class: "next-action__head" }, [
        h("span", { class: "t-label", text: "다음 행동" }),
        next.due
          ? h("span", { class: "na__due t-label", text: next.due.label })
          : next.unverified ? h("span", { class: "t-caption", text: "검수 전 안내" }) : null,
      ]),
      h("h2", { id: "na-title", class: "na__title", text: next.label }),
      more,
    ]);
  }

  /** 평소엔 버튼 한 줄로 접혀 있고, 누르면 아래로 펼쳐진다. */
  function issuesCard(c) {
    var list = h("div", { class: "issues__list", hidden: true });
    c.issues.forEach(function (g) {
      list.appendChild(h("p", { class: "issue-group__head t-label sev-" + g.severity }, [
        h("span", { class: "issue-group__dot" }),
        h("span", { text: g.label }),
        h("span", { class: "issue-group__count", text: String(g.items.length) }),
      ]));
      g.items.forEach(function (it) {
        list.appendChild(h("div", { class: "issue issue--" + g.severity }, [
          h("p", { class: "issue__text", text: it.text }),
          it.how ? h("p", { class: "issue__how", text: it.how }) : null,
        ]));
      });
    });

    var toggle = h("button", { type: "button", class: "issues__toggle", "aria-expanded": "false" }, [
      h("span", { class: "issues__mark", "aria-hidden": "true", text: "!" }),
      h("span", { class: "issues__label", text: "확인이 필요해요" }),
      h("span", { class: "issues__count", text: String(c.need_count) }),
      h("span", { class: "issues__chev", "aria-hidden": "true" }),
    ]);
    toggle.addEventListener("click", function () {
      var open = list.hidden;
      list.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
    });

    return h("section", { class: "issues" }, [
      toggle,
      list,
      h("button", { type: "button", class: "issues__ask t-body-m-strong", text: "전문가에게 물어볼 질문 만들기" }),
    ]);
  }

  function askButton() {
    return h("button", { type: "button", class: "issues__ask", text: "전문가에게 물어볼 질문 만들기" });
  }

  /** 자료는 목록으로 늘어놓지 않고 버튼 뒤에 둔다. */
  function sourcesBar(c, vertical) {
    var open = h("button", { type: "button", class: "srcbar__btn" }, [
      h("span", { text: "첨부한 자료" }),
      h("span", { class: "srcbar__count", text: String(c.sources.length) }),
    ]);
    open.addEventListener("click", function () {
      openModal("첨부한 자료 " + c.sources.length + "개", h("ul", { class: "srclist" }, c.sources.map(function (s) {
        return h("li", { class: "srclist__item" }, [
          h("span", { class: "srclist__kind t-caption", text: s.kind }),
          h("span", { class: "t-body-m c-primary", text: s.name }),
        ]);
      })));
    });

    return h("div", { class: "srcbar" + (vertical ? " srcbar--stack" : "") }, [
      h("a", { class: "srcbar__btn srcbar__btn--add", href: "new.html" }, [h("span", { text: "+  자료 추가하기" })]),
      open,
    ]);
  }

  function renderCase(root) {
    var id = new URLSearchParams(location.search).get("id");
    var c = CASES.filter(function (x) { return x.id === id; })[0] || CASES[0];
    if (!c) {
      root.appendChild(h("main", { class: "page page--case" }, [backLink(), h("p", { class: "t-body-l", text: "사건을 찾지 못했어요." })]));
      return;
    }
    document.title = c.title + " · 타래";

    var panel = h("div", { role: "tabpanel", id: "panel" }, [timelineCard(c)]);
    var rail = h("aside", { class: "rail" });

    // 다음 행동·확인이 필요해요는 타임라인에서만 본다. 인물·주장 탭에서는
    // 그 화면에서 실제로 쓰는 것(자료 · 전문가 질문)만 옆에 둔다.
    function fillSide(index) {
      rail.textContent = "";
      // 자료는 어느 탭에서나 같은 자리(맨 위)에 둔다
      rail.appendChild(sourcesBar(c, true));
      if (index === 0) {
        rail.appendChild(nextActionCard(c.next_action));
        rail.appendChild(issuesCard(c));
      } else {
        rail.appendChild(askButton());
      }
    }

    var tabNames = ["타임라인", "인물 · 관계", "주장 대조"];
    var tabs = h("div", { class: "tabs", role: "tablist" }, tabNames.map(function (name, i) {
      var tab = h("button", { type: "button", class: "tab", role: "tab", "aria-selected": i === 0 ? "true" : "false", "aria-controls": "panel", text: name });
      tab.addEventListener("click", function () {
        tabs.querySelectorAll(".tab").forEach(function (t) { t.setAttribute("aria-selected", "false"); });
        tab.setAttribute("aria-selected", "true");
        panel.textContent = "";
        panel.appendChild(i === 0 ? timelineCard(c) : i === 1 ? peopleCard(c) : slotsCard(c));
        fillSide(i);
      });
      return tab;
    }));
    fillSide(0);

    root.appendChild(h("div", { class: "disclaimer" }, [
      icon("info", 18),
      h("p", { class: "t-body-s c-secondary", text: "타래는 범인이나 사건의 진실을 판단하지 않습니다. 지금 자료로 확인되는 것과 아직 확인되지 않은 것을 나누어 보여드립니다." }),
    ]));
    root.appendChild(h("main", { class: "page page--case" }, [
      backLink(),
      // 목록에서 고른 폴더를 펼친 화면 — 탭과 색을 그대로 물려받는다
      h("section", { class: "case-folder folder--tone" + toneOf(c) }, [
        h("span", { class: "case-folder__tab" }, [h("span", { class: "t-label", text: c.type_label })]),
        h("div", { class: "case-folder__body" }, [
          h("div", { class: "case-head__info" }, [
            h("div", { class: "case-head__tags" }, [
              h("span", { class: "t-caption case-folder__dim", text: "기준일 " + c.as_of }),
              // 기한은 폴더 앞면에서와 같이 항상 보이게 둔다
              c.next_action && c.next_action.due
                ? h("span", { class: "case-folder__due t-label", text: c.next_action.due.label })
                : null,
            ]),
            h("h1", { class: "t-display", text: c.title }),
            h("p", { class: "case-head__meta t-body-m case-folder__dim", text: c.period + "  ·  자료 " + c.doc_count + "개  ·  확인 필요 " + c.need_count }),
          ]),
          h("div", { class: "case-head__progress" }, [
            h("span", { class: "t-caption case-folder__dim", text: "진행 단계" }),
            track(c.stages, true),
          ]),
        ]),
      ]),
      tabs,
      h("div", { class: "columns" }, [
        h("div", { class: "main" }, [panel]),
        rail,
      ]),
    ]));
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.getElementById("app");
    root.appendChild(nav());
    var page = document.body.getAttribute("data-page");
    if (page === "home") renderHome(root);
    else if (page === "new") renderNew(root);
    else if (page === "case") renderCase(root);
  });
})();
