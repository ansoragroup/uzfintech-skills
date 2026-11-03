# Click Merchant API: invoices, payment status, reversal

Hand-written notes. Schemas are in [`schemas/`](schemas/) and bodies in
[`examples/`](examples/). The `Auth` header, HTTP error codes and units are in
[`../common/README.md`](../common/README.md). Card tokens, fiscalization and CLICK Pass use
the same base URL and auth; they have their own folders.

- Source: https://docs.click.uz/en/merchant-api/, https://docs.click.uz/en/merchant-api/requests,
  https://docs.click.uz/en/merchant-api/errors
- Fetched: 2026-11-03
- Direction: **you call Click.**

## Transport

| Item | Value |
|---|---|
| Base URL | `https://api.click.uz/v2/merchant/` |
| Headers | `Accept: application/json`, `Content-Type: application/json`, `Auth: <merchant_user_id>:<sha1(timestamp + secret_key)>:<timestamp>` |
| Body format | JSON in the examples; the docs also list `application/xml` as supported |
| Path params | `:service_id`, `:invoice_id`, `:payment_id` and `:merchant_trans_id` are path segments, not a query string |
| Result | `error_code` (int, `0` = success) and `error_note` in the body; transport and auth problems are HTTP codes |
| Amount | soums (`float`) |

## Operations

| Op | Request | Returns |
|---|---|---|
| invoice-create | `POST invoice/create` + JSON | `invoice_id` |
| invoice-status | `GET invoice/status/:service_id/:invoice_id` | `invoice_status`, `invoice_status_note` |
| payment-status | `GET payment/status/:service_id/:payment_id` | `payment_id`, `payment_status` |
| payment-status-by-mti | `GET payment/status_by_mti/:service_id/:merchant_trans_id/:date` (date `YYYY-MM-DD`) | `payment_id`, `merchant_trans_id` |
| payment-reversal | `DELETE payment/reversal/:service_id/:payment_id` | `payment_id` |

## Invoice flow

```
your billing ──invoice/create(phone, amount, merchant_trans_id)──> Click
Click shows the invoice to the payer (CLICK app, USSD)
payer confirms ──> Click sends SHOP API Prepare ──> debit ──> Complete ──> your billing
your billing notifies your site or app that the order is paid
```

The invoice is paid through the SHOP API, so the service must have Prepare and Complete
implemented (see [`../shop-api/README.md`](../shop-api/README.md)). Treat the order as paid
when your Complete handler accepts, not when `invoice/create` returns.

## Fields

invoice-create request:

| Field | Type | Rule |
|---|---|---|
| `service_id` | int | your service |
| `amount` | float | soums |
| `phone_number` | string | the payer's CLICK phone, `998XXXXXXXXX` |
| `merchant_trans_id` | string | your order id; it arrives back as `merchant_trans_id` in Prepare / Complete |

invoice-status: `invoice_status` (bigint) and `invoice_status_note`. The docs show `-99`
"Deleted" and publish no full list. Treat negative values as "will not be paid".

payment-status: `payment_status` (int). The docs define the values on the CLICK Pass page:

| `payment_status` | Meaning |
|---|---|
| < 0 | error; see `error_note` |
| 0 | created |
| 1 | processing |
| 2 | successful |

payment-status-by-mti: finds a payment by your `merchant_trans_id` on a given **date**
(`YYYY-MM-DD`). Pass the date the payment was made. Use it to reconcile when you do not have
the `payment_id`.

## Reversal

`DELETE payment/reversal/:service_id/:payment_id` refunds a payment in full. Conditions:
- the payment completed successfully;
- it belongs to the **current reporting month**. A previous month's payment can be
  reversed only on the **first day** of the following month;
- it was made with an online card;
- UZCARD may still reject the reversal.

Plan a different refund path (bank transfer, a goodwill credit) for payments outside that
window. The current docs do not describe partial reversal.

## Gotchas

1. `timestamp` is in **seconds** (10 digits) and the digest is SHA-1 over
   `timestamp + secret_key` as a string. A clock skew or a millisecond timestamp gives 401.
2. The body is the source of truth. A 200 response can still carry a non-zero
   `error_code`. Check both the HTTP status and `error_code`.
3. `merchant_trans_id` goes into a path segment in `status_by_mti`. URL-encode it, and avoid
   `/` in your order ids.
4. The docs give no list of non-zero `error_code` values. Log `error_note` and map only
   `0` to success.
5. `payment_status = 1` is not final. Poll `payment/status` with a back-off until it is `2`
   or negative.
6. The reversal window is short. Run refunds promptly, and on day 1 of a month clear
   anything left from the previous month.

## Examples

Bodies only. Headers are described above.

- [`invoice-create.request.json`](examples/invoice-create.request.json) /
  [`invoice-create.response.json`](examples/invoice-create.response.json)
- [`invoice-status.response.json`](examples/invoice-status.response.json)
- [`payment-status.response.json`](examples/payment-status.response.json)
- [`payment-status-by-mti.response.json`](examples/payment-status-by-mti.response.json)
- [`payment-reversal.response.json`](examples/payment-reversal.response.json)
