# Paynet: money lifecycle, deadlines and reversals

Read this when you build or review a Paynet Humo / Uzcard card payment or its cancellation.
It lists the deadlines, reversal limits, retry rules and fiscal gaps to raise before the user
hits them.

- Source: [common](../common/README.md), [acquiring](../acquiring/README.md),
  [sandbox](../sandbox/README.md), [checklist](../../checklists/acquiring.md); vendor docs
  https://pay-docs.paynet.uz/acquiring-humo-uzcard,
  https://pay-docs.paynet.uz/online-payment-confirmation,
  https://pay-docs.paynet.uz/payment-status-check,
  https://pay-docs.paynet.uz/payment-cancellation,
  https://pay-docs.paynet.uz/general-principles,
  https://pay-docs.paynet.uz/reference-materials,
  https://pay-docs.paynet.uz/transaction-statuses
- Fetched: 2026-11-03

## Warn without being asked

1. **`paynet.reverse-1-month`** When the user adds cancellation, returns or a refund button:
   `reverse` works only within **1 month** of the payment, and after that it is impossible.
   It has no amount field, so it cancels the whole payment. No refund method and no
   after-deadline error code are published. [acquiring](../acquiring/README.md#flow-and-state-machine)
2. **`paynet.unknown-state-poll`** When `confirm` times out, returns `-10012`
   `UNKNOWN_TRANSACTION_STATE`, or returns an `error.code` you do not know: do not show a
   failure and do not repeat `confirm`. Poll `status` until it reaches a final state.
   [common](../common/README.md#error-codes)
3. **`paynet.retryable-means-status`** When code sees `retryable: true`: it means "read
   `status`", not "send the request again". A blind repeat of `confirm` can act twice on one
   transaction. [common](../common/README.md#response-envelope)
4. **`paynet.no-webhooks-poll`** When the user expects Paynet to notify them: no callback or
   webhook is published. Your server learns every outcome, including later `CANCELLED` or
   `RETURNED`, only by calling `status`. [common](../common/README.md#not-covered-by-the-public-docs)
5. **`paynet.success-only-paid`** When code marks an order paid: only `data.status`
   `SUCCESS` counts. A top-level `status` of `0` only means the call worked. `FAILED` can mean
   debited and returned, depending on the bank. [common](../common/README.md#transaction-statuses)
6. **`paynet.otp-ttl-from-response`** When you build the OTP screen: run the countdown from
   `ttlSeconds` in the `authorize` response and never hardcode it. After expiry, `confirm`
   returns `1008` `OTP_EXPIRED`. [acquiring](../acquiring/README.md#fields)
7. **`paynet.new-orderid-after-expiry`** When the payer retries after `1008` `OTP_EXPIRED`,
   `1009` `OTP_ATTEMPTS_EXCEEDED` or `1010` `TRANSACTION_EXPIRED`: start a new `authorize`.
   `orderId` must be unique per authorize, so use an attempt id that maps back to the order.
   [acquiring](../acquiring/README.md#gotchas)
8. **`paynet.1009-two-meanings`** When code branches on the number: `1009` is both
   `OTP_ATTEMPTS_EXCEEDED` (new authorize) and `TRANSACTION_ALREADY_FINISHED` (read
   `status`). `1007` covers four OTP constants. Branch on the string `error.code`.
   [common](../common/README.md#error-codes)
9. **`paynet.reverse-lock`** When you add a cancel button: lock it locally so a second click
   cannot send a second `reverse` while one is pending. `CANCEL_PENDING` is not final, so poll
   `status`. [checklist](../../checklists/acquiring.md#status-and-reverse)
10. **`paynet.fiscal-owner-unknown`** When the task mentions receipts, OFD or soliq: the docs do
    not say who issues the fiscal receipt for a sale or a reversal. `confirm` returns
    `attributes` ("extra data such as OFD", shape not published). Store it raw and ask Paynet
    before go-live. [acquiring](../acquiring/README.md#fields)
11. **`paynet.reverse-path-configurable`** When you code `status` or `reverse`: the public page
    shows inconsistent paths and no HTTP verb for `reverse` (expect `POST`). Keep both paths in
    configuration. [acquiring](../acquiring/README.md#path-note-status-and-reverse)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| OTP entry (`confirm`) | `ttlSeconds` from the `authorize` response | `1008` `OTP_EXPIRED`: new `authorize` | [acquiring](../acquiring/README.md#flow-and-state-machine) |
| Wrong OTP attempts | number not published | `1009` `OTP_ATTEMPTS_EXCEEDED`: new `authorize` | [common](../common/README.md#error-codes) |
| Time to finish a transaction | not published | `1010` `TRANSACTION_EXPIRED`: new `authorize` | [common](../common/README.md#error-codes) |
| `reverse` | up to 1 month after the payment | cancellation impossible; error code not documented | [acquiring](../acquiring/README.md#flow-and-state-machine), https://pay-docs.paynet.uz/payment-cancellation |
| OTP SMS delivery | none stated | `1002` `SMS_DELIVERY_FAILED` / `1005` `OTP_SEND_FAILED`: payer retries `authorize` | [common](../common/README.md#error-codes) |
| `UNKNOWN`, `CANCEL_PENDING`, `RETURN_PENDING` | how long they last is not published | keep polling `status`; do not fulfil or refund twice | [common](../common/README.md#transaction-statuses) |
| `amount` | integer tiyin; min and max not published | not documented | [acquiring](../acquiring/README.md#fields) |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| `SUCCESS` payment under 1 month old | you | `reverse?value=<transactionId or paymentId>` -> `data.status` `CANCELLED` | no (no amount field) | once; lock it locally | not documented | [acquiring](../acquiring/README.md#operations) |
| `SUCCESS` payment over 1 month old | - | none published; refund by other means | - | - | not documented | [sandbox](../sandbox/README.md#mock-scenarios-built-from-the-samples) |
| Money returned after `SUCCESS` (`RETURN_PENDING` -> `RETURNED`) | not documented | no method published; the state appears only in `status` | not documented | not documented | not documented | [common](../common/README.md#transaction-statuses) |
| OTP step abandoned or expired (`CREATED`, `PENDING_CONFIRM`) | nobody calls; the OTP or transaction expires | no call; `confirm` fails with `1008` / `1010` | - | - | none (nothing charged) | [common](../common/README.md#error-codes) |
| `FAILED` after a debit | the bank | automatic return, "depending on the bank" | not documented | - | not documented | [common](../common/README.md#transaction-statuses) |
| Sandbox | - | no test host or test data is published; whether `reverse` works in test mode is an open question | - | - | - | [sandbox](../sandbox/README.md#open-questions-for-paynet) |

`CANCELLED` covers both "never completed" and "reversed", and any debit is returned. A
reversed order must be refunded in your own books too.

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Webhooks / callbacks | none published | - | - | poll `status` instead | [common](../common/README.md#not-covered-by-the-public-docs) |
| `authorize` (you call) | you retry | - | `orderId`, unique per authorize | what a repeated `orderId` returns is not documented; after `1002`, `1005`, `1008`, `1009` `OTP_ATTEMPTS_EXCEEDED` or `1010`, use a new `orderId` | [acquiring](../acquiring/README.md#gotchas) |
| `confirm` (you call) | never repeat blindly | `ttlSeconds` | `transactionId` | `1007`: ask for the code again, same `transactionId`; timeout, `-10012` or `retryable`: read `status`; `TRANSACTION_ALREADY_FINISHED`: read `status` | [acquiring](../acquiring/README.md#flow-and-state-machine) |
| `status` (you call) | safe to repeat (read only) | - | `transactionId` or `paymentId` | polling interval and rate limit not published | [acquiring](../acquiring/README.md#operations) |
| `reverse` (you call) | you retry | within 1 month of the payment | `transactionId` or `paymentId` | what a second `reverse` returns is not documented; read `status` first and keep a local lock | [checklist](../../checklists/acquiring.md#status-and-reverse) |

## Fiscal receipts

- **Owner:** the public docs do not say whether Paynet or the merchant registers the OFD
  (soliq) receipt, for the sale or for a `reverse`.
- **Data:** `confirm`, `status` and `reverse` return `data.attributes`, which the docs
  describe only as extra data such as OFD. Its shape is not published. Store it unparsed with
  the payment so you can use it once Paynet explains it.
- **Fields, sum rules, timing:** none are published. No receipt items, IKPU codes or VAT
  fields exist in `authorize`.
- Until Paynet confirms otherwise, do not tell the user that receipts are handled, and do not
  build a duplicate receipt flow. Raise it as an onboarding question.
  [common](../common/README.md#not-covered-by-the-public-docs)

## Not documented — ask the provider

- The error code `reverse` returns after the 1-month window, and how to refund then.
- Whether a partial refund exists, and how `RETURN_PENDING` / `RETURNED` are started.
- Who issues the fiscal receipt for a sale and for a `reverse`, and the shape of
  `data.attributes`.
- How long a transaction lives before `1010` `TRANSACTION_EXPIRED`, and how many wrong OTPs
  are allowed before `1009` `OTP_ATTEMPTS_EXCEEDED`.
- Whether `reverse` applies to `CREATED` / `PENDING_CONFIRM` transactions.
- What a repeated `authorize` with the same `orderId`, or a second `reverse`, returns.
- How long `UNKNOWN`, `CANCEL_PENDING` and `RETURN_PENDING` can last, and the allowed
  `status` polling rate.
- Any callback or webhook, the base URL, a sandbox host and test cards.
- The HTTP verb and exact path of `reverse` and `status`; the amount limits.
