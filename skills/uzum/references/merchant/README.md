# Uzum Merchant API (webhooks you implement)

Hand-written notes. Field tables and JSON Schemas are generated in
[`endpoints.md`](endpoints.md) and [`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_merchant.yaml (en labels: `en_merchant.yaml`)
- Fetched: 2026-11-03
- Direction: **Uzum Bank calls you.** You expose five HTTPS endpoints; Uzum is the client.

## Transport and auth

- `POST`, `Content-Type: application/json`, HTTPS only.
- `Authorization: Basic base64(<BASIC_USER>:<BASIC_PASSWORD>)`. You choose the
  credentials and hand them to Uzum during onboarding. Reject anything else with
  error `10001`.
- Your base URL is registered with Uzum, e.g. `https://merchant.example.com/uzum`,
  and Uzum appends `/check`, `/create`, `/confirm`, `/reverse`, `/status`.
- `serviceId` identifies your service in Uzum. Validate it on every call.

## Units and types

| Field | Type | Unit / rule |
|---|---|---|
| `serviceId` | int64 | issued by Uzum |
| `timestamp`, `transTime`, `confirmTime`, `reverseTime` | int64 | Unix epoch **milliseconds** |
| `transId` | string (uuid) | Uzum's transaction id, your idempotency key |
| `amount` | int64 | **tiyin** (1 UZS = 100 tiyin) |
| `params` | object | free-form keys you agreed with Uzum, e.g. `{"account": "100001"}` |
| `data` | object | map `key -> {"value": "<string>"}`; keys are your choice (e.g. `account`, `fio`) |
| `errorCode` | **string** | e.g. `"10014"`, not a number |

## Flow and state machine

```
check (no state) ──> create ──> CREATED ──confirm──> CONFIRMED ──reverse──> REVERSED
                                   │
                                   └─reverse──> REVERSED   (cancel before confirm)
```

1. `/check`: can this `params` be paid? Do not create anything. Return `status: "OK"`
   and optional `data` to show the payer (name, order number, amount due).
2. `/create`: persist a transaction keyed by `transId` with `amount`. Return
   `status: "CREATED"` and `transTime` (your creation time, ms).
3. `/confirm`: Uzum debited the payer. Mark paid, fulfil. Return `status: "CONFIRMED"`
   and `confirmTime`.
4. `/reverse`: cancel. Return `status: "REVERSED"` and `reverseTime`.
5. `/status`: return the current state: `CREATED`, `CONFIRMED` or `REVERSED`, with
   `transTime` and the matching `confirmTime` / `reverseTime`.

Timing rules from the contract:

- If `/confirm` answers 5xx or times out, Uzum polls `/status` (up to 10 times) to
  learn the outcome. Your `/status` must reflect a confirm that committed even if the
  HTTP response was lost.
- A transaction created but not confirmed within **30 minutes** should be treated as
  failed on your side (Uzum will not confirm it later).

## Request fields per operation (required)

| Op | Required fields | Optional |
|---|---|---|
| check | `serviceId`, `timestamp`, `params` | |
| create | `serviceId`, `timestamp`, `transId`, `params`, `amount` | |
| confirm | `serviceId`, `timestamp`, `transId`, `paymentSource`, `phone` | `tariff`, `processingReferenceNumber`, `cardType` |
| reverse | `serviceId`, `timestamp`, `transId` | |
| status | `serviceId`, `timestamp`, `transId` | |

Confirm-only fields:

| Field | Values / meaning |
|---|---|
| `paymentSource` | `UZCARD`, `HUMO`, `VISA`, `MASTERCARD`, `VISA_DOMESTIC`, `MASTERCARD_DOMESTIC`, `INSTALLMENT`, `CASHBACK`, `ACCOUNT`, `WALLET`, `VISAUZS`, `UZUM_DEBIT_VISA` |
| `tariff` | only for `INSTALLMENT` (e.g. `"003"`, `"15-0-4"`), otherwise `null` |
| `processingReferenceNumber` | processing RRN; only for Uzcard, Humo, Visa Uzum, Visa Kapital, otherwise `null` |
| `phone` | payer phone, digits, `998XXXXXXXXX` |
| `cardType` | `1` corporate, `2` private |

## Responses

- Success: HTTP **200** with `status` = `OK` / `CREATED` / `CONFIRMED` / `REVERSED`.
- Business error: HTTP **400** with `{"serviceId", "timestamp" or "transId", "status": "FAILED", "errorCode": "<string>"}`.
- Echo `serviceId` and `transId` back. Echo `amount` on create/confirm/reverse.

## Error codes (`errorCode`, string)

| Code | Meaning | Typical op |
|---|---|---|
| 10001 | Access denied (bad Basic auth) | all |
| 10002 | Body is not valid JSON | all |
| 10003 | Wrong HTTP method (only POST) | all |
| 10005 | Required parameter missing | all |
| 10006 | Invalid `serviceId` | check, create |
| 10007 | Payment attribute (`params` value) not found | check, create |
| 10008 | Already paid | check, create |
| 10009 | Payment cancelled | check, create |
| 10010 | `transId` already exists (duplicate create with different data) | create |
| 10011 | Invalid amount | create |
| 10012 | Amount below minimum | check, create |
| 10013 | Amount above maximum | check, create |
| 10014 | Transaction not found | confirm, reverse, status |
| 10015 | Transaction cancelled, cannot confirm | confirm |
| 10016 | Transaction already confirmed | reverse (policy) |
| 10017 | Transaction cannot be cancelled | reverse |
| 10018 | Transaction already cancelled | reverse |
| 99999 | Internal error | all |

## Idempotency rules (derived)

- `create` with an existing `transId` and identical `params`/`amount`: return the same
  `CREATED` response (same `transTime`). Different data: `10010`.
- `confirm` on an already `CONFIRMED` transaction: return `CONFIRMED` with the original
  `confirmTime` (retries happen after timeouts). On `REVERSED`: `10015`.
- `reverse` on `REVERSED`: `10018`, or the original `REVERSED` response if you prefer
  idempotent replies. Decide once and document it.
- A second `create` for an order that already has a live transaction: decide whether
  to reject (`10008` if paid) or allow; Uzum does not dedupe by `params`.

## Gotchas

- `errorCode` is a string in the schema; sending a JSON number fails strict parsers.
- `data` values must be wrapped: `{"account": {"value": "100001"}}`, not `{"account": "100001"}`.
- Timestamps are milliseconds. Seconds will look like dates in 1970.
- `amount` is tiyin. 150 000 UZS is `15000000`.
- `status` on `/status` is the transaction state, not `OK`.
- HTTP 400 is the only error status the contract describes. Do not answer 401/404
  for business errors; use 400 + `errorCode`.

## Examples

[`examples/`](examples/): `check`, `create`, `confirm`, `reverse`, `status` request and
response pairs plus an error reply.
