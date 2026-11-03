# Click card tokens (save a card, charge it from your server)

Hand-written notes. Schemas are in [`schemas/`](schemas/) and bodies in
[`examples/`](examples/). The `Auth` header and units are in
[`../common/README.md`](../common/README.md).

- Source: https://docs.click.uz/en/merchant-api/requests (sections on card tokens)
- Fetched: 2026-11-03
- Direction: **you call Click**, base URL `https://api.click.uz/v2/merchant/`. Your server
  sees the card number and expiry once, when the token is requested.

## Operations

| Op | Request | Returns |
|---|---|---|
| card-token-request | `POST card_token/request` + JSON | `card_token`, masked `phone_number`, `temporary`; Click sends an SMS code |
| card-token-verify | `POST card_token/verify` + JSON | masked `card_number` |
| card-token-payment | `POST card_token/payment` + JSON | `payment_id`, `payment_status` |
| card-token-delete | `DELETE card_token/:service_id/:card_token` | `error_code`, `error_note` |

## Flow

```
card_token/request(card_number, expire_date, temporary)
    └─> card_token (not yet usable) + SMS code to the card's phone
card_token/verify(card_token, sms_code)
    └─> token active; masked card_number
card_token/payment(card_token, amount, transaction_parameter)
    └─> payment_id, payment_status  (poll payment/status until 2 or < 0)
card_token DELETE  (when the payer removes the card)
```

- `temporary = 1` makes a one-time token. Click deletes it automatically after the payment.
- `temporary = 0` makes a token you can charge again. Store it encrypted and bind it to
  the payer's account.

## Fields

| Op | Field | Type | Rule |
|---|---|---|---|
| request | `service_id` | int | your service |
| request | `card_number` | string | 16 digits, no spaces |
| request | `expire_date` | string | `MMYY` |
| request | `temporary` | int | `1` one-time, `0` reusable |
| verify | `card_token` | string | from `request` (UUID format) |
| verify | `sms_code` | int | the code the cardholder received |
| payment | `card_token` | string | an active token |
| payment | `amount` | float | soums |
| payment | `transaction_parameter` | string | your order id |

Responses all carry `error_code` and `error_note`.
- `request` also returns `card_token`, `phone_number` (masked) and `temporary` (bool).
- `verify` returns `card_number` (masked).
- `payment` returns `payment_id` and `payment_status`, with the same values as in the
  Merchant API (`2` = success, `1` = processing, `< 0` = error).

## Gotchas

1. The vendor example for `card_token/request` shows no `Auth` header, while every other
   call has one. Send `Auth` on all of them.
2. `expire_date` is `MMYY` here, while Paynet, for example, uses `YYMM`. Check the order of
   the digits.
3. `sms_code` is an integer in the docs. A code with a leading zero is unsafe as a number,
   so verify how Click treats it in the test environment.
4. Handling `card_number` puts your server in PCI DSS scope. Never log it, and drop it right
   after `card_token/request`.
5. `payment_status = 1` is not final. Poll `payment/status/:service_id/:payment_id`.
6. Make `transaction_parameter` unique per charge so you can reconcile the payment.
7. To refund, use `payment/reversal` from the Merchant API. Its month window applies.

## Examples

Bodies only. Headers are described in common.

- [`card-token-request.request.json`](examples/card-token-request.request.json) /
  [`card-token-request.response.json`](examples/card-token-request.response.json)
- [`card-token-verify.request.json`](examples/card-token-verify.request.json) /
  [`card-token-verify.response.json`](examples/card-token-verify.response.json)
- [`card-token-payment.request.json`](examples/card-token-payment.request.json) /
  [`card-token-payment.response.json`](examples/card-token-payment.response.json)
- [`card-token-delete.response.json`](examples/card-token-delete.response.json)
