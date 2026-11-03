# Checklist: CLICK Pass

Contracts: [`../references/common/README.md`](../references/common/README.md) and
[`../references/click-pass/README.md`](../references/click-pass/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Payment
- [ ] The scanned QR content goes into `otp_data` at once and is never stored or reused.
- [ ] `amount` is in soums; `cashbox_code` and `transaction_id` identify the till and the sale.
- [ ] `payment_status` 2 completes the sale; 0 and 1 are polled with `payment/status`; negative fails.
- [ ] After a timeout, `payment/status` is checked before the payer is charged again.

## Confirmation mode
- [ ] The code reads `confirm_mode` from each response.
- [ ] With `confirm_mode = 1`, `click_pass/confirm` is sent from code within 30 seconds.
- [ ] Turning the mode on or off uses `PUT` / `DELETE click_pass/confirmation/:service_id`.

## Data
- [ ] `card_number` and `phone_number` are masked in logs and receipts.
- [ ] The `Auth` header is built from correctly named variables, not the vendor JS sample.
- [ ] Refunds use `payment/reversal` within its month window.
