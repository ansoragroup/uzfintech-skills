# Checklist: Octo refunds and hold release

Contracts: [`../references/refunds/README.md`](../references/refunds/README.md),
[`../references/payment-page/README.md`](../references/payment-page/README.md) (hold release). Also run
[`common.md`](common.md).

## Choose the path
- [ ] Held payments (`waiting_for_capture`) are released with `set_accept` `cancel`; only `succeeded` payments go to `/refund` (`octo.cancel-only-holds`).

## Refund
- [ ] `POST /refund` sends `octo_shop_id`, `octo_secret`, `octo_payment_UUID`, `amount` and a `shop_refund_id` that is stored before the call and reused on a retry.
- [ ] Each call is at least 1 USD or the UZS equivalent and at most 10 mln UZS; larger amounts are split into several calls with distinct `shop_refund_id` values (`octo.refund-limits`).
- [ ] The running total of refunds is checked against the payment and `refunded_sum` before each call.
- [ ] `error: 22` is shown as an amount problem, not retried as is.
- [ ] `status: pending` is re-checked through the payment status; a second refund is not sent for it.
- [ ] `refund_time` is parsed both as ISO 8601 and as `yyyy-MM-dd HH:mm:ss`.

## Receipts
- [ ] For fiscalized payments, how the return receipt is issued has been confirmed with Octo (not documented).
