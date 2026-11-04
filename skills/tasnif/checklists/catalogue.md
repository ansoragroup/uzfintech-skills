# Checklist: Tasnif catalogue lookups (search, barcode mapping, re-checks)

Contract: [`../references/common/README.md`](../references/common/README.md),
[`../references/search/README.md`](../references/search/README.md),
[`../references/code/README.md`](../references/code/README.md) and
[`../references/pos/README.md`](../references/pos/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it. Then run the fiscal skill's
[receipt-line checklist](../../fiscal/checklists/receipt-line.md) for what goes on the
receipt.

## Calls
- [ ] Both base URLs (`cls-api`, `cl-api`) and the txkm base live in configuration, not in code (`tasnif.not-official-api`).
- [ ] Every call is a `GET` with `Accept: application/json`, a timeout and a `User-Agent` naming the product; no cookies, cabinet tokens or E-IMZO data are sent.
- [ ] Calls run one at a time, about one a second at most, with back-off on timeouts, 5xx and unexpected bodies; nothing crawls the catalogue (`tasnif.throttle-and-cache`).
- [ ] Card and history replies are cached per code for at least a day; the last good value survives a failed refresh.
- [ ] No checkout, payment, receipt or webhook path calls Tasnif; codes come from your own catalogue (`tasnif.no-checkout-calls`).

## Parsing
- [ ] Each endpoint is parsed with its own shape: envelope, page in the envelope (`data.content[]`) or bare object / array.
- [ ] "Found" is decided from `success` and the data, never from the HTTP status or `code` alone: 403 text on `by-mxik`, 200 `success: false` on `history` and `gtin`, 200 with `data: []` on `cl-api` information (`tasnif.check-body-not-status`).
- [ ] A body that is not the expected JSON shape is "unknown, retry later", not "no such code".
- [ ] MXIK and package codes are stored as strings; the numeric package `code` is converted on read (`tasnif.codes-as-strings`).
- [ ] Flags are compared as text (`"1"` and `1`); `history` dates are parsed as `dd.MM.yyyy HH:mm:ss`, `cl-api` dates as epoch milliseconds.
- [ ] Parsers are unit-tested against the saved replies in [`../references/sandbox/`](../references/sandbox/README.md), including the not-found ones.

## Choosing codes
- [ ] A barcode hit is shown with its card and confirmed by a person before it is stored; no hit falls back to a text search (`tasnif.barcode-hit-needs-review`).
- [ ] Package codes are taken from the card and cross-checked with the point-of-sale reply; a person chooses when the lists differ (`tasnif.package-lists-differ`).
- [ ] `permitted` is shown during setup and does not block sales on its own (`tasnif.permitted-needs-seller`).
- [ ] `lgota*`, `percent`, `cashSale` and `cashSaleAllowed` are shown as data; the accountant sets codes, VAT and benefits (`tasnif.no-tax-advice`).

## Re-checks and data
- [ ] A scheduled job re-checks stored codes with `history` (`isActive`, `updatedAt`, package codes) and sends changes to a person (`tasnif.codes-change`).
- [ ] Nothing is keyed or compared on the `history` `id` (`tasnif.history-id-unstable`).
- [ ] `createdBy` and `updatedBy` are dropped before storing; TINs stay out of logs, logged URLs and fixtures, which use `<TIN>` (`tasnif.personal-data`).
- [ ] Product pictures are downloaded once and served from your own storage, not hot-linked.
