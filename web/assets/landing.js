/* 시작 화면의 실 그림.
 *
 * 곡선이 아니라 곧은 선으로 엮는다 — 자료와 자료가 어떻게 이어지는지를 보여주는
 * 그림이라 부드러운 것보다 날카로운 쪽이 맞다. 가까운 마디끼리 잇고, 매듭에서는
 * 화면을 가로지르는 긴 선을 뻗는다.
 * 같은 그림이 매번 나오도록 난수는 씨앗을 고정해서 쓴다.
 */
(function () {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";
  var W = 520;
  var H = 520;

  // 마디 색 — 왼쪽(핑크)에서 오른쪽(남색)으로 옮겨 가게 x 좌표로 고른다
  var NODE_TONES = ["node--pink", "node--violet", "node--navy"];

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

  function toneFor(x, rand) {
    var t = x / W + (rand() - 0.5) * 0.3;   // 경계가 칼같지 않게 흔든다
    return NODE_TONES[t < 0.36 ? 0 : t < 0.68 ? 1 : 2];
  }

  function build() {
    var host = document.getElementById("net");
    if (!host) return;

    var rand = rng(20260915);
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "presentation" });
    var threads = el("g", {});
    var rings = el("g", {});
    var nodes = el("g", {});
    svg.appendChild(threads);
    svg.appendChild(rings);
    svg.appendChild(nodes);

    // ── 마디 자리 잡기 ────────────────────────────────
    // 매듭 몇 개를 두고 그 둘레에 흩뿌린다. 가장자리에도 몇 개 흘려 성글게 만든다.
    var hubs = [
      { x: 250, y: 250 }, { x: 150, y: 165 }, { x: 360, y: 190 },
      { x: 330, y: 370 }, { x: 140, y: 350 }, { x: 430, y: 290 }, { x: 215, y: 435 },
    ];
    var points = hubs.map(function (p) { return { x: p.x, y: p.y, hub: true, deg: 0 }; });

    hubs.forEach(function (hub) {
      var count = 5 + Math.floor(rand() * 4);
      for (var i = 0; i < count; i++) {
        var angle = rand() * Math.PI * 2;
        var len = 40 + rand() * 120;
        points.push({ x: hub.x + Math.cos(angle) * len, y: hub.y + Math.sin(angle) * len, deg: 0 });
      }
    });
    for (var i = 0; i < 26; i++) {
      points.push({ x: rand() * W, y: rand() * H, deg: 0 });
    }

    // ── 가까운 것끼리 곧은 선으로 잇기 ────────────────
    var seen = {};
    function link(a, b, faint) {
      if (a === b) return;
      var key = Math.min(a, b) + ":" + Math.max(a, b);
      if (seen[key]) return;
      seen[key] = true;
      var p = points[a];
      var q = points[b];
      var mid = (p.x + q.x) / 2;
      var tone = mid < W * 0.4 ? "thread--pink" : mid > W * 0.66 ? "thread--navy" : "";
      var line = el("line", {
        class: "thread " + tone + (faint ? " thread--faint" : ""),
        x1: p.x.toFixed(1), y1: p.y.toFixed(1), x2: q.x.toFixed(1), y2: q.y.toFixed(1),
      });
      line.style.animationDelay = (rand() * 6).toFixed(2) + "s";
      threads.appendChild(line);
      p.deg += 1;
      q.deg += 1;
    }

    points.forEach(function (p, idx) {
      var near = points
        .map(function (q, j) { return { j: j, d: Math.sqrt((q.x - p.x) * (q.x - p.x) + (q.y - p.y) * (q.y - p.y)) }; })
        .filter(function (n) { return n.j !== idx; })
        .sort(function (a, b) { return a.d - b.d; });
      var k = p.hub ? 5 : 2 + Math.floor(rand() * 2);
      near.slice(0, k).forEach(function (n) { link(idx, n.j, n.d > 150); });
    });

    // 매듭에서 멀리 뻗는 긴 선 — 화면을 가로지르는 결을 만든다
    hubs.forEach(function (_, hi) {
      for (var j = 0; j < 3; j++) link(hi, Math.floor(rand() * points.length), true);
    });

    // ── 마디 그리기 ───────────────────────────────────
    points.forEach(function (p) {
      var r = p.hub ? 4.5 + rand() * 2 : 1 + Math.min(p.deg, 5) * 0.55 + rand() * 1.1;
      var tone = toneFor(p.x, rand);
      var circle = el("circle", {
        class: "node " + (p.hub ? "node--hub" : tone),
        cx: p.x.toFixed(1), cy: p.y.toFixed(1), r: r.toFixed(1),
      });
      circle.style.animationDelay = (rand() * 4.5).toFixed(2) + "s";
      nodes.appendChild(circle);

      // 굵은 마디 둘레에 얇은 테 — 참고 그림의 겹친 동심원 느낌
      if (r > 2.6 && rand() > 0.3) {
        rings.appendChild(el("circle", {
          class: "ring " + tone.replace("node--", "ring--"),
          cx: p.x.toFixed(1), cy: p.y.toFixed(1), r: (r + 2.5 + rand() * 4).toFixed(1),
        }));
      }
    });

    // 아주 작은 점 몇 개 — 성긴 자리를 메운다
    for (var k = 0; k < 22; k++) {
      var x = rand() * W;
      var y = rand() * H;
      var dot = el("circle", {
        class: "node node--dot " + toneFor(x, rand),
        cx: x.toFixed(1), cy: y.toFixed(1), r: (0.8 + rand() * 0.9).toFixed(1),
      });
      dot.style.animationDelay = (rand() * 5).toFixed(2) + "s";
      nodes.appendChild(dot);
    }

    host.appendChild(svg);
  }

  document.addEventListener("DOMContentLoaded", build);
})();
