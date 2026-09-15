/* 로그인 · 회원가입 폼.
 *
 * 서버가 없다. 그래서 입력값을 어디로도 보내지 않고 저장하지도 않는다 —
 * 비밀번호를 다루는 화면이라 '되는 척'을 만들지 않는 편이 안전하다.
 * 지금 하는 일은 빈칸·길이 확인과, 통과하면 사건 목록으로 보내는 것뿐이다.
 */
(function () {
  "use strict";

  // 서버가 없어 진짜 인증은 없다. 발표·시연에서 쓸 계정 하나만 화면 안에서 맞춰 본다.
  var DEMO = { username: "삼재공삼", password: "삼재공삼" };

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

      if (page === "login") {
        var id = form.querySelector("#username").value.trim();
        var pw = form.querySelector("#password").value;
        if (id !== DEMO.username || pw !== DEMO.password) {
          show("password", "아이디나 비밀번호가 달라요. 데모 계정은 삼재공삼 / 삼재공삼 이에요.", defaults.password);
          form.querySelector("#password").focus();
          return;
        }
      }

      // 입력값은 들고 가지 않는다 — 데모 사건 목록으로만 이동한다
      form.reset();
      location.href = "cases.html";
    });
  });
})();
