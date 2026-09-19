/* 타래 화면 렌더링.
 *
 * 예시 사건은 data/cases.js 의 window.TARAE_CASES 에서 읽는다(action-engine/tools/export_web.py 가 만든다).
 * 화면에서 등록한 사건은 정리 서버(web/serve.py)의 /api 에서 읽는다 — 서버가 올린 자료를 두 엔진에 넣어 만든다.
 * 화면 문장을 여기서 지어내지 않는다 — 비어 있는 값은 비어 있다고 보여준다.
 * 사용자·엔진 문자열이 섞이므로 innerHTML 을 쓰지 않고 textContent 로만 넣는다.
 */
(function () {
  "use strict";

  /* 누가 보고 있는가.
   *
   * 서버가 없어 진짜 로그인은 없다. 여기 있는 것은 '데모 계정으로 들어왔는지'
   * 하나뿐이고, 비밀번호는 담지도 않는다(auth.js 참고).
   *
   * 새로 가입한 사람에게 데모 사건을 보여주면 남의 사건을 자기 것으로 읽는다.
   * 그래서 가입해서 들어온 화면은 빈 서류함에서 시작한다.
   */
  var SESSION_KEY = "tarae.session";

  function session() {
    try { return JSON.parse(localStorage.getItem(SESSION_KEY)) || null; } catch (e) { return null; }
  }

  /** 데모 사건을 보여줄 것인가. 기록이 없으면 보여준다 — 화면만 열어 보는 경우다. */
  function showsDemo() {
    var me = session();
    return !me || me.demo !== false;
  }

  var CASES = showsDemo() ? (window.TARAE_CASES || []) : [];

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

  /* 정리 서버 API. 두 가지가 있다.
     - 로컬 정리 서버(web/serve.py): 사진을 서버가 읽고 사건을 서버에 저장한다
     - 배포 환경(Vercel, api/): 저장하지 않는다. /api/status 가 mode "browser" 를 알리면 사건 조회·등록을
       browser-store.js 가 맡는다 — 사진은 이 브라우저에서 읽고, 사건도 이 브라우저에 남는다
     GitHub Pages 처럼 둘 다 없으면 요청이 실패한다. 그때 화면은 등록을 막고 이유를 보여준다 —
     올린 것처럼 꾸미지 않는다. 주소는 상대 경로라 하위 경로에 올려도 같은 규칙으로 돈다. */
  function fetchJson(path, options) {
    return fetch(path, options).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (body) {
        if (!res.ok) {
          var err = new Error(body.error || "정리 서버에 연결하지 못했어요.");
          err.detail = body.detail || null;
          throw err;
        }
        return body;
      });
    });
  }

  var statusPromise = null;

  /** 서버가 있으면 {ocr, case_types, mode?}, 없으면 null. 한 화면에서 한 번만 묻는다. */
  function serverStatus() {
    if (!statusPromise) statusPromise = fetchJson("api/status").catch(function () { return null; });
    return statusPromise;
  }

  function inBrowserMode() {
    return serverStatus().then(function (s) { return !!(s && s.mode === "browser" && window.TaraeBrowserStore); });
  }

  function api(path, options) {
    if (path.indexOf("api/cases") !== 0) return fetchJson(path, options);
    return inBrowserMode().then(function (browser) {
      return browser ? window.TaraeBrowserStore.request(path, options) : fetchJson(path, options);
    });
  }

  /** 이 서버에서 등록한 사건인가. 예시 사건(cases.js)은 자료를 더할 수 없다. */
  function isLocal(c) { return !!(c && c.local); }

  /** 자료를 서버에 보낸다. 엔진이 다시 정리한 사건 화면 데이터가 돌아온다.
      배포 환경에서는 사진을 이 브라우저에서 먼저 읽는다 — 그 진행 상황을 onProgress 로 알린다. */
  function uploadForm(url, fields, items, onProgress) {
    return inBrowserMode().then(function (browser) {
      return browser ? window.TaraeBrowserStore.upload(url, fields, items, onProgress) : postForm(url, fields, items);
    });
  }

  function postForm(url, fields, items) {
    var form = new FormData();
    Object.keys(fields).forEach(function (key) { if (fields[key]) form.append(key, fields[key]); });
    items.forEach(function (it) {
      if (it.file) {
        form.append("file", it.file, it.name);
        form.append("modified", it.modified || "");   // 사진을 찍은(파일이 만들어진) 때 — 날짜 없는 자료의 기준일
      } else if (it.note) {
        form.append("note", it.note);
      }
    });
    return fetchJson(url, { method: "POST", body: form });
  }

  function errorText(err) {
    return err.message + (err.detail ? " (" + err.detail + ")" : "");
  }

  /** 파일 수정 시각 → 시간대 없는 로컬 ISO. 엔진은 한국 시간 기준 naive datetime 을 쓴다. */
  function isoLocal(ms) {
    var d = new Date(ms || Date.now());
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + "T" + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
  }

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

  /** 자료 고르기. 고른 파일을 그대로 돌려준다 — 보낼지는 부르는 쪽이 정한다. */
  function pickFiles(onPicked, accept) {
    var input = h("input", { type: "file", multiple: true, accept: accept || ACCEPT, hidden: true });
    input.addEventListener("change", function () {
      var picked = Array.prototype.map.call(input.files, function (f) {
        return { kind: fileKind(f.name), name: f.name, file: f, modified: isoLocal(f.lastModified) };
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
          h("li", { text: "타임라인에서 언제 무슨 일이 있었는지 확인해요." }),
          h("li", { text: "'확인이 필요해요'를 펼쳐 어긋난 것 · 아직 확인되지 않은 것 · 빠진 것을 봐요." }),
          h("li", { text: "'다음 행동'에서 지금 할 일 하나를 확인해요. 기한이 있으면 남은 날짜가 함께 떠요." }),
          h("li", { text: "막히면 '전문가에게 물어볼 질문'을 눌러 상담에 가져갈 질문을 뽑아요." }),
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

    var me = session();
    var avatar = h("button", { type: "button", class: "nav__avatar", "aria-label": "내 정보" }, [
      h("span", { class: "t-label c-brand", text: me && me.name ? me.name.slice(0, 1) : "나" }),
    ]);
    var logout = { label: "로그아웃", danger: true, onClick: function () {
      try { localStorage.removeItem(SESSION_KEY); } catch (e) { /* 지우지 못해도 나간다 */ }
      location.href = "index.html";
    } };
    var account = dropdown(avatar, [
      { label: "내 정보", onClick: function () {
        openModal("내 정보", h("div", { class: "help" }, [
          h("p", { class: "help__text", text: me && me.name ? "아이디 · " + me.name : "데모 화면을 보고 있어요." }),
          h("p", { class: "help__text", text: "지금은 화면만 있는 데모예요. 실제 계정이 만들어지지는 않습니다." }),
        ]));
      } },
      logout,
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
        // 직접 적은 메모로만 이른 단계는 점선으로 — 진행은 보이되 자료로 확인된 단계는 아니다
        return h("div", { class: "step step--" + s.state + (s.noted ? " step--noted" : ""), role: "listitem",
                          "aria-current": s.state === "current" ? "step" : null,
                          title: s.noted ? "직접 적은 내용으로 알게 된 단계예요. 자료로 확인되지는 않았어요." : null }, [
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

  /* 카드 색은 사건 유형이 정한다 — 목록에 사건이 늘어도 같은 유형이면 같은 색이다.
     (순서대로 색을 돌려 쓰면 사건 하나가 추가될 때마다 색이 통째로 밀려서 기억이 깨진다.) */
  var TONES = {
    missing_person_suspended: 1,   // 실종
    investigation_suspended: 2,    // 고소 · 수사중지
    used_goods_fraud: 3,           // 재산범죄
  };

  function toneOf(c) {
    return TONES[c.type] || 3;   // 아직 색을 정하지 않은 유형은 가장 옅은 색으로 둔다
  }
  function visibleIssues(c) {
    return (c.issues || []).filter(function (g) {
      return g.label !== "빠진 정보" && g.label !== "읽히지 않은 부분";
    });
  }

  function visibleIssueCount(c) {
    return visibleIssues(c).reduce(function (sum, g) { return sum + g.items.length; }, 0);
  }

  function folder(c, tone) {
    var next = activeAction(c);
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
          h("p", { class: "folder__meta t-body-s", text: "확인 필요 " + visibleIssueCount(c) + " · 자료 " + c.doc_count + "개" }),
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
    var lead = h("p", { class: "t-body-l c-secondary" });

    // 내가 등록한 사건을 앞에, 예시 사건을 뒤에 둔다. 서버가 없으면 예시만 보인다.
    function draw(mine) {
      var all = mine.concat(CASES);
      grid.textContent = "";
      grid.className = "folder-grid" + (all.length ? "" : " folder-grid--empty");
      all.forEach(function (c) { grid.appendChild(folder(c, toneOf(c))); });
      grid.appendChild(h("a", { class: "folder folder--new", href: "new.html" }, [
        h("span", { class: "folder__tab", "aria-hidden": "true" }),
        h("div", { class: "folder__body" }, [
          h("span", { class: "circle-56" }, [icon("plus")]),
          h("p", { class: "t-heading c-secondary", text: "사건 등록" }),
          h("p", { class: "t-body-s c-tertiary", text: "유형을 고르고 자료를 올리면 정리가 시작돼요" }),
        ]),
      ]));
      lead.textContent = all.length
        ? "사건 카드를 선택하면 정리된 타임라인을 볼 수 있어요."
        : "아직 등록한 사건이 없어요. 첫 사건을 등록하면 여기에 쌓입니다.";
    }
    draw([]);
    api("api/cases").then(draw, function () { /* 서버가 없으면 예시만 둔다 */ });

    root.appendChild(h("main", { class: "page page--home" }, [
      // 새 사건 등록은 그리드 끝의 점선 폴더가 맡는다 — 머리말에 같은 버튼을 두지 않는다
      h("div", { class: "page-head" }, [
        h("div", { class: "page-head__title" }, [
          h("h1", { class: "t-display c-primary", text: "내 사건" }),
          lead,
        ]),
      ]),
      grid,
    ]));
  }

  // ── 02 새 사건 등록 ─────────────────────────────────────
  // 사건 유형은 화면에 적어 두지 않는다. 엔진이 다루는 유형(research-engine requirements)을 서버가 읽어 준다.

  // 엔진이 읽을 수 있는 자료만 받는다: 사진은 OCR 로 읽고, OCR 결과 JSON 은 그대로 넣는다.
  // PDF·음성은 아직 읽는 경로가 없다 — 받아 놓고 정리하지 않으면 올린 사람이 속는다.
  var ACCEPT = "image/*,.json,application/json";
  var IMAGE_EXTS = ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff"];

  function fileKind(name) {
    var ext = (name.split(".").pop() || "").toLowerCase();
    if (ext === "json") return "OCR";
    if (IMAGE_EXTS.indexOf(ext) >= 0) return "IMG";
    if (ext === "pdf") return "PDF";
    if (["m4a", "mp3", "wav", "aac"].indexOf(ext) >= 0) return "음성";
    return "문서";
  }

  function canRead(name) {
    var kind = fileKind(name);
    return kind === "IMG" || kind === "OCR";
  }

  /** 카메라를 연다. 노트북에서는 웹캠 미리보기를, 휴대폰에서는 기본 카메라를 쓴다. */
  function openCamera(onShot, fallbackInput) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      fallbackInput.click();
      return;
    }
    var video = h("video", { class: "cam__view", autoplay: true, playsinline: true, muted: true });
    var shoot = h("button", { type: "button", class: "modal__save", text: "찍기" });
    var note = h("p", { class: "modal__note", text: "찍은 사진은 자료 목록에 더해지고, 정리를 시작하면 글자를 읽어 정리합니다." });
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
      var name = "사진_" + stamp + ".jpg";
      stop();
      var dialog = document.querySelector("dialog.modal");
      if (dialog) dialog.close();
      canvas.toBlob(function (blob) {
        if (!blob) return;
        onShot({ kind: "IMG", name: name, file: new File([blob], name, { type: "image/jpeg", lastModified: now.getTime() }),
                 modified: isoLocal(now.getTime()), meta: "방금 찍음 · 정리를 시작하면 글자를 읽어요" });
      }, "image/jpeg", 0.92);
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
        meta: "직접 기록 · 기록 자료가 아니라 본인 진술로 다룹니다",
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
    var items = [];          // 올릴 자료: {kind, name, meta, file?, modified?, note?}
    var pickedType = null;
    var status;              // undefined = 확인 중, null = 서버 없음
    var list = h("div", { class: "file-list" });
    var count = h("span", { class: "t-label c-brand", text: "0" });
    var chips = h("div", { class: "chips", role: "group", "aria-label": "사건 유형" }, [
      h("p", { class: "t-body-s c-tertiary", text: "고를 수 있는 유형을 불러오는 중이에요…" }),
    ]);
    var notice = h("p", { class: "field__hint", role: "status", hidden: true });

    function say(text, warn) {
      notice.hidden = !text;
      notice.textContent = text || "";
      notice.classList.toggle("field__hint--warn", !!warn);
    }

    function drawChips() {
      chips.textContent = "";
      if (!status) {
        chips.appendChild(h("p", { class: "t-body-s c-tertiary", text: "정리 서버에 연결되지 않아 유형을 불러오지 못했어요." }));
        return;
      }
      status.case_types.forEach(function (t) {
        var node = h("button", { type: "button", class: "chip", "aria-pressed": pickedType === t.type ? "true" : "false", text: t.label });
        node.addEventListener("click", function () {
          pickedType = t.type;
          chips.querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
          node.setAttribute("aria-pressed", "true");
          say("");
        });
        chips.appendChild(node);
      });
    }

    function drawList() {
      list.textContent = "";
      count.textContent = String(items.length);
      if (!items.length) {
        list.appendChild(h("p", { class: "empty-files t-body-s c-tertiary", text: "아직 올린 자료가 없어요. 사진 한 장부터 시작해도 괜찮아요." }));
        return;
      }
      items.forEach(function (it, i) {
        var remove = h("button", { type: "button", class: "file-row__remove t-body-s", "aria-label": it.name + " 제거", text: "×" });
        remove.addEventListener("click", function () { items.splice(i, 1); drawList(); });
        list.appendChild(h("div", { class: "file-row" }, [
          h("span", { class: "file-row__kind t-caption", text: it.kind }),
          h("div", { class: "file-row__texts" }, [
            h("p", { class: "t-body-m-strong c-primary", text: it.name, title: it.name }),
            h("p", { class: "t-body-s c-tertiary", text: it.meta }),
          ]),
          remove,
        ]));
      });
    }

    function addFiles(fileList) {
      var skipped = [];
      Array.prototype.forEach.call(fileList, function (f) {
        if (!canRead(f.name)) { skipped.push(f.name); return; }
        var ocr = fileKind(f.name) === "OCR";
        items.push({ kind: fileKind(f.name), name: f.name, file: f, modified: isoLocal(f.lastModified),
                     meta: ocr ? "OCR 결과 · 읽은 글자를 그대로 정리에 넣어요" : "사진 · 정리를 시작하면 글자를 읽어요" });
      });
      drawList();
      if (skipped.length) say("아직 읽을 수 없는 형식이라 빼 두었어요: " + skipped.join(", ") + " — 사진이나 OCR 결과 JSON 을 올려 주세요.", true);
    }

    var picker = h("input", { type: "file", multiple: true, accept: ACCEPT, hidden: true });
    var camera = h("input", { type: "file", accept: "image/*", capture: "environment", hidden: true });
    picker.addEventListener("change", function () { addFiles(picker.files); picker.value = ""; });
    camera.addEventListener("change", function () { addFiles(camera.files); camera.value = ""; });

    var dropzone = h("div", { class: "dropzone" }, [
      h("span", { class: "circle-56" }, [icon("upload")]),
      h("p", { class: "t-heading c-primary", text: "여기에 끌어다 놓거나, 휴대폰으로 찍어 올려주세요" }),
      h("div", { class: "dropzone__actions" }, [
        h("button", { type: "button", class: "btn btn--primary t-body-m-strong", text: "파일 선택", onclick: function () { picker.click(); } }),
        h("button", { type: "button", class: "btn btn--secondary t-body-m-strong", text: "사진 찍기", onclick: function () { openCamera(function (shot) { items.push(shot); drawList(); }, camera); } }),
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

    // 글을 대신 가져오지는 못한다. 주소를 본인이 적은 메모로 사건에 남긴다.
    var url = h("input", { type: "url", placeholder: "URL 붙여넣기", "aria-label": "글 주소" });
    function addUrl() {
      var value = url.value.trim();
      if (!value) return;
      items.push({ kind: "LINK", name: value, note: "글 주소: " + value, meta: "글 주소 · 본인이 적은 메모로 정리에 넣어요" });
      url.value = "";
      drawList();
    }
    url.addEventListener("keydown", function (e) { if (e.key === "Enter") addUrl(); });

    var memoButton = h("button", { type: "button", class: "add-event t-body-m-strong c-brand", text: "+  기억나는 내용을 직접 적기 (선택)", style: "padding:0" });
    memoButton.addEventListener("click", function () {
      openMemoModal(function (memo) { memo.note = memo.text; items.push(memo); drawList(); });
    });

    var title = h("input", { id: "case-title", type: "text", class: "field__input", maxlength: "60", placeholder: "비워 두면 유형과 등록한 날짜로 이름을 붙여요" });

    var start = h("button", { type: "button", class: "btn btn--primary t-body-m-strong", text: "정리 시작하기" });
    start.addEventListener("click", function () {
      if (status === undefined) return say("정리 서버를 확인하는 중이에요. 잠시 뒤 다시 눌러 주세요.");
      if (!status) return say("정리 서버에 연결되지 않아 자료를 정리할 수 없어요. 저장소에서 py web/serve.py 로 화면을 열어 주세요.", true);
      if (!pickedType) return say("어떤 일에 가까운지 유형을 골라 주세요.", true);
      if (!items.length) return say("정리할 자료가 없어요. 사진이나 메모를 하나 이상 더해 주세요.", true);
      if (!status.ocr.ready && items.some(function (it) { return it.kind === "IMG"; })) {
        return say(status.ocr.reason + " 사진을 빼고 OCR 결과 JSON 이나 메모로 정리할 수 있어요.", true);
      }
      start.disabled = true;
      start.textContent = "정리하는 중…";
      say("자료를 읽고 정리하고 있어요. 사진이 많으면 조금 걸려요.");
      uploadForm("api/cases", { case_type: pickedType, title: title.value.trim() }, items, function (text) { say(text); }).then(function (view) {
        location.href = caseHref(view.id);
      }, function (err) {
        start.disabled = false;
        start.textContent = "정리 시작하기";
        say(errorText(err), true);
      });
    });

    serverStatus().then(function (s) {
      status = s;
      drawChips();
      if (!s) say("정리 서버에 연결되지 않았어요. 이 화면에서는 자료를 정리할 수 없어요 — 저장소에서 py web/serve.py 로 열어 주세요.", true);
      else if (!s.ocr.ready) say(s.ocr.reason + " OCR 결과 JSON 과 메모는 정리할 수 있어요.");
      else if (s.mode === "browser") say("사진은 이 브라우저에서 읽고, 읽은 글자만 정리 엔진에 보내요. 등록한 사건과 원본은 이 브라우저에만 남아요.");
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
        h("p", { class: "t-body-s c-tertiary", text: "유형에 따라 확인할 항목과 다음 행동이 달라져요." }),
        h("div", { class: "evform" }, [
          h("div", { class: "field" }, [h("label", { for: "case-title", text: "사건 이름 (선택)" }), title]),
        ]),
      ]),
      h("section", { class: "card section", "aria-labelledby": "s2" }, [
        h("div", { class: "section__head" }, [
          h("span", { class: "section__num t-label", text: "2" }),
          h("h2", { id: "s2", class: "t-heading c-primary", text: "가진 자료를 올려주세요" }),
          h("span", { class: "t-body-s c-tertiary", text: "통지서 · 접수증 · 진술서 사진" }),
        ]),
        dropzone,
        h("div", { class: "url-row" }, [
          h("label", { class: "input" }, [icon("link", 20), url]),
          h("button", { type: "button", class: "btn btn--secondary t-body-m-strong", text: "추가", onclick: addUrl }),
        ]),
        h("div", { class: "list-head" }, [h("span", { class: "t-label c-secondary", text: "올린 자료" }), count]),
        list,
        h("p", { class: "note t-body-s c-secondary", text: "날짜가 정리의 뼈대가 됩니다. 서류에 날짜가 없으면 사진을 찍은 날을 기준으로 삼아요." }),
        memoButton,
      ]),
      h("div", { class: "cta" }, [
        start,
        h("a", { class: "btn btn--secondary t-body-m-strong", href: "cases.html", text: "나중에 등록할게요" }),
      ]),
      notice,
    ]);

    root.appendChild(h("main", { class: "page page--new" }, [
      backLink(),
      h("div", { class: "new-folder" }, [
        h("span", { class: "new-folder__tab" }, [h("span", { class: "t-label c-tertiary", text: "새 사건" })]),
        folderBody,
      ]),
    ]));
  }

  // ── 03 사건 상세 ────────────────────────────────────────

  /** 팝업. 자료 목록·행동 설명처럼 평소엔 접어 두는 것을 담는다. */
  function openModal(title, body, headAction) {
    // 닫힌 팝업이 남아 있으면 먼저 치운다 — close 이벤트가 늦게 오는 브라우저가 있다
    document.querySelectorAll("dialog.modal").forEach(function (old) { old.remove(); });

    var dialog = h("dialog", { class: "modal" }, [
      h("div", { class: "modal__head" }, [
        h("h2", { class: "t-heading c-primary", text: title }),
        // 그 팝업에서 바로 할 수 있는 일이 있으면 닫기 옆에 둔다
        headAction || null,
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

  /** 기억나는 일을 직접 적는 창. 엔진이 읽은 것과 섞이지 않게 '직접 기록'으로 들어간다. */
  function addEventModal(c) {
    var when = h("input", { type: "date", id: "ev-when", class: "field__input" });
    var what = h("textarea", { id: "ev-what", class: "field__input field__input--area", rows: "3", placeholder: "예) 담당 수사관에게 전화했지만 연결되지 않았습니다" });
    var hint = h("p", { class: "field__hint", text: "날짜를 모르면 비워 두세요. '시점 미상'으로 들어갑니다." });

    // 등록한 사건은 엔진이 다시 정리하므로 타임라인에 오를지는 엔진이 정한다 — '타임라인에 추가'라고 약속하지 않는다
    var save = h("button", { type: "button", class: "modal__save", text: isLocal(c) ? "사건에 더하고 다시 정리" : "타임라인에 추가" });
    save.addEventListener("click", function () {
      var text = what.value.trim();
      if (!text) {
        hint.textContent = "무슨 일이 있었는지 적어 주세요.";
        hint.classList.add("field__hint--warn");
        what.focus();
        return;
      }
      if (isLocal(c)) {
        // 등록한 사건이면 메모로 서버에 보내 엔진이 다시 정리하게 한다. 날짜는 엔진이 읽는 모양으로 앞에 붙인다.
        var day = when.value ? when.value.split("-").map(Number) : null;
        var note = (day ? day[0] + ". " + day[1] + ". " + day[2] + ". " : "") + text;
        save.disabled = true;
        hint.classList.remove("field__hint--warn");
        hint.textContent = "사건을 다시 정리하고 있어요…";
        uploadForm("api/cases/" + encodeURIComponent(c.id) + "/files", {}, [{ note: note }]).then(function () {
          location.reload();
        }, function (err) {
          save.disabled = false;
          hint.textContent = errorText(err);
          hint.classList.add("field__hint--warn");
        });
        return;
      }
      insertEvent(c, {
        type: "event",
        at: when.value || null,
        time: when.value ? formatDay(c, when.value) : "시점 미상",
        title: text,
        kind: "mine",
        badge: "직접 기록",
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
      h("p", { class: "modal__note", text: isLocal(c)
        ? "직접 적은 내용은 기록 자료가 아니라 본인 메모로 사건에 더해지고, 사건 전체를 다시 정리합니다. 날짜나 절차가 드러나지 않는 내용은 타임라인 대신 '확인이 필요해요'에만 반영될 수 있어요."
        : "직접 적은 내용은 기록 자료가 아니라 '직접 기록'으로 표시됩니다. 예시 사건이라 이 화면에만 남습니다." }),
    ]));
  }

  // 점 색이 뜻하는 것. 줄에는 글씨를 두지 않고 여기서 한 번만 적는다.
  var KIND_LEGEND = [
    ["verified", "확인완료"],
    ["claim", "주장 · 미확인"],
    ["conflict", "불일치"],
    ["mine", "직접 기록"],
    ["submit", "내가 낸 것"],
    ["reply", "받은 회신"],
  ];

  /** 그 줄이 어떤 상태인지 — 팝업 제목 옆에 붙는 말. */
  function rowFlags(row) {
    var flags = [];
    if (row.conflict) flags.push(["conflict", "불일치"]);
    if (row.kind === "claim") flags.push(["unverified", row.badge]);
    if (row.kind === "mine" || row.kind === "submit" || row.kind === "reply") flags.push(["mine", row.badge]);
    if (row.needs_date) flags.push(["unverified", "날짜 확인 필요"]);
    if (!flags.length) flags.push(["verified", "확인 완료"]);
    return flags;
  }

  /** 줄을 누르면 열리는 자세히 — 원문과 출처를 그대로 보여준다. */
  function timelineDetail(row, c, onRemoved) {
    if (row.sub) return submissionDetail(row);
    // 제목에 원문을 그대로 쓴다 — 자세히를 눌렀는데 또 잘려 있으면 안 된다
    var full = row.full || row.title;
    var body = h("div", { class: "tldetail" }, [
      h("div", { class: "tldetail__flags" }, rowFlags(row).map(function (f) { return badge(f[0], f[1]); })),
      h("p", { class: "tldetail__when", text: String(row.time || "").replace(/\s+/g, " ") }),
    ]);

    var sources = row.sources || [];
    body.appendChild(h("p", { class: "tldetail__label", text: sources.length ? "출처" : "" }));
    if (!sources.length) {
      body.appendChild(h("p", { class: "tldetail__none", text: "직접 적은 내용이라 뒷받침하는 자료가 없어요." }));
    } else {
      var openable = false;
      body.appendChild(h("ul", { class: "srclist" }, sources.map(function (s) {
        var parts = [
          h("span", { class: "srclist__kind t-caption", text: s.line + "줄" }),
          h("div", { class: "srclist__texts" }, [
            h("span", { class: "t-body-m c-primary", text: s.name }),
            s.quote ? h("span", { class: "srclist__quote", text: "“" + s.quote + "”" }) : null,
          ]),
        ];
        // 열 원본이 없으면 눌리는 것과 똑같이 생기면 안 된다 — 눌러도 아무 일이 없어
        // '고장났다'로 읽힌다. 왜 못 여는지를 그 자리에 적는다.
        if (!s.href) {
          parts.push(h("span", { class: "srclist__none t-caption", text: "원본 없음" }));
          return h("li", {}, [h("div", { class: "srclist__item srclist__item--none" }, parts)]);
        }

        openable = true;
        parts.push(h("span", { class: "srclist__open t-caption", text: "원본 보기" }));
        var item = h("button", { type: "button", class: "srclist__item srclist__item--open" }, parts);
        item.addEventListener("click", function () { originalModal(s); });
        return h("li", {}, [item]);
      })));
    }
    // 직접 적은 줄에만 둔다. 서류에서 읽어 낸 줄에는 만들지 않는다.
    if (row.kind === "mine" && c) {
      var remove = h("button", { type: "button", class: "tldetail__remove t-body-m-strong", text: "이 줄 지우기" });
      remove.addEventListener("click", function () {
        var dialog = document.querySelector("dialog.modal");
        if (dialog) dialog.close();
        confirmRemoveRow(c, row, onRemoved || function () {});
      });
      body.appendChild(h("div", { class: "tldetail__foot" }, [remove]));
    }
    openModal(full, body);
  }

  /** 낸 것 · 받은 답 줄의 자세히. 자료가 아니라 내가 기록한 것이라 출처 대신 기록을 보여 준다. */
  function submissionDetail(row) {
    var s = row.sub;
    var lines = [
      h("div", { class: "tldetail__flags" }, rowFlags(row).map(function (f) { return badge(f[0], f[1]); })),
      h("p", { class: "t-body-s", text: dotDay(s.submitted_at) + "에 냄" + (s.to ? " · " + s.to : "") }),
    ];
    if (s.form_name) lines.push(h("p", { class: "t-body-s", text: "무엇을 · " + s.form_name }));
    lines.push(h("p", { class: "t-body-s", text: s.receipt ? "접수증 · " + s.receipt : "접수증이 없어 낸 사실이 본인 기록으로만 남아요." }));
    if (s.response) {
      lines.push(h("p", { class: "t-body-s", text: dotDay(s.response.received_at) + "에 회신 받음"
        + (s.response.decision_type ? " · " + s.response.decision_type : "") }));
    } else {
      lines.push(h("p", { class: "t-body-s", text: waitingText(s) }));
    }
    lines.push(h("p", { class: "modal__note", text: "내가 기록한 것이라 자료로 확인된 것은 아니에요. 통지서를 자료로 올리면 기록으로 바뀝니다." }));
    openModal(row.full || row.title, h("div", { class: "tldetail" }, lines));
  }

  /* 직접 적은 줄만 지운다.
   *
   * 올린 서류에서 읽어 낸 줄은 지우지 않는다 — 그건 자료에 그렇게 적혀 있다는
   * 사실이고, 마음에 들지 않는다고 지우면 화면이 자료와 다른 말을 하게 된다.
   * 서류를 빼려면 자료 자체를 지워야 한다.
   */
  function myNoteId(row) {
    if (row.kind !== "mine") return null;
    var src = (row.sources || [])[0];
    return src && /^note/.test(src.doc_id || "") ? src.doc_id : null;
  }

  /** 지울지 한 번 더 묻는다. 지우면 사건을 처음부터 다시 정리한다. */
  function confirmRemoveRow(c, row, done) {
    var noteId = myNoteId(row);
    var body = h("div", { class: "confirm" }, [
      h("p", { class: "confirm__q t-body-l c-primary", text: "이 줄을 지울까요?" }),
      h("p", { class: "confirm__quote t-body-s", text: row.full || row.title }),
      h("p", { class: "confirm__note t-body-s c-secondary", text: isLocal(c) && noteId
        ? "직접 적은 내용이라 지울 수 있어요. 지우면 남은 자료로 사건을 다시 정리해요."
        : "직접 적은 내용이라 이 화면에서 지웁니다." }),
    ]);

    var cancel = h("button", { type: "button", class: "confirm__cancel t-body-m-strong", text: "취소" });
    var ok = h("button", { type: "button", class: "confirm__ok t-body-m-strong", text: "지우기" });
    var fail = h("p", { class: "confirm__fail t-body-s", hidden: true });

    function close() {
      var dialog = document.querySelector("dialog.modal");
      if (dialog) dialog.close();
    }
    cancel.addEventListener("click", close);
    ok.addEventListener("click", function () {
      if (!(isLocal(c) && noteId)) {          // 예시 사건은 화면에만 있다
        c.timeline = c.timeline.filter(function (r) { return r !== row; });
        close();
        return done();
      }
      ok.disabled = true;
      ok.textContent = "지우는 중…";
      api("api/cases/" + encodeURIComponent(c.id) + "/notes/" + encodeURIComponent(noteId),
          { method: "DELETE" }).then(function () {
        close();
        location.reload();          // 엔진이 다시 정리했으므로 화면 전체를 새로 받는다
      }, function (err) {
        ok.disabled = false;
        ok.textContent = "지우기";
        fail.hidden = false;
        fail.textContent = errorText(err);
      });
    });

    body.appendChild(h("div", { class: "confirm__buttons" }, [cancel, ok]));
    body.appendChild(fail);
    openModal("직접 적은 줄 지우기", body);
  }

  /** 낸 것 · 받은 답의 날짜 표기. 사건이 월일만 쓰는데 다른 해의 일이면 연도까지 적는다. */
  function subDay(c, iso) {
    var years = {};
    c.timeline.forEach(function (r) { if (r.at) years[r.at.slice(0, 4)] = true; });
    var same = Object.keys(years).length === 1 && years[iso.slice(0, 4)];
    return same ? formatDay(c, iso) : iso.replace(/-/g, ".");
  }

  /** 타임라인에 올릴 줄 — 자료에서 읽은 줄에 내가 낸 것 · 받은 답을 날짜 순서대로 끼운다.
   *  타임라인은 이미 있었던 일만 적는다. 앞으로 할 일은 '다음 행동' 카드의 몫이다. */
  function timelineRows(c) {
    var extra = [];
    subsOf(c.id).forEach(function (s) {
      var what = s.form_name || s.label;
      extra.push({
        type: "event", kind: "submit", at: s.submitted_at, time: subDay(c, s.submitted_at),
        title: "냄 · " + what, full: s.label + (s.form_name ? " — " + s.form_name : ""),
        badge: "내가 낸 것", sub: s, sources: [],
      });
      if (s.response) {
        var answer = s.response.decision_type ? s.response.decision_type + " 통지" : "회신 받음 (결정 내용 모름)";
        extra.push({
          type: "event", kind: "reply", at: s.response.received_at, time: subDay(c, s.response.received_at),
          title: "회신 · " + answer, full: what + "에 대한 회신 — " + answer,
          badge: "받은 회신", sub: s, sources: [],
        });
      }
    });
    extra.sort(function (a, b) { return a.at < b.at ? -1 : a.at > b.at ? 1 : 0; });

    // 날짜를 모르는 줄(at 없음)은 맨 뒤에 모여 있다 — 날짜가 있는 기록은 그 앞에 둔다
    var out = [];
    var i = 0;
    c.timeline.forEach(function (row) {
      while (i < extra.length && (!row.at || extra[i].at < row.at)) out.push(extra[i++]);
      out.push(row);
    });
    while (i < extra.length) out.push(extra[i++]);
    return out;
  }

  function timelineCard(c) {
    var wrap = h("div", { class: "card tl" });
    var rows = timelineRows(c);
    var lastEvent = -1;
    rows.forEach(function (row, i) { if (row.type === "event") lastEvent = i; });

    var used = {};
    rows.forEach(function (row) {
      if (row.type !== "event") return;
      used[row.conflict ? "conflict" : row.kind] = true;
    });
    wrap.appendChild(h("div", { class: "tl__legend" }, KIND_LEGEND.filter(function (k) { return used[k[0]]; }).map(function (k) {
      return h("span", { class: "tl__legend-item tl__legend-item--" + k[0] }, [
        h("span", { class: "tl__legend-ink", text: k[1] }),
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
      more.addEventListener("click", function () {
        timelineDetail(row, c, function () {
          var panel = document.getElementById("panel");
          panel.textContent = "";
          panel.appendChild(timelineCard(c));
        });
      });


      wrap.appendChild(h("div", { class: "tl__row tl__row--" + (row.conflict ? "conflict" : row.kind)
        + (i === lastEvent ? " tl__row--last" : "") }, [
        h("div", { class: "tl__when" }, [
          h("span", { class: "tl__day t-label" + (sameDay ? " tl__day--same" : ""), text: sameDay ? "" : t.day }),
          h("span", { class: "tl__time t-caption", text: t.time }),
        ]),
        h("div", { class: "tl__rail", "aria-hidden": "true" }, [
          h("span", { class: "tl__dot tl__dot--" + (row.conflict ? "conflict" : row.kind) }),
          h("span", { class: "tl__line" }),
        ]),
        // 줄이는 일은 CSS 에 맡긴다 — 자리가 좁을 때만 잘리고, 그때는 마우스를
        // 올리면 원문이 끝까지 보인다 (자세히에도 원문이 있다)
        h("p", { class: "tl__title", title: row.full || row.title },
          [h("span", { class: "tl__text", text: row.title })]),
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

  // ── 무엇을 언제 내고 어떤 답을 받았는가 ───────────────────────────────
  //
  // 서버가 없어서 낸 기록은 이 브라우저에만 남는다(localStorage).
  // 판정 규칙은 action-engine 의 submissions.py 와 같다.
  //   · 이미 낸 행동은 다음 행동에서 내리고 '낸 것'으로 옮긴다
  //   · 접수증이 없으면 낸 사실이 본인 말뿐이라고 적는다
  //   · 답을 기다린 날수를 센다 — 며칠이면 늦은 것인지는 판단하지 않는다.
  //     회신 처리기한은 지식베이스에 없다. 없는 기한을 지어내지 않는다.

  var SUB_KEY = "tarae.submissions.v1";

  function allSubs() {
    try { return JSON.parse(localStorage.getItem(SUB_KEY)) || {}; } catch (e) { return {}; }
  }

  function saveSubs(all) {
    try { localStorage.setItem(SUB_KEY, JSON.stringify(all)); } catch (e) { /* 저장이 막혀도 화면은 돈다 */ }
  }

  // 같은 행동을 여러 번 낼 수 있다 — 이의제기서를 내고 불기소를 받으면 다음 '불복'은 항고장이다.
  // 행동 키로 가리면 두 번째 제출이 첫 번째 기록을 덮어써서 앞선 제출과 답이 사라진다. 그래서 id 로 가린다.
  function subsOf(caseId) {
    var list = allSubs()[caseId];
    if (!Array.isArray(list)) return [];
    // 예전 기록에는 id 가 없다 — 그때는 행동 하나에 기록 하나였으므로 행동 키와 낸 날로 만든다
    return list.map(function (s) {
      if (!s.id) s.id = s.action + "@" + s.submitted_at;
      return s;
    });
  }

  function putSub(caseId, sub) {
    if (!sub.id) sub.id = sub.action + "@" + sub.submitted_at + "@" + Date.now();
    var all = allSubs();
    all[caseId] = subsOf(caseId).filter(function (s) { return s.id !== sub.id; }).concat([sub]);
    saveSubs(all);
  }

  function dropSub(caseId, id) {
    var all = allSubs();
    all[caseId] = subsOf(caseId).filter(function (s) { return s.id !== id; });
    saveSubs(all);
  }

  /** 받은 답 가운데 가장 나중 것. 결정 내용을 고른 것만 센다 — 모르는 답으로는 단계를 바꾸지 않는다. */
  function latestAnswer(c) {
    var answered = null;
    subsOf(c.id).forEach(function (s) {
      if (!s.response || !s.response.decision_type) return;
      if (!answered || s.response.received_at >= answered.response.received_at) answered = s;
    });
    return answered;
  }

  /** 받은 날로 기한을 센다. 엔진이 미리 계산할 때는 기준일에 받았다고 두었으므로 날짜를 굳히지 않았다. */
  function withDue(a, received) {
    var copy = {};
    for (var k in a) if (a.hasOwnProperty(k)) copy[k] = a[k];
    copy.rows = (a.rows || []).slice();
    var d = a.due_rule ? dueFrom(received, a.due_rule.period_days) : null;
    if (d) {
      copy.due = { label: d.days < 0 ? "기한 지남" : "D-" + d.days, text: d.text + " (" + a.due_rule.label + ")", severity: d.severity };
      var where = copy.rows.findIndex(function (r) { return r.k === "어디에"; });
      copy.rows.splice(where < 0 ? copy.rows.length : where + 1, 0, { k: "언제까지", v: copy.due.text });
    }
    return copy;
  }

  /** 지금 기준의 행동 목록(우선순위 순서).
   *
   * 답을 기록했으면 엔진이 그 답으로 미리 계산해 둔 목록을 쓴다 — 단계가 바뀌면 '불복'의 서류와
   * 제출처가 바뀐다(수사중지면 이의제기서, 불기소면 항고장, 항고 기각이면 재정신청서). 옛 카드의
   * 행을 그대로 쓰면 엉뚱한 서류를 안내한다. 받은 날로 센 기한이 이미 지났으면 다음 행동에서 뺀다
   * — 엔진도 지난 기한은 다음 행동으로 올리지 않는다.
   */
  function actionsNow(c) {
    var answered = latestAnswer(c);
    var outcome = answered ? outcomeOf(c, answered) : null;
    if (outcome && outcome.actions && outcome.actions.length) {
      return outcome.actions
        .map(function (a) { return withDue(a, answered.response.received_at); })
        .filter(function (a) { return !(a.due && a.due.severity === "expired"); });
    }
    return (c.actions && c.actions.length) ? c.actions : (c.next_action ? [c.next_action] : []);
  }

  /** 지금 해야 할 행동 하나. 없으면 null.
   *
   * 답을 기다리는 중인 행동만 내린다. 답이 온 것은 그 건이 끝난 것이고, 그 답으로
   * 새 기한이 열릴 수 있다 — 불기소 통지를 받으면 항고 기한이 열리는 식이다.
   * 그래서 내고 → 답을 받고 → 다음 행동을 고르는 일이 계속 이어진다.
   */
  function activeAction(c) {
    var waiting = {};
    subsOf(c.id).forEach(function (s) { if (!s.response) waiting[s.action] = true; });
    var left = actionsNow(c).filter(function (a) { return !waiting[a.action]; });
    return left.length ? left[0] : null;
  }

  function isoDay(d) {
    return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  }

  function dotDay(iso) { return String(iso || "").split("-").join("."); }

  /** 낸 날부터 오늘까지 며칠. 답이 왔으면 세지 않는다(null). */
  function waitingDays(sub) {
    if (!sub || sub.response) return null;
    // 문자열을 Date 에 그대로 먹이지 않는다 — 브라우저마다 현지시각으로 읽는지가 갈린다.
    // 날짜 세 조각으로 직접 만들면 어디서나 같은 하루가 된다.
    var p = String(sub.submitted_at).split("-");
    if (p.length !== 3) return null;
    var from = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
    if (isNaN(from.getTime())) return null;
    var now = new Date();
    var days = Math.floor((new Date(now.getFullYear(), now.getMonth(), now.getDate()) - from) / 86400000);
    return days > 0 ? days : 0;
  }

  /** 낸 것 하나를 한 줄로. 화면 여러 곳에서 같은 문장을 쓴다. */
  function waitingText(sub) {
    if (sub.response) return dotDay(sub.response.received_at) + "에 회신 받음";
    var days = waitingDays(sub);
    if (days === null) return "회신 기다리는 중";
    return days === 0 ? "오늘 냈어요 · 회신 기다리는 중" : "회신 기다리는 중 · " + days + "일째";
  }

  // 「회신 왔어요」에서 고를 수 있는 답. 목록도 결과도 엔진이 내보낸 것을 그대로 쓴다.
  var UNKNOWN_CHOICE = "잘 모르겠어요";
  // 사건마다 엔진이 싣는 값이 먼저다(drawCase 에서 바꾼다). 없으면 엔진의 기본값과 같다.
  var SEVERITY_DAYS = { critical: 7, soon: 30 };

  /** 기한 = 통지 수령일 + 기간. 엔진이 하는 계산과 같은 식이다(rules.compute_deadlines). */
  function dueFrom(received, periodDays) {
    var p = String(received).split("-");
    if (p.length !== 3 || periodDays === null || periodDays === undefined) return null;
    var d = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]) + periodDays);
    var now = new Date();
    var left = Math.round((d - new Date(now.getFullYear(), now.getMonth(), now.getDate())) / 86400000);
    // 급한 정도를 가르는 기준도 엔진과 같다 — 팀 기준(deadlines.json 의 severity)을 엔진이 내보낸 값
    var bands = SEVERITY_DAYS;
    var sev = left < 0 ? "expired" : left <= bands.critical ? "critical" : left <= bands.soon ? "soon" : "ok";
    return {
      text: d.getFullYear() + "." + ("0" + (d.getMonth() + 1)).slice(-2) + "." + ("0" + d.getDate()).slice(-2) + "까지",
      days: left,
      severity: sev
    };
  }

  /** 기록한 답이 사건을 어떻게 바꾸는지. 엔진이 답마다 미리 내 준 결과에서 꺼낸다. */
  function outcomeOf(c, sub) {
    if (!sub.response || !sub.response.decision_type) return null;
    return (c.outcomes || {})[sub.response.decision_type] || null;
  }

  /** 「냈어요」 — 낸 날짜와 접수증을 받는다. 어디로도 보내지 않는다. */
  function openSubmitModal(c, action, done) {
    var maxDay = isoDay(new Date());
    var day = h("input", { id: "sub-day", type: "date", class: "field__input", value: maxDay, max: maxDay });
    var hint = h("p", { class: "field__hint", text: "" });

    var receipt = null;
    var picked = h("p", { class: "field__hint", text: "접수증이 없으면 낸 사실이 본인 말로만 남습니다." });
    var pick = h("button", { type: "button", class: "sub__btn t-body-s", text: "접수증 고르기" });
    pick.addEventListener("click", function () {
      pickFiles(function (files) {
        receipt = files[0].name;
        picked.textContent = "접수증 · " + receipt;
        picked.classList.remove("field__hint--warn");
      }, "image/*,application/pdf");
    });

    var save = h("button", { type: "button", class: "modal__save", text: "등록하기" });
    save.addEventListener("click", function () {
      if (!day.value) {
        hint.textContent = "낸 날짜를 골라 주세요.";
        hint.classList.add("field__hint--warn");
        day.focus();
        return;
      }
      putSub(c.id, {
        action: action.action,
        label: action.label,
        submitted_at: day.value,
        to: action.submit_to || null,
        form_name: action.form_name || null,
        receipt: receipt,
        response: null,
      });
      var dialog = document.querySelector("dialog.modal");
      if (dialog) dialog.close();
      done();
    });

    var rows = [h("p", { class: "t-body-m c-primary", text: action.label })];
    if (action.form_name) rows.push(h("p", { class: "t-body-s c-secondary", text: "무엇을 · " + action.form_name }));
    if (action.submit_to) rows.push(h("p", { class: "t-body-s c-secondary", text: "어디에 · " + action.submit_to }));

    openModal("냈어요", h("div", { class: "evform" }, [
      h("div", { class: "sub__what" }, rows),
      h("div", { class: "field" }, [h("label", { for: "sub-day", text: "언제 냈나요?" }), day, hint]),
      h("div", { class: "field" }, [
        h("span", { class: "t-body-s c-primary", text: "접수증 (선택)" }),
        pick,
        picked,
      ]),
      save,
      h("p", { class: "modal__note", text: "기록은 이 브라우저에만 남고 어디로도 보내지 않습니다. 회신 기한을 대신 판단하지는 않아요." }),
    ]));
  }

  /** 「회신 왔어요」 — 받은 날짜만 받는다. 어떤 결정인지는 통지서를 자료로 올려야 읽는다. */
  function openResponseModal(c, sub, done) {
    var maxDay = isoDay(new Date());
    var day = h("input", { id: "res-day", type: "date", class: "field__input", value: maxDay, min: sub.submitted_at, max: maxDay });
    var hint = h("p", { class: "field__hint", text: "통지서를 받은 날짜예요." });

    // 고를 수 있는 답은 엔진이 읽을 수 있는 말뿐이다 — 목록을 화면에서 지어내지 않는다
    var choices = (c.response_choices || []).concat([UNKNOWN_CHOICE]);
    var what = h("select", { id: "res-what", class: "field__input" },
      choices.map(function (name) { return h("option", { value: name, text: name }); }));
    what.value = UNKNOWN_CHOICE;
    var whatHint = h("p", { class: "field__hint", text: "통지서에 적힌 결정 이름이에요. 모르겠으면 그대로 두세요." });

    var save = h("button", { type: "button", class: "modal__save", text: "회신 받았다고 기록하기" });
    save.addEventListener("click", function () {
      if (!day.value) {
        hint.textContent = "받은 날짜를 골라 주세요.";
        hint.classList.add("field__hint--warn");
        day.focus();
        return;
      }
      sub.response = {
        received_at: day.value,
        decision_type: what.value === UNKNOWN_CHOICE ? null : what.value,
      };
      putSub(c.id, sub);
      var dialog = document.querySelector("dialog.modal");
      if (dialog) dialog.close();
      done();
    });

    openModal("회신 왔어요", h("div", { class: "evform" }, [
      h("p", { class: "t-body-m c-primary", text: sub.label }),
      h("p", { class: "t-body-s c-secondary", text: dotDay(sub.submitted_at) + "에 냈어요" }),
      h("div", { class: "field" }, [h("label", { for: "res-day", text: "언제 받았나요?" }), day, hint]),
      h("div", { class: "field" }, [h("label", { for: "res-what", text: "어떤 결정이었나요?" }), what, whatHint]),
      save,
      h("p", { class: "modal__note", text: "고른 결정으로 사건 단계와 다음 행동을 다시 계산합니다. 통지서를 자료로 올리면 기록으로 확인된 것으로 바뀝니다." }),
    ]));
  }

  /** 낸 것 목록. 하나도 없으면 아무것도 그리지 않는다. */
  function submittedCard(c, refresh) {
    var subs = subsOf(c.id);
    if (!subs.length) return null;

    var list = h("div", { class: "subs__list" }, subs.map(function (sub) {
      var waiting = h("p", { class: "sub__state t-body-s" + (sub.response ? " sub__state--done" : ""), text: waitingText(sub) });

      var actions = h("div", { class: "sub__buttons" });
      if (!sub.response) {
        var got = h("button", { type: "button", class: "sub__btn t-body-s", text: "회신 왔어요" });
        got.addEventListener("click", function () { openResponseModal(c, sub, refresh); });
        actions.appendChild(got);
      }
      var undo = h("button", { type: "button", class: "sub__undo t-body-s", text: "기록 지우기" });
      undo.addEventListener("click", function () { dropSub(c.id, sub.id); refresh(); });
      actions.appendChild(undo);

      // 받은 답이 사건을 어떻게 바꾸는지. 엔진이 답마다 미리 낸 결과를 그대로 읽는다.
      var outcome = outcomeOf(c, sub);
      var result = null;
      if (outcome) {
        var lines = [
          h("p", { class: "t-body-s", text: "사건 단계 · " + outcome.st }),
        ];
        (outcome.deadlines || []).forEach(function (t) {
          var due = dueFrom(sub.response.received_at, t.period_days);
          if (!due) return;
          lines.push(h("div", { class: "sub__due sev-" + due.severity }, [
            h("p", { class: "t-body-m-strong", text: t.label + " · " + due.text }),
            h("p", { class: "t-body-s", text: due.days < 0 ? "기한 지남" : "D-" + due.days }),
            t.submit_to ? h("p", { class: "t-body-s", text: "어디에 · " + t.submit_to }) : null,
            t.statute ? h("p", { class: "t-caption", text: t.statute }) : null,
          ]));
        });
        if (outcome.next) lines.push(h("p", { class: "t-body-s", text: "다음 행동 · " + outcome.next }));
        lines.push(h("p", { class: "t-caption sub__outcome-note", text: "고르신 결정으로 계산했어요. 통지서를 자료로 올리면 기록으로 확인된 것이 됩니다." }));
        result = h("div", { class: "sub__outcome" }, lines);
      }

      return h("div", { class: "sub" }, [
        h("p", { class: "sub__label t-body-m-strong", text: sub.label }),
        h("p", { class: "sub__when t-body-s", text: dotDay(sub.submitted_at) + "에 냄" + (sub.to ? " · " + sub.to : "") }),
        waiting,
        sub.response && sub.response.decision_type
          ? h("p", { class: "sub__answer t-body-m-strong", text: "받은 답 · " + sub.response.decision_type })
          : null,
        sub.receipt
          ? h("p", { class: "sub__receipt t-body-s", text: "접수증 · " + sub.receipt })
          : h("p", { class: "sub__receipt sub__receipt--none t-body-s", text: "낸 기록이 자료로 남아 있지 않아요 (접수증 없음)" }),
        result,
        actions,
      ]);
    }));

    var box = h("details", { class: "subs" }, [
      h("summary", { class: "subs__head" }, [
        h("span", { class: "t-label", text: "낸 것" }),
        h("span", { class: "subs__count t-label", text: String(subs.length) }),
        h("span", { class: "subs__chevron", "aria-hidden": "true" }),
      ]),
      list,
    ]);
    box.open = !!subsOpen[c.id];
    box.addEventListener("toggle", function () { subsOpen[c.id] = box.open; });
    return box;
  }

  // 사건마다 '낸 것'을 펼쳐 두었는지. 새로 그려도 닫히지 않게 기억한다(처음엔 접혀 있다)
  var subsOpen = {};

  // ── 서류 초안 ────────────────────────────────────────────────────────
  //
  // 엔진(action_engine.draft)이 조립한 것을 그대로 그린다. 화면에서 문장을 짓지 않는다.
  // 초안 표시는 뗄 수 없다 — 사람이 읽고 고치기 전에는 제출용이 아니다.

  var LEVEL_LABEL = { record: "기록", statement: "진술" };

  /** 복사해 갈 글. 화면에 보이는 것과 같은 내용이어야 한다. */
  function draftText(c, d) {
    var nl = String.fromCharCode(10);
    var lines = ["[초안] " + d.form_name, "사건 · " + c.title, ""];

    lines.push("■ 적을 것");
    d.fields.forEach(function (f) { lines.push("  " + f.label + ": " + f.value); });
    if (d.unfilled.length) {
      lines.push("");
      lines.push("■ 직접 적어야 하는 것");
      d.unfilled.forEach(function (f) { lines.push("  " + f.label + ": (" + f.reason + ")"); });
    }

    d.sections.forEach(function (sec) {
      lines.push("");
      lines.push("■ " + sec.heading);
      if (sec.heading === "사건 경위" && d.prose) {
        lines.push("  " + d.prose);
        lines.push("");
        lines.push("  (아래는 위 문장이 어느 자료에서 나왔는지입니다)");
      }
      if (!sec.lines.length && sec.note) lines.push("  (" + sec.note + ")");
      sec.lines.forEach(function (ln) {
        lines.push("  " + (ln.date ? ln.date + " " : "") + ln.text
          + "  [" + (LEVEL_LABEL[ln.level] || ln.level) + " · " + ln.source + "]");
      });
    });

    lines.push("");
    lines.push("※ 타래가 자료에서 뽑아 만든 초안입니다. 그대로 내지 마시고 읽어 보고 고쳐 주세요.");
    return lines.join(nl);
  }

  function draftModal(c, d) {
    var body = h("div", { class: "draft" }, [
      h("p", { class: "draft__badge t-label", text: "초안 · 그대로 내지 마세요" }),
      h("div", { class: "draft__head" }, [
        h("p", { class: "t-heading c-primary", text: d.form_name }),
        d.form_source ? h("p", { class: "t-body-s c-secondary", text: d.form_source }) : null,
        d.form_url
          ? h("a", { class: "draft__link t-body-s", href: d.form_url, target: "_blank", rel: "noopener", text: "공식 서식 내려받기" })
          : null,
      ]),
    ]);

    // 채운 칸 — 어디서 왔는지를 같이 적는다
    body.appendChild(h("p", { class: "draft__h t-label", text: "적을 것" }));
    body.appendChild(h("div", { class: "draft__fields" }, d.fields.map(function (f) {
      return h("div", { class: "draft__field" }, [
        h("span", { class: "draft__key t-caption", text: f.label }),
        h("span", { class: "draft__val t-body-s", text: f.value }),
        h("span", { class: "draft__from t-caption", text: f["from"] === "knowledge_base" ? "법령·서식" : "내 자료" }),
      ]);
    })));

    if (d.unfilled.length) {
      body.appendChild(h("p", { class: "draft__h t-label", text: "직접 적어야 하는 것" }));
      body.appendChild(h("div", { class: "draft__fields" }, d.unfilled.map(function (f) {
        return h("div", { class: "draft__field draft__field--blank" }, [
          h("span", { class: "draft__key t-caption", text: f.label }),
          h("span", { class: "draft__val t-body-s", text: f.reason }),
        ]);
      })));
    }

    d.sections.forEach(function (sec) {
      body.appendChild(h("p", { class: "draft__h t-label", text: sec.heading }));
      // 문장으로 엮은 것이 있으면 먼저 보여주고, 아래 줄들이 그 출처가 된다.
      // 없으면 줄만 나온다 — 그것만으로도 초안은 성립한다.
      if (sec.heading === "사건 경위" && d.prose) {
        body.appendChild(h("p", { class: "draft__prose t-body-m", text: d.prose }));
        body.appendChild(h("p", { class: "draft__note t-caption", text: "위 문장은 아래 줄에서만 만들었어요. 자료에 없는 말은 들어가지 않습니다." }));
      }
      if (sec.note) body.appendChild(h("p", { class: "draft__note t-body-s", text: sec.note }));
      if (!sec.lines.length) return;
      body.appendChild(h("ol", { class: "draft__lines" }, sec.lines.map(function (ln) {
        return h("li", { class: "draft__line draft__line--" + ln.level }, [
          h("span", { class: "draft__date t-caption", text: ln.date || "날짜 모름" }),
          h("span", { class: "draft__text t-body-s", text: ln.text }),
          h("span", { class: "draft__src t-caption", text: (LEVEL_LABEL[ln.level] || ln.level) + " · " + ln.source }),
        ]);
      })));
    });

    if (d.dropped) {
      body.appendChild(h("p", { class: "draft__note t-body-s", text: "출처를 달 수 없는 " + d.dropped + "건은 넣지 않았어요." }));
    }

    var text = draftText(c, d);
    var copy = h("button", { type: "button", class: "modal__save", text: "복사하기" });
    copy.addEventListener("click", function () {
      function done() { copy.textContent = "복사했어요"; setTimeout(function () { copy.textContent = "복사하기"; }, 1600); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
    });
    body.appendChild(copy);
    body.appendChild(h("p", { class: "modal__note", text: "자료에 있는 날짜와 문구만 모았습니다. 사유처럼 판단이 들어가는 칸은 비워 두었어요 — 타래는 대신 쓰지 않습니다." }));

    openModal("서류 초안", body);
  }

  function draftButton(c, next) {
    if (!next || !next.draft) return null;
    var button = h("button", { type: "button", class: "na__draft t-body-m-strong", text: "서류 초안 보기" });
    button.addEventListener("click", function () { draftModal(c, next.draft); });
    return button;
  }

  /** 카드 제목 아래 한 줄 — 무엇을 · 언제까지, 그리고 받은 답으로 바뀐 추천이면 어느 답 때문인지.
   *  '불복 절차'만으로는 이의제기서인지 항고장인지 재정신청서인지 모른다. */
  function nextActionSub(c, next) {
    var parts = [];
    if (next.form_name) parts.push(next.form_name);
    if (next.due && next.due.text) parts.push(next.due.text);
    var answered = latestAnswer(c);
    var lines = [];
    if (parts.length) lines.push(h("p", { class: "na__sub t-body-s", text: parts.join(" · ") }));
    if (answered && outcomeOf(c, answered)) {
      lines.push(h("p", { class: "na__basis t-caption", text: dotDay(answered.response.received_at) + "에 받은 '"
        + answered.response.decision_type + "' 회신으로 다시 고른 행동이에요" }));
    }
    return lines.length ? h("div", { class: "na__subs" }, lines) : null;
  }

  function nextActionCard(c, refresh) {
    var next = activeAction(c);
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

    // 낼 것이 없는 단계에는 제출 버튼을 붙이지 않는다 — 엔진이 제출 절차가 아니라고 한 자리다.
    // 버튼은 무엇을·어디에가 적힌 팝업 안에 둔다. 카드만 보고 누르면 무엇을 냈는지 모른 채 누른다.
    function submitButton() {
      if (next.state === "no_submission") return null;
      var did = h("button", { type: "button", class: "modal__act t-body-m-strong", text: "제출했어요" });
      did.addEventListener("click", function () {
        var dialog = document.querySelector("dialog.modal");
        if (dialog) dialog.close();
        openSubmitModal(c, next, refresh);
      });
      return did;
    }

    var more = h("button", { type: "button", class: "na__more t-body-m-strong", text: "자세히 보기" });
    more.addEventListener("click", function () { openModal(next.label, detailBody(), submitButton()); });

    return h("section", { class: "next-action", "aria-labelledby": "na-title" }, [
      h("div", { class: "next-action__head" }, [
        h("span", { class: "t-label", text: "다음 행동" }),
        next.due
          ? h("span", { class: "na__due t-label", text: next.due.label })
          : next.unverified ? h("span", { class: "t-caption", text: "검수 전 안내" }) : null,
      ]),
      h("h2", { id: "na-title", class: "na__title", text: next.label }),
      nextActionSub(c, next),
      h("div", { class: "na__buttons" }, [more]),
      draftButton(c, next),
    ]);
  }

  /** 평소엔 버튼 한 줄로 접혀 있고, 누르면 아래로 펼쳐진다. */
  function issuesCard(c) {
    var list = h("div", { class: "issues__list", hidden: true });
    var visibleGroups = visibleIssues(c);
    var visibleCount = visibleGroups.reduce(function (sum, g) { return sum + g.items.length; }, 0);

    visibleGroups.forEach(function (g) {
      list.appendChild(h("p", { class: "issue-group__head t-label sev-" + g.severity }, [
        h("span", { class: "issue-group__dot" }),
        h("span", { text: g.label }),
        h("span", { class: "issue-group__count", text: String(g.items.length) }),
      ]));
      g.items.forEach(function (it) {
        list.appendChild(h("div", { class: "issue issue--" + g.severity, "data-kind": it.kind || null }, [
          h("p", { class: "issue__text", text: it.text }),
          it.how ? h("p", { class: "issue__how", text: it.how }) : null,
        ]));
      });
    });

    var toggle = h("button", { type: "button", class: "issues__toggle", "aria-expanded": "false" }, [
      h("span", { class: "issues__mark", "aria-hidden": "true", text: "!" }),
      h("span", { class: "issues__label", text: "확인이 필요해요" }),
      h("span", { class: "issues__count", text: String(visibleCount) }),
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
  };

  /** 상담에 가져갈 질문지를 만든다 — 사건 요약 + 확인이 필요한 것 + 다음 행동. */
  function askSheet(c) {
    var lines = [];
    lines.push("[사건] " + c.title + " (" + c.type_label + ")");
    lines.push("[기간] " + c.period + " · 자료 " + c.sources.length + "개 · 확인 필요 " + visibleIssueCount(c));
    lines.push("");

    visibleIssues(c).forEach(function (g) {
      var frame = ASK_FRAME[g.label] || "이 부분을 어떻게 보면 될까요?";
      lines.push("■ " + g.label + " — " + frame);
      g.items.forEach(function (it) {
        lines.push("  · " + it.text + (it.how ? " (" + it.how + ")" : ""));
      });
      lines.push("");
    });

    var next = activeAction(c);
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
    var button = h("button", { type: "button", class: "issues__ask" }, [
      h("span", { text: "전문가에게 물어볼 질문" }),
      icon("chevron-right", "18"),
    ]);
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
        h("p", { class: "ask__lead", text: "지금 화면에 올라온 내용에서 뽑았어요. 상담 전에 읽어 보고 빼거나 더할 수 있어요." }),
        area,
        copy,
      ]));
    });
    return button;
  }

  /* 올린 원본을 그대로 띄운다.
   *
   * 사진이면 사진을, OCR 결과 JSON 이면 읽은 글자를 보여준다. 정리된 화면만 보면
   * '엔진이 뭘 보고 이렇게 말하는지'를 확인할 길이 없다.
   *
   * 예시 사건에는 올린 파일이 없다(href 가 없다). 그때는 누를 수 없게 그린다 —
   * 눌러도 아무 일이 없는 것보다 낫다.
   */
  function originalModal(src) {
    var body = h("div", { class: "orig" });
    var loading = h("p", { class: "orig__note t-body-s c-tertiary", text: "여는 중…" });
    body.appendChild(loading);

    function fail(message) {
      loading.textContent = message;
      loading.className = "orig__note orig__note--warn t-body-s";
    }

    if (src.media === "application/json") {
      // OCR 결과는 그림이 아니라 읽은 글자다. 줄 번호를 붙여 두면 '몇 줄' 이 바로 짚어진다.
      api(src.href).then(function (doc) {
        var lines = [];
        (doc.pages || []).forEach(function (page) {
          (page.lines || []).forEach(function (line) { lines.push(line.text); });
        });
        loading.remove();
        if (!lines.length) return fail("읽은 글자가 없어요.");
        body.appendChild(h("ol", { class: "orig__lines" }, lines.map(function (t) {
          return h("li", { class: "orig__line t-body-s", text: t });
        })));
      }, function (err) { fail(errorText(err)); });
    } else {
      var img = h("img", { class: "orig__img", alt: src.name, src: src.href });
      img.addEventListener("load", function () { loading.remove(); });
      img.addEventListener("error", function () { fail("원본을 열지 못했어요."); });
      body.appendChild(img);
    }

    body.appendChild(h("p", { class: "modal__note", text: "올릴 때 받은 그대로예요. 이 컴퓨터 밖으로 나가지 않습니다." }));
    openModal(src.name, body);
  }

  function sourceListModal(c) {
    openModal("첨부한 자료 " + c.sources.length + "개", h("div", {}, [
      h("ul", { class: "srclist" }, c.sources.map(function (s) {
        var parts = [
          h("span", { class: "srclist__kind t-caption", text: s.kind }),
          h("span", { class: "t-body-m c-primary", text: s.name }),
          s.isNew ? h("span", { class: "srclist__new", text: "방금 추가" }) : null,
        ];
        if (!s.href) {
          parts.push(h("span", { class: "srclist__none t-caption", text: "원본 없음" }));
          return h("li", { class: "srclist__item srclist__item--none" + (s.isNew ? " srclist__item--new" : "") }, parts);
        }

        parts.push(h("span", { class: "srclist__open t-caption", text: "원본 보기" }));
        var item = h("button", { type: "button", class: "srclist__item srclist__item--open" }, parts);
        item.addEventListener("click", function () { originalModal(s); });
        return h("li", {}, [item]);
      })),
      h("p", { class: "modal__note", text: isLocal(c)
        ? "이름을 누르면 올린 원본을 볼 수 있어요. 자료를 더하면 올린 자료 전체로 사건을 처음부터 다시 정리해요."
        : "예시 사건이라 올린 원본이 없어요. 내 자료로 보려면 새 사건을 등록해 주세요." }),
    ]));
  }

  /** 자료는 목록으로 늘어놓지 않고 버튼 뒤에 둔다. */
  function sourcesBar(c, vertical) {
    var count = h("span", { class: "srcbar__count", text: String(c.sources.length) });

    var open = h("button", { type: "button", class: "srcbar__btn" }, [
      icon("document", "18"),
      h("span", { text: "첨부한 자료" }),
      count,
      icon("chevron-right", "18"),
    ]);
    open.addEventListener("click", function () { sourceListModal(c); });

    var add = h("button", { type: "button", class: "srcbar__btn srcbar__btn--add" }, [
      icon("plus", "18"),
      h("span", { text: "자료 추가하기" }),
    ]);
    add.addEventListener("click", function () {
      if (!isLocal(c)) {
        openModal("자료 추가하기", h("div", { class: "help" }, [
          h("p", { class: "help__text", text: "예시 사건이라 자료를 더할 수 없어요. 내 자료로 정리해 보려면 새 사건을 등록해 주세요." }),
          h("a", { class: "btn btn--primary t-body-m-strong", href: "new.html", text: "새 사건 등록" }),
        ]));
        return;
      }
      pickFiles(addFiles);
    });

    /** 고른 자료를 서버에 보내 사건 전체를 다시 정리하고, 끝나면 새 결과로 화면을 다시 그린다. */
    function addFiles(picked) {
      var skipped = picked.filter(function (f) { return !canRead(f.name); }).map(function (f) { return f.name; });
      var readable = picked.filter(function (f) { return canRead(f.name); });
      var message = h("p", { class: "help__text", role: "status" });
      openModal("자료 추가하기", h("div", { class: "help" }, [
        message,
        skipped.length ? h("p", { class: "help__text field__hint--warn", text: "읽을 수 없는 형식이라 뺐어요: " + skipped.join(", ") }) : null,
      ]));
      if (!readable.length) {
        message.textContent = "더할 자료가 없어요. 사진이나 OCR 결과 JSON 을 골라 주세요.";
        return;
      }
      message.textContent = readable.length + "개 자료를 읽고 사건을 다시 정리하고 있어요…";
      uploadForm("api/cases/" + encodeURIComponent(c.id) + "/files", {}, readable).then(function () {
        location.reload();
      }, function (err) {
        message.textContent = errorText(err);
        message.classList.add("field__hint--warn");
      });
    }
    addFilesHandler = addFiles;   // 상단 메뉴의 '자료 추가하기'도 같은 일을 한다

    return h("div", { class: "srcbar" + (vertical ? " srcbar--stack" : "") }, [add, open]);
  }

  /* 둘러보기 안내 — 시연 사건 위에 다는 번호 띠. 누르면 그 자리로 옮겨 잠깐 빛낸다.
   *
   * 화면을 가리는 단계별 안내 대신 띠를 둔다: 순서를 강요하지 않고, 닫으면 다시 뜨지 않는다.
   * 어떤 사건에 달지는 화면 데이터의 guide 로 정한다(export_web.py · 사이트에-올릴-사건.json).
   */
  var GUIDE_KEY = "tarae.guide.closed.v1";

  var GUIDE_STEPS = [
    { title: "기록이 빈 기간", text: "수사중지 뒤 몇 년씩 아무 기록이 없는 구간을 짚어요",
      find: function () { var gaps = document.querySelectorAll(".tl__gap"); return gaps[gaps.length - 1]; } },
    { title: "자료끼리 어긋난 곳", text: "같은 날을 자료마다 다르게 적은 곳을 찾아요", issues: true,
      find: function () {
        return document.querySelector('.issue[data-kind="conflicting"], .issue[data-kind="suspected_conflict"]')
          || document.querySelector(".issue");
      } },
    { title: "지금 할 일 하나", text: "놓치면 안 되는 것부터 골라 이유와 함께 보여 줘요",
      find: function () { return document.querySelector(".next-action"); } },
    { title: "서류 초안", text: "자료에 적힌 것만 모아 낼 서류의 초안을 만들어요",
      find: function () { return document.querySelector(".na__draft"); } },
  ];

  function guideClosed() {
    try { return localStorage.getItem(GUIDE_KEY) === "1"; } catch (e) { return false; }
  }

  function guideBand(showTimeline) {
    if (guideClosed()) return null;

    function spot(step) {
      showTimeline();
      if (step.issues) {
        var toggle = document.querySelector(".issues__toggle");
        if (toggle && toggle.getAttribute("aria-expanded") !== "true") toggle.click();
      }
      var target = step.find();
      if (!target) return;
      var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      target.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "center" });
      target.classList.remove("guide-spot");
      void target.offsetWidth;
      target.classList.add("guide-spot");
      setTimeout(function () { target.classList.remove("guide-spot"); }, 2600);
    }

    var close = h("button", { type: "button", class: "guide__close", "aria-label": "안내 닫기", text: "✕" });
    var band = h("section", { class: "guide", "aria-label": "둘러보기 안내" }, [
      h("div", { class: "guide__head" }, [
        h("p", { class: "guide__lead t-body-m-strong", text: "[가이드라인] 이 순서로 둘러보세요 — 누르면 확인할 수 있어요" }),
        close,
      ]),
      h("ol", { class: "guide__steps" }, GUIDE_STEPS.map(function (step, i) {
        var button = h("button", { type: "button", class: "guide__step" }, [
          h("span", { class: "guide__num", "aria-hidden": "true", text: String(i + 1) }),
          h("span", { class: "guide__body" }, [
            h("span", { class: "guide__title t-body-m-strong", text: step.title }),
            h("span", { class: "guide__text t-body-s", text: step.text }),
          ]),
        ]);
        button.addEventListener("click", function () {
          button.classList.add("guide__step--seen");
          spot(step);
        });
        return h("li", {}, [button]);
      })),
    ]);
    close.addEventListener("click", function () {
      try { localStorage.setItem(GUIDE_KEY, "1"); } catch (e) { /* 저장이 막히면 이번 화면에서만 닫는다 */ }
      band.remove();
    });
    return band;
  }

  function renderCase(root) {
    var id = new URLSearchParams(location.search).get("id");
    function notFound() {
      root.appendChild(h("main", { class: "page page--case" }, [backLink(), h("p", { class: "t-body-l", text: "사건을 찾지 못했어요." })]));
    }
    // 예전에는 id 가 맞지 않으면 첫 예시 사건을 대신 보여줬다 — 남의 사건을 내 사건으로 읽게 된다
    var demo = CASES.filter(function (x) { return x.id === id; })[0];
    if (demo) return drawCase(root, demo);
    if (!id) return notFound();
    api("api/cases/" + encodeURIComponent(id)).then(function (view) { drawCase(root, view); }, notFound);
  }

  /** 탭을 옮기면 종이가 한 장 넘어간 것처럼 보이게 한다.
      같은 애니메이션을 다시 걸려면 클래스를 뗀 뒤 리플로우를 한 번 일으켜야 한다. */
  function turnPage(node) {
    node.classList.remove("panel--turn");
    void node.offsetWidth;
    node.classList.add("panel--turn");
  }

  function drawCase(root, c) {
    document.title = c.title + " · 타래";

    if (c.severity_days) SEVERITY_DAYS = c.severity_days;
    var panel = h("div", { role: "tabpanel", id: "panel" }, [timelineCard(c)]);
    var rail = h("aside", { class: "rail" });
    var tabIndex = 0;

    // 내거나 답을 받으면 옆 카드만이 아니라 타임라인도 다시 그린다 — 거기에 낸 것 · 다음 행동이 올라가 있다
    function refresh() {
      fillSide(tabIndex);
      if (tabIndex !== 0) return;
      panel.textContent = "";
      panel.appendChild(timelineCard(c));
    }

    // 다음 행동·확인이 필요해요는 타임라인에서만 본다. 인물·주장 탭에서는
    // 그 화면에서 실제로 쓰는 것(자료 · 전문가 질문)만 옆에 둔다.
    function fillSide(index) {
      // 그릴 것이 없으면 null 을 돌려주는 카드가 있다(낸 것 · 다음 행동).
      // appendChild 는 null 을 받으면 예외를 던지고 화면 전체가 비어 버린다.
      function put(node) {
        if (node) rail.appendChild(node);
      }

      rail.textContent = "";
      // 자료는 어느 탭에서나 같은 자리(맨 위)에 둔다
      put(sourcesBar(c, true));
      if (index === 0) {
        put(nextActionCard(c, refresh));
        put(submittedCard(c, refresh));
        put(issuesCard(c));
      } else {
        put(askButton(c));
      }
    }

    var tabNames = ["타임라인", "인물 · 관계", "주장 대조"];
    var tabs = h("div", { class: "tabs", role: "tablist" }, tabNames.map(function (name, i) {
      var tab = h("button", { type: "button", class: "tab", role: "tab", "aria-selected": i === 0 ? "true" : "false", "aria-controls": "panel", text: name });
      tab.addEventListener("click", function () {
        tabs.querySelectorAll(".tab").forEach(function (t) { t.setAttribute("aria-selected", "false"); });
        tab.setAttribute("aria-selected", "true");
        tabIndex = i;
        panel.textContent = "";
        panel.appendChild(i === 0 ? timelineCard(c) : i === 1 ? peopleCard(c) : slotsCard(c));
        turnPage(panel);
        fillSide(i);
      });
      return tab;
    }));
    fillSide(0);

    function showTimeline() {
      var first = tabs.querySelector(".tab");
      if (first.getAttribute("aria-selected") !== "true") first.click();
    }

    root.appendChild(h("div", { class: "disclaimer" }, [
      icon("info", 18),
      h("p", { class: "t-body-s c-secondary", text: "타래는 범인이나 사건의 진실을 판단하지 않습니다." }),
    ]));
    root.appendChild(h("main", { class: "page page--case" }, [
      backLink(),
      c.guide ? guideBand(showTimeline) : null,
      // 목록에서 고른 폴더를 펼친 화면 — 탭과 색을 그대로 물려받는다
      h("section", { class: "case-folder folder--tone" + toneOf(c) }, [
        h("span", { class: "case-folder__tab" }, [h("span", { class: "t-label", text: c.type_label })]),
        h("div", { class: "case-folder__body" }, [
          h("div", { class: "case-head__info" }, [
            h("div", { class: "case-head__tags" }, [
              h("span", { class: "t-caption case-folder__dim", text: "기준일 " + c.as_of }),
              // 기한은 폴더 앞면에서와 같이 항상 보이게 둔다
              activeAction(c) && activeAction(c).due
                ? h("span", { class: "case-folder__due t-label", text: activeAction(c).due.label })
                : null,
            ]),
            h("h1", { class: "t-display", text: c.title }),
            h("p", { class: "case-head__meta t-body-m case-folder__dim", text: c.period + "  ·  자료 " + c.doc_count + "개  ·  확인 필요 " + visibleIssueCount(c) }),
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
