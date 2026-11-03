# CLICK Pass (charge by scanning the payer's QR in the CLICK app)

Hand-written notes. Schemas are in [`schemas/`](schemas/) and bodies in
[`examples/`](examples/). The `Auth` header is in [`../common/README.md`](../common/README.md).

- Source: https://docs.click.uz/en/merchant-api/click-pass
- Fetched: 2026-11-03
- Direction: **your POS or cashier backend calls Click**, base URL
  `https://api.click.uz/v2/merchant/`, with the Merchant API `Auth` header. The payer shows
  a one-time QR from the CLICK app and the cashier scans it.

## Operations

| Op | Request | Purpose |
|---|---|---|
| click-pass-payment | `POST click_pass/payment` + JSON | charge the payer from the scanned QR |
| click-pass-confirm | `POST click_pass/confirm` + JSON | confirm a payment when confirmation mode is on |
| click-pass-confirmation-on | `PUT click_pass/confirmation/:service_id` | turn confirmation mode on for the service |
| click-pass-confirmation-off | `DELETE click_pass/confirmation/:service_id` | turn it off |
| status | `GET payment/status/:service_id/:payment_id` | shared with the Merchant API |
| reversal | `DELETE payment/reversal/:service_id/:payment_id` | shared with the Merchant API; same month rules |

## Flow

```
cashier scans QR ──> click_pass/payment(otp_data, amount)
    ├─ payment_status 2 ──────────────────────────────> paid
    ├─ payment_status 0 / 1 ──> poll payment/status ──> 2 paid, < 0 failed
    └─ confirm_mode 1 ──> click_pass/confirm within 30 s, otherwise Click cancels it
```

Confirmation mode is a setting of the `service_id`. When it is on, every CLICK Pass payment
of that service waits for `click_pass/confirm`, and Click cancels any payment that is not
confirmed within **30 seconds**. Use it when the cashier must check something (for example
the card type) before accepting.

## Fields

payment request:

| Field | Type | Rule |
|---|---|---|
| `service_id` | int | your service |
| `otp_data` | string | the raw content of the scanned QR |
| `amount` | float | soums |
| `cashbox_code` | string | optional; your till id |
| `transaction_id` | string | optional; your id for this sale |

payment response:

| Field | Type | Meaning |
|---|---|---|
| `error_code`, `error_note` | int, string | `0` = accepted |
| `payment_id` | bigint | Click's payment id |
| `payment_status` | int | `< 0` error, `0` created, `1` processing, `2` success |
| `confirm_mode` | bit | `1` when the payment waits for `click_pass/confirm` |
| `card_type` | string | `private` or `corporate` |
| `processing_type` | string | `UZCARD`, `HUMO` or `WALLET` |
| `card_number` | string | masked |
| `phone_number` | string | the payer's phone |

confirm request: `service_id`, `payment_id`. The confirm and the confirmation on / off
responses carry only `error_code` and `error_note`.

## Gotchas

1. `otp_data` is a one-time code, as its name says. Send it right after scanning and never
   store or reuse it.
2. With confirmation mode on, the 30-second limit includes the cashier's decision. Confirm
   from code, not after a manual step that can stall.
3. Read `confirm_mode` from each response instead of assuming the service setting.
4. `phone_number` and `card_number` are personal data. Mask them in logs and receipts.
5. Send `transaction_id` so you can match a payment to a sale if the response is lost, and
   poll `payment/status` after any timeout before charging again.
6. The vendor's JavaScript `Auth` sample declares `merchant_user_id` / `secret_key` but then
   uses `merchantUserId` / `secretKey`. Do not copy it as is.

## Examples

- [`click-pass-payment.request.json`](examples/click-pass-payment.request.json) /
  [`click-pass-payment.response.json`](examples/click-pass-payment.response.json)
- [`click-pass-confirm.request.json`](examples/click-pass-confirm.request.json) /
  [`click-pass-confirm.response.json`](examples/click-pass-confirm.response.json)
