"""Step 5 analysis: which warning sign works for a model you can only reach through an API?

There's no internal state to read, so there's no probe. The signals are:
  stated           100 minus the confidence Claude wrote
  disagreement     how many of the other four answers differ from the first one
  text_and_answer  the invoice text plus Claude's answer (the cheap checker from step 4)
  input_only       the invoice text alone
  answer_given     how often each answer Claude gives turns out wrong
  case_type        reference only, as before

Same rules as the Qwen analysis: five rotations over suppliers, 95% ranges from resampling
suppliers, and automation cut-offs picked on other suppliers before they're used.

Run:  uv run python -m the_tell.compare_claude --run haiku-full-off
"""

import argparse
import json
from pathlib import Path

import numpy as np

from the_tell.analysis import (
    _auroc,
    answer_given_scores,
    case_type_scores,
    cutoff_at_risk,
    input_only_scores,
    is_wrong,
    summarise,
    supplier_folds,
    with_answer,
)
from the_tell.generate import read_jsonl
from the_tell.prompt import user_message

LEAD = "text_and_answer"
TRAINED = ["input_only", "text_and_answer", "answer_given", "case_type"]
ADVANCE = ["stated", "disagreement", "text_and_answer", "answer_given"]
RISKS = [0.02, 0.05]
MIN_WRONG = 30  # below this there's too little to train a checker on


def output_signals(results: list[dict]) -> dict[str, np.ndarray]:
    stated, disagreement = [], []
    for r in results:
        stated.append(100 - (r["confidence"] if r["confidence"] is not None else 0))
        first, rest = r["sample_answers"][0], r["sample_answers"][1:]
        disagreement.append(sum(a != first for a in rest) / len(rest))
    return {"stated": np.array(stated, float), "disagreement": np.array(disagreement)}


def analyse(results: list[dict], texts: list[str], level: str, k: int = 5) -> tuple[dict, dict, np.ndarray]:
    y = is_wrong(results, level)
    folds = supplier_folds(results, k)
    suppliers = np.array([r["supplier_id"] for r in results])
    scenarios = np.array([r["scenario"] for r in results])
    answers = np.array([str(r["predicted"]) for r in results])
    labels = np.array([r["label"] for r in results])
    bad_approval = (answers == "APPROVE") & (labels != "APPROVE")
    texts_with_answer = with_answer(texts, results)

    scores = output_signals(results)
    for n in TRAINED:
        scores[n] = np.zeros(len(results))
    tally = {(n, r): np.zeros(3, int) for n in ADVANCE for r in RISKS}
    for f in range(k):
        test, val = folds == f, folds == (f + 1) % k
        train = ~test & ~val
        fit = train | val
        scores["input_only"][test] = input_only_scores(texts, y, fit, val)[test]
        scores["text_and_answer"][test] = input_only_scores(texts_with_answer, y, fit, val)[test]
        scores["answer_given"][test] = answer_given_scores(results, y, fit)[test]
        scores["case_type"][test] = case_type_scores(results, y, fit)[test]
        # Cut-offs set in advance: train on three groups, pick the cut-off on the fourth.
        train_only = {
            "stated": scores["stated"],
            "disagreement": scores["disagreement"],
            "text_and_answer": input_only_scores(texts_with_answer, y, train, val),
            "answer_given": answer_given_scores(results, y, train),
        }
        for n, sc in train_only.items():
            for r in RISKS:
                auto = test & (sc <= cutoff_at_risk(sc[val], y[val], r))
                tally[(n, r)] += [auto.sum(), (auto & y).sum(), (auto & bad_approval).sum()]

    report = {
        "level": level,
        "counts": {"invoices": len(results), "wrong": int(y.sum()), "suppliers": len(set(suppliers))},
        "summary": summarise(scores, y, np.ones(len(y), bool), suppliers, scenarios, answers, lead=LEAD),
        "cutoff_set_in_advance": {
            n: {f"target_{r:.0%}": dict(zip(["automated", "wrong", "bad_invoices_approved"], map(int, tally[(n, r)]))) for r in RISKS}
            for n in ADVANCE
        },
    }
    return report, scores, y


def print_report(rep: dict) -> None:
    c = rep["counts"]
    print(f"\n=== Errors at the {rep['level']!r} level: {c['wrong']} of {c['invoices']} invoices wrong ===")
    sig = rep["summary"]["signals"]
    print(f"  {'signal':<16} {'AUROC':<22} {'within type':<24} {'automatable at 2% (best case)'}")
    for n, m in sig.items():
        w = m["within_type"]
        r95 = m["auroc_95"] or [np.nan, np.nan]
        w95 = w.get("auroc_95") or [np.nan, np.nan]
        print(f"  {n:<16} {m['auroc']:.2f} ({r95[0]:.2f} to {r95[1]:.2f})    {w['auroc']:.2f} ({w95[0]:.2f} to {w95[1]:.2f}) [{w['scenarios_used']}]   {m['coverage_at_2pct_error']:.0%}")
    print(f"  {LEAD} AUROC advantage over:")
    for n, d in rep["summary"][f"{LEAD}_advantage_auroc"].items():
        r = d["diff_95"]
        verdict = "" if not r else ("clearly better" if r[0] > 0 else "clearly worse" if r[1] < 0 else "not distinguishable")
        print(f"    {n:<16} {d['diff']:+.2f} ({r[0]:.2f} to {r[1]:.2f})  {verdict}" if r else f"    {n:<16} {d['diff']:+.2f}")
    print("  Automation with the cut-off set in advance:")
    for n, by in rep["cutoff_set_in_advance"].items():
        for t, d in by.items():
            rate = d["wrong"] / d["automated"] if d["automated"] else 0
            print(f"    {n:<16} aiming for {t[7:]:>3}: automated {d['automated']:>4} of {c['invoices']}, {d['wrong']} wrong ({rate:.1%}), {d['bad_invoices_approved']} bad invoices approved")
    print("  Grouped by the answer Claude gave (AUROC):")
    for g, d in sig[LEAD]["within_answer"]["per_group"].items():
        others = "  ".join(f"{n} {sig[n]['within_answer']['per_group'][g]['auroc']:.2f}" for n in ["stated", "disagreement"])
        print(f"    {g:<20} right {d['right']:>4} wrong {d['wrong']:>3}   {LEAD} {d['auroc']:.2f}  {others}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--cases", type=Path, default=Path("data/generated/cases.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("results"))
    args = ap.parse_args()

    results = [json.loads(l) for l in (Path("runs") / args.run / "results.jsonl").read_text().splitlines() if l.strip()]
    cases = {c.case_id: c for c in read_jsonl(args.cases)}
    texts = [user_message(cases[r["case_id"]]) for r in results]
    args.out.mkdir(exist_ok=True)
    wrong = sum(r["predicted"] != r["label"] for r in results)
    if wrong < MIN_WRONG:
        # Too few mistakes to train or test a checker on. The error rate is the finding.
        by = {}
        for r in results:
            by.setdefault(r["scenario"], [0, 0])[r["predicted"] != r["label"]] += 1
        summary = {"invoices": len(results), "wrong": wrong, "wrong_by_scenario": {k: v[1] for k, v in by.items() if v[1]}}
        print(json.dumps(summary, indent=2))
        (args.out / f"{args.run}_summary.json").write_text(json.dumps(summary, indent=2))
        return
    for level in ["label", "hold"]:
        rep, _, _ = analyse(results, texts, level)
        print_report(rep)
        (args.out / f"{args.run}_{level}.json").write_text(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
