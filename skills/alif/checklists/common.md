# Checklist: Alif transport, errors and webhooks (applies to every product)

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] Every call is `POST https://api.alifpay.uz/v2/<method>` with a JSON body.
- [ ] `Token` header (or `Store-Token` for branch auth) comes from secrets; sandbox and production tokens are kept apart.
- [ ] Amounts are integer tiyin everywhere (no floats, no UZS mix-up).
- [ ] No legacy methods or fields remain (`purchase`, `confirmChargeOTP`, `getPurchase`, `refundPurchase`, `pinfl`, `scoring`, `ref`, `charge`); if any do, follow [`../references/legacy-v1/README.md`](../references/legacy-v1/README.md).
- [ ] Phones are sent as `998NNNNNNNNN` (12 digits, no `+`); masked phones in responses are shown as they are and never parsed.

## Errors
- [ ] Every HTTP 200 body is checked for `error` before the result is read.
- [ ] The code branches on `error.code`, never on `message`.
- [ ] Non-200 statuses (auth, network) are handled separately from business errors.
- [ ] Before retrying a money-moving call, the state is read back (`getPayment` / `getHold` / `getInvoice`).
- [ ] On `1108`, a retry uses a **new** `id`.

## Identifiers
- [ ] Payment, hold and refund `id`s are client-generated UUIDs, persisted **before** the call.
- [ ] An `id` is reused only to read the state back, never for a new intent (`1105` duplicate).

## Webhooks
- [ ] `Signature` is verified as `base64(HMAC-SHA256(secret, raw body bytes))` with a constant-time compare.
- [ ] The signature is computed over the raw bytes, before JSON parsing.
- [ ] Bad signatures are rejected and logged; good ones get HTTP 200 fast, with the work done asynchronously.
- [ ] The handler is idempotent: repeated deliveries do not fulfil twice.
- [ ] The webhook endpoint is monitored: about an hour of failed deliveries **cancels and refunds** the payment.

## Sandbox and logging
- [ ] The base URL is configurable: `https://api-dev.alifpay.uz/v2` with the sandbox token, `https://api.alifpay.uz/v2` with the production token.
- [ ] Tests cover the sandbox cards and scenarios in [`references/sandbox/`](../references/sandbox/README.md). Test cards, test OTP and test PINFL stay in tests and fixtures, not production paths; `_` methods are called only in tests.
- [ ] Logs never contain the token, PAN, expiry, OTP, PINFL or webhook secret.
