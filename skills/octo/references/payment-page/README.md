# Octo payment page (one-stage and two-stage, payer enters the card on Octo)

Hand-written notes. Transport, auth, `test`, envelope, statuses, notifications and error
codes: [`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/).
Examples: [`examples/`](examples/).

- Source: https://help.octo.uz/payment-via-web/one-stage.html,
  https://help.octo.uz/payment-via-web/two-stage.html,
  https://help.octo.uz/payment-via-web/methods/prepare-payment.html,
  https://help.octo.uz/payment-via-web/methods/set-accept.html,
  https://help.octo.uz/payment-via-web/methods/callback.html,
  https://help.octo.uz/check-status.html, https://help.octo.uz/cancel.html (Russian pages)
- Fetched: 2026-11-04
- Needs: `octo_shop_id` and `octo_secret` from the cabinet; for receipts, registered basket
  items ([`../fiscal/`](../fiscal/README.md)).

## Flow

```
POST /prepare_payment {shop pair, shop_transaction_id, auto_capture, test, init_time,
                       total_sum, currency, description, basket, return_url, notify_url, ttl}
   └─> data {octo_payment_UUID, status created, octo_pay_url}
       redirect the payer to octo_pay_url (Octo page: card form, OTP or 3-D Secure)
one-stage (auto_capture true):
   card debited ─> notification to notify_url (status succeeded) ─> payer sent to return_url
two-stage (auto_capture false):
   funds held ─> status waiting_for_capture ─> notification + amount-confirmation callback
   POST /set_accept {octo_payment_UUID, accept_status capture|cancel, final_amount}
      └─> data status succeeded (captured) or canceled (released)
   no decision in time ─> Octo cancels the hold by itself
always: re-check with POST /prepare_payment {shop pair, shop_transaction_id} before you ship
```

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| prepare-payment | `POST /prepare_payment` | `octo_shop_id*`, `octo_secret*`, `shop_transaction_id*`, `auto_capture`, `test`, `init_time*`, `user_data{user_id*, phone*, email*}`, `total_sum*`, `currency*`, `description*`, `basket[]`, `payment_methods[]{method}`, `return_url`, `notify_url`, `language`, `ttl` | `shop_transaction_id`, `octo_payment_UUID`, `status`, `octo_pay_url`, `refunded_sum`, `total_sum` |
| check-status | `POST /prepare_payment` | `octo_shop_id*`, `octo_secret*`, `shop_transaction_id*` (nothing else) | `shop_transaction_id`, `octo_payment_UUID`, `status` |
| set-accept | `POST /set_accept` | `octo_shop_id*`, `octo_secret*`, `octo_payment_UUID*`, `accept_status*` (`capture` or `cancel`), `final_amount*` | `status`, `transfer_sum`, `refunded_sum`, `total_sum`, `payed_time` |
| capture-callback (incoming) | your endpoint; the page prints `https://secure.octo.uz/callback` | `octo_secret`, `octo_payment_UUID`, `accept_status`, `final_amount` | you answer `{accept_status, final_amount}` |

- `payment_methods[].method`: `bank_card` (Visa, Mastercard, UnionPay), `uzcard`, `humo`.
  Leave the list out to offer everything enabled for the shop (derived from the samples).
- `language`: `oz`, `uz`, `en`, `ru`; default is the browser language, then `en`.
- `return_url` must be a full URL and must carry a parameter that identifies the payment.
- `ttl` is the payment lifetime in **minutes** from creation. Warning
  [`octo.ttl-minutes`](../lifecycle/README.md).
- `user_data` is optional, but when you send it all three fields are required, and the
  fiscal page relies on its phone or e-mail for the receipt.

## Two-stage specifics

- Set `auto_capture: false` explicitly. The `prepare_payment` table says the default is
  `false`, the partner-page overview says `true`; never rely on the default.
- A smaller `final_amount` captures that amount and returns the rest to the payer. You
  cannot capture more than the hold.
- `set_accept` with `accept_status: cancel` is the only cancel method, and it works only
  for held payments. A `succeeded` payment needs a refund
  ([`../refunds/`](../refunds/README.md)). Warning
  [`octo.cancel-only-holds`](../lifecycle/README.md).
- Hold expiry: the two-stage pages say an unconfirmed hold is cancelled after
  **30 minutes**; the cancel page says up to **30 days** for Humo and Uzcard (can be
  raised in the cabinet) and up to **7 days** for Visa and Mastercard (can only be
  lowered). Plan for the shorter one. Warning [`octo.hold-auto-cancel`](../lifecycle/README.md).
- The amount-confirmation callback is resent until your answer carries `capture` or
  `waiting_user_action` (the two-stage page spells it so; the status list says
  `wait_user_action`). Answer quickly with `{accept_status, final_amount}`, then make the
  authoritative decision with `set_accept`. Warning
  [`octo.capture-callback-answer`](../lifecycle/README.md).

## Errors

| Case | Answer |
|---|---|
| wrong shop pair | `error: 2`, `errMessage: "Wrong secret"` |
| basket item not registered | `error: 403`, "Fiscal object ... not contains in system" ([`../fiscal/`](../fiscal/README.md)) |
| repeated `shop_transaction_id` | Octo uses it to stop accidental duplicates; the reply to a full repeat is not printed (the three-field form returns the existing payment) |
| any body without `error` | global handler `{title, status, detail}`: treat as failed, then check status |

## Gotchas

- `test` is optional and its absence means a **real** payment on the same host. Warning
  [`octo.test-flag-real-money`](../lifecycle/README.md).
- `shop_transaction_id` must be unique per payment attempt; it is also the key for the
  status check. Store it before you call. Warning
  [`octo.unique-shop-ids`](../lifecycle/README.md).
- The status check reuses `prepare_payment`. Send only the three fields; extra fields
  would look like a new payment request (derived).
- `return_url` is a browser redirect, not proof of payment. Decide on the status check.
- Amounts are major units (`1000.0` UZS), not tiyin.
- Notifications are not signed with your secret. Verify `signature` and re-check the
  status ([`../common/`](../common/README.md)). Warning
  [`octo.notify-verify-status`](../lifecycle/README.md).

## Examples

[`examples/`](examples/): prepare-payment request/response (two-stage, test), check-status
request/response, set-accept request/response (capture), capture-callback request and your
response.
