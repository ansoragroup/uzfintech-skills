# Octo card tokenization (bind a card, pay with the token, block it)

Hand-written notes. Transport, auth, envelope and error codes:
[`../common/README.md`](../common/README.md). Paying with a token:
[`../partner-page/`](../partner-page/README.md) (`pay` with `card_token`). Schemas:
[`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://help.octo.uz/tokenization.html, https://help.octo.uz/confirm-pay/token.html
  (Russian pages)
- Fetched: 2026-11-04
- Needs: tokenization enabled for the shop, a public HTTPS `bind_notify_url`, and the right
  to receive card data (the bind call and its callback both carry the full PAN).

## Flow

```
POST /bind_card {shop pair, shop_transaction_id, pan, exp, phone, cardHolderName, cvc2?,
                 method, return_url, notify_url?, bind_notify_url}
   └─> data {octo_payment_UUID, status created, octo_pay_url}
Uzcard / Humo:
   GET /verificationInfo/{octo_payment_UUID}  ─> data {verifyId, phone, secondsLeft}
   POST /bind_card/check_sms_key {shop pair, smsKey, paymentUUID, verifyId}
      └─> data status succeeded, first6, last4  (no token here)
Visa / Mastercard:
   payer passes the issuer OTP form at octo_pay_url
then Octo debits a verification amount and refunds it, and
   POST <bind_notify_url> {shop_transaction_id, pan, exp, cardHolderName, card_token,
                          status active|failed}  ─> you answer HTTP 200
later purchases: prepare_payment, then POST /pay/{uuid} {card_token, method, email?}
remove: POST /block_card_token {shop pair, card_token} ─> {error 0, status blocked}
```

## Methods

| Method | Endpoint | Params (`*` required) | Result |
|---|---|---|---|
| bind-card | `POST /bind_card` | `octo_shop_id*`, `octo_secret*`, `shop_transaction_id*`, `pan*`, `exp*` (YYMM), `phone*`, `cardHolderName`, `cvc2`, `method*` (`humo`, `uzcard`, `bank_card`), `return_url*`, `notify_url`, `bind_notify_url` | `data`: `octo_payment_UUID`, `status`, `octo_pay_url`, `total_sum` |
| bind-check-sms-key | `POST /bind_card/check_sms_key` | `octo_shop_id*`, `octo_secret*`, `smsKey*`, `paymentUUID*`, `verifyId*` | `data`: `status`, `processor_key`, `processing_reference`, `refunded_sum`, `total_sum`, `payed_time`, `first6`, `last4` |
| bind-callback (incoming) | `POST <bind_notify_url>` | `shop_transaction_id`, `pan`, `exp`, `cardHolderName`, `card_token`, `status` | you answer HTTP `200`, e.g. `{status: "success", message}` |
| block-card-token | `POST /block_card_token` | `octo_shop_id*`, `octo_secret*`, `card_token*` | whole body `{error, errMessage, status}` |

Token statuses: `active` (ready to pay), `blocked`, `init` (card check in progress),
`failed`. `block_card_token` codes: `0` ok, `1` format, `2` auth, `4` internal, `5` token
not found, `6` token not `active`.

## Gotchas

- The token arrives **only** in the callback to `bind_notify_url`; the
  `check_sms_key` reply has none. `bind_notify_url` is marked optional, but without it you
  never get the token. Send it on every bind (derived).
- Answer the bind callback with HTTP `200` after you have stored the token. Octo retries a
  non-200 answer up to three times and then **cancels the token**. Warning
  [`octo.bind-callback-ack`](../lifecycle/README.md).
- The bind callback carries the **raw PAN** and expiry. Do not log the body; store only
  `card_token`, the masked number and the expiry you need (derived).
- The callback has no signature. Match `shop_transaction_id` against a binding you started
  and accept only `active` tokens for a card you were binding (derived).
- Binding debits a small verification amount and refunds it; the payer sees both
  movements. The amount is not printed (the sample shows `total_sum: 1000`).
- `error: 20` "Active or pending token already exists": the card is already bound or a
  binding is in progress for this shop. Reuse the stored token instead of binding again.
- The flow diagram calls the OTP step `/bind_card/check_sms`; the method section and
  sample use `/bind_card/check_sms_key`. Use the latter.
- A crash in the card check answers `{title: "Internal Server Error", status: 500,
  detail}` without `error`; treat it as a failed bind and let the payer retry.
- The tokenization overview says later purchases ask the payer only for CVV2/CVC2, but
  the `pay` with token body has no `cvc2` field. Ask Octo which applies to your shop.
- Block a token when the payer removes the card or closes the account; a blocked token
  cannot be reactivated (derived: no unblock method is documented).

## Examples

[`examples/`](examples/): bind-card request/response, bind-check-sms-key request/response,
bind-callback request and your response, block-card-token request/response.
