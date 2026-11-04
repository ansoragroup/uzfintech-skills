# Checklist: Octo payment page (one-stage and two-stage)

Contract: [`../references/payment-page/README.md`](../references/payment-page/README.md). Also run
[`common.md`](common.md).

## Create
- [ ] `prepare_payment` sends `shop_transaction_id`, `init_time`, `total_sum`, `currency`, `description`, an explicit `auto_capture`, an explicit `test`, `return_url`, `notify_url` and `ttl`.
- [ ] `ttl` is set in **minutes** and an expired unpaid payment is replaced by a new one with a new `shop_transaction_id` (`octo.ttl-minutes`).
- [ ] `user_data` is either left out or sent with all of `user_id`, `phone` and `email`.
- [ ] `return_url` is a full URL that carries a parameter identifying the payment.
- [ ] `data.octo_payment_UUID` is stored, and the payer is redirected to `data.octo_pay_url`.

## Confirm
- [ ] The order is fulfilled only after the notification **and** a status check return `succeeded` (or `waiting_for_capture` for a hold); the `return_url` redirect proves nothing.
- [ ] After a lost `prepare_payment` reply, the three-field status call with the same `shop_transaction_id` is made before any new attempt (`octo.unique-shop-ids`).
- [ ] The status check sends only `octo_shop_id`, `octo_secret` and `shop_transaction_id`.

## Two-stage (if used)
- [ ] `auto_capture: false` is sent explicitly; the default is never relied on.
- [ ] `set_accept` `capture` is called before the hold expires; the code assumes 30 minutes unless Octo confirmed a longer window for the shop (`octo.hold-auto-cancel`).
- [ ] `final_amount` never exceeds the hold; a smaller value is used to capture part and return the rest.
- [ ] The amount-confirmation callback is answered with `{accept_status, final_amount}` carrying `capture` or `waiting_user_action`, so Octo stops resending it (`octo.capture-callback-answer`).
- [ ] Unneeded holds are released with `set_accept` `cancel`; a `succeeded` payment is refunded instead (`octo.cancel-only-holds`).
- [ ] A `set_accept` that times out is followed by a status check, not by a blind repeat (derived).
