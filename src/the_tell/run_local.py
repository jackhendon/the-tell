"""Runs the local open model over invoice cases.

For each case it records three things, all from the same moment: the point where the
model has read everything and written "OUTCOME:", but not yet chosen an outcome.

  1. Its internal state there: the activations at every layer for that last token.
     This is what the probe (step 4) learns from.
  2. The log-probability it puts on each of the seven outcomes as its next word. Logs,
     because the model is often 99.9999% sure, and plain probabilities round those to
     the same number, which would throw away the differences we want to rank by.
  3. Its actual answer, written token by token (always the most likely next token),
     which includes its stated confidence.

Results go to runs/<run>/results.jsonl and runs/<run>/acts/<case_id>.npy. The run is
resumable: cases already recorded are skipped.

Run:  uv run python -m the_tell.run_local --run pilot --limit 20
"""

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from the_tell.domain import Case, Label
from the_tell.generate import read_jsonl
from the_tell.prompt import SYSTEM_PROMPT, build_messages, parse_answer

MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"
REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"  # pinned: the exact files never change
ANSWER_PREFIX = "OUTCOME:"  # written for the model; it continues with " PRICE_VARIANCE" etc.
MAX_NEW_TOKENS = 24


def load_model(device: str):
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=REVISION,
        dtype=torch.bfloat16,
        use_safetensors=True,  # weights are plain numbers, cannot run code
        trust_remote_code=False,  # never run Python shipped with the model
    ).to(device)
    model.eval()
    return tok, model


def outcome_first_tokens(tok) -> dict[Label, int]:
    """The first token of each outcome as the model would write it after "OUTCOME:".

    These must all be different. Then the model's choice of first token is its choice of
    outcome, and one forward pass gives the probability of every outcome at once.
    """
    first = {label: tok.encode(" " + label.value, add_special_tokens=False)[0] for label in Label}
    if len(set(first.values())) != len(first):
        raise RuntimeError(f"Outcome names share a first token, so one pass cannot score them: {first}")
    return first


def stop_token_ids(tok) -> set[int]:
    ids = {tok.eos_token_id, tok.convert_tokens_to_ids("<|im_end|>")}
    return {i for i in ids if i is not None}


@torch.inference_mode()
def run_case(c: Case, tok, model, first_tokens: dict[Label, int], stops: set[int]) -> tuple[dict, np.ndarray]:
    prompt = tok.apply_chat_template(build_messages(c), tokenize=False, add_generation_prompt=True) + ANSWER_PREFIX
    input_ids = tok(prompt, return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
    started = time.time()

    # One pass over the whole prompt. Everything we measure comes from its last position.
    out = model(input_ids, output_hidden_states=True, use_cache=True)
    activations = torch.stack([h[0, -1] for h in out.hidden_states]).float().cpu().numpy().astype(np.float16)
    logprobs = torch.log_softmax(out.logits[0, -1].float(), dim=-1)
    outcome_logprobs = {label.value: logprobs[tid].item() for label, tid in first_tokens.items()}

    # Write the answer: always take the most likely next token, reusing the cached prompt.
    generated: list[int] = []
    next_id = out.logits[0, -1].argmax()
    past = out.past_key_values
    for _ in range(MAX_NEW_TOKENS):
        if next_id.item() in stops:
            break
        generated.append(next_id.item())
        out = model(next_id.view(1, 1), past_key_values=past, use_cache=True)
        past = out.past_key_values
        next_id = out.logits[0, -1].argmax()

    raw = ANSWER_PREFIX + tok.decode(generated)
    answer = parse_answer(raw)
    record = {
        "case_id": c.case_id,
        "label": c.label.value,
        "scenario": c.scenario,
        "difficulty": c.difficulty,
        "supplier_id": c.supplier.supplier_id,
        "amount_at_risk_pence": c.amount_at_risk_pence,
        "predicted": answer.label.value if answer.label else None,
        "confidence": answer.confidence,
        "outcome_logprobs": outcome_logprobs,
        "outcome_mass": sum(np.exp(v) for v in outcome_logprobs.values()),  # near 1.0 means it kept to the format
        "raw": raw,
        "prompt_tokens": input_ids.shape[1],
        "seconds": round(time.time() - started, 2),
    }
    return record, activations


def write_metadata(run_dir: Path, device: str, model, total_cases: int) -> None:
    meta = {
        "total_cases": total_cases,
        "model_id": MODEL_ID,
        "revision": REVISION,
        "dtype": "bfloat16",
        "device": device,
        "layers": model.config.num_hidden_layers,
        "hidden_size": model.config.hidden_size,
        "system_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()[:16],
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "machine": platform.machine(),
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (run_dir / "metadata.json").write_text(json.dumps(meta, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="name of the run folder under runs/")
    ap.add_argument("--cases", type=Path, default=Path("data/generated/cases.jsonl"))
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    run_dir = Path("runs") / args.run
    (run_dir / "acts").mkdir(parents=True, exist_ok=True)
    results_path = run_dir / "results.jsonl"
    done = {json.loads(l)["case_id"] for l in results_path.read_text().splitlines()} if results_path.exists() else set()

    cases = read_jsonl(args.cases)[: args.limit]
    todo = [c for c in cases if c.case_id not in done]
    print(f"{len(cases)} cases, {len(done)} already done, {len(todo)} to run. Loading {MODEL_ID} on {device}...", flush=True)

    tok, model = load_model(device)
    write_metadata(run_dir, device, model, len(cases))
    first_tokens = outcome_first_tokens(tok)
    stops = stop_token_ids(tok)

    correct = 0
    for i, c in enumerate(todo, 1):
        record, acts = run_case(c, tok, model, first_tokens, stops)
        np.save(run_dir / "acts" / f"{c.case_id}.npy", acts)
        with results_path.open("a") as f:
            f.write(json.dumps(record) + "\n")
        correct += record["predicted"] == record["label"]
        print(
            f"[{i}/{len(todo)}] {c.case_id} truth={record['label']:<18} model={str(record['predicted']):<18} "
            f"conf={record['confidence']} logp(answer)={max(record['outcome_logprobs'].values()):.2e} "
            f"{record['seconds']}s  running accuracy {correct}/{i}",
            flush=True,
        )


if __name__ == "__main__":
    main()
