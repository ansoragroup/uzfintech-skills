# Checklist: Alif Payments (pay, confirm, refunds, payouts, receipts)

Contract: [`../references/payments/README.md`](../references/payments/README.md). Also run
[`common.md`](common.md).

## Charging
- [ ] `pay` sends a fresh UUID `id`, persisted first; `amount` equals `sum(price x amount - discount)` of the receipt items.
- [ ] `amount` is within 50,000..20,000,000,000 tiyin.
- [ ] `method` is flat in the request (`{type, pan, exp}` / `{type, token}` / `{type, id}`); the response is read from `method.payload`.
- [ ] `CARD`: `OTP_REQUIRED` leads to `confirmPayment {id, otp}`; `1100` / `1101` / `1106` and `INCORRECT_OTP` / `EXPIRED_OTP` are handled.
- [ ] `TOKEN` + `force: true` is not combined with `payouts`, and a partial charge is reconciled against the order.
- [ ] `HOLD` uses a new payment `id`, distinct from the hold `id`.
- [ ] `MOBI_SHOW_QR` handles `QR_EXPIRED`.

## State handling
- [ ] Only `SUCCEEDED` is treated as paid; `PENDING`, `PENDING_REVERSAL` and `HELD` are polled with `getPayment`.
- [ ] Decline statuses map to user messages; `UNKNOWN_ERROR` is read back, never blindly re-charged.
- [ ] Timeouts lead to `getPayment {id}` before any retry.

## Webhook
- [ ] `Signature` is verified; the body is parsed as `body.get("payload", body)`.
- [ ] The payment state is confirmed with `getPayment` before fulfilment; deliveries are idempotent.
- [ ] The webhook destination for `/pay` is confirmed with Alif (no `webhook_url` param).

## Refunds and payouts
- [ ] `refundPayment` is used for full refunds; the result is checked (`REVERTED` via `getPayment`).
- [ ] `refundPaymentPartial` is used only for instalment payments, with its own refund `id`, `amount` > 50,000, and polling via `getRefund` (`DONE` / `PENDING` / `FAILED`).
- [ ] With `skip_payouts`, `applyPayouts` is called once on the business trigger (delivery), `1005` is handled, and only a full refund is used before that.
- [ ] `payouts` use `tin` (9) or `pin` (14) and sum to no more than `amount`.

## Fiscal
- [ ] `registerReceipt` sends the `ofd.soliq.uz` `qr_code_url`, `is_refund` for refunds, and `tin` xor `pinfl`.
- [ ] Latitude and longitude are sent under their own names (the vendor descriptions are swapped).
