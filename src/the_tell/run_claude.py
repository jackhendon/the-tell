"""Step 5: the same invoices, answered by Claude Haiku 5.5 through the API.

There's no internal state to read through an API, so this records what you can get:
the answer, the stated confidence, and how often Claude changes its answer when asked
the same question again. Each invoice is asked SAMPLES times.

Set-up choices, and why:
  - Thinking: run both ways (--thinking off|on). The pilot showed that with thinking off,
    Haiku often writes its reasoning out in the reply before answering, so it needs room
    for that. With thinking on (low effort) it reasons privately and replies in two lines.
  - No temperature setting. Haiku 5.5 doesn't accept one, so every answer is already a
    sample at its default setting. Asking five times shows how much it varies.
  - The system prompt (role, policy, answer format) is identical to the Qwen run and is
    cached, so it's billed at a tenth of the price after the first call.
  - The key is read from .env only. This laptop may also have a work login, and the run
    must never fall back to it.

Three commands:
  pilot    a few invoices, answered straight away, with the cost of a full run projected
  submit   every invoice as one batch (half price, results within 24 hours)
  collect  fetch the batch results once it has finished

Run:  uv run python -m the_tell.run_claude pilot --run haiku-pilot
"""

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import anthropic

from the_tell.domain import Case
from the_tell.generate import read_jsonl
from the_tell.prompt import SYSTEM_PROMPT, parse_answer, user_message

MODEL = "claude-haiku-5-5"
SAMPLES = 5
# Room for written-out reasoning (thinking off) or private reasoning (thinking on).
MAX_TOKENS = {"off": 1500, "on": 3000}

# US dollars per million tokens, Claude Haiku 5.5, prompts up to 100K tokens.
PRICE = {"input": 0.10, "output": 0.50, "cache_read": 0.01, "cache_write": 0.125}
BATCH_DISCOUNT = 0.5


def load_key(path: Path = Path(".env")) -> str:
    """The API key from .env, and nowhere else."""
    if path.exists():
        for line in path.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "ANTHROPIC_API_KEY" and value.strip():
                return value.strip()
    raise SystemExit("No ANTHROPIC_API_KEY in .env. Add your personal key there; nothing else is used.")


def make_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=load_key())


def request_params(c: Case, thinking: str) -> dict:
    extra = {"thinking": {"type": "disabled"}} if thinking == "off" else {"thinking": {"type": "adaptive"}, "output_config": {"effort": "low"}}
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS[thinking],
        **extra,
        "system": [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_message(c)}],
    }


def custom_id(case_id: str, sample: int) -> str:
    return f"{case_id}__s{sample}"


def call_record(cid: str, message) -> dict:
    """What we keep from one reply. Text is read by block type, never by position."""
    text = "".join(b.text for b in message.content if b.type == "text")
    u = message.usage
    return {
        "custom_id": cid,
        "raw": text,
        "stop_reason": message.stop_reason,
        "usage": {
            "input": u.input_tokens,
            "output": u.output_tokens,
            "cache_read": u.cache_read_input_tokens or 0,
            "cache_write": u.cache_creation_input_tokens or 0,
        },
    }


def cost(usage: dict, batch: bool) -> float:
    dollars = sum(usage[k] * PRICE[k] for k in PRICE) / 1_000_000
    return dollars * (BATCH_DISCOUNT if batch else 1)


def read_calls(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return {r["custom_id"]: r for r in map(json.loads, path.read_text().splitlines()) if r}


def append(path: Path, record: dict) -> None:
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")


def build_results(cases: list[Case], calls: dict[str, dict]) -> list[dict]:
    """One record per invoice, in the same shape as the Qwen run where it can be.

    The first sample is "the answer", as a single call would be in real use. The other
    four are only used to measure how often Claude would have answered differently.
    """
    out = []
    for c in cases:
        replies = [calls.get(custom_id(c.case_id, s)) for s in range(SAMPLES)]
        if any(r is None for r in replies):
            continue
        answers = [parse_answer(r["raw"]) for r in replies]
        first = answers[0]
        out.append({
            "case_id": c.case_id,
            "label": c.label.value,
            "scenario": c.scenario,
            "difficulty": c.difficulty,
            "supplier_id": c.supplier.supplier_id,
            "amount_at_risk_pence": c.amount_at_risk_pence,
            "predicted": first.label.value if first.label else None,
            "confidence": first.confidence,
            "sample_answers": [a.label.value if a.label else None for a in answers],
            "sample_confidences": [a.confidence for a in answers],
            "raw": first.raw,
            "stop_reasons": [r["stop_reason"] for r in replies],
        })
    return out


def summarise(results: list[dict], calls: dict[str, dict], batch: bool, total_cases: int) -> None:
    n = len(results)
    wrong = [r for r in results if r["predicted"] != r["label"]]
    unreadable = sum(a is None for r in results for a in r["sample_answers"])
    varied = sum(len(set(r["sample_answers"])) > 1 for r in results)
    usage = Counter()
    for c in calls.values():
        usage.update(c["usage"])
    spent = cost(usage, batch)
    print(f"\n{n} invoices, {len(calls)} calls")
    print(f"  wrong (first answer): {len(wrong)} of {n} ({len(wrong) / max(n, 1):.0%})")
    print(f"  unreadable answers:   {unreadable} of {len(calls)}")
    print(f"  stated confidence:    {dict(Counter(r['confidence'] for r in results))}")
    print(f"  invoices where the {SAMPLES} answers were not all the same: {varied} of {n}")
    print(f"  stop reasons:         {dict(Counter(s for r in results for s in r['stop_reasons']))}")
    print(f"  tokens: {dict(usage)}")
    print(f"  cost so far: ${spent:.4f}" + (" (batch price)" if batch else ""))
    if n and not batch:
        per_invoice = cost(usage, batch=True) / n
        print(f"  projected full run as a batch: {total_cases} invoices x {SAMPLES} answers = ${per_invoice * total_cases:.2f}")
    print("\n  by scenario (right/wrong, first answer):")
    by = Counter((r["scenario"], r["predicted"] == r["label"]) for r in results)
    for sc in sorted({r["scenario"] for r in results}):
        print(f"    {sc:28} {by[(sc, True)]} right, {by[(sc, False)]} wrong")


def pilot(args, cases: list[Case], run_dir: Path) -> None:
    """One invoice per scenario (or more with --per-scenario), answered straight away."""
    chosen, seen = [], Counter()
    for c in cases:
        if seen[c.scenario] < args.per_scenario:
            chosen.append(c)
            seen[c.scenario] += 1
    calls_path = run_dir / "calls.jsonl"
    done = read_calls(calls_path)
    client = make_client()
    todo = [(c, s) for c in chosen for s in range(SAMPLES) if custom_id(c.case_id, s) not in done]
    print(f"{len(chosen)} invoices x {SAMPLES} answers; {len(todo)} calls to make", flush=True)
    for i, (c, s) in enumerate(todo, 1):
        cid = custom_id(c.case_id, s)
        try:
            message = client.messages.create(**request_params(c, args.thinking))
        except anthropic.AuthenticationError:
            raise SystemExit("The API key in .env was rejected.")
        except anthropic.APIStatusError as e:
            raise SystemExit(f"API error {e.status_code} on {cid}: {e.message}")
        append(calls_path, call_record(cid, message))
        if i % 25 == 0:
            print(f"  {i}/{len(todo)}", flush=True)
    calls = read_calls(calls_path)
    results = build_results(chosen, calls)
    (run_dir / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results))
    summarise(results, calls, batch=False, total_cases=len(cases))


BATCH_SIZE = 2000  # requests per batch; one batch of all 10,000 was too big to upload reliably


def submit(args, cases: list[Case], run_dir: Path) -> None:
    """Sends the run as several batches. Each batch is recorded as soon as it's accepted,
    so if an upload fails, running submit again sends only the batches still missing."""
    batch_file = run_dir / "batch.json"
    info = json.loads(batch_file.read_text()) if batch_file.exists() else {"thinking": args.thinking, "batches": []}
    if info["thinking"] != args.thinking:
        raise SystemExit(f"This run was started with thinking {info['thinking']}.")
    requests = [{"custom_id": custom_id(c.case_id, s), "params": request_params(c, args.thinking)} for c in cases for s in range(SAMPLES)]
    chunks = [requests[i : i + BATCH_SIZE] for i in range(0, len(requests), BATCH_SIZE)]
    client = make_client()
    for n, chunk in enumerate(chunks):
        if n < len(info["batches"]):
            continue  # already submitted
        batch = client.messages.batches.create(requests=chunk)
        info["batches"].append({"id": batch.id, "requests": len(chunk), "submitted": time.strftime("%Y-%m-%d %H:%M:%S")})
        batch_file.write_text(json.dumps(info, indent=2))
        print(f"Submitted batch {n + 1}/{len(chunks)}: {batch.id} ({len(chunk)} requests)", flush=True)


def collect(args, cases: list[Case], run_dir: Path) -> None:
    info = json.loads((run_dir / "batch.json").read_text())
    client = make_client()
    batches = [client.messages.batches.retrieve(b["id"]) for b in info["batches"]]
    for b in batches:
        print(f"Batch {b.id}: {b.processing_status}, counts {b.request_counts}")
    if any(b.processing_status != "ended" for b in batches):
        return
    calls_path = run_dir / "calls.jsonl"
    done = read_calls(calls_path)
    failed = 0
    for result in (r for b in batches for r in client.messages.batches.results(b.id)):
        if result.custom_id in done:
            continue
        if result.result.type == "succeeded":
            append(calls_path, call_record(result.custom_id, result.result.message))
        else:
            failed += 1
    calls = read_calls(calls_path)
    results = build_results(cases, calls)
    (run_dir / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results))
    if failed:
        print(f"{failed} requests did not succeed; their invoices are left out of results.jsonl.")
    summarise(results, calls, batch=True, total_cases=len(cases))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["pilot", "submit", "collect"])
    ap.add_argument("--run", required=True)
    ap.add_argument("--cases", type=Path, default=Path("data/generated/cases.jsonl"))
    ap.add_argument("--per-scenario", type=int, default=1, help="pilot only")
    ap.add_argument("--thinking", choices=["off", "on"], default="off")
    args = ap.parse_args()

    run_dir = Path("runs") / args.run
    run_dir.mkdir(parents=True, exist_ok=True)
    cases = read_jsonl(args.cases)
    {"pilot": pilot, "submit": submit, "collect": collect}[args.command](args, cases, run_dir)


if __name__ == "__main__":
    main()
