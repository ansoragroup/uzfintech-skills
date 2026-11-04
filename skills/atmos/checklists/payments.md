# Checklist: Atmos Payments (Uzcard / Humo, refunds, multi-payments, hosted page)

Contract: [`../references/payments/README.md`](../references/payments/README.md). Also run
[`common.md`](common.md).

## Create and pay
- [ ] `pay/create` sends `amount` (tiyin), `account` (your order id, numeric and unique), `store_id`, `terminal_id` when the store has more than one terminal, and `ofd_items`.
- [ ] Both ids are stored on the order: the draft `transaction_id` and, after `apply`, `success_trans_id`.
- [ ] `pay/pre-apply` sends either `card_token` or `card_number` + `expiry` (`YYmm`), never both.
- [ ] The SMS flow (card number from your form) runs only on PCI DSS certified systems; otherwise the payment page, the widget or a card token is used.
- [ ] Token payments send `otp` `111111`; SMS payments send the code the payer typed.
- [ ] `pay/otp-resend` is offered only in the SMS flow; `STPIMS-ERR-098` lets the payer retry.

## Outcome
- [ ] The order is marked paid only when `store_transaction.confirmed` is `true` and `success_trans_id` is set, read from `apply` or `pay/get`.
- [ ] A lost `apply` answer (timeout, 5xx, `STPIMS-ERR-118`) leads to `pay/get`, never to a second `apply`.
- [ ] `STPIMS-ERR-092` from `pay/get` is not treated as a failure when `store_transaction` shows a confirmed payment.
- [ ] A widget `success_redirect` or a payment-page `redirectLink` is not treated as proof of payment.

## Refunds
- [ ] `pay/reverse` sends `success_trans_id` in its `transaction_id` field.
- [ ] A partial refund calls `create-reverse-partial`, then `confirm-reverse-partial` with `ofd_items` for the refunded part, and reads `get-reverse-partial`.
- [ ] `STPIMS-ERR-101` leads to a read and a later retry, not a loop.

## Multi-payment (`bulk`)
- [ ] `bulk/pay/create` sends `store_id` and `params[]` with `account` and `amount` per part; the parts add up to the debit.
- [ ] `store_transactions[]` from `bulk/pay/apply` are matched to the parts and each part is fulfilled once.

## Hosted page and widget
- [ ] The payment page URL carries `storeId`, `transactionId` and an optional `redirectLink`; production uses `https://checkout.pays.uz`.
- [ ] The widget `key` holds no secret (`consumer_secret`, `api_key`); which key it takes was confirmed with Atmos.
- [ ] The test widget and test page (`http://`) are not used in production.
