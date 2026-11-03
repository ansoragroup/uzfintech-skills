# Checklist: Uzum FastPay and Dynamic QR

Contracts: [`../references/fastpay/README.md`](../references/fastpay/README.md),
[`../references/dynamicqr/README.md`](../references/dynamicqr/README.md).

## Auth (both)
- [ ] `Authorization: <merchant_service_user_id>:<sha1_hex(timestamp + secret_key)>:<timestamp>`.
- [ ] `timestamp` in milliseconds; the same value in hash and header; generated per request.
- [ ] Lowercase hex SHA-1 (40 chars).
- [ ] Clock synced (NTP); requests older than 50 s fail with `403`.
- [ ] `secret_key` from secrets; never logged.

## Responses (both)
- [ ] `error_code` checked on every HTTP 200 body; HTTP 401 also handled.
- [ ] `error_message` keys mapped (`operation.is.inProcess` -> poll status).

## FastPay
- [ ] `order_id` unique per sale and persisted before the call; `transaction_id` UUID per attempt.
- [ ] `amount` in tiyin; `otp_data` passed as scanned, never logged.
- [ ] `DUPLICATED` resolved with `status` (earlier sale may be paid), not treated as failure.
- [ ] Timeout / in-process -> poll `status`; no new `order_id` for the same sale.
- [ ] `fiscal` called after fiscalization with an unescaped URL.
- [ ] Reversal only when enabled; full amount; result checked.
- [ ] Safe Mode (`416`) message shown to the cashier.

## Dynamic QR
- [ ] `create` -> encode `payment_link` into the QR.
- [ ] Poll `status-by-order` until `SUCCESS` / `FAILED` / `CANCELLED` / `REVERSED`; `HOLD` is not final.
- [ ] Abandoned QR -> `cancel-order`.
- [ ] `reversal` handles `REVERSE_PENDING`.
- [ ] Mixed snake / camel field names parsed correctly.
