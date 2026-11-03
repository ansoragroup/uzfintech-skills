# Alif Payments (direct charges: card + OTP, card token, hold, alif mobi QR; payouts; fiscal)

Hand-written notes. Transport, auth, errors and webhook signing: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.alifpay.uz/payments/ (Russian page)
- Fetched: 2026-11-03
- Direction: your backend calls Alif; Alif sends a payment webhook on completion.

## Methods

| Method | Params (`*` required) | Result |
|---|---|---|
| `pay` | `id*`, `amount*`, `method*`, `receipt`, `payouts`, `skip_payouts` | payment struct |
| `confirmPayment` | `id*`, `otp*` | payment struct |
| `getPayment` | `id*` | payment struct |
| `refundPayment` | `id*` | `{id}`; full refund + refund receipt if a sale receipt exists |
| `applyPayouts` | `id*` | `{id}`; releases funds of a `skip_payouts` payment (idempotent) |
| `refundPaymentPartial` | `id*` (your refund id), `payment_id*`, `amount*` (> 50,000), `webhook_url` | `{id, status, amount, webhook_url}` |
| `getRefund` | `id*` (refund id) | `{id, status, amount}` |
| `registerReceipt` | `id*` (payment), `fiscal_data*{qr_code_url*, is_refund, phone_number}`, `location{latitude, longitude}`, `tin` \| `pinfl`, `sale_point_address` | `{ok}` |
| `_completeInstallmentRefund` (test, beta) | `refund_id*`, `approve` | see gotchas |

## `method` (request) by `type`

| `type` | Fields | Behaviour |
|---|---|---|
| `CARD` | `pan*` (16 digits), `exp*` (`MMYY`) | one-off; SMS OTP to the card's notification phone; status `OTP_REQUIRED` until `confirmPayment` |
| `TOKEN` | `token*`, `force` | card token from [cards](../cards/README.md); `force: true` takes whatever balance is there (from 1,000 UZS) if short; not allowed with `payouts` |
| `HOLD` | `id*` (hold id) | charge funds held by [`hold`](../hold/README.md) |
| `MOBI_SHOW_QR` | `token*` (funding source id) | alif mobi QR; status can end `QR_EXPIRED` |

The request puts card fields **flat** in `method` (`{type, pan, exp}`); the response nests
them as `method{type, payload{pan (masked), phone (masked)}}`.

## Payment struct

`id`, `amount` (tiyin charged, after discounts), `status`, `method`, `receipt{type, phone,
items[], payment_id, results[{merchant_id, url, refund}]}`, `payouts[{amount, tin | pin}]`.

- `amount`: 50,000 .. 20,000,000,000 tiyin; **excludes** discounts, so it must equal
  `sum(price x amount - discount)` of the receipt items.
- `receipt.type`: `0` purchase (default), `1` advance, `2` credit.
- `receipt.items[]`: `name*`, `amount*` (qty), `price*` (unit, tiyin), `spic*`, `discount`
  (line total), `marking_code`, `vat_percent`, `tin` (9) xor `pin` (14). Items are optional
  overall but required for fiscal receipts.
- `receipt.payment_id`: the Soliq PaymentId cash registers use to register the receipt.
- `payouts`: split to other merchants by `tin` or `pin`; sum <= `amount`; the remainder is
  yours.
- `skip_payouts: true`: charge and fiscalize now, credit nobody until `applyPayouts` (e.g. on
  delivery). Until then only a full `refundPayment` is possible. `applyPayouts` returns `1005`
  if the payment is unknown, not `skip_payouts`, not `SUCCEEDED`, or refunded.

## Statuses

| Status | Final? | Meaning |
|---|---|---|
| `SUCCEEDED` | yes | charged |
| `OTP_REQUIRED` | no | call `confirmPayment` |
| `PENDING` | no | processing; poll `getPayment` / wait for webhook |
| `PENDING_REVERSAL` | no | refund in progress |
| `HELD` | no | funds held (instalment hold flow) |
| `REVERTED` | yes | refunded / cancelled |
| `INSUFFICIENT_FUNDS`, `INVALID_CARD`, `BLOCKED_CARD`, `EXPIRED_CARD`, `PIN_TRIES_EXCEEDED`, `SMS_NOTIFICATION_IS_OFF`, `DECLINED`, `QR_EXPIRED`, `CREDIT_RESTRICTED_BY_CLIENT` | yes | declined |
| `INCORRECT_OTP`, `EXPIRED_OTP` | per vendor: OTP problem | ask for the code again or restart with a new `id` |
| `UNKNOWN_ERROR` | unknown | read back with `getPayment`; never re-charge with the same intent blindly |

The vendor does not classify statuses as final; the column above is guidance. Only
`SUCCEEDED` means paid.

## Partial refunds (instalment only)

`refundPaymentPartial` creates a refund request; on approval money returns to the buyer's
instalment limit. Refund `status`: `DONE` (done or approved), `PENDING` (under review),
`FAILED` (no reason given). Poll `getRefund` or wait for the refund webhook.

## Webhook

Sent when a payment completes (success or failure). The doc describes a `payload` attribute
holding the payment struct, while the changelog says the body **is** the payment struct.
Accept both: `body.get("payload", body)`. Verify `Signature` first. The `/pay` request has no
`webhook_url` field and the doc does not say where its webhook goes; confirm the URL with Alif at onboarding.

## Gotchas

- Generate `id` yourself (UUID), store it before calling, and reuse it only to read back. On
  `1108` insufficient funds, a retry needs a **new** `id`.
- `amount` must match the items after discounts; mismatches give `1005`.
- `registerReceipt` doc swaps the descriptions of `latitude` and `longitude`; use the field
  names as written (latitude = north-south).
- `_completeInstallmentRefund`: params say `refund_id` / `approve` but the vendor example
  sends `id`, and the response is documented as `{ok: true}` while the example shows
  `{"message": "success"}`. Test-only; tolerate both.
- `pay` with `CARD` returns masked phone formats that vary (`+998*****NNNN`,
  `********NNNN`); display as-is, never parse.

## Examples

[`examples/`](examples/): pay CARD request / OTP_REQUIRED response, confirmPayment request /
SUCCEEDED response, pay TOKEN request, webhook body, refundPayment, refundPaymentPartial,
error response.
