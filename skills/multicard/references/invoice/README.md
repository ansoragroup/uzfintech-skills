# Multicard Invoice (hosted payment page, QR fast pay, callbacks)

Hand-written notes. Transport, auth, errors, signatures and `ofd`:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://docs.multicard.uz/4488544f0 (guide), https://docs.multicard.uz/19729296e0,
  https://docs.multicard.uz/19729297e0, https://docs.multicard.uz/19729298e0,
  https://docs.multicard.uz/19729299e0, https://docs.multicard.uz/19729300e0,
  https://docs.multicard.uz/19729301e0 (Russian pages)
- Fetched: 2026-11-03
- Direction: you create the invoice and send the payer to Multicard; Multicard calls your
  `callback_url` after the debit.

## Flow

```
POST /payment/invoice {store_id, amount, invoice_id, callback_url, ofd}
   └─> data.uuid (store it), data.checkout_url (redirect), data.short_link (QR, prod only)
payer pays on checkout_url: card, or an app (Payme, Click, Uzum, Anorbank, Oson, Alif, ...)
   └─> Multicard POSTs the success callback to callback_url ─> you answer 200 {success: true}
   └─> payer returns to return_url / return_error_url
optional: status webhooks on every status change
GET /payment/invoice/{uuid} ─> invoice with the nested payment
```

Fulfil the order only after a verified success callback, or after `GET` shows the nested
`payment.status` = `success`. The return URL is not proof of payment.

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| create-invoice | `POST /payment/invoice` | `store_id*` (int id or cashbox uuid), `amount*`, `invoice_id*`, `callback_url*`, `ofd*`, `lang` (`ru`, `uz`, `en`), `return_url`, `return_error_url`, `sms` (`998XXXXXXXXX`: send the link by SMS), `ttl` (seconds, default 1 day) | invoice: `uuid`, `checkout_url`, `short_link`, `deeplink`, `payment`, echo of the request |
| get-invoice | `GET /payment/invoice/{uuid}` | path `uuid` | invoice, `payment` filled once paid |
| delete-invoice | `DELETE /payment/invoice/{uuid}` | path `uuid` | `null` |
| scanpay | `PUT /payment/{uuid}/scanpay` | path invoice `uuid`; `code*` (QR code read from the payer's app) | payment |

Callbacks you receive:

| Callback | When | Body | Your answer |
|---|---|---|---|
| success callback | after a successful debit | `store_id`, `amount`, `invoice_id`, `billing_id`, `payment_time`, `phone`, `card_pan`, `ps`, `card_token`, `uuid` (payment), `receipt_url`, `sign` | HTTP 200 `{"success": true}` |
| status webhook | every status change, if enabled | `uuid`, `amount`, `invoice_id`, `status`, `billing_id`, `payment_time`, `refund_time`, `phone`, `card_pan`, `ps`, `card_token`, `receipt_url`, `sign` | any 2xx |

Signatures, retries and the refund-on-reject rule: [`../common/README.md`](../common/README.md).

## Scanpay (PaymeGo, ClickPass and similar)

The payer shows a QR code in their app (Payme, Click, Uzum, Anorbank, Xazna); your cashier
or kiosk reads it and sends `code` for an existing invoice `uuid`.

- A wrong QR answers `400` with a message for the payer.
- On a timeout, `ERROR_DEBIT_UNKNOWN` or HTTP 500, read the status with
  `GET /payment/invoice/{uuid}` (or `GET /payment/{payment uuid}`); do not resend.

## Errors

| Case | Answer |
|---|---|
| get an expired invoice | `400 ERROR_TRANS_NOT_READY` |
| unknown invoice uuid | `404 ERROR_NOT_FOUND` |
| delete a paid invoice | `400` |

## Gotchas

- `ofd` is **required** on create, even when the store fiscalizes with a default IKPU.
- `uuid` in the create answer is the **invoice** uuid. The payment has its own uuid
  (`data.payment.uuid`, and `uuid` in callbacks). Store both.
- `invoice_id` comes back as `invoice_id` in callbacks and as `store_invoice_id` in the
  payment object.
- Rejecting the success callback (non-200, or `success` not `true`) refunds the payer. Return
  `{"success": false, "message": "..."}` only when you really cannot fulfil the order.
- A repeated callback for the same payment `uuid` must get the same success answer.
- `short_link` is returned only in production; build QR codes from it there and from
  `checkout_url` in the sandbox.
- `ttl` is in seconds. An expired invoice answers `ERROR_TRANS_NOT_READY`; create a new one.

## Examples

[`examples/`](examples/): create-invoice request/response, get-invoice response (paid),
delete-invoice response, scanpay request/response, success callback request with the
accept and reject answers, status webhook request.
