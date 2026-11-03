# Uzum PaymentHub: errors

- Source: https://developer.uzumbank.uz/paymenthub/error-codes/
- Fetched: 2026-11-03

Two channels:

1. **BaaS error**: top-level JSON-RPC `error {code, message}`. The call did nothing (or its
   outcome is unknown for `-31615`). `message` is a stable technical key.
2. **Processing decline**: the call succeeded; the receipt in `result` has `state` `50` or
   `51` and a free-text `error`. The processing lists are not exhaustive and their wording
   can change, so drive logic from `state`, not from `error`.

## Generic JSON-RPC errors (any method)

| Code | `message` | Meaning |
|---|---|---|
| -32700 | `request.not.valid` | body is not a JSON-RPC request |
| -32600 | `invalid.request.msg`, `invalid.jsonrpc.object` | bad JSON-RPC structure |
| -32601 | `json.rpc.method.not.found` | unknown method |
| -32602 | `params.not.valid` | bad params (also the validation keys below) |
| -32603 | `internal.error`, `user.not.found`, `requisite.account.not.found` | internal error |
| -32504 | `json.rpc.method.permission.denied` | your login may not call this method |

## Parameter validation (`-32602`, key in `message`)

| `message` | Methods |
|---|---|
| `id.not.valid` | pay / confirm / check methods |
| `ext.id.not.valid` | `receipt.create.requisite`, `receipt.account.create.transfer` |
| `merchant.id.not.valid`, `merchant.fields.are.empty` | `receipt.create`, `merchant.info` |
| `amount.invalid` | create / pay methods |
| `pan.not.valid`, `token.not.valid`, `card.not.valid`, `token.or.pan.not.valid` | card and card-funded methods |
| `account.number.invalid`, `mfo.not.valid` | account and requisite methods |
| `sender.not.valid`, `sender.account.not.valid`, `sender.name.not.valid`, `sender.type.required` | requisite and account-to-card methods |
| `receiver.not.valid`, `receiver.name.not.valid` | requisite and account-to-card methods |
| `payment.details.not.valid`, `requisite.detail.not.valid` | requisite methods |
| `document.detail.not.valid`, `description.length.exceeded` | `receipt.account.create.transfer` |

## Domain errors

| Code | `message` | Meaning | Action |
|---|---|---|---|
| -31602 | `receipt.not.found`, `comparison.not.found`, `otp.operation.not.found`, `record.not.found` | object not found / not yours | fix id |
| -31603 | `category.not.found`, `category.disabled` | category | - |
| -31604 | `processing.not.available`, `uzcard.not.available`, `humo.not.available`, `abs.not.available`, `card.binder.not.available`, `supplier.not.available` | dependency down | retry later (check status first for pay/confirm) |
| -31605 | `service.not.found`, `service.not.available` | service missing or disabled | - |
| -31606 / -31607 | `amount.less.than.minimum` / `amount.greater.than.maximum` | service limits | - |
| -31608 | `card_not_found`, `card.not.active`, `card.is.not.binded`, `card.is.expired`, `card.is.coorporate`, `operation.forbidden.for.corporate.cards`, `unsupported.card.type` | card problem | ask for another card |
| -31609 | `operation.forbidden`; `account.not.found` (confirm.transfer) | forbidden by settings / state | - |
| -31610 | `requested.data.not.valid` | provider rejected customer data | show to user |
| -31611 | `account.not.found`, `data.not.found` | account | - |
| -31612 | `receipt.can.not.pay`, `otp.already.confirmed` | wrong receipt state | check status |
| -31613 | `ext.id.exist` | duplicate `ext_id` | look up by `ext_id`, do not recreate |
| -31614 | `bank.not.found` | no bank for PAN / MFO | - |
| -31615 | `operation.being.processing`, `comparison.not.finished.yet`, `account.not.available.try.again.later` | in progress / unknown | **poll** `receipt.check.id`; never re-create |
| -31616 | `operation_failed` | operation failed | - |
| -31617 / -31618 / -31622 | `otp.has.expired` / `incorrect.otp.code` / `incorrect.attempts.are.exceeded` | OTP (`cards.add.confirm`) | resend or restart |
| -31619 | `operation.limit.exceeded` | limit (account to card) | - |
| -31620 | `card_not_found` | card or token not found | - |
| -31621 | `insufficient.funds` | listed for an undocumented hold method | - |
| -31623 | `receiver.suspicious` | receiver flagged | do not retry |
| -31647 | `card.is.expired` | processing says expired | - |
| -31648 | `sms.info.not.active` | card has no SMS notifications (`cards.add`) | - |
| -31649 | `phone.number.not.match.with.attached` | `requester_phone` mismatch | - |
| -31650 | `daily.limit.used` | card daily limit | - |
| -31651 | `card.temporary.blocked` | card temporarily blocked | - |

## Processing decline strings (`result.error`, examples only)

The vendor lists what BaaS currently receives from HUMO, UzCard and Uzum Bank Visa. They are
diagnostic, not a contract. Common ones:

- HUMO: `Blocked card`, `Stolen card`, `Expired card`, `Suspected fraud`, `Lost card`,
  `Restriced card` (sic), `Allowable PIN tries exceeded`, `insufficient.funds`,
  `otp.attempts.exhausted`, `limit.passed`, `Service not available`.
- UzCard: `card.blocked`, `card.expired`, `card.not.found`, `card.insufficient.funds`,
  `Insufficient funds!`, `Daily limit used!`, `Limit passed!`, `Time out SV!`,
  `Transaction not found!`, `Operation is not possible with corporate cards!`,
  `transaction.not.permitted.by.law`, `card.process.with.another.operation`.
- Uzum Bank Visa (snake_case keys): `validation_error`, `payment_process_timeout`,
  `payment_not_found`, `error_3ds`, `expired_card`, `card_not_found`, `card_auth_failed`,
  `operation_fraud`, `operation_not_permitted`, `invalid_amount`, `amount_exceeds_limit`,
  `amount_is_insufficient`, `amount_exceeds_bank_limit`, `reversal_not_allowed`,
  `refund_not_allowed`, `payment_in_progress`, `invalid_card`.

Timeouts such as `Time out SV!` or `payment_process_timeout` mean "unknown", not "failed":
poll the receipt.
