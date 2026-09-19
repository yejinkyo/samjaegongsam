"""문서 유형 분류: 판결문 / 진술서 / 영수증 / 메모 (+ 고소장·녹취록·메신저·보도·감정서).

- ``KeywordDocClassifier``: 라벨 데이터 없이 동작하는 서식 키워드 기반 기준선
- ``NaiveBayesDocClassifier``: 문자 bigram 나이브 베이즈. 파일럿 라벨로 학습
- ``EnsembleDocClassifier``: 둘을 가중 평균 (학습 모델이 있을 때)
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ..schema import DocumentType

_T = DocumentType


@dataclass
class DocTypePrediction:
    doc_type: DocumentType
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)


class DocumentClassifier(Protocol):
    def predict(self, lines: list[str], handwritten_ratio: float = 0.0) -> DocTypePrediction: ...


def _softmax(raw: dict[DocumentType, float], temperature: float) -> dict[DocumentType, float]:
    top = max(raw.values())
    exps = {k: math.exp((v - top) / temperature) for k, v in raw.items()}
    total = sum(exps.values())
    return {k: v / total for k, v in exps.items()}


class KeywordDocClassifier:
    RULES: dict[DocumentType, list[tuple[str, float]]] = {
        _T.JUDGMENT: [
            (r"판\s*결", 2.0), (r"주\s*문", 1.5), (r"이\s*유", 0.8), (r"피\s*고\s*인", 1.0),
            (r"선\s*고", 1.2), (r"법\s*원", 1.0), (r"판\s*사|재\s*판\s*장", 1.2),
            (r"\d{4}\s*(고단|고합|고정|노|도)\s*\d+", 2.0),
        ],
        _T.COMPLAINT: [
            (r"고\s*소\s*장|진\s*정\s*서", 3.0), (r"피\s*고\s*소\s*인", 2.0), (r"고\s*소\s*인|진\s*정\s*인", 1.0),
            (r"고소\s*취지|진정\s*취지", 2.0),
        ],
        _T.STATEMENT: [
            (r"진\s*술\s*서", 3.0), (r"진\s*술\s*인", 1.5), (r"사실과\s*다름(이)?\s*없", 2.0),
            (r"(서명|날인|무인)", 0.8), (r"위\s*(와\s*같이|내용)", 0.5),
        ],
        _T.TRANSCRIPT: [
            (r"녹\s*취\s*록", 3.0), (r"^\s*(문|답)\s*[:：]", 1.5), (r"녹음\s*(파일|일시)", 1.5),
        ],
        _T.RECEIPT: [
            (r"영\s*수\s*증|이체\s*확인증|접\s*수\s*증|거래\s*명세", 3.0), (r"합\s*계|총\s*액", 1.0),
            (r"사업자\s*등록\s*번호|승인\s*번호", 1.5), (r"(거래|이체|접수)\s*일시", 1.5),
            (r"(입금|출금)\s*계좌|이체\s*금액", 1.5), (r"접수\s*번호", 1.2), (r"발급", 0.6),
        ],
        _T.NOTICE: [
            (r"통\s*지\s*서", 2.0), (r"(수사\s*중지|불송치|불기소|기소\s*중지|수사\s*결과|처분\s*결과)\s*(결정|통지)?", 1.5),
            (r"결\s*정\s*(일\s*자|내\s*용|일)", 1.5), (r"경찰서장|검사장|지청장", 1.0), (r"피\s*의\s*자", 0.6),
        ],
        _T.MESSENGER: [
            (r"^\s*\[[^\]]{1,20}\]\s*\[(오전|오후)\s*\d{1,2}:\d{2}\]", 2.0),
            (r"^\s*\d{4}년\s*\d{1,2}월\s*\d{1,2}일\s*[월화수목금토일]요일\s*$", 1.5),
        ],
        # 감정서는 감정 기관이 발급한 기록이다. 없으면 '전문 분석 미실시'를 가릴 수 없다
        _T.FORENSIC: [
            (r"감\s*정\s*서|감정\s*결과\s*(통보|회보)", 3.0), (r"감정\s*(대상|일자|의뢰|결과|물)", 1.5),
            (r"국립과학수사연구원|과학수사연구소", 1.5), (r"유전자\s*(분석|감정)|DNA\s*(분석|감정)", 1.0),
        ],
        _T.NEWS: [(r"기자", 1.0), (r"(입력|수정)\s*\d{4}[.\-]", 1.5), (r"무단\s*전재|재배포\s*금지", 2.5)],
        _T.MEMO: [],
    }

    def __init__(self, temperature: float = 1.0, min_evidence: float = 1.0):
        self.temperature = temperature
        self.min_evidence = min_evidence
        self._compiled = {
            t: [(re.compile(p, re.MULTILINE), w) for p, w in rules] for t, rules in self.RULES.items()
        }

    def predict(self, lines: list[str], handwritten_ratio: float = 0.0) -> DocTypePrediction:
        text = "\n".join(lines)
        raw: dict[DocumentType, float] = {}
        for doc_type, rules in self._compiled.items():
            score = 0.0
            for pattern, weight in rules:
                hits = len(pattern.findall(text))
                if hits:
                    # 같은 서식이 반복되는 메신저는 비율로, 나머지는 존재 여부로 센다
                    score += weight * (min(hits, 5) if doc_type is _T.MESSENGER else 1)
            raw[doc_type] = score
        avg_len = sum(len(ln) for ln in lines) / max(len(lines), 1)
        raw[_T.MEMO] = handwritten_ratio * 3.0 + (0.8 if avg_len < 20 and len(lines) <= 15 else 0.0)

        best_raw = max(raw.values())
        probs = _softmax(raw, self.temperature)
        best = max(probs, key=probs.__getitem__)
        confidence = probs[best]
        if best_raw < self.min_evidence:
            # 근거 부족: 유형을 확정하지 않는다
            confidence = min(confidence, 0.3)
            best = _T.UNKNOWN
        return DocTypePrediction(best, confidence, {k.value: round(v, 4) for k, v in probs.items()})


class NaiveBayesDocClassifier:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.class_counts: Counter[str] = Counter()
        self.token_counts: dict[str, Counter[str]] = {}
        self.vocab: set[str] = set()

    @staticmethod
    def tokens(text: str) -> list[str]:
        compact = re.sub(r"\s+", " ", text)
        return [compact[i : i + 2] for i in range(len(compact) - 1)]

    def fit(self, samples: Iterable[tuple[str, DocumentType]]) -> NaiveBayesDocClassifier:
        for text, label in samples:
            key = DocumentType(label).value
            self.class_counts[key] += 1
            counter = self.token_counts.setdefault(key, Counter())
            toks = self.tokens(text)
            counter.update(toks)
            self.vocab.update(toks)
        return self

    @property
    def is_trained(self) -> bool:
        return bool(self.class_counts)

    def predict(self, lines: list[str], handwritten_ratio: float = 0.0) -> DocTypePrediction:
        if not self.is_trained:
            raise RuntimeError("학습되지 않은 분류기입니다")
        toks = self.tokens("\n".join(lines))
        total_docs = sum(self.class_counts.values())
        v = len(self.vocab) or 1
        logp: dict[str, float] = {}
        for key, n_docs in self.class_counts.items():
            counter = self.token_counts[key]
            denom = sum(counter.values()) + self.alpha * v
            lp = math.log(n_docs / total_docs)
            lp += sum(math.log((counter.get(t, 0) + self.alpha) / denom) for t in toks)
            logp[key] = lp
        top = max(logp.values())
        norm = top + math.log(sum(math.exp(x - top) for x in logp.values()))
        probs = {k: math.exp(x - norm) for k, x in logp.items()}
        best = max(probs, key=probs.__getitem__)
        return DocTypePrediction(DocumentType(best), probs[best], {k: round(p, 4) for k, p in probs.items()})

    def to_json(self, path: str | Path) -> None:
        payload = {
            "alpha": self.alpha,
            "class_counts": dict(self.class_counts),
            "token_counts": {k: dict(c) for k, c in self.token_counts.items()},
        }
        Path(path).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> NaiveBayesDocClassifier:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        clf = cls(data["alpha"])
        clf.class_counts = Counter(data["class_counts"])
        clf.token_counts = {k: Counter(c) for k, c in data["token_counts"].items()}
        clf.vocab = {t for c in clf.token_counts.values() for t in c}
        return clf


class EnsembleDocClassifier:
    def __init__(self, members: list[tuple[DocumentClassifier, float]]):
        self.members = members

    def predict(self, lines: list[str], handwritten_ratio: float = 0.0) -> DocTypePrediction:
        combined: dict[str, float] = {}
        total_w = sum(w for _, w in self.members)
        for clf, weight in self.members:
            pred = clf.predict(lines, handwritten_ratio)
            for key, p in pred.scores.items():
                combined[key] = combined.get(key, 0.0) + weight * p / total_w
        best = max(combined, key=combined.__getitem__)
        return DocTypePrediction(DocumentType(best), combined[best], combined)
