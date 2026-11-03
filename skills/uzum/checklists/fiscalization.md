# Checklist: Uzum Fiscalization (OFD receipts)

Contract: [`../references/fiscalization/README.md`](../references/fiscalization/README.md).

- [ ] Base URL and `X-API-Key` from config (test vs production hosts differ; key separate from Checkout).
- [ ] The test-host receipt and refund variants in [`references/sandbox/`](../references/sandbox/README.md#fiscalization) pass before the production key is requested; production fiscalization is never used for tests.
- [ ] `operation_id` is a new UUID per receipt, persisted, and reused only for retries of that receipt.
- [ ] `payment_id` stored on sale; refund sends the **same** `payment_id`.
- [ ] `date_time` is Tashkent time of the payment and sent within 24 h.
- [ ] `cash_amount + card_amount` == sum of item `price` **before** discounts; discounts in item `discount`.
- [ ] Amounts are integer tiyin.
- [ ] Every item has `product_name` (<= 63 chars), `price`, `count`, `spic`, `package_code`, `vat_percent`.
- [ ] Commission sales send `commission_info` with exactly one of `TIN` (9) / `PINFL` (14).
- [ ] Marked goods send `labels` (outside the OpenAPI schema; confirm with your manager).
- [ ] `card_type 3` sends `card_number` = Checkout `ofdPan`.
- [ ] HTTP 202 is stored as "pending" and polled via `GET /v2/receipt/{operation_id}/receipt_url`, not treated as failure.
- [ ] 400 `code 2` (already sent) is reconciled, not retried with a new `operation_id`.
- [ ] 500 / network errors retried with the same `operation_id` and backoff.
- [ ] 422 `detail[]` is logged as a bug in the payload.
- [ ] Refund receipts use `card_type` 1 or 2 only and a new `operation_id`.
- [ ] `receipt_url` is saved and shown to the customer.
