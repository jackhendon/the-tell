# Decisions

The calls that shaped this project, why I made them, and what would make me change them.
I drafted these with Claude during the build.

## 1. Seven outcomes, one problem per invoice

The model picks APPROVE or one of six specific problems. Every invoice has one problem at
most.

I wanted the mistakes to tell me something. "Hold" on its own hides whether the model
thought it was a duplicate or a price issue, and it rules out testing on a problem type
the probe has never seen. One problem per invoice keeps "right" unambiguous.

What would change my mind: if real accounts teams mostly see invoices with several
problems at once.

## 2. Scoring it twice

Every answer is scored on the exact outcome, then again on just approve or hold. On the
second score, holding a bad invoice for the wrong reason counts as right.

When I reviewed the labels, every disagreement was between two reasons for holding.
Scoring twice shows whether that was driving the result. It wasn't. The two scores came
out almost the same.

Wherever I measure automation, I count bad invoices paid separately. They're the mistakes
that cost money.

What would change my mind: evidence that holding for the wrong reason is expensive in
practice.

## 3. Code does the maths, the model makes the call

Code works out the totals, the price changes and what's been delivered. The model makes
the decision in one go, with no tools.

Arithmetic mistakes are a solved problem: you fix them with code. And a single step gives
me one clean moment to read the model's internal state.

The checks only state facts, the kind a spreadsheet could work out:

> invoiced £15.81 against PO £15.54, +1.7%

They never apply a rule, so you won't see "above tolerance" in them. A test fails if they
ever name an outcome or use words like "tolerance" or "should".

What would change my mind: if most of the remaining mistakes were the model misreading
facts. They weren't. Both models caught every problem the checks spelled out.

## 4. Labels I can trust, and keeping suppliers apart

Each invoice is built with a known problem, or none, so I know the right answer without
labelling anything by hand. A separate oracle works every label out again from the
policy, and the generator stops if the two ever disagree.

The oracle shares my reading of the policy, though, so it can't catch a policy that's
ambiguous. So I checked 40 by hand, and had another model label the same 40 blind. It
agreed on all 40.

Suppliers are split into five groups and rotated, so every invoice is scored by a checker
that's never seen its supplier. I also kept tax errors, then quantity errors, out of
training completely, to see if a checker could spot a kind of mistake it hadn't seen. On
tax errors it got them almost exactly backwards.

What would change my mind: if the review had found the invoices unrealistic.

## 5. The probe has to beat the cheap options

I compared the model's stated confidence, the probability it gave its answer, how often
it disagreed with itself, and a probe on its internal state. Then three cheap checkers:
one that reads the invoice text, one that only knows the model's answer, and one that
knows both.

If the probe can't beat the text-only checker, it's just learned which invoices are hard.
If it can't beat text plus answer, it's mostly reading the answer the model is about to
give. I added that last one after the first results came in, and it turned out to be the
one that mattered.

I used linear probes because they're simple to explain, and recent research found sparse
autoencoders don't reliably do better on this kind of task.

## 6. Qwen3-4B on my laptop

A 4B open model, run through Hugging Face. It loads as safetensors only, with no remote
code and a pinned version, so nothing from the download ever runs on my machine.

It's a standard architecture, it fits in 24 GB, and it gets enough wrong to be worth
studying.

## 7. Claude Haiku 5.5, run twice

All 2,000 invoices, five answers each. Once with thinking off, to match Qwen, and once
with thinking on at low effort, which is how you'd actually use it. I ran pilots on 30
invoices first to check the set-up and the cost. The whole thing came to about $3.

I only used Haiku because it's the cheap model you'd put on a high-volume job like this.
With thinking on it got all 2,000 right, so a bigger model had nothing left to show.

What would change my mind: harder invoices that Haiku still gets wrong with thinking on.
Then a bigger model's worth a look.

## 8. Setting cut-offs in advance

When a checker decides what goes straight through, its cut-off is picked on one group of
suppliers and used as it is on another. Any figure that picks the cut-off after seeing the
answers is labelled best case.

In real life you set the cut-off before you know the answers. Done that way, aiming for
2% wrong got the probe 3.1%.

## 9. Comparing checkers like for like

To compare two checkers, each one hands over the same share of invoices.

A checker that hands over fewer invoices lets fewer bad ones through, however good it is.
I got this wrong the first time round, and the conclusion flipped once I fixed it.

## 10. Python, and a fresh repo

Python, because that's where the ML tooling is. A fresh repo, because the TypeScript
scaffold I started with belonged to a different project.
