# Decisions

Short records of the choices that shape the experiment, and what would change my mind.
Drafted with Claude during the build.

## D1. The model picks one of seven outcomes

- **Decision:** APPROVE or one of six specific problems. At most one problem per invoice.
- **Why:** specific outcomes make mistakes informative and allow a held-out-problem test
  (D4). One problem per invoice keeps "right" unambiguous.
- **Rejected:** approve or hold only. Simpler, but it hides what kind of mistake was made.
- **Would change my mind:** if real accounts teams mostly see invoices with several
  problems at once.

## D2. What counts as wrong

- **Decision:** scored twice. Once on the exact outcome, and once on approve versus hold,
  where holding a bad invoice for the wrong reason counts as right.
- **Why:** every outcome disagreement found in the label review was between two reasons
  for holding. The second score shows whether that kind of ambiguity drives the result.
  It didn't: both scores give almost the same numbers.
- **Bad invoices paid** are counted separately wherever automation is measured, because
  they're the mistakes that cost money.
- **Would change my mind:** evidence that holding for the wrong reason is costly in
  practice.

## D3. Code does the arithmetic, the model does the judgement

- **Decision:** deterministic code computes totals, differences and matches. The model
  decides in one step, with no tool loop.
- **Why:** arithmetic mistakes are better fixed with code than predicted. One step gives
  one clean moment to read the model's internal state.
- **Checks state facts only:** they show what a spreadsheet could work out ("invoiced
  £15.81 against PO £15.54, +1.7%") and never apply a rule ("above tolerance"). A test
  fails if the checks ever name an outcome or use words like "tolerance" or "should".
- **Would change my mind:** if the remaining mistakes turned out to be mostly misread
  facts. They weren't: both models caught every problem the checks spelled out.

## D4. Labels by construction, suppliers kept apart, problem types held out

- **Decision:** a generator adds known problems; an oracle re-checks every label; I
  reviewed a sample of 40 against the deciding rule, and another model labelled the same
  40 blind. Suppliers are split into five groups and rotated, so every invoice is scored
  by a checker that never saw its supplier. Tax errors and quantity errors were each held
  out of training in turn.
- **Why:** thousands of reliable labels without hand-labelling, and a test of whether a
  checker spots mistakes in general or only familiar ones.
- **Known limit:** the oracle shares my reading of the policy, so it can't catch an
  ambiguous policy. Only human review can.
- **Would change my mind:** if the review had found the synthetic cases unrealistic.

## D5. The probe has to beat cheap baselines

- **Decision:** compare stated confidence, answer probability, agreement across samples,
  a linear probe on the internal state, and three cheap checkers: the invoice text alone,
  the answer the model gave, and the text plus the answer.
- **Why:** if the probe can't beat a checker that only sees the invoice, it has learned
  which invoices are hard. If it can't beat text plus answer, it's mostly reading the
  answer. That second baseline was added once the first results came in, and it turned
  out to be the important one.
- **Linear probes:** recent work found sparse autoencoders don't reliably beat linear
  probes for this kind of task, and linear probes are simpler to explain.

## D6. Qwen3-4B, run locally

- **Decision:** a 4B open model through Hugging Face `transformers`, safetensors only,
  no remote code, pinned revision.
- **Why:** standard architecture, fits in 24 GB, and makes enough mistakes to study.

## D7. Repeat the output-based signals on Claude Haiku 5.5

- **Decision:** all 2,000 invoices, five answers each, run twice: thinking off to match
  Qwen, and thinking on at low effort, which is how you'd normally use it. Pilots on 30
  invoices first, to check the set-up and measure cost. Total spend about $3.
- **Why Haiku only:** it's the low-cost model you'd put on a high-volume task like this.
  With thinking on it got all 2,000 right, so a stronger model had nothing left to show.
- **Would change my mind:** harder invoices where Haiku with thinking does go wrong. Then
  a larger model is worth comparing.

## D8. Automation cut-offs are set in advance

- **Decision:** a checker's cut-off is picked on one group of suppliers and applied
  unchanged to another. Best-case figures, which pick the cut-off after seeing the
  answers, are labelled as best case.
- **Why:** in real use the cut-off has to be chosen before the answers are known. Aiming
  for 2% wrong this way gave 3.1% for the probe.

## D9. Checkers are compared at the same volume

- **Decision:** to compare two checkers, each hands over the same share of invoices,
  with ranges from resampling suppliers.
- **Why:** a checker that hands over fewer invoices lets fewer bad ones through, whatever
  its quality. An earlier comparison made that mistake, and the conclusion flipped once it
  was fixed.

## D10. Python, new repo

- **Decision:** Python for the ML tooling, and a fresh repo, because the earlier
  TypeScript scaffold belonged to a different project.
