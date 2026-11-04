# Atmos Card linking (Uzcard / Humo card tokens for repeat and recurring charges)

Hand-written notes. Transport, auth and error codes: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/). Visa / Mastercard
binding is a separate API: [`../mps/README.md`](../mps/README.md).

- Source: https://docs.atmos.uz/en/#card-linking, https://docs.atmos.uz/en/#request-to-link-a-card,
  https://docs.atmos.uz/en/#card-linking-confirmation,
  https://docs.atmos.uz/en/#list-of-merchant-linked-cards,
  https://docs.atmos.uz/en/#cancel-linked-card
- Fetched: 2026-11-04
- Needs: a Bearer token ([auth](../common/README.md#auth)); card linking enabled for your
  merchant account (ask Atmos). Your server receives the full PAN and expiry: PCI DSS scope.

## Flow

```
POST /partner/bind-card/init {card_number, expiry}
   └─> transaction_id, phone (masked)       SMS code sent to the cardholder
POST /partner/bind-card/confirm {transaction_id, otp}
   └─> data {card_id, pan (masked), expiry, card_holder, balance, phone, card_token}
store card_id + card_token against YOUR customer
charge later: pay/create -> pay/pre-apply {card_token} -> pay/apply {otp: 111111}
POST /partner/list-cards {page, page_size}   -> cardDataSmallList[]
POST /partner/remove-card {id: card_id, token: card_token}   -> data with nulls
```

All four calls are on the API host: `https://apigw.atmos.uz/partner/...`.

## Methods

| Method | Endpoint | Params (`*` required) | Result |
|---|---|---|---|
| bind-card-init | `POST /partner/bind-card/init` | `card_number*` (16 digits), `expiry*` (`YYmm`) | `transaction_id`, `phone` |
| bind-card-confirm | `POST /partner/bind-card/confirm` | `transaction_id*`, `otp*` | `data {card_id, pan, expiry, card_holder, balance, phone, card_token}` |
| list-cards | `POST /partner/list-cards` | `page`, `page_size` | `cardDataSmallList[] {card_id, card_token, pan, expiry}` |
| remove-card | `POST /partner/remove-card` | `id*` (card_id), `token*` (card_token) | `data` with every field `null` |

## Errors

The `/partner` calls use the same `result.code` envelope as payments
([error codes](../common/README.md#error-codes-resultcode)). The ones you will meet here:
card not found or wrong expiry (`STPIMS-ERR-004`, `-030`, `-043`, `-090`), wrong code
(`STPIMS-ERR-098`), SMS not sent (`STPIMS-ERR-102`), card blocked or expired
(`STPIMS-ERR-058`, `-067` ... `-088`).

## Gotchas

- The token is bound to your **merchant**, not to a customer. `list-cards` returns every
  card linked to the merchant. Keep your own customer → `card_id` / `card_token` mapping
  and never show another customer's card from `list-cards`.
- No `store_id` in these calls; the Bearer token decides the merchant.
- The confirm answer carries `balance` and the holder name. Do not log or show the
  balance, and do not keep it (derived).
- Charging a token uses `otp: "111111"` on `pay/apply`. That fixed value is part of the
  token flow, not a sandbox code. Whether a given card can be charged without an SMS is
  decided by Atmos, not by you.
- `expiry` is `YYmm` (for example `2903` for 03/2029). Test cards print `MM/YY`.
- Removing a card needs both `id` and `token`. After removal any charge with that token
  fails; delete it on your side in the same step.
- There is no documented callback when a cardholder blocks or reissues a card; expect
  charge errors and ask the customer to link the card again.
- Card linking for Visa / Mastercard is not here: use `/mps-extend/.../card/bind` or the
  owner-link page in [`../mps/`](../mps/README.md).

## Examples

[`examples/`](examples/): bind-card-init, bind-card-confirm, list-cards, remove-card
(request and response each).
