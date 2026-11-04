# Octo fiscalization (basket items in prepare_payment, receipt data afterwards)

Hand-written notes. Octo registers the fiscal receipt with the tax service (soliq) for
the shop; you describe the goods in `prepare_payment` and can read the receipt back.
Transport, auth and the basket model: [`../common/README.md`](../common/README.md). Schema:
[`schemas/fiscal-data.json`](schemas/fiscal-data.json). Examples: [`examples/`](examples/).

- Source: https://help.octo.uz/fiscal-data.html,
  https://help.octo.uz/payment-via-web/methods/prepare-payment.html (Russian pages)
- Fetched: 2026-11-04
- Needs: every product registered in Octo's database **before** the first payment, through
  your Octo bank manager (not through the API).

## Flow

```
once per product: send your manager the shop name, inn or pinfl, package_code, spic, nds
                  ─> the manager adds the product to Octo's database
each payment:     POST /prepare_payment {..., user_data{user_id, phone, email}, basket[...]}
                  ─> unregistered item: error 403 "Fiscal object ... not contains in system"
after payment:    POST /fiscal-data {octo_shop_id, octo_secret, payment_uuid}
                  ─> data {terminalID, receiptId, dateTime, fiscalSign, qrCodeURL, ...}
```

## Basket item

Model: [`../common/schemas/basket-item.json`](../common/schemas/basket-item.json).

| Field | Rule |
|---|---|
| `position_desc*` | product name in Latin letters, digits, spaces and `- . _ ( )` |
| `count*` | quantity |
| `price*` | unit price in major units; `count x price` across items should add up to `total_sum` (derived: the vendor sample does not) |
| `spic` | IKPU code; marked optional in the table but part of the registered fiscal object, so send it |
| `inn` / `pinfl` | from 01.08.2025: `inn` for a legal entity, `pinfl` for an individual entrepreneur; send the one you registered |
| `package_code*` | package code registered for the product |
| `nds*` | `1` VAT included, `0` no VAT |

The values must match the registered record exactly: the `403` message lists `spic`,
`package_code`, `nds`, `inn` and `pinfl`, so any of them can cause a mismatch. Warning
[`octo.fiscal-registered-items`](../lifecycle/README.md).

## Payer contact

- The fiscal page says `prepare_payment` **must** carry `user_data` with an e-mail (Octo
  sends a link to the receipt) or a phone (the receipt is registered to that number).
- The `prepare_payment` table marks `user_data` optional but, once sent, requires
  `user_id`, `phone` and `email` together. Send all three when you need a receipt.

## Single-product shops

A shop that sells one kind of product may leave `basket` out. Octo then uses the active
product that the manager set up in the cabinet.

## Method

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| fiscal-data | `POST /fiscal-data` | `octo_shop_id*`, `octo_secret*`, `payment_uuid*` | `phone`, `code`, `message`, `terminalID`, `receiptId`, `dateTime` (`YYYYMMDDHHMMSS`), `fiscalSign`, `qrCodeURL` |

- `payment_uuid` is the `octo_payment_UUID`; the field name differs from every other method.
- A wrong pair answers `{error: 1, errMessage: "wrong secret", data: null}`, not code `2`.
- The partner-page transaction object also carries `fiscalDetails{status, errorCode,
  message}` ([`../partner-page/`](../partner-page/README.md)).

## Gotchas

- Registration is manual and takes a round trip with the manager; add new products there
  before you list them in the shop (derived).
- Keep your catalog's `spic`, `package_code`, `nds` and `inn`/`pinfl` in one table that
  matches what you registered, and build the basket from it (derived).
- When the receipt is not ready yet, the reply is not printed; retry `fiscal-data` later
  instead of failing the order (derived).
- Return receipts for refunds are not documented ([`../refunds/`](../refunds/README.md)).

## Examples

[`examples/`](examples/): prepare-payment-basket request (validated against
[`../payment-page/schemas/prepare-payment.json`](../payment-page/schemas/prepare-payment.json)),
error-fiscal-object response, fiscal-data request/response.
