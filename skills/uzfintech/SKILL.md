---
name: uzfintech
description: Router for the Uzbekistan payment skills in this plugin - Payme, Click, Uzum, Alif, Paynet, Multicard, Atmos, Octo, Oson, Kapitalbank and the cross-cutting fiscal skill. One features table (card payments, hosted checkout, merchant callbacks, card tokens and recurring charges, holds, full and partial refunds, QR, split, installments, payouts, who fiscalizes), a cheatsheet of the rules that differ per provider (amount units, auth and sign.py schemes, callback answers, refund rules, test hosts), QR notes on UzQR and Rahmat, and cross-provider warnings. Use when choosing a payment provider in Uzbekistan, comparing providers, planning a multi-provider checkout, or asking which provider supports holds, refunds, recurring payments, QR or fiscalization - then hand off to that provider's own skill for the exact contract.
---

# Uzbek payment providers: which one, and where to read it

This file is a router. Answer from the files referenced below, not from memory. It says
**whether** a provider documents a feature and **which skill** to load; every field, unit,
signature, error code and window is in that provider's own skill.

## Skills

| Skill | What it covers |
|---|---|
| [payme](../payme/SKILL.md) | Merchant API (JSON-RPC you implement), Subscribe cards and receipts with holds, Checkout link / form and QR |
| [click](../click/SKILL.md) | SHOP API Prepare / Complete, Advanced and Split Shop, Merchant API, card tokens, CLICK Pass, links and widget, fiscal data |
| [uzum](../uzum/SKILL.md) | Merchant API webhooks, Checkout and card binding, Fiscalization, FastPay, Dynamic QR, Nasiya, PaymentHub, CrossBorder, Remit Core |
| [alif](../alif/SKILL.md) | Checkout invoices, card + OTP and token payments, holds, alif mobi QR, Nasiya, refunds, payouts and split, receipts |
| [paynet](../paynet/SKILL.md) | host-to-host Humo / Uzcard acquiring with SMS OTP: authorize, confirm, status, reverse |
| [multicard](../multicard/SKILL.md) | invoices and scanpay, card binding, holds, refunds, payouts to cards, split, fiscal items, callbacks |
| [atmos](../atmos/SKILL.md) | Uzcard / Humo and Visa / Mastercard (MPS), payment page and widget, card linking, holds, reversals, Callback API |
| [octo](../octo/SKILL.md) | payment page or own card form, one- and two-stage payments, card tokens, refunds, fiscal basket, test flag |
| [oson](../oson/SKILL.md) | invoice with `pay_url`, status, signed notification; rebuilt from Oson's plugins |
| [kapitalbank](../kapitalbank/SKILL.md) | corporate internet-banking API: UZS payment orders, statuses, statements, invoices, purpose codes |
| [fiscal](../fiscal/SKILL.md) | MXIK, package codes, marking, receipt types, and who registers the receipt per provider |

## Pages

| Page | What it covers | Reference |
|---|---|---|
| Providers | features table, how to pick, QR payments (app QR, UzQR, Rahmat) | [references/providers/](references/providers/README.md) |
| Cheatsheet | per provider: amount unit, auth and `sign.py` scheme, callback answer, refund rule, holds, fiscal owner, test hosts; one source link per cell | [references/cheatsheet/](references/cheatsheet/README.md) |
| Lifecycle | cross-provider warnings, deadlines, refunds, retries, what is not documented | [references/lifecycle/](references/lifecycle/README.md) |

## Which provider for which task?

Features only. "Load" means: open that skill's SKILL.md and its "Which product?" table
before you say anything about the contract. In a feature row, a provider that is not listed
does not publish the feature or it does not apply; the
[features table](references/providers/README.md#features) says which.

| The user wants to... | Load |
|---|---|
| a hosted payment page or payment link | payme (Checkout), click (link, button, widget), uzum (Checkout), alif (Checkout), multicard (invoice), atmos (page, widget), octo (payment page), oson (invoice) |
| the provider to call the merchant's server about each payment | payme (Merchant API), click (SHOP API), uzum (Merchant API), atmos (Callback API), multicard (callback, webhook), alif, octo and oson (notifications) |
| save a card and charge it later (one-click, subscriptions) | payme (Subscribe), click (card tokens), uzum (Checkout binding), alif, multicard, atmos, octo |
| block funds now and capture later | payme, uzum (Checkout TWO_STEP), alif, multicard, atmos, octo |
| refunds, especially partial ones | partial: uzum (Checkout), multicard, atmos, octo, alif (instalments only); full only: payme, click, paynet; no API: oson |
| QR payments | [QR payments](references/providers/README.md#qr-payments) first, then the skill it names |
| split one payment between recipients | payme (`receivers`), click (Split Shop), alif, multicard, atmos (multi-payments) |
| instalments / buy now, pay later | uzum (Nasiya), alif (Nasiya) |
| payouts to cards, transfers, payments between companies | multicard (payouts), uzum (PaymentHub, CrossBorder, Remit Core), alif (split payouts), kapitalbank (payment orders) |
| Visa / Mastercard / UnionPay | octo, atmos (MPS); check multicard and uzum for the scheme field |
| Humo / Uzcard host to host with OTP, no callbacks | paynet |
| fiscal receipts, or who registers them | fiscal, then the provider's skill |
| UZS payment orders, statements, purpose codes | kapitalbank |
| compare units, auth, callbacks, refunds or test hosts | [cheatsheet](references/cheatsheet/README.md), then each provider's skill |
| several providers behind one checkout | [lifecycle](references/lifecycle/README.md#warn-without-being-asked), the cheatsheet, then each skill |
| test without moving real money | [cheatsheet](references/cheatsheet/README.md#refunds-holds-receipts-and-test-hosts), then the provider's sandbox page |

## Rules that apply everywhere

- One provider at a time. Load each named provider's skill and answer for each in its own
  part. Never carry units, auth, signatures, callback answers, retry or refund rules from
  one provider to another, even when names look alike.
- This skill only routes. Field names, bodies, error codes, units, windows and signatures
  come from the provider's skill; quote them from there. When the router and a provider
  skill disagree, the provider skill wins.
- "not published" means the provider's docs, as captured in its skill, do not describe the
  feature. Say so and list it as a question for the provider; do not guess either way.
- Choose by documented features and the merchant's must-haves. Commercial terms differ per
  merchant contract: never quote, estimate or compare them.
- Amounts: convert per provider in that provider's adapter. The units differ (tiyin, soum,
  decimal major units, unstated).

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the consequence and
the fix. Every source, deadline and refund path is in
[references/lifecycle/](references/lifecycle/README.md).

- `uzfintech.one-provider-at-a-time`: answer per provider from its own skill; the router
  tables say only whether a feature exists.
- `uzfintech.units-differ-per-provider`: tiyin at Payme, Uzum, Alif, Multicard, Atmos and
  Paynet; soum at Click and Oson; decimal major units at Octo; unstated at Kapitalbank.
- `uzfintech.callback-answers-differ`: the wrong answer refunds at Multicard, blocks the
  debit at Atmos and cancels after about an hour at Alif; Payme wants HTTP 200 for errors.
- `uzfintech.http-200-is-not-success`: Alif and Kapitalbank return errors in HTTP 200;
  Paynet's top-level `status` only says the call worked.
- `uzfintech.redirect-is-not-payment`: the return URL proves nothing; mark paid on a
  verified callback or a status read.
- `uzfintech.read-state-before-resend`: after a timeout read the state at that provider;
  never resend a money call.
- `uzfintech.refund-rules-differ`: full only at Payme, Click and Paynet, with month windows
  at Click and Paynet; no refund API at Oson or in the Uzum Merchant API.
- `uzfintech.hold-windows-differ`: days at Payme and Alif, minutes at Multicard and Atmos,
  30 minutes by default at Octo; none published at Click, Paynet or Oson.
- `uzfintech.test-money-differs`: Octo tests on production with `test: true`; Click, Paynet,
  Oson and Kapitalbank publish no sandbox host.
- `uzfintech.qr-products-differ`: ask which QR is meant; UzQR and Rahmat have no public
  developer API here, and Rahmat is not any provider's product in these sources.

## Top gotchas

1. A shared `toMinor()` helper is right for Multicard and wrong for Octo, whose `total_sum`
   is in decimal major units, and for Click and Oson, which take soum.
2. "Uzum" is several products with different auth and callbacks: Merchant API, Checkout,
   FastPay and Dynamic QR. Pick the product before the provider's rules.
3. "Payme" has two protocols: Payme calls your Merchant API (Basic auth), you call
   Subscribe (`X-Auth`). Pick the protocol before the rules.
4. Kapitalbank is a corporate banking API, not card acquiring. Do not route card payments to
   it.
5. Oson publishes no API reference; its skill is rebuilt from plugins. Say so whenever you
   use it.

## Tools

`sign.py` and `validate.py` in `scripts/` are the shared copies every skill carries; this
skill has no schemas or signatures of its own. `python3 scripts/sign.py --list` prints every
signature scheme by provider (`payme.basic`, `click.prepare`, `uzum.fastpay`,
`multicard.callback`, `octo.notify`, ...). To sign or validate a real payload, use the
provider's skill, which names the scheme, the fields and the secret it reads.

## Answering rules

- Reply in the user's language, but never translate field names, codes or enum values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation.
- For "which provider?", name the providers that document every must-have feature, say what
  is "not published" for each, and hand off to their skills. Do not rank them.
- For two or more providers, give one short block per provider, each sourced from its own
  skill.
- Use placeholders such as `https://merchant.example.com` for the merchant's own URLs.
- If a fact is not in these files, say the docs do not specify it and point to the "Not
  documented" list in [references/lifecycle/](references/lifecycle/README.md).
