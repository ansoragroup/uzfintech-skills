# Checklist: Paynet Humo / Uzcard acquiring

Contracts: [`../references/common/README.md`](../references/common/README.md) and
[`../references/acquiring/README.md`](../references/acquiring/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport and secrets
- [ ] Every call goes over HTTPS with a minimum of TLS 1.2. The base URL and the `status` / `reverse` paths are configuration, not literals.
- [ ] `Authorization: Basic base64(service_id:secret_key)` is built from secrets on every request. Test and production credentials are kept apart.
- [ ] Logs never contain the Basic header, `secret_key`, PAN, expiry or OTP.

## Envelope and errors
- [ ] The top-level `status` is checked for `0` before `data` is read. `data` may be `null`.
- [ ] The code branches on the string `error.code`, never on the numeric code or on `message`. Shared numbers (`1007`, `1009`) are handled per constant.
- [ ] `-10012` / `UNKNOWN_TRANSACTION_STATE`, `retryable: true`, timeouts and unknown codes all lead to `status` polling, not to a repeated `confirm`.
- [ ] The top-level numeric `status` is never confused with `data.status`, which is a string state.

## authorize
- [ ] `amount` is an integer in tiyin; no floats and no UZS/tiyin mix-up.
- [ ] `expiry` is sent as `YYMM` and `pan` as 16 digits. Both are dropped from memory right after the call and never stored.
- [ ] `orderId` is unique per authorize call. A new attempt for the same order gets a new value that maps back to the order.
- [ ] `transactionId` is persisted with the order before the OTP screen is shown.
- [ ] `1006` (no phone on the card), `9004` and `9007` (card not accepted) ask the payer for another card.

## confirm
- [ ] The OTP form uses `ttlSeconds` and shows `phoneMask`.
- [ ] `OTP_INVALID` / `OTP_REQUIRED` / `OTP_NOT_FOUND` let the payer retry with the same `transactionId`. `OTP_EXPIRED`, `OTP_ATTEMPTS_EXCEEDED` and `TRANSACTION_EXPIRED` start a new authorize.
- [ ] The order is marked paid only after `confirm` succeeds, or after `status` returns `SUCCESS`. `paymentId` is stored.

## status and reverse
- [ ] `status` polling stops on a final state (`SUCCESS`, `FAILED`, `CANCELLED`, `RETURNED`) and backs off. `UNKNOWN`, `CREATED`, `PENDING_CONFIRM` and `*_PENDING` keep polling, with an upper bound and an alert.
- [ ] `reverse` is offered only for payments younger than 1 month, and the result is read from `data.status`.
- [ ] Reversals are idempotent locally: a second click does not send a second reverse while one is pending.
