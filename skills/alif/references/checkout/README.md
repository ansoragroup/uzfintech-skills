# Alif Checkout (online cashier: hosted payment page by invoice)

Hand-written notes. Transport, auth, errors and webhook signing: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.alifpay.uz/checkout/ (Russian page)
- Fetched: 2026-11-03
- Direction: you create an invoice, redirect the buyer to the Alif page, Alif calls your
  `webhook_url`; you can read the invoice at any time.

## Flow

```
POST /invoice {items, webhook_url, redirect_url, ...} -> {id, price, created_at, timeout, ...}
redirect buyer -> https://checkout.alifpay.uz/?invoice=<id>
buyer pays (card or alif mobi app) ->
  webhook POST <webhook_url> (body = invoice struct, header Signature)
  browser -> redirect_url (success) | cancel_url ("back to the merchant" link)
POST /getInvoice {id} -> invoice + payment{status, ...}   (source of truth)
POST /refundInvoice {id} -> payment.status REVERTED
```

Optional: `sendInvoice {id, phone}` sends the pay link by SMS or alif app push (limit: error
`1109`).

## Methods

| Method | Params (`*` required) | Result |
|---|---|---|
| `invoice` | see below | invoice (request echo + `id`, `price`, `created_at`, `timeout`) |
| `getInvoice` | `id*` | invoice + `payment`, `merchant{id, name}` |
| `refundInvoice` | `id*` | invoice with `payment.status = REVERTED` and `receipts[{url, refund}]` |
| `sendInvoice` | `id*`, `phone*` | `{id}` |
| `addInvoiceReceiptURL` | `invoice_id*`, `url*` (absolute URL on `ofd.soliq.uz`) | `{invoice_id}`; invoice must be paid |
| `chargeInvoiceHold` (beta) | `id*`, `items*` (same item shape) | charges an invoice paid with `hold.enabled` |
| `_payInvoiceWithMobi` (test only) | `invoice_id*`, `installment` (bool; true = instalment, else card) | invoice |

## `POST /invoice` parameters

| Field | Type | Rule |
|---|---|---|
| `items*` | array | at least one item; one line for the full sum is fine when no fiscal split is needed |
| `webhook_url` | string | `https://` only |
| `redirect_url` | string | `https://` only; after successful payment |
| `cancel_url` | string | `https://` only; when the buyer abandons |
| `phone` | string | 12 digits starting `998`; used for the fiscal receipt |
| `receipt` | bool | register fiscal receipts (then every item needs `spic`) |
| `timeout` | int | seconds until the invoice can no longer be paid |
| `meta` | object | any JSON, echoed back |
| `payouts` | array | `{amount, tin (9) \| pin (14)}`; sum <= invoice total; remainder goes to you |
| `hold.enabled` (beta) | bool | instalment payments only; funds are held, then `chargeInvoiceHold` |

Item: `name*`, `amount*` (quantity, natural number), `price*` (unit price, tiyin), `spic`
(IKPU code; required when `receipt: true`), `discount` (total discount for the line in tiyin,
<= `price x amount`), `vat_percent` (VAT computed after discount), `marking_code` (32 chars,
first 16 digits; required for some IKPU codes), `tin` (9 digits) **xor** `pin` (14 digits) of the
commission principal.

Total: `sum(price x amount - discount)` must be **50,000 .. 20,000,000,000 tiyin**
(500 .. 200,000,000 UZS). The response `price` is this total.

## Invoice struct (response / webhook body)

Request fields plus `id`, `price`, `created_at`, `timeout`, `payment`, `merchant{id, name}`.
`payment` is the payment struct from [`../payments/README.md`](../payments/README.md):
`{id, amount, status, method{type, payload}, payouts, receipt{results[{merchant_id, url, refund}]}}`.

`payment.method.type`: `CARD` (`payload.pan` masked) or `MOBI` (`payload{bml, phone, txn_id,
user_id, source}`; `bml` true = instalment).

## Gotchas

- Errors come back with **HTTP 200** and an `error` object. Check it first.
- The webhook must get HTTP 200 within about an hour of retries, or the payment is
  **cancelled and refunded**. Verify `Signature` over the raw body, return 200, then confirm
  with `getInvoice` before fulfilling.
- `payment` is absent until the buyer pays. Treat only `payment.status == "SUCCEEDED"` as paid.
- `price` in the item is the **unit** price; `amount` is the **quantity**. Discount is the
  line total, not per unit.
- Fiscal receipt links live in `payment.receipt.results` on `getInvoice`, but
  `refundInvoice` returns them as a top-level `receipts` array (vendor inconsistency).
- The doc does not list invoice-level statuses; the invoice is "paid" when its payment is
  `SUCCEEDED` and "refunded" when it is `REVERTED`.
- `refundInvoice` is a full refund. Partial refunds exist only for instalment payments
  (`refundPaymentPartial`, see payments).
- Vendor samples use truncated ids; do not validate invoice ids as full UUIDs.

## Examples

[`examples/`](examples/): invoice create request/response, getInvoice response (paid),
webhook body, refundInvoice response, sendInvoice request.
