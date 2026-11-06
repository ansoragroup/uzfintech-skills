# BTS API: sources, transport, auth, statuses, errors

Hand-written notes that apply to every BTS product: directory, quote, order and webhook.
Test host and simulator: [`../sandbox/README.md`](../sandbox/README.md). Lifecycle traps:
[`../lifecycle/README.md`](../lifecycle/README.md).

- Source: https://docs.bts.uz/page/auth-login, https://docs.bts.uz/page/auth-login-refresh,
  https://docs.bts.uz/page/status
- Fetched: 2026-11-06
- Spec: there is no machine-readable spec, only the HTML pages above. The schemas here
  are hand-written from those pages and checked against a production client.

## Transport

| Item | Value |
|---|---|
| Test base URL | `https://apitest.bts.uz:28345` |
| Production base URL | BTS issues it with the contract. Keep it in configuration (`bts.host-from-config`) |
| Paths | `/auth/...` for login, `/v1/...` for everything else |
| Body | JSON with `Content-Type: application/json`. The incoming webhook is form-data |
| Headers | `Accept: application/json`, `language: ru` / `uz` / `en`, `Authorization: Bearer <ACCESS_TOKEN>` |
| TLS | keep certificate and host verification on |

## Auth

```
POST /auth/login    {"login": "<BTS_LOGIN>", "password": "<BTS_PASSWORD>"}
  └─> data.access_token (about 24 h), data.refresh_token (about 30 days)
POST /auth/refresh  {"refresh_token": "<REFRESH_TOKEN>"}
  └─> a new access_token; an expired refresh token answers 422, so log in again
```

- Cache the access token and renew it before it expires (`bts.token-lifetime`). A safe
  client:
  - treats the token as valid for 20 hours;
  - runs only one login at a time, and concurrent callers wait for its result;
  - on a `401`, logs in once more and repeats the call once.
- Wrong login or password answers `401` in the framework shape
  `{"name":"Unauthorized","message":"Incorrect login or password.","code":0,"status":401,"type":"..."}`.
- A missing field answers `422`:
  `{"status":false,"message":"Validation error.","status_code":422,"errors":{"password":["..."]}}`.

## Envelope

Most replies share one shape:

```json
{"status": true, "status_code": 200, "message": "success", "data": {}, "errors": null}
```

`message` is a code such as `success`, `success.updated`, `error.validation`,
`error.not_found` or `error.already_cancelled`. Some `401`, `400` and `404` replies use
the framework shape shown under Auth instead, so parse both.

## Statuses

These come from `GET /v1/status/index` ([directory](../directory/README.md)). The names
are in Russian, as BTS returns them.

| Status | Meaning | Final? |
|---|---|---|
| `100` У отправителя | created and still with the sender; the only state you can cancel | no |
| `200` Курьер принял | the courier picked it up | no |
| `300` В офисе отправления | at the origin branch | no |
| `400` Во внутренней перевозке | moving inside the origin region | no |
| `500` В РЦ | at a sorting centre | no |
| `600` В мешке | bagged for line haul | no |
| `700` В перевозке | line haul between cities | no |
| `800` В офисе доставки | at the destination branch, ready for pickup | no |
| `900`, `1000` | seen in practice but missing from the list (`bts.undocumented-codes`) | no |
| `1100` Курьер доставляет | out for delivery | no |
| `1200` Доставлен | delivered | yes |
| `1300` Удалён | cancelled or deleted | yes |
| `1400` Срок истек | the storage time ran out; treat it as returned to the sender | yes |

A typical mapping to a shop's own states:

| BTS code | Shop state |
|---|---|
| 100 | created |
| 200 | picked_up |
| 300-700 | in_transit |
| 800 | ready_for_pickup |
| 900, 1000, 1100 | out_for_delivery |
| 1200 | delivered |
| 1300 | cancelled (an interpretation; confirm it with BTS) |
| 1400 | returned (an interpretation; confirm it with BTS) |
| anything else | in_transit, and log the code |

## Errors

| HTTP | Meaning | What to do |
|---|---|---|
| 200 | `status: true` | use `data` |
| 400 | bad request, for example `error.already_cancelled` | permanent; read `message` |
| 401 | the token is missing or expired | log in once and repeat the call once |
| 404 | `error.not_found` / `Ресурс не найден.` | permanent |
| 408 | timeout | repeat reads; never repeat `order/add` blindly |
| 422 | `error.validation`, with the field list in `errors` | permanent; fix the input |
| 425, 429, 5xx | the server is busy or broken | back off and repeat reads; check before repeating writes |

Do not follow 3xx answers on API calls. Redact `Authorization`, `password`,
`refresh_token` and `itx-apiKey` from logs.

## Configuration a client needs

| Field | Secret? | Notes |
|---|---|---|
| `api_base_url` | no | the test or production host |
| `language` | no | `ru`, `uz` or `en` |
| `login`, `password` | yes | issued by BTS |
| `client_id` | no | your account id at BTS, if BTS issued one |
| `sender_name`, `sender_phone`, `sender_address`, `sender_city_code`, `sender_branch_code` | no | the shipper, sent in every `order/add` |
| `pickup_type` | no | `courier` or `self` |
| `package_id`, `post_type_id` | no | issued by BTS for your account |
| default weight and box size | no | used when an item has none, for example 1 kg and 30 x 20 x 10 cm |
| `webhook_token` | yes | the `itx-apiKey` you register; keep the previous value during rotation |

Turn BTS on at checkout only when the sender fields and `webhook_token` are set.

## Fargo

Fargo, another Uzbek courier, has no public API, and an integration waits on a contract.
Until Fargo issues documentation, book and track Fargo shipments by hand in the Fargo
cabinet and record the tracking number on the order. Do not guess endpoints.
