"""The two headline charts, as PNGs for the README.

1. Risk-coverage: automate the invoices each signal is least doubtful about first. How
   many can be automated before errors among them exceed a given rate?
2. Layer sweep: how well a probe at each layer of the model predicts its mistakes.

Colours are the validated reference palette (light mode). Two of them sit below 3:1
contrast on the background, so each line also has its own dash style, and the README
shows the same numbers as a table.

Run:  uv run python -m the_tell.charts --run qwen3-4b-full
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from the_tell.analysis import analyse, load_run, risk_coverage
from the_tell.generate import read_jsonl
from the_tell.prompt import user_message

SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"

# signal -> (legend name, colour, dash). Fixed order, so a colour always means the same signal.
# The text-only baseline is left off the chart: the text-and-answer baseline beats it
# everywhere, and the strongest cheap baseline is the fair one to draw. Both are in the tables.
SERIES = {
    "probe": ("Probe on internal state", "#2a78d6", "-"),
    "text_and_answer": ("Invoice text + the model's answer", "#eb6834", (0, (6, 3))),
    "answer_prob": ("Answer probability", "#1baf7a", (0, (2, 2))),
    "stated": ("Stated confidence", "#eda100", (0, (6, 2, 2, 2))),
    "case_type": ("Known hard case types (reference)", "#8a8984", (0, (1, 3))),
}


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def risk_coverage_chart(scores: dict, y: np.ndarray, mask: np.ndarray, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5.4), dpi=200, facecolor=SURFACE)
    _style(ax)
    top = 4.0
    for key, (name, colour, dash) in SERIES.items():
        cov, risk = risk_coverage(scores[key][mask], y[mask])
        if len(cov) == 1:  # every invoice got the same score: the signal cannot rank them at all
            name += " (cannot rank: one value for all)"
        ax.plot(cov * 100, risk * 100, color=colour, linestyle=dash, linewidth=2, label=name,
                marker="o" if len(cov) <= 3 else None, markersize=7)
        settled = risk[cov >= 0.05]  # the first few invoices are too few for a stable rate
        top = max(top, float(settled.max()) * 100 if len(settled) else 0)
    ax.axhline(2, color=INK_2, linewidth=1, linestyle=":")
    ax.text(1, 2 + top * 0.015, "2% error", color=INK_2, fontsize=8)
    ax.set_xlim(0, 101)
    ax.set_ylim(0, top * 1.08)
    ax.set_xlabel("Share of invoices automated, least doubtful first (%)", color=INK, fontsize=10)
    ax.set_ylabel("Error rate among automated invoices (%)", color=INK, fontsize=10)
    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=22)
    ax.text(0, 1.02, "Each invoice scored by a model trained only on other suppliers", transform=ax.transAxes, color=INK_2, fontsize=8.5)
    ax.legend(frameon=False, fontsize=8.5, labelcolor=INK, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def layer_chart(report: dict, path: Path) -> None:
    sweep = report["layer_sweep"]
    mean, lo, hi = (np.array(sweep[k]) for k in ["mean", "min", "max"])
    layers = np.arange(len(mean))
    fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=200, facecolor=SURFACE)
    _style(ax)
    colour = SERIES["probe"][1]
    ax.fill_between(layers, lo, hi, color=colour, alpha=0.15, linewidth=0, label="range across the 5 rotations")
    ax.plot(layers, mean, color=colour, linewidth=2, marker="o", markersize=3.5, label="average")
    ax.axhline(0.5, color=INK_2, linewidth=1, linestyle=":")
    ax.text(layers[-1], 0.5 + 0.01, "chance", color=INK_2, fontsize=8, ha="right", va="bottom")
    best = int(mean.argmax())
    ax.annotate(f"best on average: layer {best}", (best, mean[best]), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8.5, color=INK)
    ax.set_xlabel("Layer (0 = word embeddings, before any processing)", color=INK, fontsize=10)
    ax.set_ylabel("AUROC on validation suppliers", color=INK, fontsize=10)
    ax.set_title("How well a probe at each layer predicts the model's mistakes", color=INK, fontsize=11, loc="left")
    ax.set_ylim(min(0.4, float(lo.min()) - 0.05), 1.0)
    ax.legend(frameon=False, fontsize=8.5, labelcolor=INK, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--cases", type=Path, default=Path("data/generated/cases.jsonl"))
    ap.add_argument("--held-out", default=None)
    ap.add_argument("--out", type=Path, default=Path("results"))
    args = ap.parse_args()

    results, acts = load_run(Path("runs") / args.run)
    cases = {c.case_id: c for c in read_jsonl(args.cases)}
    texts = [user_message(cases[r["case_id"]]) for r in results]
    args.out.mkdir(exist_ok=True)

    for level, title in [("label", "Predicting a wrong outcome"), ("hold", "Predicting a wrong approve-or-hold decision")]:
        report, scores, y, scored = analyse(results, acts, texts, level, args.held_out)
        (args.out / f"{args.run}_{level}.json").write_text(json.dumps(report, indent=2))
        risk_coverage_chart(scores, y, scored, title, args.out / f"{args.run}_risk_coverage_{level}.png")
        if level == "label":
            layer_chart(report, args.out / f"{args.run}_layers.png")
        print(f"{level}: charts written to {args.out}/")


if __name__ == "__main__":
    main()
