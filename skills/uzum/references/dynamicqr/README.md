# Uzum Dynamic QR (merchant prints a QR, payer scans it in the Uzum Bank app)

Hand-written notes. Generated tables: [`endpoints.md`](endpoints.md); schemas:
[`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_dynamicqr.yaml (en labels: `en_dynamicqr.yaml`)
- Fetched: 2026-11-03

## Host and auth

Base URL `https://mobile.apelsin.uz`. Same credentials and `Authorization` header as
[FastPay](../fastpay/README.md#authorization-header):
`<merchant_service_user_id>:<sha1_hex(timestamp + secret_key)>:<timestamp_ms>`.
Headers: `Authorization`, `Content-Type: application/json`, `Accept`.

## Operations (all `POST /api/dynamic-qr/merchant/payment/...`)

| Path | Request | Response |
|---|---|---|
| `create` | `amount` (tiyin), `order_id`, `service_id`, `details` (free object shown to payer) | `payment_link` (encode it into the QR), `error_code` |
| `status-by-order` | `order_id`, `service_id` | `payment_id`, `payment_status`, `error_code`, `client_phone_number`, `processingReferenceNumber`, `cardType` |
| `fiscal` | `payment_id`, `service_id`, `fiscal_url` | `payment_id`, `payment_status`, `error_code` |
| `reversal` | `payment_id`, `service_id` | `payment_status` `REVERSE_PENDING` or `REVERSED` |
| `cancel-order` | `order_id`, `service_id` | `payment_id`, `payment_status`, `error_code`, `error_message` |

## State machine (`payment_status`)

```
CREATED ──payer pays──> SUCCESS ──reversal──> REVERSE_PENDING ──> REVERSED
   │           └──> FAILED                     (PARTIAL_CANCELLED possible)
   └──cancel-order──> CANCELLED
HOLD: funds held, not yet final
```

No callbacks: poll `status-by-order` until a final status (`SUCCESS`, `FAILED`,
`CANCELLED`, `REVERSED`).

## Errors

HTTP 200 for business errors (spec also declares 401 for auth). `error_code`: `0` success, `400` missing required field, `401` auth
(format, inactive ids, hash, foreign `service_id`), `503` service not found / inactive.

`error_message` keys: `apelsin.pay.authorization.error`, `apelsin.pay.service.not.working`,
`apelsin.pay.fiscalization.service.not.working`, `apelsin.pay.unsupported.operation`,
`apelsin.pay.reverse.not.allowed`, `unsupported.fiscal.url`, `order.not.found`,
`order.id.duplicated`, `operation.not.found`, `external.service.unavailable`,
`operation.failed`, `operation.forbidden`, `operation.is.inProcess`.

## Gotchas

- Field naming is mixed: `client_phone_number` (snake) next to
  `processingReferenceNumber` and `cardType` (camel) in the same response.
- `reversal` can return `REVERSE_PENDING`; poll until `REVERSED`.
- Cancel unpaid orders (`cancel-order`) when the QR is abandoned so a late scan cannot pay.

## Examples

[`examples/`](examples/): create request/response, status-by-order response.
