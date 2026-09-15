/* 시작 화면의 실 그림.
 *
 * 가운데 몇 개의 매듭에서 실이 뻗어 나가고, 마디마다 다른 박자로 반짝인다.
 * 같은 그림이 매번 나오도록 난수는 씨앗을 고정해서 쓴다.
 */
(function () {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";
  var W = 520;
  var H = 520;

  /** 씨앗 고정 난수 — 새로고침해도 같은 그림이 나온다 */
  function rng(seed) {
    var s = seed;
    return function () {
      s = (s * 1103515245 + 12345) % 2147483648;
      return s / 2147483648;
    };
  }

  function el(name, attrs) {
    var node = document.createElementNS(NS, name);
    Object.keys(attrs).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    return node;
  }

  function build() {
    var host = document.getElementById("net");
    if (!host) return;

    var rand = rng(20260915);
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "presentation" });
    var threads = el("g", {});
    var nodes = el("g", {});
    svg.appendChild(threads);
    svg.appendChild(nodes);

    // 매듭 — 실이 모였다 갈라지는 자리
    var hubs = [
      { x: 250, y: 250, r: 5 },
      { x: 150, y: 150, r: 3.5 },
      { x: 370, y: 190, r: 3.5 },
      { x: 320, y: 380, r: 3.5 },
      { x: 130, y: 350, r: 3 },
    ];

    // 매듭끼리 잇는 실
    [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [3, 4]].forEach(function (pair, i) {
      var a = hubs[pair[0]];
      var b = hubs[pair[1]];
      var mx = (a.x + b.x) / 2 + (rand() - 0.5) * 60;
      var my = (a.y + b.y) / 2 + (rand() - 0.5) * 60;
      var path = el("path", { class: "thread", d: "M" + a.x + " " + a.y + " Q" + mx + " " + my + " " + b.x + " " + b.y });
      path.style.animationDelay = (i * 0.6).toFixed(2) + "s";
      threads.appendChild(path);
    });

    // 매듭에서 바깥으로 뻗는 실과 그 끝의 마디
    var tips = [];
    hubs.forEach(function (hub, hi) {
      var count = hi === 0 ? 7 : 4;
      for (var i = 0; i < count; i++) {
        var angle = rand() * Math.PI * 2;
        var len = 70 + rand() * 150;
        var x = hub.x + Math.cos(angle) * len;
        var y = hub.y + Math.sin(angle) * len;
        var cx = hub.x + Math.cos(angle) * len * 0.55 + (rand() - 0.5) * 50;
        var cy = hub.y + Math.sin(angle) * len * 0.55 + (rand() - 0.5) * 50;
        var path = el("path", { class: "thread", d: "M" + hub.x + " " + hub.y + " Q" + cx + " " + cy + " " + x + " " + y });
        path.style.animationDelay = (rand() * 5).toFixed(2) + "s";
        threads.appendChild(path);
        tips.push({ x: x, y: y, r: 1.6 + rand() * 2 });
      }
    });

    tips.concat(hubs.map(function (hub) { return { x: hub.x, y: hub.y, r: hub.r, hub: true }; }))
      .forEach(function (n) {
        var circle = el("circle", { class: "node" + (n.hub ? " node--hub" : ""), cx: n.x, cy: n.y, r: n.r });
        circle.style.animationDelay = (rand() * 4.5).toFixed(2) + "s";
        nodes.appendChild(circle);
      });

    host.appendChild(svg);
  }

  document.addEventListener("DOMContentLoaded", build);
})();
