/* 로그인 · 회원가입 폼.
 *
 * 서버가 없다. 그래서 입력값을 **어디로도 보내지 않는다.** 가입한 계정은 이 브라우저
 * 안에만 있고, 다른 기기에서는 보이지 않는다. 진짜 인증이 아니다.
 *
 * 비밀번호는 그대로 적어 두지 않는다(scramble 참고). 그건 보안이 아니라 최소한의
 * 예의다 — 데모라도 사람들은 다른 곳에서 쓰는 비밀번호를 그대로 넣는다.
 *
 * 남기는 것은 두 가지다.
 *   tarae.account — 이 브라우저에서 가입한 계정 (아이디 + 대조용 숫자)
 *   tarae.session — 지금 누구로 보고 있는가 (아이디 + 데모 계정인가)
 *
 * session 이 없으면 데모 사건이 보인다. 가입해서 들어오면 빈 서류함에서 시작한다 —
 * 그러지 않으면 처음 쓰는 사람이 남의 사건을 자기 것으로 읽는다.
 */
(function () {
  "use strict";

  // 서버가 없어 진짜 인증은 없다. 발표·시연에서 쓸 계정 하나만 화면 안에서 맞춰 본다.
  var DEMO = { username: "삼재공삼", password: "삼재공삼" };

  /* 다음 화면이 누구를 보여줄지 남긴다.
   *
   * 가입한 사람에게 데모 사건을 보여주면 남의 사건을 자기 것으로 읽는다.
   * demo:false 면 사건 목록이 빈 서류함에서 시작한다(app.js 의 showsDemo). */
  var SESSION_KEY = "tarae.session";
  var ACCOUNT_KEY = "tarae.account";

  function remember(name, isDemo) {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({ name: name, demo: isDemo }));
    } catch (e) { /* 저장이 막혀도 화면은 넘어간다 */ }
  }

  /* 가입한 계정을 이 브라우저에만 둔다.
   *
   * 여기서 하는 것은 **보안이 아니다.** 서버가 없어서 진짜 인증을 할 수가 없고,
   * 브라우저에 있는 값은 누구나 열어 볼 수 있다. 아래 숫자는 비밀번호를 지키려는 것이
   * 아니라 **그대로 적어 두지 않으려는 것**뿐이다 — 사람들은 다른 곳에서 쓰는 비밀번호를
   * 그대로 넣기 때문에, 데모라도 평문으로 남기면 안 된다.
   *
   * 실제 서비스에서는 이 확인이 전부 서버에서 일어나야 한다. */
  function scramble(text) {
    var hash = 2166136261;                       // FNV-1a
    for (var i = 0; i < text.length; i++) {
      hash ^= text.charCodeAt(i);
      hash = (hash * 16777619) >>> 0;
    }
    return String(hash);
  }

  function saveAccount(name, password) {
    try {
      localStorage.setItem(ACCOUNT_KEY, JSON.stringify({ name: name, check: scramble(name + ":" + password) }));
    } catch (e) { /* 저장이 막혀도 화면은 넘어간다 */ }
  }

  function matchesAccount(name, password) {
    try {
      var saved = JSON.parse(localStorage.getItem(ACCOUNT_KEY));
      return Boolean(saved) && saved.name === name && saved.check === scramble(name + ":" + password);
    } catch (e) {
      return false;
    }
  }

  var RULES = {
    username: function (v) {
      if (!v) return "아이디를 입력해 주세요.";
      if (v.length < 4) return "4자 이상으로 만들어 주세요.";
      return null;
    },
    password: function (v, page) {
      if (!v) return "비밀번호를 입력해 주세요.";
      if (page === "signup" && v.length < 8) return "8자 이상으로 만들어 주세요.";
      return null;
    },
    birth: function (v) {
      if (!v) return "생년월일을 입력해 주세요.";
      if (new Date(v) > new Date()) return "오늘보다 뒤의 날짜예요.";
      return null;
    },
  };

  function hintFor(name) { return document.querySelector('[data-hint="' + name + '"]'); }

  function show(name, message, fallback) {
    var hint = hintFor(name);
    if (!hint) return;
    hint.textContent = message || fallback || "";
    hint.classList.toggle("field__hint--warn", Boolean(message));
  }

  /* 간편 가입은 아직 되지 않는다.
   *
   * 카카오·네이버·구글 로그인은 받은 코드를 앱 비밀키와 함께 그쪽 서버에 보내
   * 토큰으로 바꾸는 단계가 있다. 그 비밀키는 화면에 둘 수 없다 — 누구나 열어 볼 수
   * 있어서, 두는 순간 남이 우리 앱 행세를 할 수 있다. 그래서 서버가 생기기 전에는
   * 만들 수 없다. 되는 척하는 버튼을 두는 대신 왜 안 되는지 적는다.
   */
  function wireSocial() {
    document.querySelectorAll("[data-social]").forEach(function (button) {
      button.addEventListener("click", function () {
        var note = document.querySelector(".social__note");
        if (note) {
          note.textContent = "준비 중입니다.";
          note.classList.add("social__note--warn");
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var page = document.body.getAttribute("data-page");
    wireSocial();
    var form = document.querySelector(".auth__form");
    if (!form) return;

    // 처음 안내 문구를 기억해 뒀다가, 오류를 고치면 그 문구로 되돌린다
    var defaults = {};
    form.querySelectorAll("[data-hint]").forEach(function (hint) {
      defaults[hint.getAttribute("data-hint")] = hint.textContent;
    });

    function check(input) {
      var rule = RULES[input.name];
      if (!rule) return null;
      var message = rule(input.value.trim(), page);
      show(input.name, message, defaults[input.name]);
      return message;
    }

    form.querySelectorAll("input").forEach(function (input) {
      input.addEventListener("blur", function () { check(input); });
      input.addEventListener("input", function () {
        if (hintFor(input.name) && hintFor(input.name).classList.contains("field__hint--warn")) check(input);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();   // 어디로도 보내지 않는다
      var first = null;
      form.querySelectorAll("input").forEach(function (input) {
        var message = check(input);
        if (message && !first) first = input;
      });
      if (first) {
        first.focus();
        return;
      }

      var name = (form.querySelector("#username") || {}).value;
      name = (name || "").trim();

      var pw = form.querySelector("#password").value;

      if (page === "login") {
        if (name === DEMO.username && pw === DEMO.password) {
          remember(DEMO.username, true);        // 데모 사건이 들어 있는 화면
        } else if (matchesAccount(name, pw)) {
          remember(name, false);                // 이 브라우저에서 가입한 계정 — 빈 서류함
        } else {
          show("password", "아이디나 비밀번호가 달라요. 이 브라우저에서 가입한 계정이거나 데모 계정(삼재공삼 / 삼재공삼)만 들어갈 수 있어요.", defaults.password);
          form.querySelector("#password").focus();
          return;
        }
      } else {
        saveAccount(name, pw);                  // 다시 로그인할 수 있게 이 브라우저에만 둔다
        remember(name, false);                  // 막 만든 계정 — 빈 서류함에서 시작한다
      }

      // 비밀번호는 어디에도 남기지 않는다
      form.reset();
      location.href = "cases.html";
    });
  });
})();
