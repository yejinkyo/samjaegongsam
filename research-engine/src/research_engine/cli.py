"""research-engine CLI.

    research-engine run CASE.json --out result.json
    research-engine schema --out-dir schemas/
    research-engine eval-ocr lines.jsonl [--scorer scorer.json]
    research-engine train-readability lines.jsonl --out scorer.json
    research-engine train-doc-classifier docs.jsonl --out doc_classifier.json
    research-engine eval-ner gold.jsonl
    research-engine eval-nli pairs.jsonl --out policy.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .schema import ISSUE_CATEGORY_LABELS, ActionTrigger, CaseAnalysis, CaseCard


def _print(obj) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def cmd_run(args: argparse.Namespace) -> int:
    from .analysis import CaseAnalyzer, ConservativePolicy
    from .ingest import DocumentIngestor, EnsembleDocClassifier, KeywordDocClassifier, NaiveBayesDocClassifier
    from .ingest.confidence import ReadabilityScorer
    from .pipeline import ResearchPipeline, load_case
    from .requirements import load_requirements

    case = load_case(args.case)
    classifier = KeywordDocClassifier()
    if args.doc_classifier:
        classifier = EnsembleDocClassifier(
            [(KeywordDocClassifier(), 0.4), (NaiveBayesDocClassifier.from_json(args.doc_classifier), 0.6)]
        )
    scorer = ReadabilityScorer.from_json(args.scorer) if args.scorer else None
    policy = ConservativePolicy.from_json(args.policy) if args.policy else None
    pipeline = ResearchPipeline(
        ingestor=DocumentIngestor(classifier=classifier, scorer=scorer),
        analyzer=CaseAnalyzer(policy=policy),
        requirements=load_requirements(case.case_type, args.requirements) if args.requirements else None,
    )
    result = pipeline.run(case)
    payload = result.model_dump_json(indent=2)
    if args.out:
        _prepare(args.out).write_text(payload, encoding="utf-8")
    analysis = result.analysis
    card = analysis.case_card
    lines = [
        f"[{card.case_type_label}] ({card.requirements_status})",
        "  " + " → ".join(f"{s.label}({s.state.value})" for s in card.stages),
        f"  확보 자료 {card.evidence_doc_count} · 확인 필요 {card.needs_confirmation_count} · "
        f"완료 {card.slots_done}/{card.slots_total}",
        "",
        "확인이 필요해요",
    ]
    for issue in analysis.issues:
        lines.append(f"  [{ISSUE_CATEGORY_LABELS[issue.category]}] {issue.message}")
        lines.append(f"      trigger: {issue.trigger.key}")
    pending = [q for q in result.clarifications if q.status == "pending"]
    if pending:
        lines += ["", f"되물을 질문 {len(pending)}개 (첫 질문)", f"  {pending[0].question} — {pending[0].doc_id} {pending[0].line_no}줄"]
    if not args.out:
        sys.stdout.write(payload + "\n")
    else:
        sys.stdout.write("\n".join(lines) + f"\n\n전체 결과: {args.out}\n")
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    from .pipeline import CaseInput, PipelineResult

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, model in {
        "case_input": CaseInput,
        "pipeline_result": PipelineResult,
        "case_analysis": CaseAnalysis,
        "case_card": CaseCard,
        "action_trigger": ActionTrigger,
    }.items():
        (out / f"{name}.schema.json").write_text(
            json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
    sys.stdout.write(f"JSON Schema {out}에 저장\n")
    return 0


def cmd_eval_ocr(args: argparse.Namespace) -> int:
    from .eval.ocr_eval import evaluate_ocr, load_line_labels
    from .ingest.confidence import ReadabilityScorer

    scorer = ReadabilityScorer.from_json(args.scorer) if args.scorer else None
    report = evaluate_ocr(load_line_labels(args.labels), scorer, args.max_cer, args.target_precision)
    _write_or_print(report, args.out)
    return 0


def cmd_train_readability(args: argparse.Namespace) -> int:
    from .eval.ocr_eval import evaluate_ocr, load_line_labels, training_samples
    from .ingest.confidence import ReadabilityScorer

    labels = load_line_labels(args.labels)
    scorer = ReadabilityScorer().fit(training_samples(labels, args.max_cer))
    report = evaluate_ocr(labels, scorer, args.max_cer, args.target_precision)
    if report["recommended_threshold"] is not None:
        scorer.threshold = report["recommended_threshold"]
    scorer.to_json(_prepare(args.out))
    sys.stdout.write(f"저장: {args.out} (threshold={scorer.threshold})\n")
    return 0


def cmd_train_doc_classifier(args: argparse.Namespace) -> int:
    from .ingest import NaiveBayesDocClassifier
    from .schema import DocumentType

    rows = [json.loads(r) for r in Path(args.labels).read_text(encoding="utf-8").splitlines() if r.strip()]
    clf = NaiveBayesDocClassifier().fit((r["text"], DocumentType(r["doc_type"])) for r in rows)
    clf.to_json(_prepare(args.out))
    sys.stdout.write(f"저장: {args.out} ({len(rows)}건, 유형 {len(clf.class_counts)}개)\n")
    return 0


def cmd_eval_ner(args: argparse.Namespace) -> int:
    from .eval.ner_eval import evaluate_extraction

    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    _write_or_print(evaluate_extraction(args.gold, args.target_f1, as_of), args.out)
    return 0


def cmd_eval_nli(args: argparse.Namespace) -> int:
    from .eval.nli_eval import load_pair_labels, tune_thresholds

    report = tune_thresholds(load_pair_labels(args.pairs), args.target_precision)
    if args.out and report["recommended_policy"]:
        policy = {k: v for k, v in report["recommended_policy"].items() if k != "contradiction"}
        _prepare(args.out).write_text(json.dumps(policy, indent=2), encoding="utf-8")
        sys.stdout.write(f"정책 저장: {args.out}\n")
    _print(report)
    return 0


def _prepare(out: str) -> Path:
    """--out 경로의 상위 폴더가 없으면 만든다."""
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _write_or_print(report: dict, out: str | None) -> None:
    if out:
        _prepare(out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _print(report)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research-engine", description="사건 자료 재구성 파이프라인")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="case.json → 1~4단계 실행")
    run.add_argument("case")
    run.add_argument("--out")
    run.add_argument("--requirements", help="사건 유형 항목 정의 JSON (기본: 내장)")
    run.add_argument("--policy", help="eval-nli가 만든 판정 정책 JSON")
    run.add_argument("--scorer", help="train-readability가 만든 신뢰도 스코어러 JSON")
    run.add_argument("--doc-classifier", help="train-doc-classifier가 만든 모델 JSON")
    run.set_defaults(func=cmd_run)

    schema = sub.add_parser("schema", help="출력 JSON Schema 내보내기 (기능2·행동 강령 엔진 연동용)")
    schema.add_argument("--out-dir", default="schemas")
    schema.set_defaults(func=cmd_schema)

    for name, func, help_ in (
        ("eval-ocr", cmd_eval_ocr, "OCR CER + 판독 임계값 스윕"),
        ("train-readability", cmd_train_readability, "판독 신뢰도 스코어러 학습"),
    ):
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("labels")
        sp.add_argument("--max-cer", type=float, default=0.1)
        sp.add_argument("--target-precision", type=float, default=0.95)
        if name == "eval-ocr":
            sp.add_argument("--scorer")
            sp.add_argument("--out")
        else:
            sp.add_argument("--out", required=True)
        sp.set_defaults(func=func)

    clf = sub.add_parser("train-doc-classifier", help="문서 유형 분류기 학습")
    clf.add_argument("labels")
    clf.add_argument("--out", required=True)
    clf.set_defaults(func=cmd_train_doc_classifier)

    ner = sub.add_parser("eval-ner", help="엔티티·시간 추출 정확도")
    ner.add_argument("gold")
    ner.add_argument("--target-f1", type=float, default=0.85)
    ner.add_argument("--as-of")
    ner.add_argument("--out")
    ner.set_defaults(func=cmd_eval_ner)

    nli = sub.add_parser("eval-nli", help="Contradiction 임계값 튜닝 (precision 우선)")
    nli.add_argument("pairs")
    nli.add_argument("--target-precision", type=float, default=0.95)
    nli.add_argument("--out")
    nli.set_defaults(func=cmd_eval_nli)
    return p


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
