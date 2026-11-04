# Checklist: fiscal receipt lines (applies to every provider)

Contract: [`../references/receipt-line/README.md`](../references/receipt-line/README.md) and
[`../references/providers/README.md`](../references/providers/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it. Then run the provider's own
fiscal checklist from its skill.

## Codes
- [ ] MXIK and package codes are stored, imported and serialized as strings, never as integers or JSON numbers (`fiscal.mxik-as-string`).
- [ ] Every MXIK has exactly 17 digits; `scripts/mxik.py check` passes for each code in the catalogue and in fixtures.
- [ ] Each package code comes from the same MXIK's Tasnif card (`packages[].code`), not from a SKU, barcode or unit name (`fiscal.package-code-required`).
- [ ] Items without a confirmed code are kept out of checkout; no placeholder codes are sent (`fiscal.missing-mxik-blocks-payment`).
- [ ] Tasnif data is cached per product; no request path calls tasnif.soliq.uz during checkout.

## Price, quantity and VAT
- [ ] Each provider adapter builds its own lines: unit price or line total as that provider defines it, in tiyin (Octo: major units) (`fiscal.price-semantics-differ`).
- [ ] The line sum is checked against the payment amount with the provider's own rule before the call.
- [ ] Discounts go in the provider's discount field as a line total where it says so (Multicard items carry none).
- [ ] VAT comes from the seller's tax settings per product; no rate is hard-coded in code (`fiscal.vat-per-product`).
- [ ] Click lines carry both `VATPercent` and the `VAT` amount; Octo `nds` is `1` or `0`.

## Marked goods and agents
- [ ] Products in a marked group are flagged in the catalogue, and each sold unit's scanned code goes in the provider's marking field (`fiscal.marked-goods-need-codes`).
- [ ] Marking codes are never generated, reused across sales or copied from fixtures into live calls.
- [ ] Agent sales carry the principal's TIN (9 digits) or PINFL (14 digits) where the provider has a field for it.

## Receipts
- [ ] Exactly one party registers the sale receipt for each payment (`fiscal.one-receipt-per-payment`).
- [ ] Sale-receipt failures are stored and retried before any refund needs a refund receipt (`fiscal.refund-needs-sale-receipt`).
- [ ] Receipt links are stored whole, as returned; nothing rebuilds them from parts.
- [ ] Tests and CI never reach a production fiscal module or endpoint (`fiscal.test-fiscalization-only-in-tests`).
