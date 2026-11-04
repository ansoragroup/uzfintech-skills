# Receipt types, who registers them, and the OFD receipt link

Hand-written notes. An online sale in Uzbekistan ends in a fiscal receipt registered with
the tax committee's fiscal data operator (OFD). Each payment provider either registers it
for you from the receipt lines you send, or expects you to register it on your own fiscal
module and send back the link. Line fields: [`../receipt-line/`](../receipt-line/README.md);
field names per provider: [`../providers/`](../providers/README.md).

- Source: the provider references linked in each row (their lifecycle pages carry the full
  rules); receipt-link samples in the Click and Octo references
- Fetched: 2026-11-04

## Receipt types

| Type | What it records | Where providers name it |
|---|---|---|
| Sale | goods or services paid and delivered | Payme `receipt_type` `0`; Uzum `receipt_type` `0`, Checkout `PURCHASE`; Alif `receipt.type` `0` |
| Refund (return) | money returned for an earlier sale | Payme `SetFiscalData` `type` `CANCEL`; Uzum `/v2/refund_receipt`, Checkout `REFUND`; Alif automatic on full refund, or `is_refund`; Multicard `refund_tax`, or `is_refund` on your link |
| Advance (prepayment) | money taken before delivery | Uzum `receipt_type` `1`, Checkout `PREPAID`; Alif `receipt.type` `1` |
| Credit | goods handed over before full payment | Uzum `receipt_type` `2`; Alif `receipt.type` `2` |

- Uzum says advance and credit receipts get **no fiscal receipt** from the tax committee
  (a non-fiscal link is available from the manager). After a Checkout `PREPAID`, the final
  sale is issued with `purchaseReceipt`.
- Payme names a single value `0` for "sale / return"; the refund is a separate `CANCEL`
  receipt that Payme reports. Store it as its own record
  (`payme.cancel-is-the-refund`, `payme.no-second-receipt`).
- Click, Multicard, Octo, Atmos and Paynet document no advance or credit receipt. Ask before
  you take prepayments through them.
- Which type a given business event needs (prepayment for a pre-order, instalment, partial
  delivery) is an accounting decision. This skill only shows the fields.

## Who registers the receipt

| Provider | Registers | You send | You get back |
|---|---|---|---|
| Payme | Payme, from `detail` | `detail.items[]` | `SetFiscalData` `PERFORM` / `CANCEL` with `qr_code_url` |
| Payme (own module) | you | `receipts.set_fiscal_data` | - |
| Click | Click with `submit_items`, **or** you with `submit_qrcode`, one per payment | items or your link | `get_ofd_data`: `paymentId`, `qrCodeURL` |
| Uzum Merchant API, FastPay, Dynamic QR | you (Uzum Fiscalization or own register) | `/v2/receipt`, `/v2/refund_receipt` | `receipt_url` (202 = pending, poll) |
| Uzum Checkout | Uzum when auto-fiscalization is on (off by default, one-step only); otherwise you | `merchantParams.cart` | receipt callback `receiptUrl`, `getReceipts` |
| Alif | Alif when you ask (`receipt: true` / `receipt{}`), otherwise you | items with `spic` | `receipt.results[{url, refund}]`; own: `registerReceipt`, `addInvoiceReceiptURL` |
| Multicard | store setting `tax_registration` (`1` Multicard, `0` you) | `ofd[]` | `tax`, `refund_tax` with `qr_url`; own: `PATCH /payment/{uuid}/fiscal` |
| Octo | Octo, from `basket`, items registered first by the bank manager | `basket[]` | `POST /fiscal-data`: `qrCodeURL`, `fiscalSign` |
| Atmos | Atmos when you send fiscal lines (derived from the returned link) | `ofd_items[]` | `ofd_url` (and a second link `ofd_url_commission`) |
| Paynet | not documented | - | `data.attributes` (shape unpublished) |

The one rule that holds everywhere: **one sale receipt per payment.** If the provider
registers it, do not also register it on your own module or another OFD. Warning
[`fiscal.one-receipt-per-payment`](../lifecycle/README.md#warn-without-being-asked).

## Refund receipts

- Uzum and Alif register a refund receipt only when the sale receipt exists
  (`uzum.fiscal-refund-needs-sale`, `alif.refund-receipt-needs-sale-receipt`). Warning
  [`fiscal.refund-needs-sale-receipt`](../lifecycle/README.md#warn-without-being-asked).
- Click has no refund-receipt call (`click.no-refund-receipt-api`).
- Multicard partial refunds send `ofd` for a new receipt and cancel the old one
  (`multicard.partial-refund-new-receipt`).
- Atmos full `pay/reverse` takes no fiscal lines; partial `confirm-reverse-partial` takes
  `ofd_items`.
- Octo and Paynet describe no refund receipt.
- When you register receipts yourself, issue the refund receipt on the same module that made
  the sale, link it to that sale, and do not let it exceed the sale total.

## The receipt link (`ofd.soliq.uz`)

Providers and fiscal modules return the receipt as a link to the tax committee's receipt
page. The samples in the Click and Octo references have this shape:

```text
https://ofd.soliq.uz/epi?t=<TERMINAL_ID>&r=<RECEIPT_NUMBER>&c=<YYYYMMDDhhmmss>&s=<FISCAL_SIGN>
```

| Parameter | Meaning (derived from the samples and from Octo's reply fields) |
|---|---|
| `t` | fiscal module (terminal) id; Octo `terminalID` |
| `r` | receipt number on that module; Octo `receiptId` |
| `c` | receipt date and time, `YYYYMMDDhhmmss`; Octo `dateTime` |
| `s` | fiscal sign; Octo `fiscalSign` |

- The parameter meanings are not documented by the tax committee in any source here; treat
  them as derived. Store the whole URL as the provider returned it; do not rebuild it.
- Alif's `addInvoiceReceiptURL` wants an absolute URL on `ofd.soliq.uz`; other providers do
  not state a host rule.
- Never open or post receipt links from tests against a production fiscal module; a test
  receipt there is a real receipt. See [`../sandbox/`](../sandbox/README.md).

## Timing

Only Uzum Fiscalization publishes a deadline: `date_time` must be within 24 hours after the
confirmed payment and not in the future, otherwise 422 (`uzum.fiscal-receipt-24h`). Click
fiscalizes only after a successful payment (`payment_status` `2`). The other providers
publish no deadline; register right after the payment is confirmed and ask the provider
for its limit.
