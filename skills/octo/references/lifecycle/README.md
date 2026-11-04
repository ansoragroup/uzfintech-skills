# Octo: money lifecycle, deadlines and reversals

Read this when building or reviewing an Octo integration, and raise these traps before
they cost money: the optional `test` flag, two-stage holds that cancel themselves,
callbacks that keep coming or cancel a token, notifications that are not signed with
your secret, refund limits and fiscal items that must be registered first.

- Source: https://help.octo.uz/payment-via-web/methods/prepare-payment.html (`test`,
  `ttl`), https://help.octo.uz/payment-via-web/one-stage.html (OTP limit),
  https://help.octo.uz/payment-via-web/two-stage.html (hold, capture callback),
  https://help.octo.uz/payment-via-web/methods/set-accept.html,
  https://help.octo.uz/payment-via-web/methods/callback.html,
  https://help.octo.uz/cancel.html (hold windows), https://help.octo.uz/check-status.html,
  https://help.octo.uz/notifications.html, https://help.octo.uz/refunds.html,
  https://help.octo.uz/tokenization.html, https://help.octo.uz/otp-resend.html,
  https://help.octo.uz/fiscal-data.html (Russian pages), plus the references linked in
  each row
- Fetched: 2026-11-04

## Warn without being asked

1. **`octo.test-flag-real-money`**: when creating payments in any non-production
   environment → send `test: true` explicitly from configuration. The flag is optional,
   there is no sandbox host, and a missing flag creates a **real** payment on
   `secure.octo.uz`. [common](../common/README.md#the-test-flag)
2. **`octo.hold-auto-cancel`**: when using two-stage payments (`auto_capture: false`) →
   call `set_accept` before the hold expires, or Octo cancels it and the payer gets the
   money back. The two-stage pages say 30 minutes; the cancel page says up to 30 days for
   Humo and Uzcard and up to 7 days for Visa and Mastercard, set in the cabinet. Plan for
   30 minutes until Octo confirms your shop's setting.
   [payment-page](../payment-page/README.md#two-stage-specifics)
3. **`octo.capture-callback-answer`**: when handling the amount-confirmation callback →
   answer `{accept_status, final_amount}` with `capture` (or `waiting_user_action` to stop
   the resends and decide later with `set_accept`). Any other answer makes Octo send it
   again. [payment-page](../payment-page/README.md#two-stage-specifics)
4. **`octo.notify-verify-status`**: when handling `notify_url` → verify `signature`
   (`sha1` over `unique_key`, `octo_payment_UUID`, `status`, upper-case hex) with
   `scripts/sign.py octo.notify`, then re-read the status with the three-field
   `prepare_payment` call before you ship. Octo says the notification is not signed with
   your secret. [common](../common/README.md#notifications-notify_url)
5. **`octo.cancel-only-holds`**: when cancelling a payment → `set_accept` with `cancel`
   works only on a hold (`waiting_for_capture`). A `succeeded` payment can only be
   returned with `/refund`. [refunds](../refunds/README.md#limits)
6. **`octo.refund-limits`**: when adding refunds → only `succeeded` payments; each refund
   at least 1 USD or the UZS equivalent and at most 10 mln UZS; the total may not exceed
   the payment. Split large refunds into several calls, each with a new `shop_refund_id`;
   `error: 22` means the amount broke a limit. [refunds](../refunds/README.md#limits)
7. **`octo.unique-shop-ids`**: when generating `shop_transaction_id` or `shop_refund_id` →
   make it unique per attempt and store it before the call. It is your only key for the
   status check after a lost reply. [payment-page](../payment-page/README.md#gotchas)
8. **`octo.ttl-minutes`**: when setting `ttl` → it is the payment lifetime in **minutes**
   from creation; after it the payment can no longer be paid, so create a new one. The
   default is not printed (the samples send `15`).
   [payment-page](../payment-page/README.md#methods)
9. **`octo.otp-three-tries`**: when building the Uzcard / Humo OTP step on your page →
   three wrong codes cancel the payment and a new one must be created; `check_pan`
   resends the code (`error: 17` at the resend limit). Show the attempts left.
   [partner-page](../partner-page/README.md#otp-rules)
10. **`octo.bind-callback-ack`**: when handling `bind_notify_url` → store the token, then
    answer HTTP `200`. Octo retries a failed delivery up to three times and then
    **cancels the token**. The token arrives only in this callback.
    [cards](../cards/README.md#gotchas)
11. **`octo.fiscal-registered-items`**: when sending `basket` → every item (`spic`,
    `package_code`, `nds`, `inn` or `pinfl`) must already be registered with Octo through
    your bank manager, or `prepare_payment` fails with `error: 403`. Send `user_data` with
    a phone or e-mail for the receipt. [fiscal](../fiscal/README.md#basket-item)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Unpaid payment | `ttl` minutes from creation; default not printed | cannot be paid; create a new payment | https://help.octo.uz/payment-via-web/methods/prepare-payment.html |
| Two-stage hold (two-stage pages) | 30 minutes | Octo cancels the hold; funds return to the card | https://help.octo.uz/payment-via-web/two-stage.html |
| Two-stage hold (cancel page) | up to 30 days Humo / Uzcard (raise in the cabinet); up to 7 days Visa / Mastercard (lower only) | same | https://help.octo.uz/cancel.html |
| Uzcard / Humo OTP | `secondsLeft` from `verificationInfo`; `120` after a resend | `secondsLeft: 0`; resend with `check_pan` | [partner-page](../partner-page/README.md#otp-rules) |
| Wrong OTP entries | 3 | payment cancelled | https://help.octo.uz/payment-via-web/one-stage.html |
| OTP resends | limit not printed | `error: 17` | https://help.octo.uz/otp-resend.html |
| Bind callback delivery | 1 + up to 3 retries | token cancelled | https://help.octo.uz/tokenization.html |
| Capture callback | resent until your answer carries `capture` or `waiting_user_action` | keeps coming; the hold still expires | https://help.octo.uz/payment-via-web/two-stage.html |
| Refund amount | at least 1 USD equivalent, at most 10 mln UZS per call, total up to the payment | `error: 22` | https://help.octo.uz/refunds.html |
| Refund after payment | not documented | | https://help.octo.uz/refunds.html |
| Fiscal receipt data | not documented | | https://help.octo.uz/fiscal-data.html |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| `created` payment never paid | `ttl` | none; it expires | n/a | n/a | none | [payment-page](../payment-page/README.md#methods) |
| Capture a hold | you | `POST /set_accept {accept_status: capture, final_amount}` | yes, a smaller `final_amount` returns the rest | once (derived) | from the `basket` sent at creation (derived) | https://help.octo.uz/payment-via-web/methods/set-accept.html |
| Release a hold | you; Octo at hold expiry | `POST /set_accept {accept_status: cancel}` | `final_amount` for a partial cancel (cancel page) | once | not documented | https://help.octo.uz/cancel.html |
| Refund a `succeeded` payment | you | `POST /refund {shop_refund_id, octo_payment_UUID, amount}` | yes | unlimited calls within the limits | not documented | https://help.octo.uz/refunds.html |
| Wrong OTP three times | Octo | automatic cancel | n/a | n/a | none | https://help.octo.uz/payment-via-web/one-stage.html |
| Card-binding verification debit | Octo | refunded by Octo automatically | n/a | once | none (derived) | https://help.octo.uz/tokenization.html |
| Remove a stored card | you | `POST /block_card_token {card_token}` | n/a | once; no unblock documented | n/a | https://help.octo.uz/tokenization.html |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| `notify_url` notification | not documented | not documented | `octo_payment_UUID` + `status` (derived) | apply each status once; re-check the status | https://help.octo.uz/notifications.html |
| Capture callback | until `capture` or `waiting_user_action` | not documented | `octo_payment_UUID` | same answer again; decide once with `set_accept` | https://help.octo.uz/payment-via-web/two-stage.html |
| Bind callback (`bind_notify_url`) | up to 3 after a failed answer, then the token is cancelled | not documented | `shop_transaction_id` of the binding | store the token once, answer `200` every time | https://help.octo.uz/tokenization.html |
| `prepare_payment` (you call) | n/a | n/a | `shop_transaction_id` | after a lost reply, call the three-field status form; do not create a new id until you know the first one failed (derived) | https://help.octo.uz/check-status.html |
| `set_accept` (you call) | n/a | n/a | `octo_payment_UUID` | on a timeout, re-check the status before resending (derived) | https://help.octo.uz/payment-via-web/methods/set-accept.html |
| `refund` (you call) | n/a | n/a | `shop_refund_id` | reuse the same id on a retry; duplicate reply not printed | https://help.octo.uz/refunds.html |
| `bind_card` (you call) | n/a | n/a | `shop_transaction_id` | `error: 20` when a token is already active or pending | https://help.octo.uz/tokenization.html |

## Fiscal receipts

- **Who**: Octo registers the receipt with the tax service for the shop, from the
  `basket` in `prepare_payment`; you read it back with `POST /fiscal-data`.
  [fiscal](../fiscal/README.md#flow)
- **Before the first sale**: each product (`spic`, `package_code`, `nds`, `inn` from a legal
  entity or `pinfl` from an individual entrepreneur) is registered by your bank manager.
  An unregistered item fails the payment with `error: 403`.
- **Payer contact**: `user_data` with an e-mail (receipt link) or a phone (receipt
  registered to it).
- **Single-product shops**: `basket` may be left out; Octo uses the active product from
  the cabinet.
- **Receipt fields**: `terminalID`, `receiptId`, `dateTime` (`YYYYMMDDHHMMSS`),
  `fiscalSign`, `qrCodeURL` (ofd.soliq.uz); the partner transaction object adds
  `fiscalDetails{status, errorCode, message}`.
- **Refunds and partial captures**: return receipts are not described.

## Not documented — ask the provider

- The real hold window for your shop (30 minutes vs 30 days / 7 days) and which page is
  current.
- The default `ttl`, and the default `auto_capture` (`false` in the table, `true` in the
  partner overview).
- Notification retries, the expected answer and its timeout; the separator in the
  `signature` string and the role of `hash_key`.
- How long after payment a refund is allowed; what a repeated `shop_refund_id` returns;
  whether refunds and partial captures produce return receipts.
- The reply to a repeated `shop_transaction_id` with a full body.
- The OTP resend limit and the Humo wrong-code limit.
- The capture callback answer deadline, and whether the callback carries `octo_secret` in
  production (the sample does).
- When `fiscal-data` is available after payment and its reply before the receipt is ready.
- Whether `test: true` applies to `bind_card`, `refund` and `fiscal-data`.
