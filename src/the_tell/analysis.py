"""Step 4: which signal best predicts the model's mistakes?

Every signal is turned into a "doubt score" per invoice: higher means "more likely wrong".

How it is tested (rotation): suppliers are split into five groups. Five times over, one
group is the test group, one picks the probe's settings (validation), and the other three
train it. Every invoice is scored exactly once, by a model that never saw its supplier,
so every invoice counts towards the result.

Error bars: the whole measurement is repeated on 1,000 resamples of the suppliers (drawn
with replacement), and the middle 95% of the results is reported. Suppliers rather than
invoices are resampled, because invoices from one supplier are not independent.

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
  text_and_answer  the input-only model, also told the answer the model gave. Every word is
               paired with the answer ("APPROVE_credit"), so it can learn which answers
               are wrong for which kinds of invoice. The internal state at the moment we
               read it already holds the coming answer, so this is the fairest cheap
               comparison: does the probe know more than "this text, and that answer"?
  answer_given the error rate, on train-supplier invoices, of the answer the model gave
               (how often "PRICE_VARIANCE" turned out wrong, and so on). Usable in a real
               system. If the probe cannot beat this, it is only reading the model's answer.
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


def supplier_folds(results: list[dict], k: int = 5, seed: int = 0) -> np.ndarray:
    """Assign every supplier to one of k groups, so all of a supplier's invoices are always
    on the same side of the train/test line. Otherwise a probe could score well by
    recognising a supplier it had already seen."""
    suppliers = sorted({r["supplier_id"] for r in results})
    random.Random(seed).shuffle(suppliers)
    fold = {s: i % k for i, s in enumerate(suppliers)}
    return np.array([fold[r["supplier_id"]] for r in results])


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


def with_answer(texts: list[str], results: list[dict]) -> list[str]:
    """Each invoice text with every word also paired with the model's answer."""
    return [t + " " + " ".join(f"{r['predicted']}_{w}" for w in t.split()) for t, r in zip(texts, results)]


def input_only_scores(texts: list[str], y: np.ndarray, fit_mask: np.ndarray, val: np.ndarray) -> np.ndarray:
    """Predicts the model's errors from the invoice text alone, never looking inside the model."""
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    X = vec.fit_transform(texts)
    best_C = max(PROBE_C + [0.1, 1.0, 10.0], key=lambda C: _auroc(y[val], LogisticRegression(C=C, class_weight="balanced", max_iter=3000).fit(X[fit_mask & ~val], y[fit_mask & ~val]).decision_function(X[val])))
    return LogisticRegression(C=best_C, class_weight="balanced", max_iter=3000).fit(X[fit_mask], y[fit_mask]).decision_function(X)


def answer_given_scores(results: list[dict], y: np.ndarray, fit_mask: np.ndarray) -> np.ndarray:
    """How often each answer the model gives turns out to be wrong, learned on the fit invoices."""
    return _rate_by(results, "predicted", y, fit_mask)


def case_type_scores(results: list[dict], y: np.ndarray, fit_mask: np.ndarray) -> np.ndarray:
    return _rate_by(results, "scenario", y, fit_mask)


def _rate_by(results: list[dict], key: str, y: np.ndarray, fit_mask: np.ndarray) -> np.ndarray:
    rates: dict[str, list[bool]] = {}
    for r, wrong, use in zip(results, y, fit_mask):
        if use:
            rates.setdefault(str(r[key]), []).append(bool(wrong))
    overall = float(y[fit_mask].mean())
    return np.array([np.mean(rates[str(r[key])]) if str(r[key]) in rates else overall for r in results])


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


def within_type_auroc(score: np.ndarray, y: np.ndarray, mask: np.ndarray, scenarios: np.ndarray, min_each: int = 3) -> dict:
    """Can the signal tell right from wrong among invoices of the same kind?

    If the model's mistakes are systematic (it gets one kind of invoice wrong most of the
    time), a signal can look good just by recognising the kind of invoice. That is a fact
    about the input, not about the model's doubt. Measuring separately inside each scenario
    removes that advantage: "knowing the hard case types" scores exactly 0.5 here.
    Only scenarios with at least min_each right and min_each wrong answers are used.
    """
    per, weights, detail = [], [], {}
    for sc in np.unique(scenarios[mask]):
        m = mask & (scenarios == sc)
        wrong = int(y[m].sum())
        if wrong >= min_each and m.sum() - wrong >= min_each:
            per.append(_auroc(y[m], score[m]))
            weights.append(m.sum())
            detail[str(sc)] = {"right": int(m.sum()) - wrong, "wrong": wrong, "auroc": per[-1]}
    if not per:
        return {"auroc": float("nan"), "scenarios_used": 0, "invoices_used": 0, "per_group": {}}
    return {"auroc": float(np.average(per, weights=weights)), "scenarios_used": len(per), "invoices_used": int(sum(weights)), "per_group": detail}


# --- Error bars ---

BOOTSTRAP_REPS = 1000


def bootstrap(scores: dict[str, np.ndarray], y: np.ndarray, mask: np.ndarray, groups: np.ndarray, scenarios: np.ndarray | None = None, seed: int = 0) -> dict:
    """95% ranges for each signal's metrics, and for the probe's AUROC advantage over each
    other signal (paired: both measured on the same resample, which is much less noisy than
    comparing two separate ranges)."""
    rng = np.random.default_rng(seed)
    by_group = {g: np.nonzero(mask & (groups == g))[0] for g in np.unique(groups[mask])}
    keys = list(by_group)
    draws: dict[str, list] = {f"{n}.{m}": [] for n in scores for m in ["auroc", "cov2", "cov5"]}
    draws.update({f"probe_minus.{n}": [] for n in scores if n != "probe"})
    if scenarios is not None:
        draws.update({f"{n}.within": [] for n in scores})
        draws.update({f"probe_minus_within.{n}": [] for n in scores if n != "probe"})
    for _ in range(BOOTSTRAP_REPS):
        idx = np.concatenate([by_group[keys[i]] for i in rng.integers(0, len(keys), len(keys))])
        yb = y[idx]
        if not 0 < yb.sum() < len(yb):
            continue
        aurocs = {}
        for n, s in scores.items():
            aurocs[n] = _auroc(yb, s[idx])
            draws[f"{n}.auroc"].append(aurocs[n])
            draws[f"{n}.cov2"].append(coverage_at_risk(s[idx], yb, 0.02))
            draws[f"{n}.cov5"].append(coverage_at_risk(s[idx], yb, 0.05))
        for n in scores:
            if n != "probe":
                draws[f"probe_minus.{n}"].append(aurocs["probe"] - aurocs[n])
        if scenarios is not None:
            within = {n: within_type_auroc(s[idx], yb, np.ones(len(idx), bool), scenarios[idx])["auroc"] for n, s in scores.items()}
            if not np.isnan(within["probe"]):
                for n in scores:
                    draws[f"{n}.within"].append(within[n])
                    if n != "probe":
                        draws[f"probe_minus_within.{n}"].append(within["probe"] - within[n])
    return {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in draws.items() if v}


def summarise(scores: dict[str, np.ndarray], y: np.ndarray, mask: np.ndarray, groups: np.ndarray, scenarios: np.ndarray, answers: np.ndarray) -> dict:
    point = evaluate(scores, y, mask)
    ci = bootstrap(scores, y, mask, groups, scenarios)
    out = {"signals": {}, "probe_advantage_auroc": {}, "probe_advantage_within_type": {}}
    for n, m in point.items():
        out["signals"][n] = {
            "auroc": m["auroc"], "auroc_95": ci.get(f"{n}.auroc"),
            "coverage_at_2pct_error": m["coverage_at_2pct_error"], "coverage_at_2pct_error_95": ci.get(f"{n}.cov2"),
            "coverage_at_5pct_error": m["coverage_at_5pct_error"], "coverage_at_5pct_error_95": ci.get(f"{n}.cov5"),
            "within_type": within_type_auroc(scores[n], y, mask, scenarios) | {"auroc_95": ci.get(f"{n}.within")},
            # Same idea, grouped by the answer the model gave: among invoices it approved, can
            # the signal find the ones it should have held?
            "within_answer": within_type_auroc(scores[n], y, mask, answers),
        }
    for n in point:
        if n != "probe":
            out["probe_advantage_auroc"][n] = {"diff": point["probe"]["auroc"] - point[n]["auroc"], "diff_95": ci.get(f"probe_minus.{n}")}
            w = out["signals"]
            out["probe_advantage_within_type"][n] = {"diff": w["probe"]["within_type"]["auroc"] - w[n]["within_type"]["auroc"], "diff_95": ci.get(f"probe_minus_within.{n}")}
    return out


# --- The whole analysis ---


def analyse(results: list[dict], acts: np.ndarray, texts: list[str], level: str, held_out: str | None, k: int = 5):
    y = is_wrong(results, level)
    folds = supplier_folds(results, k)
    suppliers = np.array([r["supplier_id"] for r in results])
    labels = np.array([r["label"] for r in results])
    scenarios = np.array([r["scenario"] for r in results])
    answers = np.array([str(r["predicted"]) for r in results])
    excluded = labels == held_out if held_out else np.zeros(len(results), bool)  # never trained on

    scores = output_signals(results)
    texts_with_answer = with_answer(texts, results)
    for name in ["probe", "input_only", "text_and_answer", "answer_given", "case_type"]:
        scores[name] = np.zeros(len(results))
    sweeps, chosen = [], []
    for f in range(k):
        test = folds == f
        val = (folds == (f + 1) % k) & ~excluded
        train = ~test & ~val & ~excluded
        sweep = probe_layer_sweep(acts, y, train, val)
        best = max(sweep, key=lambda d: d["val_auroc"])
        fit = train | val  # refit on train + validation once settings are chosen
        scores["probe"][test] = probe_scores(acts, y, fit, best["layer"], best["C"])[test]
        scores["input_only"][test] = input_only_scores(texts, y, fit, val)[test]
        scores["text_and_answer"][test] = input_only_scores(texts_with_answer, y, fit, val)[test]
        scores["answer_given"][test] = answer_given_scores(results, y, fit)[test]
        scores["case_type"][test] = case_type_scores(results, y, fit)[test]
        sweeps.append([d["val_auroc"] for d in sweep])
        chosen.append({"fold": f, "layer": best["layer"], "C": best["C"]})
        print(f"  fold {f + 1}/{k}: probe layer {best['layer']}, C={best['C']}", flush=True)

    sweeps = np.array(sweeps)  # (folds, layers)
    report = {
        "level": level,
        "counts": {"invoices": len(results), "wrong": int(y.sum()), "folds": k, "suppliers": len(set(suppliers))},
        "probe_per_fold": chosen,
        "layer_sweep": {
            "mean": sweeps.mean(0).tolist(), "min": sweeps.min(0).tolist(), "max": sweeps.max(0).tolist(),
        },
        "in_distribution": summarise(scores, y, ~excluded, suppliers, scenarios, answers),
    }
    if held_out:
        report["held_out_label"] = held_out
        report["held_out_counts"] = {"invoices": int(excluded.sum()), "wrong": int(y[excluded].sum())}
        report["held_out"] = summarise(scores, y, excluded, suppliers, scenarios, answers)
    return report, scores, y, ~excluded


def _range(r) -> str:
    return f"({r[0]:.2f} to {r[1]:.2f})" if r else ""


def _pct_range(r) -> str:
    return f"({r[0]:.0%} to {r[1]:.0%})" if r else ""


def print_report(rep: dict) -> None:
    c = rep["counts"]
    print(f"\n=== Errors at the {rep['level']!r} level: {c['wrong']} of {c['invoices']} invoices wrong ===")
    print(f"Rotation: {c['folds']} groups of suppliers ({c['suppliers']} suppliers); every invoice scored once by a model that never saw its supplier")
    print("Probe layer chosen in each rotation:", ", ".join(str(d["layer"]) for d in rep["probe_per_fold"]))
    for section in ["in_distribution", "held_out"]:
        if section not in rep:
            continue
        title = "All invoices" if section == "in_distribution" else f"Held-out problem type {rep['held_out_label']} (never trained on)"
        if section == "in_distribution" and "held_out_label" in rep:
            title = f"All invoices except {rep['held_out_label']}"
        print(f"\n{title}   [95% ranges in brackets]")
        print(f"  {'signal':<15} {'AUROC':<22} {'within type':<24} {'automatable at 2% error':<26} {'at 5% error'}")
        for name, m in rep[section]["signals"].items():
            w = m["within_type"]
            print(
                f"  {name:<15} {m['auroc']:.2f} {_range(m['auroc_95']):<17} "
                f"{w['auroc']:.2f} {_range(w.get('auroc_95')):<14} [{w['scenarios_used']}]  "
                f"{m['coverage_at_2pct_error']:>4.0%} {_pct_range(m['coverage_at_2pct_error_95']):<21} "
                f"{m['coverage_at_5pct_error']:>4.0%} {_pct_range(m['coverage_at_5pct_error_95'])}"
            )
        print("  (within type: AUROC inside each kind of invoice, averaged; number of kinds used in square brackets)")
        for key, what in [("probe_advantage_auroc", "AUROC"), ("probe_advantage_within_type", "within-type AUROC")]:
            print(f"  Probe {what} advantage over:")
            for name, d in rep[section][key].items():
                r = d["diff_95"]
                verdict = "" if not r else ("  clearly better" if r[0] > 0 else "  clearly worse" if r[1] < 0 else "  not distinguishable")
                print(f"    {name:<15} {d['diff']:+.2f} {_range(r)}{verdict}")
        sig = rep[section]["signals"]
        for key, what in [("within_type", "Inside each kind of invoice"), ("within_answer", "Grouped by the answer the model gave")]:
            print(f"  {what} (AUROC; groups with at least 3 right and 3 wrong):")
            shown = ["probe", "text_and_answer", "input_only", "answer_given", "answer_prob"]
            print(f"    {'group':<28} {'right':>5} {'wrong':>5}   " + "  ".join(f"{n:>15}" for n in shown))
            for g, d in sig["probe"][key]["per_group"].items():
                print(f"    {g:<28} {d['right']:>5} {d['wrong']:>5}   " + "  ".join(f"{sig[n][key]['per_group'][g]['auroc']:>15.2f}" for n in shown))


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
        print(f"\nRotating over suppliers ({level!r} level)...", flush=True)
        rep, _, _, _ = analyse(results, acts, texts, level, args.held_out)
        print_report(rep)
        suffix = f"_heldout_{args.held_out}" if args.held_out else ""
        (args.out / f"{args.run}_{level}{suffix}.json").write_text(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
