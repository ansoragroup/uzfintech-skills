# Multicard Payments (payment on your own page: token, card data, split, apps; refunds)

Hand-written notes. Transport, auth, errors, statuses, signatures, `ofd` and `split`:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/) (payment
object: [`../common/schemas/payment.json`](../common/schemas/payment.json)). Examples:
[`examples/`](examples/).

- Source: https://docs.multicard.uz/4488547f0 (guide), https://docs.multicard.uz/19729310e0,
  https://docs.multicard.uz/19729311e0, https://docs.multicard.uz/19729312e0,
  https://docs.multicard.uz/19729313e0, https://docs.multicard.uz/19729314e0,
  https://docs.multicard.uz/19729315e0, https://docs.multicard.uz/19729316e0,
  https://docs.multicard.uz/24802978e0, https://docs.multicard.uz/19729317e0 (Russian pages)
- Fetched: 2026-11-03
- Needs: a bound card token ([`../cards/`](../cards/README.md)), or card data with a PCI DSS
  certificate, or a payment app chosen by the payer.

## Flow (card token or card data)

```
POST /payment {card, amount, store_id, invoice_id, callback_url, device_details, ofd}
   └─> data.uuid (store it), data.otp_hash, data.checkout_url   (status draft, nothing debited)
confirm, one of:
   a) redirect the payer to data.checkout_url
   b) PUT /payment/{uuid} {otp, debit_available}   (otp_hash != null: SMS code)
      PUT /payment/{uuid} with an empty body       (otp_hash == null: acceptless debit)
   └─> data.status success | error   (or poll on ERROR_DEBIT_UNKNOWN / ERROR_CALLBACK_TIMEOUT)
   └─> success callback to callback_url (if passed)
GET /payment/{uuid} ─> payment
```

Whether a bound card is debited with or without an SMS code is a Multicard setting for your
account; read `otp_hash` on every create instead of assuming.

App payments (`payment_system`) need no confirm call: redirect the payer to
`data.checkout_url` (a universal / app link) and wait for the callback or poll.

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| create-payment-token | `POST /payment` | `card*{token*}`, `amount*`, `store_id*`, `invoice_id*`, `callback_url`, `device_details{ip*, user_agent*}`, `ofd` | payment (`draft`) |
| create-payment-card (PCI DSS) | `POST /payment` | `card*{pan*, expiry*}` (expiry `yymm`), then as above | payment (`draft`) |
| create-payment-split | `POST /payment` | as token, plus `billing_id`, `split` | payment (`draft`) |
| create-payment-app | `POST /payment` | `payment_system*` (`payme`, `click`, `uzum`, `anorbank`, `alif`, `oson`, `xazna`, `beepul`, `trastpay`, `sbp`), `amount*`, `store_id*`, `invoice_id*`, `billing_id`, `callback_url`, `return_url`, `ofd` | payment with `checkout_url` |
| confirm-payment | `PUT /payment/{uuid}` | `otp*`, `debit_available*` (both marked required; empty body for acceptless) | payment |
| send-fiscal-link | `PATCH /payment/{uuid}/fiscal` | `url*`, `is_refund` | not specified |
| refund-payment | `DELETE /payment/{uuid}` | path `uuid` | payment (`revert`) |
| refund-payment-partial | `DELETE /payment/{uuid}/partial` | `refund_amount*`, `ofd*`, `card_pan` | not specified |
| get-payment | `GET /payment/{uuid}` | path `uuid` | payment |

`debit_available: true` lets Multicard debit what is on the card when the balance is below
`amount`. Check `payment_amount` and `total_amount` in the answer before you fulfil
(derived).

## Split payments

`split` sends parts of a payment to other recipients ([`../common/README.md`](../common/README.md#split-split)):

- `account`: a legal entity's bank account; `recipient` is the requisites uuid Multicard
  gives you;
- `wallet`: your partner wallet (funds can later be paid out to cards or a bank account);
- the sum of `split[].amount` must not exceed the payment amount minus the commission. The
  commission is set per merchant contract; take it from `commission_amount` in the answer,
  never from a hard-coded rate.

## Fiscal link

If **you** fiscalize the payment yourself, send the receipt link with
`PATCH /payment/{uuid}/fiscal {url, is_refund}` after the payment, and again with
`is_refund: true` after a refund (derived from the field name). When Multicard fiscalizes,
read the receipt from `tax.qr_url` / `refund_tax.qr_url` instead.

## Refunds

- Full refund: `DELETE /payment/{uuid}` with no body. The payment becomes `revert`, and
  `refund_time` is set.
- Partial refund: `DELETE /payment/{uuid}/partial {refund_amount, ofd}`. Multicard must
  enable partial refunds on your terminal first. The vendor says `ofd` is the data for a
  NEW receipt and the old receipt is cancelled; which items it lists is not stated, so ask
  Multicard.
  `card_pan` (a **full** PAN) is required only for payments made in an app (Payme, Click,
  ...); leave it out for Uzcard, Humo, Visa and Mastercard card payments.
- A refund that is no longer possible answers `404 ERROR_NOT_FOUND`; the page text calls it
  a `400`.

## Errors

| Case | Answer |
|---|---|
| create: validation error, wrong card number or expiry, unknown `payment_system` | `400` (`ERROR_FIELDS`, `ERROR_CARD_NOT_FOUND`) |
| confirm: wrong SMS code | `400 ERROR_WRONG_OTP` |
| confirm: already confirmed | `400 ERROR_FIELDS` |
| confirm: outcome unknown | `400 ERROR_DEBIT_UNKNOWN` or `ERROR_CALLBACK_TIMEOUT`: poll `GET /payment/{uuid}` until `success` or `error` |
| refund: not possible | `404 ERROR_NOT_FOUND` |

## Gotchas

- Creating a payment debits nothing; only the confirm step (or the payer on `checkout_url`)
  does. A `draft` payment is not a sale.
- Never resend the confirm call after a timeout, a 5xx, `ERROR_DEBIT_UNKNOWN` or
  `ERROR_CALLBACK_TIMEOUT`. Poll the payment until a final status.
- `billing_id` is an integer in the request examples and `string(64)` in the payment model;
  keep your value numeric and short so it fits both (derived).
- `device_details` needs both `ip` and `user_agent` of the payer's device, not your server.
- `phone` in the payment model is described as the last 4 digits; the schema shows a full
  number. Do not rely on either.
- The partial refund example on the vendor page is malformed JSON; follow the field table.
- `return_url` on app payments is not honoured by every app; rely on the callback or polling.
- Card-data payments and partial refunds of app payments send full PANs: PCI DSS scope.

## Examples

[`examples/`](examples/): pay-token request/response, pay-card request, pay-split request,
pay-app request/response, confirm-payment request/response, fiscal-link request, refund
response, refund-partial request, get-payment response, `ERROR_DEBIT_UNKNOWN` error.
