# Checklist: Click Merchant API (invoices, status, reversal, card tokens)

Contracts: [`../references/common/README.md`](../references/common/README.md),
[`../references/merchant-api/README.md`](../references/merchant-api/README.md) and
[`../references/card-tokens/README.md`](../references/card-tokens/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] Calls go to `https://api.click.uz/v2/merchant/` with `Auth`, `Accept` and `Content-Type`.
- [ ] Path parameters are path segments, URL-encoded; order ids contain no `/`.
- [ ] Amounts are sent in soums.

## Invoices
- [ ] `invoice/create` sends `service_id`, `amount`, `phone_number` (`998XXXXXXXXX`) and
  `merchant_trans_id`, and stores `invoice_id`.
- [ ] The order is marked paid by the SHOP API Complete handler, not by `invoice/create`.
- [ ] A negative `invoice_status` is treated as "will not be paid".

## Status and reconciliation
- [ ] `payment_status` 1 (and 0) is polled with a back-off until 2 or negative.
- [ ] `status_by_mti` is called with the payment date (`YYYY-MM-DD`) when no `payment_id` is known.

## Reversal
- [ ] Refunds use `DELETE payment/reversal/:service_id/:payment_id`, full amount only.
- [ ] The current-month window (and day 1 for the previous month) is enforced or surfaced.
- [ ] A rejected reversal falls back to another refund path.

## Card tokens
- [ ] `card_number` and `expire_date` (`MMYY`) are never logged or stored; they are dropped
  after `card_token/request`.
- [ ] The token is used only after `card_token/verify` succeeds.
- [ ] Reusable tokens (`temporary = 0`) are stored encrypted and bound to the payer's account.
- [ ] `card_token/payment` sends a unique `transaction_parameter` and handles `payment_status` 1.
- [ ] Removing a saved card calls `DELETE card_token/:service_id/:card_token`.
