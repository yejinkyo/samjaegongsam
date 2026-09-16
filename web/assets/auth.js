/* 로그인 · 회원가입 폼.
 *
 * 서버가 없다. 그래서 입력값을 어디로도 보내지 않는다 — 비밀번호를 다루는 화면이라
 * '되는 척'을 만들지 않는 편이 안전하다. **비밀번호는 저장하지 않는다.**
 *
 * 이 브라우저에 남기는 것은 아이디와 '데모 계정인가' 하나뿐이다. 그게 없으면
 * 새로 가입한 사람에게도 데모 사건이 보이고, 남의 사건을 자기 것으로 읽게 된다.
 */
(function () {
  "use strict";

  // 서버가 없어 진짜 인증은 없다. 발표·시연에서 쓸 계정 하나만 화면 안에서 맞춰 본다.
  var DEMO = { username: "삼재공삼", password: "삼재공삼" };

  /* 다음 화면이 누구를 보여줄지만 남긴다. 비밀번호는 담지 않는다.
   *
   * 가입한 사람에게 데모 사건을 보여주면 남의 사건을 자기 것으로 읽는다.
   * demo:false 면 사건 목록이 빈 서류함에서 시작한다(app.js 의 showsDemo). */
  var SESSION_KEY = "tarae.session";

  function remember(name, isDemo) {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({ name: name, demo: isDemo }));
    } catch (e) { /* 저장이 막혀도 화면은 넘어간다 */ }
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

  document.addEventListener("DOMContentLoaded", function () {
    var page = document.body.getAttribute("data-page");
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

      if (page === "login") {
        var pw = form.querySelector("#password").value;
        if (name !== DEMO.username || pw !== DEMO.password) {
          show("password", "아이디나 비밀번호가 달라요. 데모 계정은 삼재공삼 / 삼재공삼 이에요.", defaults.password);
          form.querySelector("#password").focus();
          return;
        }
        remember(DEMO.username, true);          // 데모 사건이 들어 있는 화면
      } else {
        remember(name, false);                  // 막 만든 계정 — 빈 서류함에서 시작한다
      }

      // 비밀번호는 어디에도 남기지 않는다
      form.reset();
      location.href = "cases.html";
    });
  });
})();
