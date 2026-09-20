/* 배포 환경(Vercel)의 사건 등록 — 사진 읽기와 사건 저장을 브라우저가 맡는다.
 *
 * 로컬 정리 서버(web/serve.py)는 사진을 Tesseract 로 읽고 사건을 local-cases/ 에 쌓는다.
 * 배포 환경의 함수는 상태를 두지 않으므로 그 두 가지를 브라우저로 옮긴다.
 *
 *   사진 → tesseract.js 로 이 브라우저에서 읽음 → OCR 결과 JSON
 *   OCR 결과 · 메모 → POST api/analyze (두 엔진을 돌려 화면 데이터만 돌려받음)
 *   사건 · 원본 사진 · 화면 데이터 → 이 브라우저의 IndexedDB
 *
 * app.js 는 /api/status 의 mode 가 "browser" 일 때 사건 API 호출을 여기로 보낸다. 주소와 돌려주는 모양은
 * 로컬 정리 서버와 같다 — 화면 코드는 어느 쪽인지 몰라도 된다.
 */
(function () {
  "use strict";

  var DB_NAME = "tarae";
  var STORE = "cases";
  var CASE_ID = /^[0-9a-f]{12}$/;
  var IMAGE_EXTS = ["png", "jpg", "jpeg", "webp", "gif", "bmp"];

  // 사진 읽기 엔진. 로컬 서버와 같은 Tesseract 를 브라우저용으로 옮긴 것이다. 처음 한 번 한국어 데이터를 받는다.
  var TESSERACT_URL = "https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js";

  function fail(message, detail) {
    var err = new Error(message);
    err.detail = detail || null;
    return err;
  }

  function pad(n) { return (n < 10 ? "0" : "") + n; }

  function isoLocal(ms) {
    var d = new Date(ms || Date.now());
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + "T" + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
  }

  function newCaseId() {
    var bytes = new Uint8Array(6);
    crypto.getRandomValues(bytes);
    return Array.prototype.map.call(bytes, function (b) { return (b < 16 ? "0" : "") + b.toString(16); }).join("");
  }

  // ── 저장 (IndexedDB) ───────────────────────────────────────────────

  var dbPromise = null;

  function openDb() {
    if (!dbPromise) {
      dbPromise = new Promise(function (resolve, reject) {
        if (!window.indexedDB) return reject(fail("이 브라우저는 사건을 저장할 수 없어요."));
        var req = indexedDB.open(DB_NAME, 1);
        req.onupgradeneeded = function () { req.result.createObjectStore(STORE, { keyPath: "id" }); };
        req.onsuccess = function () { resolve(req.result); };
        req.onerror = function () { reject(fail("사건을 저장할 곳을 열지 못했어요.", String(req.error))); };
      });
    }
    return dbPromise;
  }

  function withStore(mode, work) {
    return openDb().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE, mode);
        var req = work(tx.objectStore(STORE));
        tx.oncomplete = function () { resolve(req && req.result); };
        tx.onerror = function () { reject(fail("사건을 저장하지 못했어요.", String(tx.error))); };
        tx.onabort = tx.onerror;
      });
    });
  }

  function loadCase(id) {
    if (!CASE_ID.test(id)) return Promise.reject(fail("사건을 찾지 못했어요."));
    return withStore("readonly", function (s) { return s.get(id); }).then(function (rec) {
      if (!rec) throw fail("사건을 찾지 못했어요.");
      return rec;
    });
  }

  function saveCase(rec) { return withStore("readwrite", function (s) { return s.put(rec); }); }
  function allCases() { return withStore("readonly", function (s) { return s.getAll(); }); }

  // ── 화면 데이터 ────────────────────────────────────────────────────

  var objectUrls = {};

  /** 원본을 열 주소를 붙인다(로컬 서버의 with_files 와 같은 일). 원본은 이 브라우저 안의 파일이다. */
  function toView(rec) {
    var view = JSON.parse(JSON.stringify(rec.view));
    view.local = true;
    view.created_at = rec.created_at;
    var files = {};
    rec.documents.forEach(function (d) {
      var key = rec.id + "/" + d.doc_id;
      if (!objectUrls[key]) {
        var blob = d.blob || new Blob([JSON.stringify(d.ocr)], { type: "application/json" });
        objectUrls[key] = URL.createObjectURL(blob);
      }
      files[d.doc_id] = { href: objectUrls[key], media: d.blob ? (d.blob.type || "image/jpeg") : "application/json" };
    });
    function mark(src) {
      var f = files[src.doc_id];
      if (f) { src.href = f.href; src.media = f.media; }
    }
    (view.sources || []).forEach(mark);
    (view.timeline || []).forEach(function (row) { (row.sources || []).forEach(mark); });
    return view;
  }

  /** 사건 하나의 자료 전체를 엔진에 보내 다시 정리한다. 서버는 아무것도 남기지 않는다. */
  function analyze(rec) {
    var now = new Date();
    var body = JSON.stringify({
      case_id: rec.id,
      case_type: rec.case_type,
      title: rec.title || "",
      as_of: now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate()),
      documents: rec.documents.map(function (d) { return d.ocr; }),
      user_notes: rec.notes,
    });
    return fetch("api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: body }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (!res.ok) throw fail(data.error || "정리 서버에 연결하지 못했어요.", data.detail);
        rec.view = data;
        rec.title = data.title;
        return rec;
      });
    });
  }

  // ── 사진 읽기 (tesseract.js) ────────────────────────────────────────

  var scriptPromise = null;
  var workerPromise = null;
  var progressListener = null;

  function loadTesseract() {
    if (!scriptPromise) {
      scriptPromise = new Promise(function (resolve, reject) {
        if (window.Tesseract) return resolve(window.Tesseract);
        var tag = document.createElement("script");
        tag.src = TESSERACT_URL;
        tag.onload = function () { resolve(window.Tesseract); };
        tag.onerror = function () {
          scriptPromise = null;
          reject(fail("사진 읽기 도구를 받지 못했어요. 인터넷 연결을 확인해 주세요."));
        };
        document.head.appendChild(tag);
      });
    }
    return scriptPromise;
  }

  function ocrWorker() {
    if (!workerPromise) {
      workerPromise = loadTesseract().then(function (Tesseract) {
        return Tesseract.createWorker("kor", 1, {
          logger: function (m) {
            if (progressListener && m.status === "loading language traineddata") {
              progressListener("한국어 글자 데이터를 받는 중이에요 (처음 한 번만) " + Math.round((m.progress || 0) * 100) + "%");
            }
          },
        });
      }).catch(function (err) {
        workerPromise = null;
        throw err.detail !== undefined ? err : fail("사진 읽기 도구를 준비하지 못했어요.", String(err));
      });
    }
    return workerPromise;
  }

  /** 로컬 서버의 전처리(흑백 · 작은 사진 확대)와 맞춘다. 너무 큰 사진은 줄여 읽는 시간을 줄인다. */
  function toCanvas(file) {
    return createImageBitmap(file).then(function (bitmap) {
      var scale = bitmap.width < 1500 ? 1500 / bitmap.width : Math.min(1, 2500 / bitmap.width);
      var canvas = document.createElement("canvas");
      canvas.width = Math.round(bitmap.width * scale);
      canvas.height = Math.round(bitmap.height * scale);
      var ctx = canvas.getContext("2d");
      ctx.filter = "grayscale(1)";
      ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      if (bitmap.close) bitmap.close();
      return canvas;
    }, function () {
      throw fail(file.name + " 을(를) 사진으로 열지 못했어요.");
    });
  }

  function box(b) { return [b.x0, b.y0, b.x1, b.y1]; }

  /* 단어 상자들을 한 줄 문자열로. research-engine 의 join_words(ingest/ocr.py)와 같은 규칙이다 —
     Tesseract 한국어 모델은 음절마다 상자를 주므로, 간격이 글자 높이의 절반보다 좁으면 붙인다. */
  function joinWords(words) {
    var ordered = words.slice().sort(function (a, b) { return a.bbox[0] - b.bbox[0]; });
    var heights = ordered.map(function (w) { return w.bbox[3] - w.bbox[1]; }).sort(function (a, b) { return a - b; });
    var height = heights[Math.floor(heights.length / 2)] || 1;
    var out = ordered[0].text;
    for (var i = 1; i < ordered.length; i++) {
      var gap = ordered[i].bbox[0] - ordered[i - 1].bbox[2];
      out += (gap < height * 0.5 ? "" : " ") + ordered[i].text;
    }
    return out;
  }

  function linesOf(data) {
    if (data.lines && data.lines.length) return data.lines;
    var out = [];
    (data.blocks || []).forEach(function (block) {
      (block.paragraphs || []).forEach(function (para) { out = out.concat(para.lines || []); });
    });
    return out;
  }

  function readPhoto(file, docId, modified) {
    return Promise.all([ocrWorker(), toCanvas(file)]).then(function (both) {
      var canvas = both[1];
      return both[0].recognize(canvas, {}, { blocks: true }).then(function (result) {
        var lines = linesOf(result.data).map(function (line) {
          var words = (line.words || []).filter(function (w) { return w.text && w.text.trim(); }).map(function (w) {
            return { text: w.text.trim(), bbox: box(w.bbox), confidence: Math.max(0, Math.min(1, w.confidence / 100)) };
          });
          if (!words.length) return null;
          var conf = words.reduce(function (sum, w) { return sum + w.confidence; }, 0) / words.length;
          return { text: joinWords(words), bbox: box(line.bbox), confidence: conf, words: words };
        }).filter(Boolean);
        return {
          doc_id: docId,
          file_name: file.name,
          captured_at: modified || null,
          pages: [{ page_no: 1, width: canvas.width, height: canvas.height, lines: lines }],
        };
      });
    });
  }

  // ── 자료 더하기 ────────────────────────────────────────────────────

  function kindOf(name) {
    var ext = (name.split(".").pop() || "").toLowerCase();
    if (ext === "json") return "json";
    return IMAGE_EXTS.indexOf(ext) >= 0 ? "image" : null;
  }

  function nextId(prefix, list, key) {
    var n = 1;
    var used = {};
    list.forEach(function (x) { used[x[key]] = true; });
    while (used[prefix + n]) n++;
    return prefix + n;
  }

  /** 올린 파일·메모를 사건에 더한다. 읽을 수 없는 형식은 조용히 버리지 않고 거절한다(로컬 서버와 같음). */
  function addItems(rec, items, onProgress) {
    var rejected = items.filter(function (it) { return it.file && !kindOf(it.name); }).map(function (it) { return it.name; });
    if (rejected.length) {
      return Promise.reject(fail("아직 읽을 수 없는 형식이 있어요: " + rejected.join(", ") + " — 사진(이미지)이나 OCR 결과 JSON 만 정리할 수 있어요."));
    }
    var photos = items.filter(function (it) { return it.file && kindOf(it.name) === "image"; }).length;
    var read = 0;
    progressListener = onProgress || null;

    return items.reduce(function (chain, it) {
      return chain.then(function () {
        if (it.note) {
          rec.notes.push({ note_id: nextId("note", rec.notes, "note_id"), text: it.note, created_at: isoLocal() });
          return;
        }
        if (!it.file) return;
        var docId = nextId("doc", rec.documents, "doc_id");
        if (kindOf(it.name) === "json") {
          return it.file.text().then(function (text) {
            var doc;
            try { doc = JSON.parse(text); } catch (e) { doc = null; }
            if (!doc || typeof doc !== "object" || !Array.isArray(doc.pages)) throw fail(it.name + " 은 OCR 결과 JSON 형식이 아니에요.");
            // 사건 안에서 문서 id 가 겹치지 않게 새로 붙인다. 파일 이름은 올린 그대로 둔다.
            doc.doc_id = docId;
            doc.file_name = doc.file_name || it.name;
            rec.documents.push({ doc_id: docId, file_name: it.name, ocr: doc, blob: null });
          });
        }
        read += 1;
        if (onProgress) onProgress("사진을 읽고 있어요 " + read + "/" + photos + " — " + it.name);
        return readPhoto(it.file, docId, it.modified).then(function (doc) {
          rec.documents.push({ doc_id: docId, file_name: it.name, ocr: doc, blob: it.file });
        });
      });
    }, Promise.resolve()).then(function () {
      progressListener = null;
      if (!rec.documents.length && !rec.notes.length) throw fail("올린 자료가 없어요. 사진이나 메모를 하나 이상 더해 주세요.");
      if (onProgress) onProgress("자료를 정리하고 있어요…");
      return rec;
    }, function (err) {
      progressListener = null;
      throw err;
    });
  }

  // ── app.js 가 부르는 곳 ─────────────────────────────────────────────

  /** 사건 조회 · 메모 지우기. 주소는 로컬 정리 서버와 같다. */
  function request(path, options) {
    var method = ((options && options.method) || "GET").toUpperCase();
    var m;
    if (method === "GET" && path === "api/cases") {
      return allCases().then(function (recs) {
        return recs.filter(function (r) { return r.view; })
          .sort(function (a, b) { return a.created_at < b.created_at ? 1 : -1; })
          .map(toView);
      });
    }
    if (method === "GET" && (m = path.match(/^api\/cases\/([^/]+)$/))) {
      return loadCase(decodeURIComponent(m[1])).then(toView);
    }
    if (method === "DELETE" && (m = path.match(/^api\/cases\/([^/]+)\/notes\/([^/]+)$/))) {
      var noteId = decodeURIComponent(m[2]);
      return loadCase(decodeURIComponent(m[1])).then(function (rec) {
        // 직접 적은 줄만 지운다. 올린 서류에서 읽어 낸 줄은 자료 자체를 빼야 한다.
        var index = rec.notes.map(function (n) { return n.note_id; }).indexOf(noteId);
        if (noteId.indexOf("note") !== 0 || index < 0) throw fail("그 메모를 찾지 못했어요.");
        if (rec.notes.length + rec.documents.length <= 1) throw fail("마지막 남은 자료는 지울 수 없어요.");
        rec.notes.splice(index, 1);
        return analyze(rec).then(function () { return saveCase(rec); }).then(function () { return toView(rec); });
      });
    }
    return Promise.reject(fail("없는 주소예요."));
  }

  /** 사건 등록 · 자료 더하기. 새 사건은 정리에 성공했을 때만 저장한다. */
  function upload(url, fields, items, onProgress) {
    var m;
    if (url === "api/cases") {
      var rec = { id: newCaseId(), case_type: fields.case_type, title: fields.title || "", created_at: isoLocal(), documents: [], notes: [], view: null };
      return addItems(rec, items, onProgress).then(analyze).then(function () { return saveCase(rec); }).then(function () { return toView(rec); });
    }
    if ((m = url.match(/^api\/cases\/([^/]+)\/files$/))) {
      // 실패하면 저장하지 않으므로 사건은 더하기 전 상태로 남는다
      return loadCase(decodeURIComponent(m[1])).then(function (existing) {
        return addItems(existing, items, onProgress).then(analyze).then(function () { return saveCase(existing); }).then(function () { return toView(existing); });
      });
    }
    return Promise.reject(fail("없는 주소예요."));
  }

  window.TaraeBrowserStore = { request: request, upload: upload };
})();
