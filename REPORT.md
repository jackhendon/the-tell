# Can an AI tell you when to check its work?

*A note for a finance director. The technical write-up is in [README.md](README.md).*

## What I tested

If you let an AI review supplier invoices, it will get some wrong. The real question is
whether you can tell which ones, so a person checks those and the rest go straight
through.

I modelled the test around the accounts team at a small chain of cafes. I gave a small
AI model 2,000 made-up supplier invoices. Each came with:

- its purchase order and delivery note
- any credit notes from the supplier
- a written invoice policy

For each one, the model had to approve or hold the invoice, give the reason, and say how
confident it was. I knew the right answer for every invoice, because I built each one
with a known problem, or none.

Then I tested different ways of predicting which of its answers would be wrong.

## What happened

It got 388 of the 2,000 wrong, about 1 in 5:

- **221 bad invoices approved.** These are the expensive ones, because they get paid.
- **154 good invoices held.** These cost clerk time.
- **13 bad invoices held for the wrong reason.**

Its mistakes were very repetitive. It mostly:

- got VAT rates wrong, for example charging plain biscuits at 20% when they're zero-rated
- held invoices over price rises that were agreed or within tolerance
- treated a standing weekly order as a duplicate

A typical example: a supplier put the price of tea up 1.6%. The policy allows 2%. The
model held the invoice and said it was 100% sure.

When the automated checks set a problem out plainly, such as a changed bank account or
VAT that didn't add up, it caught every one.

## Can you trust its confidence?

No. It said it was 100% confident on 1,990 of the 2,000 invoices, including 378 it got
wrong.

If you only let through the invoices it was confident about, you'd let through almost
all of its mistakes.

## Is there a better warning sign?

Yes, with a catch. I trained a separate checker that looks inside the model while it
works, and learns from past examples what it looks like when it's about to be wrong.

I tested it the way you'd use it: set the checker up on one group of suppliers, then
let it decide on invoices from suppliers it had never seen. Aiming for 2 in 100 wrong, it
let the model handle 1,316 of the 2,000 invoices (66%) on its own:

- 41 of those were wrong, about 3 in 100. A bit worse than the target.
- 30 were bad invoices that would have been paid.
- The other 684 invoices would go to a person, and they include 191 of the 221 bad
  invoices the model approved.

The model's own confidence couldn't safely hand over a single invoice, so that's a big
step up.

## The catch

The checker only recognises the kinds of mistakes it has seen before.

I trained one version without showing it any VAT mistakes, then tested it on VAT
invoices. It rated the model's VAT mistakes as the safest answers of all.

So if the model starts making a new kind of mistake, say after a policy change or a new
supplier, the checker won't flag it.

I also tried a much simpler checker, one that just reads the invoice and the model's
answer. It handed over fewer invoices (1,095, or 55%), but only 9 of those were bad
invoices that would have been paid, against 30 for the checker that looks inside the
model.

> If paying bad invoices is what worries you most, the simpler checker is the safer
> choice here.

## What I'd recommend

1. Don't use an AI model's own confidence to decide what to automate. Here it was
   useless.
2. Where a rule can be written down, put it in ordinary software. VAT rates by product
   and the price tolerance are both simple lookups. The model got those wrong far more
   than anything else, and caught every problem the automated checks had already spelled
   out.
3. Set the checker's threshold on one batch of invoices and test it on another before
   trusting it. Here, aiming for 2% wrong gave about 3%.
4. If you use a checker to decide what goes straight through, always send a random
   sample of the "safe" invoices to a person too. That's how you'd notice a new kind of
   mistake before it costs money.
5. Start in shadow mode. Run the model alongside the current process, compare its
   decisions with your team's for a few weeks, and only then let anything through
   unchecked.

## How far to trust this

- The invoices, suppliers and policy are all made up.
- The model is a small one that runs on a laptop. A larger model would make fewer
  mistakes.
- Real invoices are messier.

So treat the numbers as a guide to how these warning signs behave. Your own invoices
would give different numbers. The next step is to run the same test on a larger
commercial model (Claude).
