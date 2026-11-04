# Tasnif lookups: traps, freshness, retries and open questions

Read this when building or reviewing anything that searches, stores, imports or re-checks
MXIK codes through the Tasnif endpoints, and raise these traps before a catalogue import
goes live or a checkout starts depending on Tasnif.

- Source: the probes in [`../sandbox/`](../sandbox/README.md), the clients pinned in
  [`../common/`](../common/README.md#sources), and the pages linked in each item
- Fetched: 2026-11-04

## Warn without being asked

1. **`tasnif.not-official-api`**: when building on any endpoint here → say that the tax
   committee publishes no API reference, terms of use or SLA for them; they are the site's
   own calls and can change or close without notice. Keep base URLs in configuration, parse
   defensively, and keep a manual way to enter a code.
   [common](../common/README.md#hosts)
2. **`tasnif.no-checkout-calls`**: when a sale, payment or receipt path needs a code →
   read it from your own catalogue, never from Tasnif at request time. A slow or closed
   site must not stop a sale. Resolve codes when a product is created or edited, in a
   background job. [common](../common/README.md#politeness-and-caching)
3. **`tasnif.check-body-not-status`**: when deciding "not found" → read the body. An
   unknown code is HTTP 403 `text/plain` on `by-mxik`, HTTP 200 `success: false` on
   `history` and `by-params?gtin=`, and HTTP 200 `success: true` with an empty list on
   `cl-api` information; a 403 on `class/search` means a bad request instead. Treat any
   other shape as "unknown, retry later", not as "no such code".
   [common](../common/README.md#not-found-and-errors)
4. **`tasnif.codes-as-strings`**: when storing a code or a package code → keep both as
   text. Goods codes start with `0`, and the replies send the package `code` as a JSON
   number. The fiscal rule is `fiscal.mxik-as-string`.
   [code](../code/README.md#the-card-mxikgetby-mxik)
5. **`tasnif.package-lists-differ`**: when picking a package code → the card, `history`
   and the point-of-sale reply can list different packages (two on the card, one in
   `cl-api` information for `04016001002000000`). Take the list from the card, cross-check
   the point-of-sale reply for the seller, and let a person choose.
   [code](../code/README.md#packages-card-and-history-can-differ)
6. **`tasnif.barcode-hit-needs-review`**: when mapping barcodes to codes → a `gtin` hit is
   the link the catalogue holds, not a ruling that the product must use that code, and no
   hit does not mean the product has no code. Show the hit with its card and store what a
   person confirms. [search](../search/README.md#barcode-to-code)
7. **`tasnif.permitted-needs-seller`**: when reading `cl-api` information → `permitted` was
   `false` in every call without `tin` / `terminalId`, and what it means is not documented.
   Show it during product setup; do not block sales on it.
   [pos](../pos/README.md#cl-api-information)
8. **`tasnif.history-id-unstable`**: when storing a `history` reply → its 32-character `id`
   changed on every call. Key by `mxikCode`; compare `isActive`, `updatedAt` and the
   package codes, never the `id`. [code](../code/README.md#history-integration-mxikgethistorymxik)
9. **`tasnif.throttle-and-cache`**: when calling any endpoint → no limits are published.
   One request at a time, about one a second at most, a timeout, a cache of at least a day
   per code, back-off on errors; never crawl the catalogue.
   [common](../common/README.md#politeness-and-caching)
10. **`tasnif.codes-change`**: when codes are stored → the catalogue is edited and codes
    are deactivated without a published change notice. Re-check stored codes on a schedule
    with `history`, and send changes to a person instead of rewriting products silently.
    [code](../code/README.md#history-integration-mxikgethistorymxik)
11. **`tasnif.no-tax-advice`**: when a reply carries `lgotaId` / `lgotaName`, `percent`,
    `cashSale` or `cashSaleAllowed` → these are data from the service, not advice. Which
    code, VAT treatment or benefit applies is the merchant's accountant's decision; the
    receipt side is `fiscal.vat-per-product`. [pos](../pos/README.md#txkm-vat-payer-check)
12. **`tasnif.personal-data`**: when logging, caching or saving replies → `createdBy` and
    `updatedBy` can hold a staff member's full name, and the point-of-sale calls carry a
    TIN. Drop those fields before storing, keep TINs out of logs and URLs you log, and use
    `<TIN>` in code and fixtures. [code](../code/README.md#the-card-mxikgetby-mxik)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Any call | no published rate limit or timeout; the tool uses 20 s and about one request a second | not documented; expect blocking for crawling | [common](../common/README.md#politeness-and-caching) |
| Stored codes and packages | no change notice; codes and packages are edited and deactivated | a receipt or a provider rejects the line (`fiscal.missing-mxik-blocks-payment`) | [code](../code/README.md#history-integration-mxikgethistorymxik) |
| VAT-payer status | valid on the day of the call | a seller's VAT setting goes stale | [pos](../pos/README.md#txkm-vat-payer-check) |

## Cancel, reverse and refund

Not applicable: Tasnif is a read-only catalogue. There is nothing to cancel, reverse or
refund, and no write endpoint is covered here.

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| A stored code turns out wrong | the merchant | edit the product in your catalogue; nothing is sent to Tasnif | - | - | receipts already issued stay as they are; corrections follow the provider's refund flow | [fiscal lifecycle](../../../fiscal/references/lifecycle/README.md#cancel-reverse-and-refund) |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Every `GET` here | none (no webhooks) | - | not needed: reads only | safe to repeat; back off (1 min, 5 min, 30 min) on a timeout, 5xx or an unexpected body, and keep the last good value | [common](../common/README.md#politeness-and-caching) |
| Scheduled re-check | - | - | `mxikCode` (never the `history` `id`) | compare with the stored values; report changes once | [code](../code/README.md#history-integration-mxikgethistorymxik) |

## Fiscal receipts

Tasnif registers no receipts. The code and the package code you store from it go on
receipt lines as strings: [fiscal receipt-line](../../../fiscal/references/receipt-line/README.md)
and the fiscal warnings `fiscal.mxik-as-string`, `fiscal.package-code-required` and
`fiscal.marked-goods-need-codes`.

## Not documented — ask the tax authority

- An official integration API for Tasnif, its terms of use, rate limits and an SLA.
- The meaning of `permitted`, `cashSale`, `label`, `usePackage`, `useCard`,
  `nonChangeable`, `isUnitPackage`, `status` and `isActive`, and when `permitted` is
  `true`.
- The meaning of `cashSaleAllowed`, `fractionalSale` and `baseCalculationAmount` in the
  txkm VAT check.
- A change feed or export of edited and deactivated codes.
- The parameter of `mxik/search/dv-cert-number` and which certificate it means.
- Who may reuse the product pictures.
- Access to the partner-only marking and KCM endpoints.
