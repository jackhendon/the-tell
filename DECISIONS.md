# Decisions

Short records of the choices that shape the experiment.

**Status of every entry below: DRAFT, written by Claude from the design discussion.**
Rewrite each in your own words during the walkthrough, and change anything you would not
defend.

## D1. The model picks one of seven labels

- **Decision:** APPROVE or one of six specific problems. At most one problem per invoice.
- **Why:** Specific labels make errors informative and allow a held-out-problem test (D4).
  One problem per invoice keeps "right" unambiguous.
- **Rejected:** approve / hold only. Simpler, but hides what kind of mistake was made.
- **Would change my mind:** if real AP teams mostly see invoices with several problems at once.

## D2. What counts as wrong, and what it costs

- **Decision:** wrong means the label differs from the true one. Costs are asymmetric:
  approving a bad invoice loses the money at risk; holding a good one costs £5 of review time.
- **Scored twice:** on the exact label, and on approve versus hold. Every label disagreement
  found in review was between two reasons for holding, so the second level shows whether
  any remaining ambiguity is driving the result.
- **Why:** the experiment needs a clean right/wrong; the business case needs money.
- **Would change my mind:** evidence that wrong-reason holds are costly in practice.

## D3. Code does the arithmetic, the model does the judgement

- **Decision:** deterministic code computes totals, differences and matches; the model
  decides in one step with no tool loop.
- **Why:** arithmetic errors are fixed by code, not predicted. One step gives one clean
  moment to read the model's internal state.
- **Facts, not verdicts:** the checks show what a spreadsheet could work out ("invoiced
  £15.81 against PO £15.54, +1.7%") and never apply a rule ("above tolerance"). A test
  fails if the checks ever name an outcome or use words like "tolerance" or "should".
- **Would change my mind:** if the remaining errors turn out to be mostly misreading facts.

## D4. Labels by construction, split by supplier, one problem type held out

- **Decision:** a generator injects known problems; an oracle re-checks every label; a
  human reviews a sample against the deciding rule. Train/test split by supplier, with one
  problem type kept entirely out of probe training.
- **Why:** hundreds of reliable labels without hand-labelling, and a test of whether the
  probe detects mistakes in general or only familiar hard cases.
- **Known limit:** the oracle shares the generator author's reading of the policy, so it
  cannot catch an ambiguous policy. Only human review can.
- **Would change my mind:** if the review finds the synthetic cases unrealistic.

## D5. Five signals, and the probe must beat the dumb baseline

- **Decision:** compare stated confidence, agreement across samples, answer probability,
  a linear probe on activations, and an error predictor that only sees the input.
- **Why:** if the probe cannot beat the input-only baseline, it has learned which cases
  are hard, not what the model is uncertain about. Linear probes rather than sparse
  autoencoders because recent work found SAEs do not reliably beat linear probes.

## D6. Qwen3 4B, run locally

- **Decision:** a 4B open model through Hugging Face `transformers`, safetensors only,
  no remote code, pinned revision.
- **Why:** standard architecture, fits in 24 GB, and makes enough mistakes to study.

## D7. Repeat the output-based signals on Claude

- **Decision:** Haiku 5.5 and Opus 5.5, three samples each, on about 400 test cases.
  Pilot of 20 cases first to measure real cost.

## D8. Python, new repo

- **Decision:** Python for the ML tooling; a fresh repo because the earlier TypeScript
  scaffold belonged to a different project.
