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

  // 사건 화면이 켜져 있으면 자료 추가를 그 화면이 맡는다. 없으면 새 사건 등록으로 보낸다.
  var addFilesHandler = null;

  /** 버튼에 붙는 작은 메뉴. 바깥을 누르거나 Esc 를 누르면 닫힌다. */
  function dropdown(trigger, items) {
    var menu = h("div", { class: "menu", hidden: true }, items.map(function (it) {
      if (it.href) return h("a", { class: "menu__item", href: it.href, text: it.label });
      var button = h("button", { type: "button", class: "menu__item" + (it.danger ? " menu__item--danger" : ""), text: it.label });
      button.addEventListener("click", function () { close(); it.onClick(); });
      return button;
    }));

    function close() {
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", onOutside, true);
      document.removeEventListener("keydown", onKey);
    }
    function onOutside(e) { if (!wrap.contains(e.target)) close(); }
    function onKey(e) { if (e.key === "Escape") close(); }

    trigger.setAttribute("aria-expanded", "false");
    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      if (!menu.hidden) return close();
      menu.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      document.addEventListener("click", onOutside, true);
      document.addEventListener("keydown", onKey);
    });

    var wrap = h("div", { class: "menu-wrap" }, [trigger, menu]);
    return wrap;
  }

  /** 자료 고르기 — 서버가 없어 파일을 보내지는 않는다. 고른 것을 화면에만 더한다. */
  function pickFiles(onPicked) {
    var input = h("input", { type: "file", multiple: true, accept: "image/*,application/pdf,audio/*", hidden: true });
    input.addEventListener("change", function () {
      var picked = Array.prototype.map.call(input.files, function (f) {
        return { kind: fileKind(f.name), name: f.name, isNew: true };
      });
      input.remove();
      if (picked.length) onPicked(picked);
    });
    document.body.appendChild(input);
    input.click();
  }

  function helpModal() {
    function block(title, lines) {
      return h("section", { class: "help__block" }, [
        h("h3", { class: "help__title", text: title }),
      ].concat(lines.map(function (t) { return h("p", { class: "help__text", text: t }); })));
    }
    openModal("타래는 무엇을 하나요?", h("div", { class: "help" }, [
      h("section", { class: "help__block help__how" }, [
        h("h3", { class: "help__title", text: "이렇게 쓰세요" }),
        h("ol", { class: "help__steps" }, [
          h("li", { text: "사건을 등록하고 가진 자료를 사진으로 올려요. 접수증 · 통지서 · 문자 캡처 · 손으로 쓴 메모 무엇이든 괜찮아요." }),
          h("li", { text: "타임라인에서 언제 무슨 일이 있었는지 확인해요. 줄 옆 '자세히'를 누르면 원문과 어느 자료에서 왔는지가 나와요." }),
          h("li", { text: "'확인이 필요해요'를 펼쳐 어긋난 것 · 아직 확인되지 않은 것 · 빠진 것을 봐요." }),
          h("li", { text: "'다음 행동'에서 지금 할 일 하나를 확인해요. 기한이 있으면 남은 날짜가 함께 떠요." }),
          h("li", { text: "막히면 '전문가에게 물어볼 질문 만들기'를 눌러 상담에 가져갈 질문을 뽑아요." }),
        ]),
      ]),
      block("흩어진 자료를 시간 순으로 엮어요", [
        "사건 자료는 보통 여기저기 흩어져 있어요. 접수증은 서랍에, 문자는 휴대폰에, 통지서는 봉투 안에요.",
        "사진으로 찍어 올리면 글자를 읽어서 '언제 무슨 일이 있었는지' 한 줄로 세워 드려요.",
      ]),
      block("확인된 것과 아닌 것을 갈라 놓아요", [
        "접수증·통지서처럼 기관이 남긴 기록은 '확인완료'로, 사람의 말은 '주장 · 미확인'으로 나눠 표시해요.",
        "자료끼리 숫자나 날짜가 어긋나면 어느 자료 몇 줄이 다른지 짚어 드려요.",
      ]),
      block("비어 있는 곳을 알려 드려요", [
        "기록이 몇 년씩 비어 있거나, 있어야 할 자료가 없으면 그 자리를 표시해요.",
        "'없는 것'을 아는 게 중요해요. 수사기관에 무엇을 더 내야 하는지가 거기서 나오거든요.",
      ]),
      block("다음에 할 일을 하나 골라 드려요", [
        "놓치면 되돌릴 수 없는 것부터 봐요. 기한이 있는 절차가 가장 앞에 오고, 왜 그 행동인지 이유를 같이 보여 드려요.",
      ]),
      block("하지 않는 것", [
        "누가 범인인지, 무엇이 진실인지는 판단하지 않아요. 자료에 적힌 것과 적히지 않은 것만 보여 드려요.",
        "법조문·기한·제출처는 검증된 자료에 있을 때만 알려 드려요. 확인되지 않은 것은 빈칸으로 두고 '확인 중'이라고 적어요. 잘못된 기한 하나가 사건을 끝낼 수 있으니까요.",
        "법률 자문이 아니에요. 변호사·법률구조공단 상담을 대신하지 않아요.",
      ]),
    ]));
  }

  function nav() {
    var menuButton = h("button", { type: "button", class: "nav__menu", "aria-label": "메뉴 열기" }, [
      h("span", { class: "nav__bars", "aria-hidden": "true" }),
    ]);
    var menu = dropdown(menuButton, [
      { label: "내 사건", href: "cases.html" },
      { label: "새 사건 등록", href: "new.html" },
    ]);

    var avatar = h("button", { type: "button", class: "nav__avatar", "aria-label": "내 정보" }, [
      h("span", { class: "t-label c-brand", text: "나" }),
    ]);
    var account = dropdown(avatar, [
      { label: "내 정보", onClick: function () { openModal("내 정보", h("p", { class: "help__text", text: "계정 화면은 아직 준비 중이에요." })); } },
      { label: "로그아웃", href: "index.html", danger: true },
    ]);

    var help = h("button", { type: "button", class: "nav__link t-body-m c-secondary", text: "도움말" });
    help.addEventListener("click", helpModal);

    // 왼쪽은 로고만, 오른쪽은 도움말 · 프로필 · 메뉴 순서
    return h("header", { class: "nav" }, [
      h("a", { class: "nav__brand", href: "index.html" }, [
        h("img", { class: "nav__logo", src: "assets/logo.png", alt: "", width: "28", height: "28" }),
        h("span", { class: "nav__name t-heading c-primary", text: "타래" }),
      ]),
      h("nav", { class: "nav__right", "aria-label": "주 메뉴" }, [help, account, menu]),
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
    // '중지'는 그 자체가 상태다 — '중지 단계'라고 쓰지 않는다
    if (current.label === "중지") return "중지";
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

  /** 카메라를 연다. 노트북에서는 웹캠 미리보기를, 휴대폰에서는 기본 카메라를 쓴다. */
  function openCamera(onShot, fallbackInput) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      fallbackInput.click();
      return;
    }
    var video = h("video", { class: "cam__view", autoplay: true, playsinline: true, muted: true });
    var shoot = h("button", { type: "button", class: "modal__save", text: "찍기" });
    var note = h("p", { class: "modal__note", text: "찍은 사진은 이 화면의 자료 목록에만 더해집니다. 아직 어디로도 보내지 않아요." });
    var stream = null;

    function stop() {
      if (stream) stream.getTracks().forEach(function (t) { t.stop(); });
      stream = null;
    }

    shoot.addEventListener("click", function () {
      if (!stream) return;
      var canvas = document.createElement("canvas");
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
      var now = new Date();
      var stamp = now.getFullYear() + pad(now.getMonth() + 1) + pad(now.getDate()) + "_" + pad(now.getHours()) + pad(now.getMinutes()) + pad(now.getSeconds());
      onShot({ kind: "IMG", name: "사진_" + stamp + ".jpg", meta: "방금 찍음 · 정리를 시작하면 날짜를 읽어요" });
      stop();
      var dialog = document.querySelector("dialog.modal");
      if (dialog) dialog.close();
    });

    openModal("사진 찍기", h("div", { class: "cam" }, [video, shoot, note]));
    var dialog = document.querySelector("dialog.modal");
    dialog.addEventListener("close", stop);

    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(function (s) {
      stream = s;
      video.srcObject = s;
    }, function () {
      // 권한을 막았거나 카메라가 없을 때 — 파일 선택으로 물러난다
      stop();
      dialog.close();
      fallbackInput.click();
    });
  }

  function pad(n) { return (n < 10 ? "0" : "") + n; }

  /** 자료가 없어도 기억나는 내용을 적어 둘 수 있게 한다. */
  function openMemoModal(onAdd) {
    var what = h("textarea", { id: "memo-what", class: "field__input field__input--area", rows: "5", placeholder: "예) 6월 2일 저녁에 판매자에게 전화했지만 받지 않았습니다" });
    var hint = h("p", { class: "field__hint", text: "날짜가 기억나면 함께 적어 주세요. 정리를 시작하면 시간축에 같이 올립니다." });
    var save = h("button", { type: "button", class: "modal__save", text: "자료에 더하기" });

    save.addEventListener("click", function () {
      var text = what.value.trim();
      if (!text) {
        hint.textContent = "내용을 적어 주세요.";
        hint.classList.add("field__hint--warn");
        what.focus();
        return;
      }
      onAdd({
        kind: "메모",
        name: text.length > 28 ? text.slice(0, 27) + "…" : text,
        meta: "직접 적음 · 기록 자료가 아니라 본인 진술로 다룹니다",
        text: text,
      });
      var dialog = document.querySelector("dialog.modal");
      if (dialog) dialog.close();
    });

    openModal("기억나는 내용 적기", h("div", { class: "evform" }, [
      h("div", { class: "field" }, [h("label", { for: "memo-what", text: "무슨 일이 있었나요?" }), what, hint]),
      save,
      h("p", { class: "modal__note", text: "직접 적은 내용은 접수증·통지서 같은 기록 자료와 구분해서 표시됩니다." }),
    ]));
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
        h("button", { type: "button", class: "btn btn--secondary t-body-m-strong", text: "사진 찍기", onclick: function () { openCamera(function (shot) { files.push(shot); drawList(); }, camera); } }),
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

    var memoButton = h("button", { type: "button", class: "add-event t-body-m-strong c-brand", text: "+  기억나는 내용을 직접 적기 (선택)", style: "padding:0" });
    memoButton.addEventListener("click", function () {
      openMemoModal(function (memo) { files.push(memo); drawList(); });
    });

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
        memoButton,
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

  /** 그 사건이 쓰는 날짜 표기(연도까지 / 월일만)에 맞춘다. */
  function formatDay(c, iso) {
    var multiYear = c.timeline.some(function (r) { return /^\d{4}\./.test(String(r.time || "")); });
    return multiYear ? iso.replace(/-/g, ".") : iso.slice(5).replace("-", "/");
  }

  /** 시간 순서를 지켜 끼워 넣는다. 날짜를 모르는 줄은 맨 뒤로 간다. */
  function insertEvent(c, row, iso) {
    function key(r) {
      var t = String(r.time || "");
      var digits = t.replace(/[^0-9]/g, "");
      if (!digits) return "999999999999";                       // 시점 미상은 맨 뒤
      var full = /^\d{4}\./.test(t) ? digits : "0000" + digits;  // 월일만 쓰는 사건은 연도 자리를 비운다
      return (full + "000000000000").slice(0, 12);
    }
    if (!iso) { c.timeline.push(row); return; }
    var mine = key(row);
    var at = c.timeline.findIndex(function (r) { return key(r) > mine; });
    if (at < 0) c.timeline.push(row);
    else c.timeline.splice(at, 0, row);
  }

  /** 기억나는 일을 직접 적는 창. 엔진이 읽은 것과 섞이지 않게 '내가 적음'으로 들어간다. */
  function addEventModal(c) {
    var when = h("input", { type: "date", id: "ev-when", class: "field__input" });
    var what = h("textarea", { id: "ev-what", class: "field__input field__input--area", rows: "3", placeholder: "예) 담당 수사관에게 전화했지만 연결되지 않았습니다" });
    var hint = h("p", { class: "field__hint", text: "날짜를 모르면 비워 두세요. '시점 미상'으로 들어갑니다." });

    var save = h("button", { type: "button", class: "modal__save", text: "타임라인에 추가" });
    save.addEventListener("click", function () {
      var text = what.value.trim();
      if (!text) {
        hint.textContent = "무슨 일이 있었는지 적어 주세요.";
        hint.classList.add("field__hint--warn");
        what.focus();
        return;
      }
      insertEvent(c, {
        type: "event",
        time: when.value ? formatDay(c, when.value) : "시점 미상",
        title: text,
        kind: "mine",
        badge: "내가 적음",
        conflict: false,
        needs_date: !when.value,
        source: "직접 입력",
      }, when.value);
      var panel = document.getElementById("panel");
      panel.textContent = "";
      panel.appendChild(timelineCard(c));
      var dialog = document.querySelector("dialog.modal");
      if (dialog) dialog.close();
    });

    openModal("기억나는 일 적기", h("div", { class: "evform" }, [
      h("div", { class: "field" }, [h("label", { for: "ev-when", text: "언제 있었나요?" }), when]),
      h("div", { class: "field" }, [h("label", { for: "ev-what", text: "무슨 일이 있었나요?" }), what, hint]),
      save,
      h("p", { class: "modal__note", text: "직접 적은 내용은 기록 자료가 아니라 '내가 적음'으로 표시됩니다. 지금은 이 화면에만 남습니다." }),
    ]));
  }

  // 점 색이 뜻하는 것. 줄에는 글씨를 두지 않고 여기서 한 번만 적는다.
  var KIND_LEGEND = [
    ["verified", "확인완료"],
    ["claim", "주장 · 미확인"],
    ["conflict", "불일치"],
    ["mine", "내가 적음"],
  ];

  /** 그 줄이 어떤 상태인지 — 팝업 제목 옆에 붙는 말. */
  function rowFlags(row) {
    var flags = [];
    if (row.conflict) flags.push(["conflict", "불일치"]);
    if (row.kind === "claim") flags.push(["unverified", row.badge]);
    if (row.kind === "mine") flags.push(["mine", row.badge]);
    if (row.needs_date) flags.push(["unverified", "날짜 확인 필요"]);
    if (!flags.length) flags.push(["verified", "확인 완료"]);
    return flags;
  }

  /** 줄을 누르면 열리는 자세히 — 원문과 출처를 그대로 보여준다. */
  function timelineDetail(row) {
    var body = h("div", { class: "tldetail" }, [
      h("div", { class: "tldetail__flags" }, rowFlags(row).map(function (f) { return badge(f[0], f[1]); })),
      h("p", { class: "tldetail__when", text: String(row.time || "").replace(/\s+/g, " ") }),
      h("p", { class: "tldetail__full", text: row.full || row.title }),
    ]);

    var sources = row.sources || [];
    body.appendChild(h("p", { class: "tldetail__label", text: sources.length ? "출처" : "" }));
    if (!sources.length) {
      body.appendChild(h("p", { class: "tldetail__none", text: "직접 적은 내용이라 뒷받침하는 자료가 없어요." }));
    } else {
      body.appendChild(h("ul", { class: "srclist" }, sources.map(function (s) {
        return h("li", { class: "srclist__item" }, [
          h("span", { class: "srclist__kind t-caption", text: s.line + "줄" }),
          h("div", { class: "srclist__texts" }, [
            h("span", { class: "t-body-m c-primary", text: s.name }),
            s.quote ? h("span", { class: "srclist__quote", text: "“" + s.quote + "”" }) : null,
          ]),
        ]);
      })));
      body.appendChild(h("p", { class: "modal__note", text: "원본 사진을 띄우는 것은 아직 연결되지 않았어요. 지금은 어느 자료 몇 줄에서 왔는지까지 보여드려요." }));
    }
    openModal(row.title, body);
  }

  function timelineCard(c) {
    var wrap = h("div", { class: "card tl" });
    var rows = c.timeline;
    var lastEvent = -1;
    rows.forEach(function (row, i) { if (row.type === "event") lastEvent = i; });

    var used = {};
    rows.forEach(function (row) {
      if (row.type !== "event") return;
      used[row.conflict ? "conflict" : row.kind] = true;
    });
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

      var more = h("button", { type: "button", class: "tl__more", text: "자세히" });
      more.addEventListener("click", function () { timelineDetail(row); });

      wrap.appendChild(h("div", { class: "tl__row" + (i === lastEvent ? " tl__row--last" : "") }, [
        h("div", { class: "tl__when" }, [
          h("span", { class: "tl__day t-label" + (sameDay ? " tl__day--same" : ""), text: sameDay ? "" : t.day }),
          h("span", { class: "tl__time t-caption", text: t.time }),
        ]),
        h("div", { class: "tl__rail", "aria-hidden": "true" }, [
          h("span", { class: "tl__dot tl__dot--" + (row.conflict ? "conflict" : row.kind) }),
          h("span", { class: "tl__line" }),
        ]),
        h("p", { class: "tl__title", text: row.title }),
        more,
      ]));
    });

    var add = h("button", { type: "button", class: "tl__add t-body-m-strong c-brand", text: "+  기억나는 일을 직접 추가" });
    add.addEventListener("click", function () { addEventModal(c); });
    wrap.appendChild(add);
    return wrap;
  }

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
      askButton(c),
    ]);
  }

  // 갈래마다 어떻게 물을지. 질문 문장은 여기서 정하고, 내용은 엔진이 올린 것을 그대로 넣는다.
  var ASK_FRAME = {
    "자료끼리 어긋남": "자료마다 다르게 적혀 있습니다. 어느 쪽을 기준으로 봐야 하나요?",
    "확인되지 않음": "기록으로 확인되지 않는 내용입니다. 어떻게 확인할 수 있을까요?",
    "빠진 정보": "이 자료가 없습니다. 어디에서 받을 수 있나요?",
    "읽히지 않은 부분": "자료가 잘 읽히지 않습니다. 원본을 다시 내야 하나요?",
  };

  /** 상담에 가져갈 질문지를 만든다 — 사건 요약 + 확인이 필요한 것 + 다음 행동. */
  function askSheet(c) {
    var lines = [];
    lines.push("[사건] " + c.title + " (" + c.type_label + ")");
    lines.push("[기간] " + c.period + " · 자료 " + c.sources.length + "개 · 확인 필요 " + c.need_count);
    lines.push("");

    (c.issues || []).forEach(function (g) {
      var frame = ASK_FRAME[g.label] || "이 부분을 어떻게 보면 될까요?";
      lines.push("■ " + g.label + " — " + frame);
      g.items.forEach(function (it) {
        lines.push("  · " + it.text + (it.how ? " (" + it.how + ")" : ""));
      });
      lines.push("");
    });

    var next = c.next_action;
    if (next) {
      lines.push("■ 다음 행동 — " + next.label);
      if (next.due) lines.push("  · 기한: " + next.due.text);
      if (next.state === "filled" && next.rows.length) {
        next.rows.forEach(function (r) { lines.push("  · " + r.k + ": " + r.v); });
        lines.push("  · 이 절차를 진행하려면 무엇을 더 준비해야 하나요?");
      } else {
        lines.push("  · 이 행동을 어디에 어떻게 해야 하는지 알고 싶습니다.");
      }
    }
    return lines.join(String.fromCharCode(10)).trim();
  }

  function askButton(c) {
    var button = h("button", { type: "button", class: "issues__ask", text: "전문가에게 물어볼 질문 만들기" });
    button.addEventListener("click", function () {
      var text = askSheet(c);
      var area = h("textarea", { class: "ask__text", rows: "14", readonly: true });
      area.value = text;

      var copy = h("button", { type: "button", class: "modal__save", text: "복사하기" });
      copy.addEventListener("click", function () {
        function done() { copy.textContent = "복사했어요"; setTimeout(function () { copy.textContent = "복사하기"; }, 1600); }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () { area.select(); });
        } else {
          area.select();
        }
      });

      openModal("전문가에게 물어볼 질문", h("div", { class: "ask" }, [
        h("p", { class: "ask__lead", text: "지금 화면에 올라온 것에서 뽑았어요. 상담 전에 읽어 보고 빼거나 더할 수 있어요." }),
        area,
        copy,
        h("p", { class: "modal__note", text: "법률 자문이 아니라 물어볼 거리입니다. 답은 변호사·법률구조공단 같은 곳에서 들으세요." }),
      ]));
    });
    return button;
  }

  function sourceListModal(c) {
    openModal("첨부한 자료 " + c.sources.length + "개", h("div", {}, [
      h("ul", { class: "srclist" }, c.sources.map(function (s) {
        return h("li", { class: "srclist__item" + (s.isNew ? " srclist__item--new" : "") }, [
          h("span", { class: "srclist__kind t-caption", text: s.kind }),
          h("span", { class: "t-body-m c-primary", text: s.name }),
          s.isNew ? h("span", { class: "srclist__new", text: "방금 추가" }) : null,
        ]);
      })),
      h("p", { class: "modal__note", text: "방금 올린 자료는 이 화면에만 더해집니다. 정리 엔진에 넣는 것은 아직 연결되지 않았어요." }),
    ]));
  }

  /** 자료는 목록으로 늘어놓지 않고 버튼 뒤에 둔다. */
  function sourcesBar(c, vertical) {
    var count = h("span", { class: "srcbar__count", text: String(c.sources.length) });

    var open = h("button", { type: "button", class: "srcbar__btn" }, [
      h("span", { text: "첨부한 자료" }),
      count,
    ]);
    open.addEventListener("click", function () { sourceListModal(c); });

    var add = h("button", { type: "button", class: "srcbar__btn srcbar__btn--add" }, [h("span", { text: "+  자료 추가하기" })]);
    add.addEventListener("click", function () { pickFiles(addFiles); });

    function addFiles(picked) {
      c.sources = c.sources.concat(picked);
      count.textContent = String(c.sources.length);
      sourceListModal(c);
    }
    addFilesHandler = addFiles;   // 상단 메뉴의 '자료 추가하기'도 같은 일을 한다

    return h("div", { class: "srcbar" + (vertical ? " srcbar--stack" : "") }, [add, open]);
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
        rail.appendChild(askButton(c));
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
