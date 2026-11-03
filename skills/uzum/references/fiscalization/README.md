# Uzum Fiscalization (OFD receipts)

Hand-written notes. Generated tables: [`endpoints.md`](endpoints.md); schemas:
[`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_fiscalization.yaml (en labels: `en_fiscalization.yaml`)
- Fetched: 2026-11-03
- Use when you take payments outside Uzum Checkout auto-fiscalization (Merchant API,
  FastPay, own acquiring) and must register the sale receipt with the tax OFD.

## Hosts and auth

| Env | Base URL |
|---|---|
| Test | `https://test-ofd.ipt-merch.com` |
| Production | `https://ofd-key.inplat-tech.com` |

Header `X-API-Key: <FISCAL_API_KEY>`. This key is separate from the Checkout key.

## Operations

| Method | Path | Purpose |
|---|---|---|
| POST | `/v2/receipt` | sale receipt (or advance / credit receipt) |
| POST | `/v2/refund_receipt` | refund receipt for an earlier sale |
| POST | `/v2/qr_payment` | register a QR-code receipt printed by your own cash register |
| GET | `/v2/receipt/{operation_id}/receipt_url` | fetch the receipt URL later |
| GET | `/health/` | liveness |

## `/v2/receipt` request

| Field | Type | Rule |
|---|---|---|
| `operation_id` * | uuid | your idempotency key; new per receipt, reuse only for retries |
| `payment_id` | uuid | payment id; optional on sale, **required** and equal to the sale's on refund |
| `date_time` * | date-time | Tashkent time of the payment; must be within 24 h of it |
| `cash_amount` *, `card_amount` * | int | tiyin; sum = receipt total **before** discounts |
| `card_type` | int | `1` corporate, `2` private, `3` social card |
| `card_number` | string | required for `card_type` 3: pass the `ofdPan` from Checkout `getOrderStatus` |
| `phone_number` | string | optional, `998XXXXXXXXX` (max 12); no cashback without it |
| `ppt_id` | string | optional processing-centre transaction id |
| `receipt_type` | int | `0` sale, `1` advance (prepaid), `2` credit |
| `items[]` * | array | see below |

Item fields:

| Field | Rule |
|---|---|
| `product_name` * | up to 63 chars |
| `price` * | line price in tiyin, before discount |
| `discount`, `voucher` | tiyin |
| `count` * | number (fractional allowed) |
| `spic` * | product classification code (IKPU) from tasnif.soliq.uz |
| `package_code` * | package code for that SPIC |
| `vat_percent` * | integer percent, e.g. `12`, `0` |
| `commission_info` | `{TIN}` (9 digits) **or** `{PINFL}` (14 digits), exactly one; for commission / agent sales |
| `owner_type` | `0` reseller, `1` producer, `2` service provider |
| `labels` | marking codes array; mandatory for marked goods categories since 2024-03-01, **not present in the OpenAPI schema** |

## Responses

| HTTP | Body | Meaning / action |
|---|---|---|
| 200 | `{receipt_id, payment_id, receipt_url}` | registered (`receipt_id` is the tax-committee number) |
| 202 | `{code, message}` | accepted, not fiscalized yet: `0` OFD timeout, `1` OFD comms error (will retry), `2` still retrying. Poll the receipt URL later |
| 400 | `{code: 1}` | SPIC or package code invalid |
| 400 | `{code: 2}` | a receipt with the same `payment_id` and `receipt_type` was already sent |
| 400 (refund) | `{message}` | refund no longer possible (expired) |
| 403 | `{message}` | auth: header missing, duplicated, or key unknown |
| 404 (refund, receipt_url) | `{message}` | receipt not found by `payment_id` / `operation_id` |
| 422 | `{detail[]}` | FastAPI validation; fix the payload |
| 500 | `{message}` | server error; retry with the same `operation_id` |

`refund_receipt` 200 returns `{receipt_id, receipt_url}`. `receipt_url` GET returns
`{receipt_url}` or 202 `{message}` while pending.

## `/v2/refund_receipt`

Same item shape. `payment_id` must be the sale's `payment_id`; `card_type` only `1` or `2`.
New `operation_id`.

## `/v2/qr_payment`

Required: `payment_id`, `operation_id` (uuid), `paid_sum` (tiyin), `date_time`,
`commission_info {TIN|PINFL}`, `phone_number`, `receipt_info {terminal_id, receipt_seq}`.
Optional: `sale_point_address`. 202 semantics as above (`code` 0/1).

## Gotchas

- Amounts are **before discounts**; discounts go in `discount` per item.
- `date_time` later than 24 h after confirmation is rejected.
- The Testing section mentions `/v2/receipt_url/{operation_id}`; the spec path is
  `/v2/receipt/{operation_id}/receipt_url`. Use the spec path.
- `commission_info` with both `TIN` and `PINFL` is invalid.
- 202 is not an error. Store `operation_id` and poll.
- Test SPIC values and keys come from your Uzum manager.

## Examples

[`examples/`](examples/): sale receipt request/response, 202 pending, refund receipt.
