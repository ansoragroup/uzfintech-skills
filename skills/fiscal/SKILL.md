---
name: fiscal
description: Provider-neutral fiscal receipt knowledge for Uzbekistan online payments - the 17-digit MXIK (IKPU / SPIC) product code from the tax committee's Tasnif catalogue (tasnif.soliq.uz) and its levels, package codes versus units, VAT and benefit (lgota) fields, Asl Belgisi marking codes for marked goods, receipt types (sale, refund, advance, credit), the ofd.soliq.uz receipt link, and one table of who registers the receipt and which field carries each value at Payme, Click, Uzum (Fiscalization and Checkout), Alif, Multicard, Octo, Paynet and Atmos, plus direct ОФД (ofd.uz) integration with your own ВФМ (signed receipts, test.ofd.uz). Includes an offline MXIK checker with an opt-in Tasnif lookup. Use when a provider rejects receipt items or a basket, when choosing or validating MXIK and package codes, mapping one catalogue to several providers, deciding who issues the sale or refund receipt, handling marked goods, or testing fiscalization without creating real receipts.
---

# Fiscal receipts (MXIK, package codes, marking, receipt types)

This file is a router. Answer from the files referenced below, not from memory. For a
provider's exact request and response bodies, open that provider's own skill; this skill
explains the shared concepts and maps them across providers.

## Pages

| Page | What it covers | Reference |
|---|---|---|
| MXIK | 17-digit structure, the text-not-number rule, finding a code on Tasnif, the site's public JSON endpoints (not a documented API), third-party clients | [references/mxik/](references/mxik/README.md) |
| Receipt line | package code and unit, quantity and price per provider, VAT, benefits (`lgota`), marking codes (Asl Belgisi), principal TIN / PINFL | [references/receipt-line/](references/receipt-line/README.md) |
| Receipts | sale, refund, advance and credit receipts; who registers; refund receipts; the `ofd.soliq.uz` link | [references/receipts/](references/receipts/README.md) |
| Providers | one mapping table: who registers, MXIK, package code, VAT, marking, refund receipt, deadline, with links to each provider's reference | [references/providers/](references/providers/README.md) |
| Direct OFD (ВФМ) | onboarding, certificate, CMS signing, `test.ofd.uz` endpoints, ReceiptInfo fields, `ReceiptSeq`, refund, advance and credit receipts, daily report, reply codes, txkm registration API | [references/ofd-direct/](references/ofd-direct/README.md) |
| Sandbox and samples | which providers test fiscalization, rules for tests, vendor sample codes, saved Tasnif replies | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle | warnings, deadlines, refunds, retries, what is not documented | [references/lifecycle/](references/lifecycle/README.md) |

## Which page?

| The user wants to... | Use |
|---|---|
| fix "invalid SPIC / IKPU / package" or a rejected basket | `scripts/mxik.py check`, then [mxik](references/mxik/README.md) and [receipt-line](references/receipt-line/README.md#package-code-and-unit) |
| find the code and package code of a product | [mxik](references/mxik/README.md#finding-the-right-code) (the Tasnif site; the lookup is opt-in) |
| search Tasnif by barcode, re-check stored codes, read the point-of-sale `cl-api` reply | [tasnif skill](../tasnif/SKILL.md) |
| send one catalogue to several providers | [providers](references/providers/README.md#mapping) and [receipt-line](references/receipt-line/README.md#quantity-and-price) |
| know whether the provider or the shop registers the receipt | [receipts](references/receipts/README.md#who-registers-the-receipt) |
| issue a refund receipt | [receipts](references/receipts/README.md#refund-receipts), then the provider's lifecycle page |
| sell tobacco, alcohol, medicines, appliances, water or soft drinks | [receipt-line](references/receipt-line/README.md#marking-codes-asl-belgisi) |
| take prepayments or sell on credit | [receipts](references/receipts/README.md#receipt-types) |
| send receipts straight to ofd.uz with your own ВФМ / certificate | [ofd-direct](references/ofd-direct/README.md) |
| test receipts | [sandbox](references/sandbox/README.md) |
| exact fields of one provider | that provider's skill, linked from [providers](references/providers/README.md) |

## Rules that apply everywhere

- An MXIK has exactly **17 digits** and is **text**. Goods codes start with `0`; never store
  or serialize it as a number. The package code is text too.
- The package code comes from the **same code's** Tasnif card (`packages[].code`); it is not
  a SKU, barcode or unit name.
- One sale receipt per payment. When the provider registers it, do not register it again.
- Price fields differ per provider (unit price or line total; tiyin, or Octo's major
  units). Build lines in each provider's adapter and check its sum rule.
- VAT values, the choice of code and benefits come from the seller's tax settings and
  accountant. Never guess a rate.
- Marked goods carry one scanned code per sold unit; never invent or reuse one.
- Tests never touch a production fiscal module or endpoint.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the consequence and
the fix. Every source, deadline and refund path is in
[references/lifecycle/](references/lifecycle/README.md).

- `fiscal.mxik-as-string`: a code stored as a number loses its leading zero and reaches the
  provider with 16 digits; keep MXIK and package codes as strings.
- `fiscal.package-code-required`: Payme (also for services), Click, Uzum, Multicard and Octo
  require the package code; take it from the code's own Tasnif card.
- `fiscal.missing-mxik-blocks-payment`: at Octo, Multicard, Uzum Checkout and Alif a missing
  or wrong code fails the payment itself, not only the receipt.
- `fiscal.price-semantics-differ`: `price` is a unit price at most providers, Click also
  wants the line total, Atmos only the line amount, Octo uses major units.
- `fiscal.vat-per-product`: take VAT per product from the seller's settings; Click also
  wants the VAT amount, Octo only `nds` `1` / `0`.
- `fiscal.marked-goods-need-codes`: marked product groups need each unit's code in the
  provider's marking field; Payme and Octo document none.
- `fiscal.one-receipt-per-payment`: never register a sale the provider already registered;
  Uzum answers 400 `code` `2`, Click takes one of two calls.
- `fiscal.refund-needs-sale-receipt`: Uzum and Alif issue refund receipts only when the sale
  receipt exists; watch sale-receipt failures.
- `fiscal.test-fiscalization-only-in-tests`: only Uzum Fiscalization and the direct OFD
  (`test.ofd.uz`) have test hosts; a receipt on production is a real tax record.
- `fiscal.ofd-receipt-seq-per-vfm`: with your own ВФМ, assign `ReceiptSeq` once per receipt
  and resend that number on retry; a new certificate restarts it at 1.
- `fiscal.ofd-receipt-24h`: the ОФД rejects a receipt more than 24 h old (code `100`).

## Top gotchas

1. A 16-digit "IKPU" is almost always a 17-digit code that lost its leading `0` in an
   integer column, a spreadsheet or a JSON number. `scripts/mxik.py check` prints the
   candidate; confirm it on Tasnif before you use it.
2. A 13-digit value is usually an EAN-13 barcode, and a long mixed string a marking code;
   neither goes in the MXIK field.
3. Tasnif's search reply has no package codes; only the by-code reply (or the site's code
   card) lists them, as numbers. Convert to strings once.
4. The Tasnif JSON endpoints are what the official site calls, not a documented integration
   API, and may change. Confirm codes in the site UI.
5. Click wants both the unit price (`GoodPrice`) and the line total (`Price`), plus the VAT
   amount (`VAT`). Copying a Payme `price` into Click `Price` breaks the sum.
6. Uzum Fiscalization rejects a sale receipt older than 24 hours (422); send receipts right
   after confirmation, not from a nightly batch.
7. Alif documents no package-code field, Atmos no VAT field, Paynet no receipt fields at
   all. Say so instead of inventing a field.
8. Advance and credit receipts at Uzum get no fiscal receipt from the tax committee.

## Validate an implementation

Run [checklists/receipt-line.md](checklists/receipt-line.md), then the provider's own
fiscal checklist from its skill. Mark each item pass, fail or n.a. with a file:line
citation.

## Tools: run them, do not compute by hand

`scripts/` next to this file holds python3 scripts, standard library only. Run them from
this skill's folder.

```sh
python3 scripts/mxik.py check 04016001002000000 [more codes]   # offline: 17 digits, levels, hints
python3 scripts/mxik.py lookup 04016001002000000               # offline: prints the Tasnif URL only
python3 scripts/mxik.py lookup 04016001002000000 --online      # one public GET: name, flags, packages
python3 scripts/mxik.py lookup "коврик" --online               # search by name (no package codes)
python3 scripts/mxik.py lookup --file references/sandbox/tasnif-by-mxik.ru.json
python3 scripts/mxik.py --selftest
```

`check` exits 1 for an invalid code. Use `--online` only when the user agrees to a call to
tasnif.soliq.uz, and never from production request paths. `sign.py` and `validate.py` are
the shared copies every skill carries; this skill has no schemas or signatures of its own,
so validate a provider payload with that provider's skill.

## Answering rules

- Reply in the user's language, but never translate field names, codes or enum values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation.
- For a rejected basket, ask for (or check) the full 17-digit MXIK and the package code from
  the same code's card on https://tasnif.soliq.uz/, and the provider's exact error, before
  anything else.
- Quote fields exactly as the provider references print them. If a fact is not there, say
  the docs do not specify it and point to the "Not documented" list in
  [references/lifecycle/](references/lifecycle/README.md).
- Do not give tax advice: no VAT rates, no choice of code, no benefit eligibility. Say which
  field carries the value and that the seller's accountant or the tax authority decides it.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them.
- Examples use placeholders (merchant.example.com, `<API_KEY>`, phone 998901234567, order
  "100001") and the sample codes in [references/sandbox/](references/sandbox/README.md).
  Never use real customers' TIN, PINFL or marking codes.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
