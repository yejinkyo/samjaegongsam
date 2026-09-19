/* 「로그인 없이 둘러보기」 — 심사 · 시연에서 계정 없이 바로 예시 사건으로 들어간다.
 *
 * 로그인하지 않은 화면은 원래 예시 사건을 보여 준다(app.js 의 showsDemo). 다만 이 브라우저에서
 * 전에 가입해 들어온 적이 있으면 '빈 서류함' 기록이 남아 있어 예시 사건이 안 보인다.
 * 그래서 누르면 '예시 사건을 보는 중'으로 기록을 바꾸고 사건 목록으로 간다.
 */
(function () {
  "use strict";

  document.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest("[data-browse]");
    if (!link) return;
    try {
      localStorage.setItem("tarae.session", JSON.stringify({ name: "", demo: true }));
    } catch (e) { /* 저장이 막혀도 예시 사건은 보인다 — 기록이 없으면 예시 사건을 보여 준다 */ }
  });
})();
