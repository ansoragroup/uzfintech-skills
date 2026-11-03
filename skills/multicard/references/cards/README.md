# Multicard Cards (card binding by hosted form or API, card management)

Hand-written notes. Transport, auth and errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/) (card object: [`../common/schemas/card.json`](../common/schemas/card.json)).
Examples: [`examples/`](examples/).

- Source: https://docs.multicard.uz/4488545f0 (form guide), https://docs.multicard.uz/4488546f0
  (API guide), https://docs.multicard.uz/19729302e0, https://docs.multicard.uz/19729303e0,
  https://docs.multicard.uz/19729304e0, https://docs.multicard.uz/19729305e0,
  https://docs.multicard.uz/19729306e0, https://docs.multicard.uz/19729307e0,
  https://docs.multicard.uz/19729308e0, https://docs.multicard.uz/19729309e0,
  https://docs.multicard.uz/22557089e0 (Russian pages)
- Fetched: 2026-11-03
- Result: a `card_token` you use for token payments, holds and payouts.

## Flow A: hosted bind form (no PCI DSS needed)

```
POST /payment/card/bind {store_id, redirect_url, redirect_decline_url, callback_url, phone}
   └─> data.session_id (store it), data.form_url (redirect or WebView; session lives 15 min)
payer enters the card on Multicard's form
   └─> callback_url gets the card object (payer_id = session_id, card_token)
   └─> or poll GET /payment/card/bind/{session_id}
payer returns to redirect_url / redirect_decline_url
```

## Flow B: bind API (PCI DSS certificate required)

```
POST /payment/card {pan, expiry (yymm), user_phone}  ─> SMS code to the card's phone
   └─> data.card_token (status draft)
PUT /payment/card/{card_token} {otp, pinfl?}         ─> card status active
```

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| create-bind-link | `POST /payment/card/bind` | `store_id*` (int), `redirect_url*`, `redirect_decline_url*`, `callback_url`, `phone` (`998XXXXXXXXX`), `pinfl` (14 digits) | `session_id`, `form_url` |
| get-bind-status | `GET /payment/card/bind/{session_id}` | path `session_id` | card |
| get-card | `GET /payment/card/{card_token}` | path `card_token` | card |
| check-pinfl | `POST /payment/card/check-pinfl` | `pan*` (full PAN), `pinfl*` | `true`, `false` or `null` (unknown) |
| revoke-card | `DELETE /payment/card/{card_token}` | path `card_token` | `[]` |
| add-card (PCI DSS) | `POST /payment/card` | `pan*`, `expiry*` (yymm), `user_phone*`, `cvc`, `holder_name`, `session_id` | card (`draft`) |
| confirm-card (PCI DSS) | `PUT /payment/card/{card_token}` | `otp*`, `pinfl` | card (`active`) |
| check-card-by-pan (PCI DSS) | `GET /payment/card/check/{pan}` | path `pan` | `masked_pan`, `bank{bin, name, ...}`, `ps`, `holder_name` |

Card object: `card_token`, `card_pan` (masked), `ps` (`uzcard`, `humo`, `visa`,
`mastercard`, `unionpay`), `status` (`draft`, `active`, `deleted`), `phone`, `holder_name`,
`pinfl`, `payer_id`, `card_status{code, description}` (`code` `0` = active), `sms_inform`,
`added_on`.

## Bind callback

Multicard `POST`s the card object to `callback_url` after a successful bind.

- Answer **HTTP 200**. Otherwise it is resent every 60 s, 5 attempts in total.
- The callback carries **no signature**. Match `payer_id` to a `session_id` you issued, then
  confirm with `GET /payment/card/bind/{session_id}` before saving the token (derived).

## Ownership checks (Uzcard and Humo only)

- `pinfl` on create-bind-link or confirm-card makes Multicard check that the card belongs
  to that person; `pinfl` is returned on the card only in that case.
- `phone` / `user_phone` is checked against the card's SMS-banking number. It is required
  for Humo cards.
- `check-pinfl` checks a full PAN against a PINFL without binding.

## Errors

| Case | Answer |
|---|---|
| add-card: SMS banking off, bad card data, unsupported card, validation | `400` |
| add-card: a code was already sent | `429` |
| confirm-card: wrong code | `400 ERROR_WRONG_OTP` |
| confirm-card: code expired | `423` |
| get-card / revoke-card: unknown token | `400` |

## Gotchas

- The schema marks `callback_url` and `phone` on create-bind-link as required, but the text
  says the callback is sent only if `callback_url` is passed and `phone` is required for
  Humo. Send both to be safe.
- `user_phone` on add-card is marked required; the text says required for Humo.
- Store `session_id` before redirecting: the callback and the status call key on it.
- The bind session expires after 15 minutes; create a new link after that.
- `check-pinfl`, add-card and check-card-by-pan take a **full PAN**. Without PCI DSS, use
  only the hosted form and the token.
- Store the token and the masked PAN; never log PANs, expiry, CVC or OTPs.
- After revoke-card the token is unusable; remove it from your vault too.

## Examples

[`examples/`](examples/): bind-link request/response, bind-status response, bind-callback
request, card-info response, check-pinfl request/response, revoke-card response, add-card
request/response, confirm-card request/response, check-card response, wrong-OTP error.
