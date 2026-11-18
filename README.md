# The Tell

**Can you look inside a language model and tell it's about to get an answer wrong?**

In poker, a tell is something a player does without meaning to that gives their hand
away. I wanted to know if language models have one: a signal in the model's internal
state, readable before it answers, that predicts a wrong answer better than the model's
own confidence does.

I've modelled the test around the accounts team at a small chain of cafes (accounts
payable, if you work somewhere bigger). For each supplier invoice, the model gets:

- the purchase order and what was delivered
- any earlier invoices and open credit notes
- a written invoice policy
- a few automated pre-checks

Then it decides whether to approve or hold the invoice, and why.

I picked it because the right answer can be checked and mistakes cost money. And the
business question is the one this project asks: which invoices can you leave to the
model, and which need a person?

For a non-technical version of the results, see [REPORT.md](REPORT.md).

## The short version

> A model can't tell you when it's wrong, and a checker trained on its past mistakes only
> catches the kinds of mistake it has already seen.

I ran a small open model (Qwen3-4B-Instruct) over 2,000 synthetic invoices on my laptop,
and saved its internal state just before it gave each answer.

- It got 388 wrong (19%).
- On 378 of those it said it was 100% confident.
- A probe, which is a simple classifier trained on its internal state, predicts the
  mistakes far better than anything the model says about itself.
- Used as a filter, it would let the model handle about two thirds of invoices. Aiming for
  2% of those wrong, it came out at 3.1% on suppliers it hadn't seen. The model's own
  confidence can't safely hand over any.

The probe is less clever than that sounds, though. Most of what it picks up is the
answer the model is about to give.

- A cheap baseline that reads the invoice text plus the model's answer gets close: 0.89
  AUROC against the probe's 0.92.
- The probe only clearly beats that baseline on one kind of mistake: holding good
  invoices over price rises that were fine.
- Trained without any tax errors and then tested on them, it got them almost exactly
  backwards.

So there is a tell. It's mostly the model's own decision showing through, plus the
pattern of mistakes the probe has already seen. A new kind of mistake gets straight past
it.

![Risk-coverage chart](results/qwen3-4b-full_risk_coverage_label.png)

## Results

How to read the table:

- Each signal gives every invoice a "doubt" score.
- AUROC measures how well that score ranks wrong answers above right ones. 0.5 is a coin
  toss, 1.0 is perfect.
- "Automatable" is the largest share of invoices you could leave to the model, least
  doubtful first, with no more than 2% of them wrong. It picks the cut-off after seeing
  which answers were wrong, so it's a best case. The next section sets it in advance.
- Ranges in brackets are 95% ranges.

| Signal | AUROC | Automatable at 2% error (best case) |
|---|---|---|
| Model's stated confidence | 0.51 (0.51 to 0.52) | 0% |
| Model's probability for its answer | 0.47 (0.44 to 0.51) | 0% |
| Which answer the model gave | 0.72 (0.69 to 0.74) | 35% (32% to 38%) |
| Invoice text only | 0.82 (0.80 to 0.84) | 28% (10% to 40%) |
| Invoice text + the model's answer | 0.89 (0.87 to 0.90) | 55% (50% to 61%) |
| **Probe on internal state** | **0.92 (0.90 to 0.93)** | **61% (57% to 66%)** |
| Known hard case types (reference only) | 0.98 (0.97 to 0.99) | 79% (77% to 82%) |

The last row isn't something you could use. It relies on the generator's own label for
what kind of invoice each one is, which no real system would have. It's there to show
how much of the problem comes down to some kinds of invoice being hard.

Scoring only the approve-or-hold decision gives almost the same numbers: probe 0.92, 62%
automatable at best. That's the version where holding a bad invoice for the wrong reason counts
as right.

Full tables, including everything below, are in [results/report.txt](results/report.txt).

### Setting the cut-off in advance

In real use you'd have to choose the cut-off before seeing the answers. So in each of the
five rotations, I trained each checker on three groups of suppliers, picked the cut-off on
a fourth, and applied both unchanged to the fifth. Aiming for 2% wrong:

| Checker | Invoices automated | Wrong among those | Bad invoices approved |
|---|---|---|---|
| Probe on internal state | 1,316 (66%) | 41 (3.1%) | 30 |
| Invoice text + the model's answer | 1,095 (55%) | 30 (2.7%) | 9 |
| Which answer the model gave | 699 (35%) | 8 (1.1%) | 0 |

Two things stand out:

- Both trained checkers overshoot the 2% target. A cut-off picked on one group of
  suppliers doesn't carry over exactly to another.
- The probe automates the most invoices, but lets through the most bad ones. Its extra
  mistakes are mostly the model approving invoices it should have held.

If the cost you care about is paying bad invoices, the simpler text-and-answer checker
comes out ahead here. Aiming for 5% gives the same pattern (in `results/report.txt`).

### The model's mistakes are few and repetitive

Seven patterns account for 367 of the 388 mistakes:

| What the invoice had | Model got it wrong | What it did |
|---|---|---|
| 0% VAT on goods that should be 20% (crisps, drinks) | 65 of 65 | Approved |
| 20% VAT on plain biscuits, which are zero-rated | 58 of 59 | Mostly approved |
| A standing weekly order, same goods as last week on a different PO | 54 of 57 | Called it a duplicate |
| Billed for the full order when only part was delivered | 51 of 82 | Approved |
| A price rise inside the 2% tolerance | 50 of 50 | Held for price |
| A price rise agreed and noted on the PO | 42 of 45 | Held for price |
| 20% VAT on goods that should be 0% (tea, milk) | 47 of 53 | Mostly approved |

Here's a typical one. The pre-checks in the prompt showed this price change, from a
supplier on a variable-price contract:

```
TEA-ASM-1K     PO    £26.34  invoiced    £26.76  change +1.6%
```

The policy it was given says:

> Tolerance: 2% for suppliers on variable-price contracts

And the model answered:

```
OUTCOME: PRICE_VARIANCE
CONFIDENCE: 100
```

The standing orders are the same story. The policy spells it out:

> Standing orders billed against different purchase orders are not duplicates.

It still called 54 of the 57 standing orders duplicates.

It did catch every one of these:

- VAT that didn't add up (56 of 56)
- a change of supplier bank account or VAT number
- a duplicate invoice

In all of those, the pre-checks state the fact plainly. It struggled when it had to apply
a rule itself, like which VAT rate goes with which product, or whether a price change is
inside tolerance.

This matters for the probe. Because the mistakes cluster so tightly, a signal can look
good just by recognising the kind of invoice. Most of the extra tests below are there to
separate that from anything deeper.

### The model's own confidence is no use

- It was asked for a confidence from 0 to 100. It said 100 on 1,990 invoices, and 378 of
  those were wrong.
- On the other ten it said 0, and all ten were wrong. Each time it held the invoice for a
  price problem that wasn't there. That's a real signal, but it only covers ten invoices
  out of 2,000.
- The probability it gave its chosen answer was above 99.9% on 93% of invoices. On
  average it was slightly higher for wrong answers than right ones.
- I also worked out how often it would disagree with itself if sampled at temperature
  0.7. That comes straight from the same probabilities, so it adds nothing here. It
  matters later for Claude, which doesn't expose probabilities.

### The probe mostly reads the answer it's about to give

The probe reads the model at the point where it has written "OUTCOME:" and is about to
choose an outcome. By then the answer is already decided inside the model, and a linear
probe can read it.

Beating the model's confidence is easy. The harder test is whether the probe knows more
than the invoice and the answer put together.

The text-and-answer baseline tests that. It's a plain bag-of-words classifier over the
invoice text, where every word is also paired with the model's answer (for example
`APPROVE_credit`). That lets it learn which answers tend to be wrong for which kinds of
invoice.

It reaches 0.89. The probe beats it by 0.03 (0.02 to 0.05). The gap is small, and the
range stays above zero, so it's there.

The layer chart tells the same story:

- **Layer 0:** exactly 0.5. The last word of the prompt is the same for every invoice,
  and nothing has been mixed in yet.
- **Layer 1:** about 0.8, roughly what the invoice text alone gets.
- **Layer 22 onwards:** about 0.92. This is where the model's answer takes shape.

![Probe accuracy by layer](results/qwen3-4b-full_layers.png)

I also measured each signal inside each kind of invoice, where knowing the kind of
invoice is no help. The probe scores 0.66 (0.57 to 0.84) there, but that turns out to be
the answer again.

In the two scenarios that carry most of that number, every wrong answer was APPROVE and
every right one was QUANTITY_VARIANCE. Knowing the answer alone scores 1.00 there. Inside
a kind of invoice, the probe does no better than text plus answer.

### Where the probe does better: false alarms on price

Grouping by the answer the model gave, the probe clearly beats the baseline in one place.

- The model held 334 invoices for a price variance.
- 102 of those were wrong, nearly all of them good invoices with a price rise that was
  inside tolerance or agreed.
- The probe separates the wrong ones from the right ones at 0.89 AUROC.
- Text plus answer manages 0.55.

My best guess is that the probe can read the size of the price change from the model's
internal state, and a bag-of-words model can't really read numbers. That would mean the
model works out the rise is 1.6%, as in the example above, then flags it anyway.

I haven't tested that directly yet, so I'm treating it as a lead.

### It doesn't recognise a new kind of mistake

To test whether the probe learns something general about being wrong, I trained it with
every tax-error invoice removed, then scored the tax errors.

It scored 0.02. That's almost perfectly backwards: it rated the model's tax mistakes as
its safest answers.

Here's why:

- Without tax errors, most mistakes in training were false alarms, where the model held a
  good invoice.
- So the probe learned that APPROVE is the safe answer.
- On tax errors, the mistakes are approvals.
- Every signal that knows the model's answer falls into the same trap. Text plus answer
  scores 0.00.

Holding out quantity errors instead gives 0.60, or 0.71 on the approve-or-hold decision.
That's better, because the training set still has plenty of wrongful approvals in it,
from tax.

Within one problem type, being right or wrong depends entirely on which answer the model
gives. So this test mostly asks whether the probe learned the right lesson about which
answers are risky. That depends on which mistakes it was shown.

## How it was tested

### Labels

- Every invoice starts clean, and a scenario adds exactly one problem. So the right
  answer is known from how the invoice was built.
- A separate oracle works out every label again from the policy rules, and generation
  stops if the two ever disagree.
- The oracle and the generator share my reading of the policy. So I also checked a sample
  of 40 by hand against the rule that decides each one.
- I gave a blind copy of the same 40 to another model (Codex) to label on its own. It
  agreed on all 40.
- The review led to several fixes to the policy wording and the generator, written up in
  `data/review_findings.md`.

### Pre-checks state facts only

The prompt includes deterministic pre-checks: does the VAT number match, what was
delivered, what's been invoiced before. They never apply a policy rule, so the decision
is still the model's to make.

### No probe scores a supplier it was trained on

- The 40 suppliers are split into five groups.
- Each group is scored by a probe trained on the other four: three to train, and one to
  pick the layer and how strongly to regularise.
- So every invoice is scored once, by a probe that never saw its supplier.
- Every trained baseline uses the same rotation.

### Error bars

I resampled the 40 suppliers 1,000 times, with replacement, and reran the measurement.
I resample suppliers because invoices from one supplier aren't independent of each other.

Comparisons between the probe and a baseline are paired: both are measured on the same
resample each time.

### What gets saved

One forward pass per invoice. From the last position, the run saves:

- the internal state at all 37 layers
- the log-probability of each of the seven outcomes

Then the model writes its answer greedily. The probabilities are stored as logs, because
at 99.9999% plain probabilities all round to the same number.

## Limits

- The data is synthetic, and so is the policy. Real invoices are messier, and real
  mistakes may not cluster this tightly.
- One small model, one prompt, greedy decoding. A bigger model would make fewer mistakes,
  and different ones.
- Only 7 kinds of invoice had enough right and wrong answers to measure within a kind,
  and only two of those had plenty of both. The within-type numbers have wide ranges.
- The text baselines can't read numbers well. A baseline built on the pre-check numbers
  might close the gap on price. I chose cheap, generic baselines on purpose, because the
  point of a probe is that it doesn't need hand-written rules. It's still a fair challenge.
- The probe is read after the answer has formed. Reading earlier is the obvious next
  experiment.

## What I'd do next

1. Run the same comparison on Claude. There's no internal state to read there, so it
   comes down to stated confidence, agreement across samples and the text baselines.
   It's a paid API run, so I'll cost it with a 20-invoice pilot first.
2. Read the internal state before the answer forms, for example at the end of the
   invoice documents. If the probe still works there, it's seeing more than the answer.
3. Test the price lead directly. Train a probe to read the size of the price change from
   the internal state, and check whether it gets it right on the invoices the model
   wrongly held.

## Status

| Step | What | State |
|---|---|---|
| 1 | Synthetic invoice generator, labels known by construction | Done |
| 2 | Pre-checks and the prompt | Done |
| 3 | Local model run: answers and internal state, 2,000 invoices | Done |
| 4 | Probes against baselines, charts | Done |
| 5 | Same test on Claude (output signals only) | Next |
| 6 | Write-ups | Done for the local model |

## Run it

```bash
uv sync
uv run pytest                                   # 31 tests
uv run python -m the_tell.generate --n 2000     # writes data/generated/cases.jsonl
uv run python -m the_tell.review_sample         # writes data/review_sample.md
uv run python -m the_tell.prompt                # writes data/prompt_examples.md

# Run the local model (downloads about 8 GB once; about 4 s per invoice on an M4 Pro)
uv run python -m the_tell.run_local --run qwen3-4b-full
uv run python -m the_tell.viewer --run qwen3-4b-full   # watch it at http://127.0.0.1:8765

# Which signal predicts the mistakes? Tables, then charts, in results/
uv run python -m the_tell.analysis --run qwen3-4b-full
uv run python -m the_tell.analysis --run qwen3-4b-full --held-out TAX_ERROR
uv run python -m the_tell.charts --run qwen3-4b-full
```

The model runs entirely on the laptop:

- Weights load as safetensors only, with `trust_remote_code=False` and a pinned
  revision, so no code from the model download is ever run.
- The viewer only listens on 127.0.0.1.

## What's where

| File | What it does |
|---|---|
| `src/the_tell/domain.py` | Invoice, PO, delivery and credit note types. Money in pence. |
| `src/the_tell/catalogue.py` | Products, VAT rates and the 40 synthetic suppliers |
| `src/the_tell/policy.py` | The written policy the model is given |
| `src/the_tell/generate.py` | The 30 scenarios, each adding one problem or a tricky but correct invoice |
| `src/the_tell/oracle.py` | Independent re-derivation of every label |
| `src/the_tell/facts.py` | The pre-checks, which state facts and apply no rules |
| `src/the_tell/prompt.py` | The prompt and the strict answer parser |
| `src/the_tell/run_local.py` | Runs the model, saves internal state and answers |
| `src/the_tell/viewer.py` | Local page to watch a run |
| `src/the_tell/analysis.py` | The probe, the baselines and the error bars |
| `src/the_tell/charts.py` | The two charts |
| `DECISIONS.md` | Why things are built the way they are |

All data is synthetic. No real invoices, suppliers or people.
