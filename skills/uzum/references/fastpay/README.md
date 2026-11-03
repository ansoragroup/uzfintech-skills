# Uzum FastPay (payer shows a QR in the Uzum Bank app, cashier scans it)

Hand-written notes. Generated tables: [`endpoints.md`](endpoints.md); schemas:
[`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_fastpay.yaml (en labels: `en_fastpay.yaml`)
- Fetched: 2026-11-03
- Direction: you (POS / cash register backend) call Uzum. No callbacks.

## Host and credentials

Base URL: `https://mobile.apelsin.uz` (same host for all FastPay and DynamicQR calls).

Credentials issued by Uzum: `merchant_id`, `secret_key`, `service_id` (branch),
`merchant_service_user_id` (cashier / POS).

## Authorization header

```
Authorization: <merchant_service_user_id>:<sha1_hex(timestamp + secret_key)>:<timestamp>
```

- `timestamp`: Unix time in **milliseconds**, per the docs in the UTC+5 regional
  clock. Use the same value in the hash and the header.
- Hash: SHA-1 over the string concatenation `timestamp + secret_key`, lowercase hex, 40 chars.
- Requests older than **50 s** are rejected (`error_code` 403). Sync the POS clock.
- Doc inconsistency: one regex says `^\d*:(\d{40}):\d*$` (digits only), DynamicQR says
  `([\da-f]{40})`. SHA-1 hex output contains `a-f`, so send the lowercase hex digest and
  treat the digits-only regex as a documentation error.

## Operations

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/apelsin-pay/merchant/v2/payment` | charge using scanned QR data |
| POST | `/api/apelsin-pay/merchant/payment/fiscal` | attach fiscal receipt URL |
| PUT | `/api/apelsin-pay/merchant/v2/payment/reversal/{orderId}` | full reversal |
| POST | `/api/apelsin-pay/merchant/payment/status` | payment status |

### payment

Request: `amount` (tiyin), `cashbox_code` (your cash register id), `otp_data` (scanned QR
string, at least 40 chars), `order_id` (unique per sale in your system), `transaction_id`
(your UUID), `service_id`.

Response: `payment_id`, `payment_status` `SUCCESS` | `FAILED` | `DUPLICATED`, `error_code`,
`client_phone_number`, `card_type` (`1` corporate, `2` private),
`processing_reference_number` (RRN), `operation_time` (`YYYY-MM-DD HH:mm:ss.SSS`, only with
`DUPLICATED`: time of the earlier payment for this `order_id`).

### fiscal / status / reversal

- fiscal: `{payment_id, service_id, fiscal_url}`; unescape the URL if it contains
  encoded characters.
- status: `{payment_id, service_id}` -> `payment_status` `SUCCESS` | `FAILED` | `HOLD` |
  `REVERSED` | `PARTIAL_CANCELLED`.
- reversal: `PUT .../reversal/{orderId}` with `{service_id, payment_id}` -> `REVERSED`.
  Full amount only; must be enabled for your partner (`apelsin.pay.reverse.not.allowed`).

## Errors

The docs say every method answers HTTP 200, even on errors; the spec still declares an
HTTP 401 response for auth failures, so handle both. Check `error_code` (int) and
`error_message` (string key).

| error_code | Meaning |
|---|---|
| 0 | success |
| 400 | validation: short `otp_data`, bad amount, blocked service, inactive card, insufficient funds, bad `payment_id` |
| 401 | bad Authorization format, hash mismatch, inactive merchant/service/user, service not owned by partner |
| 403 | more than 50 s between timestamp and processing |
| 404 | operation not found for `payment_id` |
| 416 | payer card in Safe Mode (new users must make 3 in-app payments first) |
| 503 | service not found or inactive |

| error_message | Meaning |
|---|---|
| `null` | no error |
| `apelsin.pay.authorization.error` | auth failed |
| `apelsin.pay.safe.mode.on` | Safe Mode |
| `apelsin.pay.service.not.working` | service temporarily unavailable |
| `apelsin.pay.wrong.prefix.otp.data` | QR data has wrong prefix / length |
| `apelsin.pay.unsupported.operation` | operation not supported |
| `apelsin.pay.reverse.not.allowed` | reversal disabled for partner |
| `unsupported.fiscal.url` | bad fiscal URL |
| `order.id.duplicated` | `order_id` already paid |
| `transaction.duplicated` | `transaction_id` already used |
| `apelsin.pay.user.otp.data.expired` | QR expired (often wrong phone clock) |
| `device.not.registered` | payer device not registered |
| `operation.not.found` | operation not found or service inactive |
| `qr.duplicated` | QR already used |
| `receipt.qr.only.yours` | QR not recognized |
| `user.card.not.found` / `user.does.not.exist` | payer card / user not found |
| `external.service.unavailable` | downstream unavailable |
| `limit.was.set` | issuer / processing limit |
| `operation.failed` | declined |
| `operation.forbidden` | card type not supported or service blocked |
| `operation.is.inProcess` | processing has not answered yet: poll `status` |

## Gotchas

- `DUPLICATED` is not a failure of the earlier sale; look it up with `status`.
- On timeout or `operation.is.inProcess`, poll `status`; do not re-charge with a new
  `order_id`.
- `amount` is tiyin.
- Never log `secret_key` or the raw `otp_data`.

## Examples

[`examples/`](examples/): payment request/response, status, reversal, error.
