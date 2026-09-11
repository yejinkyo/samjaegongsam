"""OCR 신뢰도 스코어링.

엔진이 준 신뢰도만으로는 손글씨·타자기 문서에서 과신이 잦다. 줄 단위 피처를 모아
로지스틱 회귀로 '판독 가능성'을 점수화한다. 기본 가중치는 보수적인 초기값이고,
라벨링 파일럿 데이터(정답 전사)로 ``fit``하면 보정된다.

임계값 미만 줄은 자동 정제하지 않고 '읽히지 않은 부분'으로 남긴다 (proposal.md 150행).
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from ..schema import Script
from .ocr import OcrLine

FEATURES = ("ocr_conf", "min_word_conf", "garbage_ratio", "jamo_ratio", "handwritten", "typewriter", "short")

_ALLOWED = re.compile(
    r"[가-힣A-Za-z0-9\s.,:;!?()\[\]{}<>'\"“”‘’\-~/%·‧…@#&*+=_₩○●◯×※「」『』。、|]"
    r"|[一-鿿]"  # 옛 판결문의 한자 허용
)
_JAMO = re.compile(r"[ㄱ-ㆎ]")


def line_features(line: OcrLine, script: Script) -> dict[str, float]:
    text = line.text.strip()
    n = max(len(text.replace(" ", "")), 1)
    garbage = sum(1 for ch in text if not ch.isspace() and not _ALLOWED.match(ch))
    jamo = len(_JAMO.findall(text))
    word_confs = [w.confidence for w in line.words] or [line.confidence]
    return {
        "ocr_conf": line.confidence,
        "min_word_conf": min(word_confs),
        "garbage_ratio": garbage / n,
        "jamo_ratio": jamo / n,
        "handwritten": 1.0 if script is Script.HANDWRITTEN else 0.0,
        "typewriter": 1.0 if script is Script.TYPEWRITER else 0.0,
        "short": 1.0 if n <= 3 else 0.0,
    }


class ReadabilityScorer:
    DEFAULT_WEIGHTS = {
        "ocr_conf": 6.0,
        "min_word_conf": 1.5,
        "garbage_ratio": -8.0,
        "jamo_ratio": -6.0,
        "handwritten": -0.8,
        "typewriter": -0.4,
        "short": -0.5,
    }
    DEFAULT_BIAS = -4.0

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        bias: float | None = None,
        threshold: float = 0.65,
        word_threshold: float = 0.5,
    ):
        self.weights = dict(weights or self.DEFAULT_WEIGHTS)
        self.bias = self.DEFAULT_BIAS if bias is None else bias
        self.threshold = threshold
        self.word_threshold = word_threshold

    def score(self, features: dict[str, float]) -> float:
        z = self.bias + sum(self.weights.get(k, 0.0) * features.get(k, 0.0) for k in FEATURES)
        return 1.0 / (1.0 + math.exp(-z))

    def score_line(self, line: OcrLine, script: Script) -> float:
        return self.score(line_features(line, script))

    def is_readable(self, score: float) -> bool:
        return score >= self.threshold

    def low_confidence_spans(self, line: OcrLine) -> list[tuple[int, int]]:
        """단어 신뢰도가 낮은 구간을 줄 텍스트의 문자 오프셋으로 돌려준다."""
        if not line.words or " ".join(w.text for w in line.words) != line.text:
            return []
        spans, pos = [], 0
        for w in line.words:
            if w.confidence < self.word_threshold:
                spans.append((pos, pos + len(w.text)))
            pos += len(w.text) + 1
        return spans

    def fit(
        self,
        samples: list[tuple[dict[str, float], int]],
        epochs: int = 800,
        lr: float = 0.5,
        l2: float = 1e-3,
    ) -> ReadabilityScorer:
        """라벨(1=판독 가능: 정답 대비 CER이 기준 이하) 기반 배치 경사하강."""
        if not samples:
            raise ValueError("학습 샘플이 없습니다")
        m = len(samples)
        for _ in range(epochs):
            grad = dict.fromkeys(FEATURES, 0.0)
            grad_b = 0.0
            for feats, label in samples:
                err = self.score(feats) - label
                grad_b += err
                for k in FEATURES:
                    grad[k] += err * feats.get(k, 0.0)
            self.bias -= lr * grad_b / m
            for k in FEATURES:
                self.weights[k] -= lr * (grad[k] / m + l2 * self.weights[k])
        return self

    def to_json(self, path: str | Path) -> None:
        payload = {
            "weights": self.weights,
            "bias": self.bias,
            "threshold": self.threshold,
            "word_threshold": self.word_threshold,
        }
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> ReadabilityScorer:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data["weights"], data["bias"], data["threshold"], data.get("word_threshold", 0.5))
