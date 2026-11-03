# Click fiscalization (OFD receipt data for a Click payment)

Hand-written notes. Schemas are in [`schemas/`](schemas/) and bodies in
[`examples/`](examples/). The `Auth` header is in [`../common/README.md`](../common/README.md).

- Source: https://docs.click.uz/en/merchant-api/fiscalization
- Fetched: 2026-11-03
- Direction: **you call Click**, base URL `https://api.click.uz/v2/merchant/`, with the
  Merchant API `Auth` header.

## Operations

| Op | Request | Purpose |
|---|---|---|
| submit-items | `POST payment/ofd_data/submit_items` + JSON | send the goods and services of a paid payment so Click can fiscalize it |
| submit-qrcode | `POST payment/ofd_data/submit_qrcode` + JSON | send the link of a receipt you fiscalized yourself |
| get-ofd-data | `GET payment/ofd_data/:service_id/:payment_id` | read the receipt link for a payment |

Use **either** `submit_items` (Click fiscalizes) **or** `submit_qrcode` (you fiscalized
through your own cash register or OFD provider) for a payment.

## Units

All money fields here are integer **tiyin**: `received_ecash`, `received_cash`,
`received_card`, `Price`, `GoodPrice`, `VAT`, `Discount` and `Other`. Payment amounts in the
other Click APIs are soums, so multiply by 100.

## submit-items fields

Top level:

| Field | Type | Rule |
|---|---|---|
| `service_id` | int | your service |
| `payment_id` | long | the Click payment |
| `items` | Item[] | at least one item |
| `received_ecash` | int | tiyin paid electronically |
| `received_cash` | int | tiyin paid in cash |
| `received_card` | int | tiyin paid by card |

Item (`*` = required; names are PascalCase):

| Field | Type | Rule |
|---|---|---|
| `Name`* | string, max 63 | product or service name, including the unit |
| `Barcode` | string, max 13 | barcode |
| `Labels` | string[], up to 300 | marking codes for labelled goods |
| `SPIC`* | string, max 17 | IKPU (MXIK) classifier code |
| `Units` | uint64 | unit code |
| `PackageCode`* | string, max 20 | package code |
| `GoodPrice` | uint64 | price per unit, tiyin |
| `Price`* | uint64 | total for the line, tiyin |
| `Amount`* | uint64 | quantity |
| `VAT`* | uint64 | VAT amount for the line, tiyin |
| `VATPercent`* | int | VAT rate, e.g. `12` or `0` |
| `Discount` | uint64 | discount, tiyin |
| `Other` | uint64 | other discounts, tiyin |
| `CommissionInfo`* | object | `TIN` (9 chars) **or** `PINFL` (14 chars); one of the two is required |

The response is `error_code` and `error_note`.

## submit-qrcode and get-ofd-data

- `submit_qrcode`: `service_id`, `payment_id` and `qrcode` (the receipt URL on the tax
  portal). Response: `error_code`, `error_note`.
- `get_ofd_data` response: `paymentId` (long) and `qrCodeURL` (string). These two keys are
  **camelCase**, unlike every other Click response.

## Gotchas

1. Item keys are PascalCase (`Name`, `SPIC`, `VATPercent`) while the top-level keys are
   snake_case. Serializers that rename keys will break the call.
2. The `received_*` fields should add up to the payment total, in tiyin. The docs do not say
   whether Click checks this, so send consistent numbers.
3. `CommissionInfo` is marked required and described only as commission receipt data, so
   send it on every item. The docs do not say whose `TIN` / `PINFL` it holds; confirm with
   Click before going live.
4. `Price` is the line total, not the unit price. The unit price goes into `GoodPrice`.
5. Call fiscalization only after the payment succeeded (`payment_status = 2` or a Complete
   you accepted).
6. The docs list no fiscal error codes. Log `error_note` and retry later on a failure; do
   not send a second receipt for the same payment without checking `get-ofd-data` first.

## Examples

- [`submit-items.request.json`](examples/submit-items.request.json) /
  [`submit-items.response.json`](examples/submit-items.response.json)
- [`submit-qrcode.request.json`](examples/submit-qrcode.request.json)
- [`get-ofd-data.response.json`](examples/get-ofd-data.response.json)
