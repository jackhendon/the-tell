# The Tell

**Can you tell from inside a language model that it is about to get it wrong?**

In poker, a *tell* is an involuntary signal that gives away what a player is about to do.
This project looks for a language model's tell: a signal in its internal state, read
before it answers, that predicts when its answer will be wrong. And it asks whether that
signal is a better guide to "when should a human check this?" than the model's own
stated confidence.

The test bed is accounts payable: reviewing supplier invoices against purchase orders,
deliveries, credit notes and a written policy, and deciding whether to approve or hold
each one, and why.

## Status

| Step | What | State |
|---|---|---|
| 1 | Synthetic invoice generator with labels known by construction | Done |
| 2 | Deterministic pre-checks and the prompt | Done |
| 3 | Open-model run: answers, samples and internal activations | Running |
| 4 | Probes vs baselines, risk-coverage chart | Built, waiting for step 3 |
| 5 | Same test on Claude (output-based signals only) | |
| 6 | Write-ups: one for engineers, one for a finance director | |

## Run it

```bash
uv sync
uv run pytest                                   # 28 tests
uv run python -m the_tell.generate --n 2000     # writes data/generated/cases.jsonl
uv run python -m the_tell.review_sample         # writes data/review_sample.md
uv run python -m the_tell.prompt                # writes data/prompt_examples.md

# Step 3: run the local model (downloads ~8 GB once; about 4 s per invoice on an M4 Pro)
uv run python -m the_tell.run_local --run qwen3-4b-full
uv run python -m the_tell.viewer --run qwen3-4b-full   # watch it live at http://127.0.0.1:8765

# Step 4: which signal predicts the mistakes? (tables, then charts in results/)
uv run python -m the_tell.analysis --run qwen3-4b-full
uv run python -m the_tell.charts --run qwen3-4b-full
```

## How the data works

Every case starts as a clean purchase order, delivery and invoice that all match. A
scenario then introduces exactly one problem, or leaves the invoice correct but tricky
(an agreed price rise, a second partial delivery, a supplier trading name). Because the
problem is put there on purpose, the right answer is known without anyone labelling it.

An independent **oracle** re-derives each label from the policy rules, and generation
stops if the two ever disagree. That proves the generator is consistent with one reading
of the policy. It does not prove the policy is unambiguous, so a human reviews a sample
against the exact rule that decides each case (`data/review_sample.md`).

All data is synthetic. No real invoices, suppliers or people.
