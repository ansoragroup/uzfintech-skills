# Payme fiscalization (detail items, IKPU, package code, VAT, fiscal data)

Hand-written notes. Transport and errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://developer.help.paycom.uz/metody-merchant-api/checktransaction/ (the page
  that holds CheckPerformTransaction and `detail`),
  https://developer.help.paycom.uz/metody-merchant-api/setfiscaldata/,
  https://developer.help.paycom.uz/metody-subscribe-api/receipts.create/,
  https://developer.help.paycom.uz/metody-subscribe-api/receipts.set_fiscal_data/,
  https://developer.help.paycom.uz/initsializatsiya-platezhey/otpravka-cheka-po-metodu-post/
  (Russian pages)
- Fetched: 2026-11-03
- Direction: you send the items to Payme (`detail`); Payme registers the fiscal receipt and
  reports it back (`SetFiscalData`). With your own fiscal module, you report it to Payme
  (`receipts.set_fiscal_data`).

## Flow

```
items ──> detail (one of three places)
            ├─ Merchant API:  CheckPerformTransaction result.detail
            ├─ Subscribe API: receipts.create params.detail
            └─ Checkout POST: form field detail = base64(JSON)

Payme fiscalizes ──> SetFiscalData {id, type: PERFORM|CANCEL, fiscal_data} ──> your Endpoint URL
you fiscalize    ──> receipts.set_fiscal_data {id, fiscal_data} ──> Payme (Subscribe API)
```

## `detail` object

| Field | Type | Required | Meaning |
|---|---|---|---|
| `receipt_type` | number | yes | fiscal receipt type: `0` = sale / return |
| `shipping` | object | no | `{title, price}`; price in tiyin |
| `items` | array | yes | product lines |

| `items[]` field | Type | Required | Meaning |
|---|---|---|---|
| `discount` | number | no | discount for the whole line (already multiplied by `count`), tiyin |
| `title` | string | yes | product or service name |
| `price` | number | yes | **unit** price, tiyin |
| `count` | number | yes | quantity |
| `code` | string | yes | IKPU (ИКПУ, product and service identification code), 17 digits, from tasnif.soliq.uz |
| `units` | number | no | unit-of-measure code (depends on the product) |
| `package_code` | string | yes | package code listed with the IKPU on tasnif.soliq.uz |
| `vat_percent` | number | yes | VAT percent for this line |

Sum check (derived): `sum(price x count - discount) + shipping.price` should equal the
transaction `amount`. The docs do not state the rule; a mismatch risks a rejected fiscal
receipt.

## `SetFiscalData` (Payme calls you; optional)

Sent to your Endpoint URL after a receipt reaches a successful state, whichever protocol
created it.

| Param | Type | Meaning |
|---|---|---|
| `id` | string | Payme receipt (transaction) id |
| `type` | string | `PERFORM` (payment receipt) or `CANCEL` (cancel receipt) |
| `fiscal_data.receipt_id` | string per table, number in the examples | sequence number in the virtual fiscal module |
| `fiscal_data.status_code` | number | status code (the promised list is not published) |
| `fiscal_data.message` | string | OFD error detail, or a status text |
| `fiscal_data.terminal_id` | string | virtual fiscal module number |
| `fiscal_data.fiscal_sign` | string | fiscal sign |
| `fiscal_data.qr_code_url` | string | URL of the fiscal receipt |
| `fiscal_data.date` | string | OFD registration time, `YYYYMMDDhhmmss` |

- Answer `{"result": {"success": true}}`.
- Errors: `-32001` receipt not found, `-32700` invalid JSON, `-32602` invalid params (name
  the field in `message`). Here `message` is a **plain string**, unlike the localized
  Merchant API errors.
- The tax authority makes separate fiscal receipts for payment and cancel. Store a `CANCEL`
  call as a **separate** fiscal receipt; do not overwrite the `PERFORM` one.

## `receipts.set_fiscal_data` (you call Payme; Subscribe API, back-end `X-Auth`)

`{id*, fiscal_data{receipt_id* (integer), qr_code_url*, status_code, message, terminal_id,
date, fiscal_sign}}` → `{success: true}`. Use it when your own fiscal module registered the
receipt for a Subscribe API payment.

## Gotchas

- `code` is the IKPU, not your SKU. `package_code` is mandatory even for services; take it
  from the IKPU card on tasnif.soliq.uz.
- `price` is the unit price and `discount` is the line total; do not pre-multiply `price`.
- `detail` in the checkout POST form is base64 of the JSON string.
- The POST page's "data types" table calls `items` optional; every other page marks it
  required, and fiscalization needs it.
- The `receipts.set_fiscal_data` vendor example uses `;` between fields, which is invalid
  JSON. Follow the parameter table.

## Examples

[`examples/`](examples/): `check-perform-with-detail.response.json` (items with IKPU,
package code, VAT, discount, shipping) and `set-fiscal-data-cancel.request.json`. A
`PERFORM` call is in [`../merchant/examples/`](../merchant/examples/), and a
`receipts.set_fiscal_data` request is in [`../subscribe/examples/`](../subscribe/examples/).
