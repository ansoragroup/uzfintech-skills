# Octo API: transport, auth, envelope, statuses, notifications, errors

Hand-written notes. Applies to every Octo product in this skill. Schemas:
[`schemas/`](schemas/) (shared models). Examples: [`examples/`](examples/).

- Source: https://help.octo.uz/get-started.html (cabinet),
  https://help.octo.uz/statuses.html (statuses), https://help.octo.uz/notifications.html
  (`notify_url`), https://help.octo.uz/error-codes.html (processing codes),
  https://help.octo.uz/payment-via-web/methods/prepare-payment.html (envelope, `test`)
  (Russian pages; English twins under `/en/`, Uzbek under `/uz/`)
- Fetched: 2026-11-04
- Spec: VitePress pages with JSON samples and parameter tables; there is no OpenAPI file,
  no Postman collection and no `llms.txt`.

## Transport

| Item | Value |
|---|---|
| Base URL | `https://secure.octo.uz` (one host; test payments use the same host with `test: true`) |
| Format | `POST` with `Content-Type: application/json`; `verificationInfo` is a `GET` |
| Auth | `octo_shop_id` (integer) and `octo_secret` (string) **in the JSON body**; no headers, no token |
| Amounts | decimal numbers in **major units** of `currency` (`1000.0` UZS is one thousand sum, not tiyin) |
| Currency | `currency` in `prepare_payment`: `UZS`, `USD` or `RUB`; the notification reports the actual currency (`UZS` or `USD`) |
| Times you send | `init_time` as `yyyy-MM-dd HH:mm:ss`; the time zone is not documented (send Tashkent local time, derived) |
| Times you get | `payed_time`, `refund_time` as `yyyy-MM-dd HH:mm:ss`; the partner-page transaction object (`pay`, `check_sms_key`) uses epoch **milliseconds** (`createTime`, `expireTime`, `peyedTime`) although its table says UNIX timestamp |
| Ids | your id `shop_transaction_id` (string, unique per payment); Octo id `octo_payment_UUID` (36-char UUID); the partner flow also has an integer `data.id` (`paymentId`) |
| Payment page | `octo_pay_url`, for example `https://pay2.octo.uz/pay/<octo_payment_UUID>?language=uz` |
| Cabinet | `https://merchant.octo.uz` (shop id, secret, default notification URL, hold window) |

## Auth

Every server call carries the pair in the body:

```json
{"octo_shop_id": 123, "octo_secret": "<OCTO_SECRET>", "...": "..."}
```

- The secret is generated in the cabinet. Keep it on the server only; the vendor stresses
  that it must never reach the browser or app.
- A wrong pair answers `error: 2`, `errMessage: "Wrong secret"` (the `fiscal-data` page
  prints `error: 1`, `"wrong secret"`).
- Exceptions: `check_sms_key` and `check_pan` (partner OTP steps) take no secret in the
  documented body; they are bound to the integer `paymentId`. Call them from your server
  anyway (derived).

## The `test` flag

- `prepare_payment` takes `test: true` for a test payment. The flag is **optional** and
  when it is missing the payment is **real**. There is no separate sandbox host.
- The transaction object echoes it as `isTest` / `test`.
- Read the flag from configuration per environment; never default it in code (derived).
  Warning [`octo.test-flag-real-money`](../lifecycle/README.md).

## Envelope

Success:

```json
{"error": 0, "data": {"shop_transaction_id": "100001", "octo_payment_UUID": "<uuid>", "status": "created"},
 "apiMessageForDevelopers": "", "shop_transaction_id": "100001", "...": "top-level copies of data"}
```

Error (schema [`schemas/envelope.json`](schemas/envelope.json), example
[`examples/error-wrong-secret.response.json`](examples/error-wrong-secret.response.json)):

```json
{"error": 2, "errMessage": "Wrong secret", "data": null, "errorMessage": "Wrong secret",
 "apiMessageForDevelopers": "..."}
```

- Check `error == 0` first; HTTP status alone is not documented as the signal (derived).
- `errorMessage` is deprecated; read `errMessage`. The vendor announces that every field
  except `error` and `errMessage` will move into `data`, so read `data.*`, never the
  top-level copies.
- `block_card_token` answers `{error, errMessage, status}` with no `data`.
- Unhandled failures come from a global handler as `{title, status: 500, detail}` (the
  error-codes page spells it `details`); treat any body without `error` as a failure.
- In this skill, each schema's `result` is the content of `data`, and the examples keep
  only `{error, data}`. To check a real reply, trim it first:
  `jq '{error, data}' reply.json | python3 scripts/validate.py prepare-payment - --part result`.

## Statuses

| Status | Meaning |
|---|---|
| `created` | payment registered, the payer has not finished |
| `wait_user_action` | waiting for the payer (OTP entry) |
| `waiting_for_capture` | two-stage: funds are held, Octo waits for your `set_accept` |
| `succeeded` | paid (final, refundable) |
| `canceled` | cancelled by you, by timeout or after a failure |

`set_accept` and refunds also mention `failed` and `pending`; the two-stage page spells
the stop value `waiting_user_action`. Treat unknown values as non-final and re-check.

## Notifications (`notify_url`)

Schema [`schemas/notification.json`](schemas/notification.json), example
[`examples/notification.request.json`](examples/notification.request.json).

- Sent for payments created through the API, `POST` JSON to `notify_url` from
  `prepare_payment`; without it, to the URL set in the cabinet.
- Body: `shop_transaction_id*`, `octo_payment_UUID*`, `status*`, `signature*`, `hash_key*`,
  `currency*`, `card_vendor*`, plus `total_sum`, `transfer_sum`, `refunded_sum`,
  `card_country`, `maskedPan`, `rrn`, `riskLevel` (0..5), `payed_time`, `card_type`,
  `is_physical_card`.
- `signature` is `sha1(unique_key, octo_payment_UUID, status)` in upper-case hex.
  `unique_key` is a separate value from Octo's technical team, not `octo_secret`. The
  separator is not documented; concatenation without one is assumed and `hash_key`'s
  role is not explained. Check it with `scripts/sign.py`, never by hand: export
  `OCTO_UNIQUE_KEY`, then `python3 scripts/sign.py octo.notify notification.json` prints
  `MATCH` or `MISMATCH` against the body's `signature`.
- The vendor says notifications are **not** signed with your secret and advises asking
  for the real status before you change an order. Re-check with the status call
  ([`../payment-page/`](../payment-page/README.md)) on every notification. Warning
  [`octo.notify-verify-status`](../lifecycle/README.md).
- The expected answer and the retry policy are not documented. Answer HTTP `200` quickly
  and make the handler idempotent by `octo_payment_UUID` + `status` (derived).
- `card_vendor` is documented as `Mastercard`, `Uzcard`, `Humo`, `UnionPay`, yet the
  sample sends `Visa`; accept any string.

## Basket items (fiscal data)

Shared model [`schemas/basket-item.json`](schemas/basket-item.json): `position_desc*`
(Latin letters, digits, spaces and `- . _ ( )`), `count*`, `price*` (unit price), `spic`,
`inn` or `pinfl`, `package_code*`, `nds*` (`0` no VAT, `1` VAT included). Each item must
already be registered with Octo; see [`../fiscal/`](../fiscal/README.md).

## Error codes

Octo's own `error` values seen on the method pages:

| Code | Where | Meaning | Action (derived) |
|---|---|---|---|
| `0` | all | success | read `data` |
| `1` | `block_card_token`, `fiscal-data` | data format error / wrong secret | fix the request |
| `2` | all | wrong `octo_shop_id` / `octo_secret` | fix configuration; do not retry |
| `4` | `block_card_token` | internal error | retry later |
| `5` | `block_card_token` | token not found | drop the stored token |
| `6` | `block_card_token` | token is not `active` | re-read your token state |
| `17` | `check_pan` | OTP resend limit reached | start a new payment |
| `20` | `bind_card` | an active or pending token already exists for the card | reuse the existing token |
| `22` | `refund` | wrong refund amount | check limits ([`../refunds/`](../refunds/README.md)) |
| `403` | `prepare_payment` | basket item not registered as a fiscal object | register it with Octo first |

Processing-centre codes (passed through from the card networks):

| Range | Network | Meaning |
|---|---|---|
| `100`-`130` | Humo | declines, for example `101` expired card, `116` insufficient funds, `117` incorrect PIN |
| `180`-`190` | Humo | pick-up (lost, stolen, counterfeit card) |
| `191`-`499` | Humo | status and reversal messages |
| `500`-`700` | Humo | format, routing and issuer availability declines (`600` issuer timed out) |
| `9`, `10`, `11`, `12`, `15` | Uzcard | wrong PAN, wrong expiry, Uzcard unavailable, card not found or expired, card blocked |
| `16`, `17`, `18` | Uzcard | authorization already completed, SMS resend limit, time exceeded |
| `500` | Uzcard | `verification_record_not_found` |
| `702` | Uzcard | Unired card not allowed |

Code `500` means a Humo format error and an Uzcard verification error; look at the card
network before acting on it.
