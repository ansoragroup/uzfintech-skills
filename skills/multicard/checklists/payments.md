# Checklist: Multicard Payments, Refunds and Hold

Contracts: [`../references/payments/README.md`](../references/payments/README.md),
[`../references/hold/README.md`](../references/hold/README.md). Also run
[`common.md`](common.md).

## Create and confirm
- [ ] `POST /payment` sends `card.token` (or card data only with PCI DSS, or `payment_system`), tiyin `amount`, `store_id`, `invoice_id`, and `device_details` with the **payer's** `ip` and `user_agent`.
- [ ] `ofd` is sent when the store fiscalizes through Multicard.
- [ ] `data.uuid` is stored; a `draft` payment is never treated as paid.
- [ ] Confirmation follows `otp_hash`: an OTP (`PUT /payment/{uuid} {otp}`) when it is set, an empty body when it is `null`, or a redirect to `checkout_url`.
- [ ] App payments (`payment_system`) redirect to `checkout_url` and wait for the callback or poll; `return_url` is not relied on.
- [ ] With `debit_available: true`, `payment_amount` and `total_amount` are checked before fulfilment.
- [ ] A confirm that answers `ERROR_FIELDS` "already confirmed" is resolved by reading the payment, not by failing the order.

## Split
- [ ] The sum of `split[].amount` does not exceed the amount minus the commission; `recipient` is a requisites uuid from Multicard.

## Refunds
- [ ] Full refunds call `DELETE /payment/{uuid}` and expect status `revert`.
- [ ] Partial refunds call `DELETE /payment/{uuid}/partial` with `refund_amount` and `ofd`; `card_pan` is sent only for app payments; partial refunds are enabled for the terminal.
- [ ] `404 ERROR_NOT_FOUND` on refund is handled as "no longer refundable".
- [ ] If you fiscalize yourself, the receipt link is sent with `PATCH /payment/{uuid}/fiscal`, with `is_refund: true` after a refund.

## Hold
- [ ] `expiry` on create-hold is in minutes (1..43200).
- [ ] Every later hold call uses `data.payment.uuid`, not the hold `id`.
- [ ] Charge happens before expiry, for at most the held amount, with `ofd` when Multicard fiscalizes.
- [ ] Unneeded holds are released with `DELETE /payment/hold/{uuid}`; `403 ERROR_PAYMENT_APPLIED` is handled.
- [ ] A charge that times out or answers `ERROR_DEBIT_UNKNOWN` / `ERROR_CALLBACK_TIMEOUT` is polled, not repeated.
