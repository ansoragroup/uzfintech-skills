# Uzum Nasiya (BNPL / installment contracts for partners)

Hand-written notes. Generated tables: [`endpoints.md`](endpoints.md); schemas:
[`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_nasiya.yaml (the `en_nasiya.yaml`
  file is also in Russian; quoted enum labels below stay Russian where the contract is)
- Fetched: 2026-11-03
- Direction: partner calls Uzum Nasiya. The buyer signs in a Nasiya WebView.

## Host and auth

Production `https://merchants-api.uzumnasiya.uz` (the only server listed). Header
`Authorization: Bearer <NASIYA_TOKEN>`; a missing or bad token gives HTTP 401.

## Flow

```
buyers/check-status {phone}
  ├─ status 0,1,2,5,10,11,12 -> open data.webview (registration), re-check later
  ├─ status 8,9,13,14,403   -> refuse: installment not possible
  └─ status 4 (verified)    -> orders/calculate {user_id, products[]} -> tariffs[]
                               -> buyer picks tariff
                               -> orders {user_id, period = tariff, products[], callback?, ext_order_id?}
                               -> data.paymart_client.contract_id + webview_path (OTP signing)
                               -> contracts/check-status until signed
                               -> contracts/confirm {contract_id}  (or contracts/cancel)
```

SMS signing without the WebView: `/v3/buyers/send-code-sms {phone, contract_id}` sends a
4-digit code; `/v3/buyers/check-code-sms {phone, contract_id, code}` verifies it.

## Operations (all `POST`)

| Path | Request | Response `data` |
|---|---|---|
| `/api/v1/buyers/check-status` | `phone` (**integer** `998XXXXXXXXX`) | `status`, `buyer_id`, `has_limit`, `available_periods[]`, `webview`, ... |
| `/api/v1/orders/calculate` | `user_id`, `products[{product_id, price, amount}]` | array of tariffs: `tariff`, `period_months`, `total`, `origin`, `month`, `deposit`, `is_promo`, ... |
| `/api/v1/orders` | `user_id`, `period`, `products[{amount, name, price, category, unit_id, product_id?}]`, `callback?`, `ext_order_id?` | `paymart_client{contract_id, order, total, price_month, ...}`, `cart[]`, `client_act_pdf`, `webview_path` |
| `/api/v1/contracts/check-status` | `contract_id` | `contract_status`, `is_signed`, ... |
| `/api/v1/contracts/confirm` | `contract_id` | `client_act_pdf` |
| `/api/v1/contracts/cancel` | `contract_id` | full cancellation |
| `/v3/buyers/send-code-sms` | `phone` (**string**), `contract_id` | `hashed`, `is_registered` |
| `/v3/buyers/check-code-sms` | `phone`, `contract_id`, `code` | `contract_id`, `message` |

## Envelope

`{"status": "success"|"error", "error": [{"type", "text", "sub_text"}], "data": ..., "response_code": <int>}`.

## Enums

Buyer `status`:

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| 0 | not registered | 9 | blocked |
| 1 | must register and add a card | 10 | selfie needed |
| 2 | documents under review | 11 | registration page not finished |
| 4 | verified, can buy | 12 | contact person needed |
| 5 | passport photo needed | 13 | must call support |
| 8 | blacklisted (overdue > 60 days) | 14 | must call support for this vendor |
| 403 | has debt | | |

`contract_status`: `0` not confirmed, `1` active, `2` moderation, `3` overdue 60+,
`4` overdue 30+, `5` cancelled, `9` closed.

`response_code`: `0` SUCCESS, `4004` CONTRACT_NOT_FOUND, `4005` INVALID_CONTRACT_DATA,
`4009` CONTRACT_INCORRECT_STATUS, `4010` CONTRACT_ALREADY_ACTIVATED,
`5003` PARTNER_ACCESS_DENIED, `5005` INVALID_PARTNER_DATA, `1000` TECHNICAL_ERROR,
`6001` MAX_REQUEST_LIMIT. Retry only on `1000` and HTTP 5xx, with backoff.

## Gotchas

- `phone` is an integer in `check-status` but a string in the SMS endpoints.
- `period` in `orders` must be the exact `tariff` string from `calculate` (e.g. `"12 Default"`).
- `price` is the item price **without** Nasiya markup. The spec does not state the unit
  (UZS or tiyin) and its examples do not settle it. Confirm with your manager.
- `contract_id` comes from `data.paymart_client.contract_id`, not top-level.
- `confirm` after the buyer signed; `confirm` on an active contract gives `4010`.
- No webhooks are described: poll `contracts/check-status`.

## Examples

[`examples/`](examples/): check-status response, calculate request, create order
request/response, confirm response, error.
