# Paynet Acquiring API: transport, auth, envelope, errors, statuses

Hand-written notes. They apply to every Paynet operation in this skill.

- Source: https://pay-docs.paynet.uz/general-principles, https://pay-docs.paynet.uz/reference-materials
  and https://pay-docs.paynet.uz/transaction-statuses. The site is a single-page app with
  Russian, Uzbek and English texts.
- Fetched: 2026-11-03
- Direction: **you call Paynet**, host to host. The public docs describe no callback or
  webhook.

## Transport

| Item | Value |
|---|---|
| Base URL | **not published**. Paynet issues it with the credentials. Paths start with `/api/v1/payment-service/` |
| Protocol | HTTPS only. The docs list TLS 1.0 / 1.1 / 1.2, so pin at least TLS 1.2 on your side |
| Body | JSON (`Content-Type: application/json`) for `authorize` and `confirm` |
| Auth | `Authorization: Basic base64(<service_id>:<secret_key>)` on **every** request |
| Amounts | integer **tiyin** (1 UZS = 100 tiyin) |
| Card expiry | `YYMM`, 4 digits |
| Ids | strings; `transactionId` is Paynet's id, `paymentId` is the Humo / Uzcard id |

`service_id` and `secret_key` identify one payment instrument and are issued when it is
registered with Paynet. Both are secrets: keep them server-side and out of logs.

## Response envelope

Every response uses the same wrapper:

| Field | Type | Meaning |
|---|---|---|
| `status` | int | `0` means success. Anything else is a failure; the examples show `400` and the numeric error code (`9005`) |
| `message` | string | short text, for logs only |
| `data` | object or `null` | the result on success |
| `error` | object | present on failure |

`error` object:

| Field | Type | Meaning |
|---|---|---|
| `code` | string | the error constant, e.g. `INSUFFICIENT_FUNDS`. **Branch on this** |
| `message` | string | human-readable detail |
| `provider` | string or `null` | external system that answered, `HUMO` or `UZCARD` |
| `providerCode` | string or `null` | that system's own code |
| `providerMessage` | string or `null` | that system's own text |
| `retryable` | bool | per the docs: whether you should check the transaction status |
| `details` | object or `null` | free-form extra data (e.g. balance figures) |

Check `status == 0` first. The HTTP status code is not documented; do not rely on it.

## Error codes

Several constants share one numeric code, so the numeric code alone is ambiguous. Use the
string `error.code`.

| Code | `error.code` | Meaning | Action |
|---|---|---|---|
| 1000 | `GENERIC_BUSINESS_ERROR` | declined by the issuer or the payment system, reason not given | show a generic decline |
| 1001 | `PAYMENT_FAILED` | attempt made, nothing debited | final failure |
| 1002 | `SMS_DELIVERY_FAILED` | the OTP SMS was not delivered | let the payer retry `authorize` |
| 1003 | `INSUFFICIENT_FUNDS` | issuer decline: not enough funds | final failure |
| 1004 | `CARD_BLOCKED` | the issuer blocked the card | final failure |
| 1005 | `OTP_SEND_FAILED` | the OTP could not be sent | retry `authorize` later |
| 1006 | `CARD_PHONE_NOT_AVAILABLE` | no phone is linked to the card, so no OTP | ask for another card |
| 1007 | `OTP_REQUIRED`, `OTP_NOT_FOUND`, `OTP_ALREADY_USED`, `OTP_INVALID` | OTP missing, unmatched, reused or wrong | ask for the code again |
| 1008 | `OTP_EXPIRED` | the OTP lifetime (`ttlSeconds`) passed | start a new `authorize` |
| 1009 | `OTP_ATTEMPTS_EXCEEDED` | too many wrong codes | start a new `authorize` |
| 1009 | `TRANSACTION_ALREADY_FINISHED` | the transaction is final and cannot change | read the status |
| 1010 | `TRANSACTION_EXPIRED` | the time to finish the transaction ran out | start a new `authorize` |
| 1011 | `EXTERNAL_OTP_VERIFICATION_FAILED` | OTP check failed upstream; nothing debited | retry the confirmation or re-enter the card |
| 9004 | `CARD_BIN_NOT_FOUND` | the BIN is unknown to the acquirer | ask for another card |
| 9005 | `TRANSACTION_NOT_FOUND` | no transaction for that id | check the id you sent |
| 9006 | `CARD_NOT_FOUND` | the card cannot be matched to the transaction | read the status |
| 9007 | `UNSUPPORTED_CARD_TYPE` | the card type is not accepted here | ask for a Humo or Uzcard card |
| -10012 | `UNKNOWN_TRANSACTION_STATE` | outcome unknown: neither success nor failure | **must** call `status` until final |

Treat any unknown `error.code` like `UNKNOWN_TRANSACTION_STATE` on money-moving calls:
read the status before telling the payer anything.

## Transaction statuses

`status` returns one of these in `data.status`:

| Status | Final? | Meaning |
|---|---|---|
| `CREATED` | no | created, waiting for confirmation |
| `PENDING_CONFIRM` | no | waiting for the OTP confirmation |
| `UNKNOWN` | no | Paynet cannot tell yet; keep polling `status` |
| `SUCCESS` | yes | paid |
| `FAILED` | yes | not paid (or debited and returned, depending on the bank) |
| `CANCELLED` | yes | not completed, or reversed; any debit is returned |
| `RETURNED` | yes | was `SUCCESS`, then the money was returned |
| `CANCEL_PENDING` | no | a cancellation is in progress |
| `RETURN_PENDING` | no | a refund of a `SUCCESS` payment is in progress |

Only `SUCCESS` means paid. Treat the `*_PENDING` and `UNKNOWN` states as "not yet known".

## Not covered by the public docs

Ask Paynet at onboarding for these:
- the base URL and any sandbox host;
- test cards and test OTPs;
- callbacks or webhooks;
- a hosted payment page;
- how refunds differ from `reverse`;
- the shape of `data.attributes` (OFD data);
- the exact form of the `status` and `reverse` paths (see the acquiring README).
