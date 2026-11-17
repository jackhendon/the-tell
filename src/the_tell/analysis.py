"""Step 4: which signal best predicts the model's mistakes?

Every signal is turned into a "doubt score" per invoice: higher means "more likely wrong".
Each is judged on invoices from suppliers it never saw during training.

Signals, from the model's outputs:
  stated       100 minus the confidence the model wrote
  answer_prob  doubt in its chosen outcome: log(1 - p), from the log-probabilities
  agreement    expected disagreement across samples at temperature 0.7. With no reasoning
               step this is a function of answer_prob, so it adds nothing for the local
               model. It matters for Claude (step 5), where log-probabilities are not exposed.
Signals that are trained (on train-supplier invoices only):
  probe        logistic regression on the model's internal state at one layer
  input_only   the same kind of model, reading only the invoice text. If the probe cannot
               beat this, it has learned which invoices are hard, not what the model knows.
Reference only, not a usable signal:
  case_type    the error rate of each generator scenario. Uses information no real system
               has; it shows how far "knowing the hard case types" alone gets you.

Run:  uv run python -m the_tell.analysis --run qwen3-4b-full
"""

import argparse
import json
import random
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from the_tell.domain import Label
from the_tell.generate import read_jsonl
from the_tell.prompt import user_message

PROBE_C = [0.0003, 0.001, 0.003, 0.01]  # regularisation strengths tried; chosen on validation
SAMPLE_TEMPERATURE = 0.7


# --- Loading ---


def load_run(run_dir: Path) -> tuple[list[dict], np.ndarray]:
    results = [json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l.strip()]
    acts = np.stack([np.load(run_dir / "acts" / f"{r['case_id']}.npy") for r in results])
    return results, acts  # acts: (invoices, layers + 1, hidden size), float16


def is_wrong(results: list[dict], level: str) -> np.ndarray:
    """level "label": the exact outcome is wrong.
    level "hold": the approve-or-hold decision is wrong (a wrong reason for holding is fine).
    An unreadable answer is always wrong."""
    out = []
    for r in results:
        if r["predicted"] is None:
            out.append(True)
        elif level == "label":
            out.append(r["predicted"] != r["label"])
        else:
            out.append((r["predicted"] == Label.APPROVE) != (r["label"] == Label.APPROVE))
    return np.array(out)


def supplier_split(results: list[dict], seed: int = 0) -> np.ndarray:
    """60% of suppliers for training, 20% for choosing settings, 20% for the final test.
    Splitting by supplier stops a probe scoring well by recognising a supplier it has seen."""
    suppliers = sorted({r["supplier_id"] for r in results})
    random.Random(seed).shuffle(suppliers)
    n = len(suppliers)
    part = {s: "train" if i < 0.6 * n else "val" if i < 0.8 * n else "test" for i, s in enumerate(suppliers)}
    return np.array([part[r["supplier_id"]] for r in results])


# --- Signals that need no training ---


def output_signals(results: list[dict]) -> dict[str, np.ndarray]:
    stated, answer_doubt, disagreement = [], [], []
    for r in results:
        lps = np.array(list(r["outcome_logprobs"].values()))
        top = lps.max()
        stated.append(100 - (r["confidence"] if r["confidence"] is not None else 0))
        answer_doubt.append(np.log(max(-np.expm1(top), 1e-300)))  # log(1 - p), kept precise near p = 1
        scaled = np.exp((lps - top) / SAMPLE_TEMPERATURE)
        disagreement.append(1 - 1 / scaled.sum())  # chance one sample differs from the top answer
    return {"stated": np.array(stated, float), "answer_prob": np.array(answer_doubt), "agreement": np.array(disagreement)}


# --- Trained signals ---


def _fit(X: np.ndarray, y: np.ndarray, C: float):
    model = make_pipeline(StandardScaler(), LogisticRegression(C=C, class_weight="balanced", max_iter=3000))
    return model.fit(X, y)


def _auroc(y: np.ndarray, score: np.ndarray) -> float:
    return float(roc_auc_score(y, score)) if 0 < y.sum() < len(y) else float("nan")


def probe_layer_sweep(acts: np.ndarray, y: np.ndarray, train: np.ndarray, val: np.ndarray) -> list[dict]:
    """For every layer, train a probe on train invoices and score it on validation invoices."""
    sweep = []
    for layer in range(acts.shape[1]):
        X = acts[:, layer, :].astype(np.float32)
        best = max(
            ({"layer": layer, "C": C, "val_auroc": _auroc(y[val], _fit(X[train], y[train], C).decision_function(X[val]))} for C in PROBE_C),
            key=lambda d: d["val_auroc"],
        )
        sweep.append(best)
    return sweep


def probe_scores(acts: np.ndarray, y: np.ndarray, fit_mask: np.ndarray, layer: int, C: float) -> np.ndarray:
    X = acts[:, layer, :].astype(np.float32)
    return _fit(X[fit_mask], y[fit_mask], C).decision_function(X)


def input_only_scores(texts: list[str], y: np.ndarray, fit_mask: np.ndarray, val: np.ndarray) -> np.ndarray:
    """Predicts the model's errors from the invoice text alone, never looking inside the model."""
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    X = vec.fit_transform(texts)
    best_C = max(PROBE_C + [0.1, 1.0], key=lambda C: _auroc(y[val], LogisticRegression(C=C, class_weight="balanced", max_iter=3000).fit(X[fit_mask & ~val], y[fit_mask & ~val]).decision_function(X[val])))
    return LogisticRegression(C=best_C, class_weight="balanced", max_iter=3000).fit(X[fit_mask], y[fit_mask]).decision_function(X)


def case_type_scores(results: list[dict], y: np.ndarray, fit_mask: np.ndarray) -> np.ndarray:
    rates: dict[str, list[bool]] = {}
    for r, wrong, use in zip(results, y, fit_mask):
        if use:
            rates.setdefault(r["scenario"], []).append(bool(wrong))
    overall = float(y[fit_mask].mean())
    return np.array([np.mean(rates[r["scenario"]]) if r["scenario"] in rates else overall for r in results])


# --- Measuring how useful a signal is ---


def risk_coverage(score: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Hand the least doubtful invoices to automation first. For each share automated
    (coverage), the error rate among those automated invoices (risk)."""
    order = np.argsort(score, kind="stable")
    sorted_score, wrong = score[order], y[order].astype(float)
    n = np.arange(1, len(y) + 1)
    # Only measure where the score changes. Invoices with the same score cannot be told
    # apart by the signal, so it must automate all of them or none of them. (Otherwise a
    # signal that says "100" for everything would look as if it could rank invoices.)
    ends = np.r_[np.nonzero(np.diff(sorted_score))[0], len(y) - 1]
    return n[ends] / len(y), np.cumsum(wrong)[ends] / n[ends]


def coverage_at_risk(score: np.ndarray, y: np.ndarray, max_risk: float) -> float:
    """The largest share of invoices that can be automated with an error rate at or below max_risk."""
    cov, risk = risk_coverage(score, y)
    ok = cov[risk <= max_risk]
    return float(ok.max()) if len(ok) else 0.0


def evaluate(scores: dict[str, np.ndarray], y: np.ndarray, mask: np.ndarray) -> dict[str, dict]:
    return {
        name: {
            "auroc": _auroc(y[mask], s[mask]),
            "coverage_at_2pct_error": coverage_at_risk(s[mask], y[mask], 0.02),
            "coverage_at_5pct_error": coverage_at_risk(s[mask], y[mask], 0.05),
        }
        for name, s in scores.items()
    }


# --- The whole analysis ---


def analyse(results: list[dict], acts: np.ndarray, texts: list[str], level: str, held_out: str | None) -> dict:
    y = is_wrong(results, level)
    split = supplier_split(results)
    labels = np.array([r["label"] for r in results])
    excluded = labels == held_out if held_out else np.zeros(len(results), bool)  # never trained on
    train, val, test = (split == "train") & ~excluded, (split == "val") & ~excluded, (split == "test") & ~excluded

    sweep = probe_layer_sweep(acts, y, train, val)
    best = max(sweep, key=lambda d: d["val_auroc"])
    fit_mask = train | val  # refit on train + validation once settings are chosen

    scores = output_signals(results)
    scores["probe"] = probe_scores(acts, y, fit_mask, best["layer"], best["C"])
    scores["input_only"] = input_only_scores(texts, y, fit_mask, val)
    scores["case_type"] = case_type_scores(results, y, fit_mask)

    report = {
        "level": level,
        "counts": {
            "invoices": len(results),
            "wrong": int(y.sum()),
            "train": int(train.sum()), "val": int(val.sum()), "test": int(test.sum()),
            "test_wrong": int(y[test].sum()),
        },
        "probe_layer": best["layer"],
        "probe_C": best["C"],
        "layer_sweep": sweep,
        "test": evaluate(scores, y, test),
    }
    if held_out:
        report["held_out_label"] = held_out
        report["held_out_counts"] = {"invoices": int(excluded.sum()), "wrong": int(y[excluded].sum())}
        report["held_out"] = evaluate(scores, y, excluded)
    return report, scores, y, test


def print_report(rep: dict) -> None:
    c = rep["counts"]
    print(f"\n=== Errors at the {rep['level']!r} level: {c['wrong']} of {c['invoices']} invoices wrong ===")
    print(f"Split by supplier: train {c['train']}, validation {c['val']}, test {c['test']} ({c['test_wrong']} wrong in test)")
    print(f"Probe: best layer {rep['probe_layer']} of {len(rep['layer_sweep']) - 1}, regularisation C={rep['probe_C']}")
    for section in ["test", "held_out"]:
        if section not in rep:
            continue
        title = "Test suppliers" if section == "test" else f"Held-out problem type {rep['held_out_label']} (never trained on)"
        print(f"\n{title}")
        print(f"  {'signal':<12} {'AUROC':>6}  {'automatable at 2% error':>24}  {'at 5% error':>12}")
        for name, m in rep[section].items():
            print(f"  {name:<12} {m['auroc']:>6.3f}  {m['coverage_at_2pct_error']:>23.0%}  {m['coverage_at_5pct_error']:>12.0%}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--cases", type=Path, default=Path("data/generated/cases.jsonl"))
    ap.add_argument("--held-out", default=None, help="a true label kept out of all training, e.g. TAX_ERROR")
    ap.add_argument("--out", type=Path, default=Path("results"))
    args = ap.parse_args()

    results, acts = load_run(Path("runs") / args.run)
    cases = {c.case_id: c for c in read_jsonl(args.cases)}
    texts = [user_message(cases[r["case_id"]]) for r in results]

    args.out.mkdir(exist_ok=True)
    for level in ["label", "hold"]:
        rep, _, _, _ = analyse(results, acts, texts, level, args.held_out)
        print_report(rep)
        (args.out / f"{args.run}_{level}.json").write_text(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
