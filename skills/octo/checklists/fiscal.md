# Checklist: Octo fiscalization

Contract: [`../references/fiscal/README.md`](../references/fiscal/README.md). Also run
[`common.md`](common.md).

## Before the first sale
- [ ] Every product is registered with Octo through the bank manager with `spic`, `package_code`, `nds` and `inn` (legal entity) or `pinfl` (individual entrepreneur).
- [ ] The catalog keeps these values in one place, and the basket is built from it.

## Each payment
- [ ] `basket` items carry `position_desc` (Latin letters, digits, spaces and `- . _ ( )`), `count`, unit `price`, `spic`, `package_code`, `nds` and the registered `inn` or `pinfl`.
- [ ] `count x price` across items adds up to `total_sum`.
- [ ] `user_data` is sent with `user_id`, `phone` and `email` so the receipt reaches the payer.
- [ ] `error: 403` ("Fiscal object ... not contains in system") stops the checkout with an operator alert and is not retried as is (`octo.fiscal-registered-items`).
- [ ] Single-product shops that leave `basket` out have the active product set up in the cabinet.

## Receipt data
- [ ] `POST /fiscal-data` sends `payment_uuid` (the `octo_payment_UUID`) and handles `error: 1` for a wrong pair.
- [ ] `receiptId`, `fiscalSign`, `terminalID`, `dateTime` (`YYYYMMDDHHMMSS`) and `qrCodeURL` are stored with the order.
- [ ] A missing receipt is retried later instead of failing the order (derived).
