# Can an AI tell you when to check its work?

*A note for a finance director. The technical write-up is in [README.md](README.md).*

## What I tested

If you let an AI review supplier invoices, it will get some wrong. The real question is
whether you can tell which ones, so a person checks those and the rest go straight
through.

I gave a small AI model 2,000 made-up supplier invoices for a café chain, each with its
purchase order, delivery note, any credit notes, and a written invoice policy. For each
one it had to approve it or hold it, give the reason, and say how confident it was. I
knew the right answer for every invoice, because I built each one with a known problem,
or none.

Then I tested different ways of predicting which of its answers would be wrong.

## What happened

It got 388 of the 2,000 wrong, about 1 in 5. Those split two ways:

- 221 invoices had a problem and it approved them anyway. These are the expensive ones,
  because they get paid.
- 154 invoices were fine and it held them. These cost clerk time, not money.
- The rest it held for the wrong reason.

Its mistakes were very repetitive. It mostly got VAT rates wrong (for example, plain
biscuits charged at 20% when they're zero-rated), held invoices over price rises that had
already been agreed or were within tolerance, and treated a standing weekly order as a
duplicate. When the automated checks set a problem out plainly, such as a changed bank
account or VAT that didn't add up, it caught every one.

## Can you trust its confidence?

No. It said it was 100% confident on 1,990 of the 2,000 invoices, including 378 it got
wrong. If you only let through the invoices it was confident about, you'd let through
almost all of its mistakes.

## Is there a better warning sign?

Yes, with a catch. I trained a separate checker that looks inside the model while it
works and learns, from past examples, what it looks like when it's about to be wrong.

Used as a filter, the checker would have let the model handle 1,228 of the 2,000
invoices (61%) on its own. Of those, 24 were wrong, about 2 in 100. Only 14 were bad
invoices that would have been paid. The other 772 invoices would go to a person, and
they include 207 of the 221 bad invoices the model approved.

That's a big improvement on the model's own confidence, which couldn't safely hand over
any invoices at all.

## The catch

The checker only recognises the kinds of mistakes it has seen before. I trained one
version without showing it any VAT mistakes, then tested it on VAT invoices. It rated the
model's VAT mistakes as the safest answers of all. So if the model starts making a new
kind of mistake, after a policy change or a new supplier, say, the checker won't flag it.

I also found that a much simpler checker, one that just reads the invoice and the
model's answer, does nearly as well. Looking inside the model gave a small extra
improvement, mainly on invoices held over price rises that were actually fine.

## What I'd recommend

1. Don't use an AI model's own confidence to decide what to automate. Here it was
   useless.
2. Where a rule can be written down, put it in ordinary software rather than leaving it
   to the AI. VAT rates by product and the price tolerance are both simple lookups. The
   model got those wrong far more than anything else, and caught every problem that the
   automated checks had already spelled out.
3. If you use a checker to decide what goes straight through, always send a random
   sample of the "safe" invoices to a person too. That's how you'd notice a new kind of
   mistake before it costs money.
4. Start in shadow mode. Run the model alongside the current process, compare its
   decisions with your team's for a few weeks, and only then let anything through
   unchecked.

## How far to trust this

The invoices, suppliers and policy are all made up, and the model is a small one that
runs on a laptop. A larger model would make fewer mistakes, and real invoices are
messier. The numbers show how these warning signs behave, not what you'd see on your own
invoices. The next step is to run the same test on a larger commercial model (Claude).
