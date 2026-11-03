# Paynet Humo / Uzcard acquiring (card number + SMS OTP)

Hand-written notes. Schemas are in [`schemas/`](schemas/) and bodies in
[`examples/`](examples/). Transport, auth, the envelope and the error table are in
[`../common/README.md`](../common/README.md).

- Source: https://pay-docs.paynet.uz/acquiring-humo-uzcard,
  https://pay-docs.paynet.uz/online-payment-confirmation,
  https://pay-docs.paynet.uz/payment-status-check,
  https://pay-docs.paynet.uz/payment-cancellation
- Fetched: 2026-11-03
- Direction: **you call Paynet.** Your server collects the card number and expiry, Paynet
  sends the OTP to the cardholder's phone, and your server submits the OTP.
- Cards: Humo and Uzcard only.

## Operations

All paths are relative to the base URL Paynet issues, and all need the Basic header.

| Op | Request | Purpose |
|---|---|---|
| authorize | `POST /api/v1/payment-service/payment/authorize` + JSON | create the payment and send the OTP |
| confirm | `POST /api/v1/payment-service/payment/confirm` + JSON | submit the OTP and debit the card |
| status | `GET .../payment/status?value=<id>` (see the path note below) | read the current state |
| reverse | `.../payment/reverse?value=<id>` (verb and path: see below) | cancel a payment, up to 1 month old |

`<id>` for status and reverse is either `transactionId` (Paynet) or `paymentId` (Humo /
Uzcard).

### Path note (status and reverse)

The public page is inconsistent about these paths, so confirm them with Paynet before
coding:
- The method headings show `/api/v1/payment-service/payment/status/value=id` and
  `/api/v1/payment-service/payment/reverse/value=id`. That looks like a typo for a query
  string.
- The `-10012` error note says to call
  `GET /api/v1/payment-service/merchant/payment/status?value={transactionId}`, which has an
  extra `/merchant/` segment.
- The page shows no HTTP verb for reverse. It changes state, so expect `POST`.

Make the paths configurable.

## Flow and state machine

```
authorize ──> CREATED / PENDING_CONFIRM ──confirm(otp)──> SUCCESS ──reverse──> CANCELLED
    │                    │                     │
    │                    │                     ├─ OTP wrong (1007): ask again, same transactionId
    │                    │                     ├─ OTP expired / attempts out (1008, 1009, 1010): new authorize
    │                    │                     └─ -10012 / UNKNOWN: poll status until final
    └─ card / phone errors (1004, 1006, 9004, 9007): no transaction to confirm
```

1. **authorize**: send `pan`, `expiry`, `amount`, `orderId`, `currency` and `merchantId`.
   Persist `orderId` and the returned `transactionId`. Show the payer `phoneMask`, and run
   a countdown from `ttlSeconds`.
2. **confirm**: send `transactionId` and the `otp` the payer received by SMS. On success, store `paymentId`
   and treat the order as paid.
3. **status**: call it after any timeout, network error, `-10012` or `retryable: true`.
   Only `data.status == "SUCCESS"` means paid.
4. **reverse**: cancels within **1 month** of the payment. After that the cancellation is
   impossible. A successful response carries `data.status` (e.g. `CANCELLED`).

## Fields

authorize request. The page does not say which fields are optional, so send all of them:

| Field | Type | Rule |
|---|---|---|
| `pan` | string | 16 digits |
| `expiry` | string | `YYMM` |
| `amount` | integer | tiyin |
| `orderId` | string | your order / account id; **unique per request** |
| `comment` | string | free text |
| `currency` | string | ISO letters, e.g. `UZS` |
| `merchantId` | string | your platform id at Paynet |

authorize `data`: `transactionId`, `orderId`, `ttlSeconds` (OTP lifetime), `phoneMask`.

confirm request: `transactionId`, `otp`. confirm `data`: `transactionId`, `orderId`,
`paymentId`, `attributes` (extra data such as OFD; shape not published).

status / reverse `data`: `status`, `transactionId`, `orderId`, `paymentId`, `attributes`.

## Gotchas

1. The public request example writes the amount as `150 000` (with a space). That is not
   valid JSON. Send a bare integer in tiyin.
2. Numeric error codes are shared (`1007` has four constants, `1009` has two). Branch on
   `error.code`.
3. Error responses put a non-zero number in the top-level `status`. On `status` and
   `reverse` responses, `data.status` holds a **string** transaction state. Do not mix them up.
4. `orderId` must be unique per authorize. A retry after an expired OTP needs a new
   `authorize`, so plan an attempt suffix or a separate attempt id that maps back to the
   order.
5. The docs list TLS 1.0 and 1.1 as allowed. Do not lower your client's minimum TLS version
   to match.
6. Collecting a raw PAN and expiry puts your server in PCI DSS scope. Never log or store
   them, and drop them right after `authorize`.
7. `retryable` means "check the status", not "repeat the request". Never repeat a confirm
   blindly.
8. The vendor samples use placeholder-looking ids (`TXN-...`, `ORD-...`). Do not validate
   id formats; treat them as opaque strings.

## Examples

Bodies only. The Basic header is described in common.

- [`authorize.request.json`](examples/authorize.request.json) /
  [`authorize.response.json`](examples/authorize.response.json)
- [`confirm.request.json`](examples/confirm.request.json) /
  [`confirm.response.json`](examples/confirm.response.json)
- [`status.response.json`](examples/status.response.json) (request: `?value=<transactionId>`)
- [`reverse.response.json`](examples/reverse.response.json)
- [`error.response.json`](examples/error.response.json) (wrong OTP)
- [`unknown-state.response.json`](examples/unknown-state.response.json) (`-10012`: poll status)
