# Atmos common: transport, auth, errors and the Callback API

Hand-written notes that apply to every Atmos product. Schemas: [`schemas/`](schemas/).
Examples: [`examples/`](examples/).

- Source: https://docs.atmos.uz/en/#authorization-in-api, https://docs.atmos.uz/en/#token-update,
  https://docs.atmos.uz/en/#revoke-a-token, https://docs.atmos.uz/en/#system-status-and-errors,
  https://docs.atmos.uz/en/#callback-api (English page; the same content is at
  https://docs.atmos.uz/ru/ and https://docs.atmos.uz/uz/)
- Fetched: 2026-11-04

## Transport

| Item | Value |
|---|---|
| API host | `https://apigw.atmos.uz` for every product and for the token |
| Path prefixes | `/merchant` (payments), `/partner` (card linking), `/hold`, `/ppa` (PINFL), `/mps`, `/checkout` and `/mps-extend/<partner>` (Visa / Mastercard) |
| Body | JSON, `Content-Type: application/json`; only `/token` and `/revoke` take a form body |
| Amounts | integer **tiyin** (1 UZS = 100 tiyin) in every product |
| Language | optional `lang`: `uz`, `ru` or `en` (partial reversal samples send `RU`) |
| Sandbox host | none published; the docs give test cards only ([sandbox](../sandbox/README.md)) |

`partner.atmos.uz` is not described in the public API docs. The card-linking calls live at
`https://apigw.atmos.uz/partner/...`, a path on the API host, not that host. Ask Atmos
before you call anything on `partner.atmos.uz`.

## Auth

| Call | Request | Answer |
|---|---|---|
| Get a token | `POST https://apigw.atmos.uz/token`, form `grant_type=client_credentials`, header `Authorization: Basic base64(consumer_key:consumer_secret)` | `{access_token, scope, token_type: "Bearer", expires_in}` |
| Extend it | the same call with `grant_type=client_credentials` and `refresh_token=<current access_token>` | the same shape |
| Revoke it | `POST https://apigw.atmos.uz/revoke`, form `token=<access_token>`, same Basic header | the vendor sample shows the token shape |

- `consumer_key` and `consumer_secret` are issued by Atmos after the merchant is registered.
  Keep them on the server. `python3 scripts/sign.py atmos.basic` builds the Basic header
  (`ATMOS_CONSUMER_SECRET` from the environment).
- Every other call sends `Authorization: Bearer <access_token>`. Two vendor samples print
  `Bearer Bearer ...`; send the word once.
- The text gives the token **3600 seconds (1 hour)**; the samples show `expires_in` 2525
  and 1234. Cache the token, renew it before `expires_in` runs out, and on `401` get a new
  one and retry once.
- The Visa / Mastercard (MPS) section says its auth is separate, but documents the same
  `POST /token` call. It also says every MPS request carries an `apikey: <API_KEY>` header
  issued at connection; the samples show that header only on some calls. Send both headers
  on every `/mps`, `/checkout` and `/mps-extend` call (derived) and confirm with Atmos.
- The first `/token` curl puts `grant_type` in the query string; send it as the form body.

## Answer envelopes

Each module answers in its own shape. Branch on the HTTP status first, then on the code.

| Module | Success | Failure |
|---|---|---|
| `/merchant`, `/partner`, `/hold` | `result: {code: "OK", description}` plus data | `result.code` = `STPIMS-ERR-NNN` ([status.json](schemas/status.json)) |
| `/ppa` (PINFL) | `{payload, code: "200", description \| message}` | negative codes `-100` ... `-308` ([pinfl](../pinfl/README.md#errors)) |
| `/mps`, `/mps-extend` | `{payload, status: {code: 0, message: "Success", trace_id}}` | `status.code` negative ([mps](../mps/README.md#errors)) |
| `/checkout` | `{..., status: {code: "OK" or "0", description}}` | not shown in the samples |

HTTP statuses: `400` bad request, `401` not authorized, `403` forbidden, `404` not found,
`405` method does not exist, `429` too many requests, `500` server error (try later), `503`
service unavailable.

## Error codes (`result.code`)

The full `STPIMS-ERR-001` ... `STPIMS-ERR-144` list is at
https://docs.atmos.uz/en/#transaction-errors. The codes an integration must handle:

| Code | Meaning | What to do |
|---|---|---|
| `OK` | no errors | continue |
| `STPIMS-ERR-004`, `-030`, `-043`, `-090` | card not found, or wrong expiry | ask the payer to re-enter the card |
| `STPIMS-ERR-006`, `-007`, `-009` | missing or badly formatted parameters | fix the request; do not retry as is |
| `STPIMS-ERR-031` | request limit exceeded | back off |
| `STPIMS-ERR-057`, `-112` | insufficient funds | show to the payer |
| `STPIMS-ERR-058`, `-067` ... `-088` | card blocked, expired or refused by the issuer | show to the payer; tell them to call the bank |
| `STPIMS-ERR-064`, `-100` | payment cancelled / cancelled before | final; do not fulfil |
| `STPIMS-ERR-065`, `INFO-202` | payment in progress | poll `pay/get`; do not resend |
| `STPIMS-ERR-066` | the account was paid recently | try later; check for a duplicate order |
| `STPIMS-ERR-092` | transaction closed | read `store_transaction`: the vendor sample returns it for a paid transaction |
| `STPIMS-ERR-093` | error in the provider's billing; Atmos calls the merchant the provider, so this most likely means your Callback API answer (derived) | check the callback handler |
| `STPIMS-ERR-098` | wrong OTP | let the payer retry; resend with `pay/otp-resend` |
| `STPIMS-ERR-101` | transaction not cancelled | read the transaction, retry the reverse later |
| `STPIMS-ERR-102` | SMS not sent (gateway down) | resend later |
| `STPIMS-ERR-118` | payment status unknown | poll `pay/get`; never pay again |
| `STPIMS-ERR-142`, `-143`, `-144` | hold not confirmed, hold not removed, hold time expired | see [hold](../hold/README.md#errors) |
| `INFO-201` | code sent to the card's SMS number | wait for the OTP |

## Fiscal items

`ofd_items[]` carries the fiscal receipt lines ([ofd-item.json](schemas/ofd-item.json)):
`ofd_code` (IKPU / MXIK code), `name`, `amount` (tiyin) and `details[] {key, value}` with
keys `quantity`, `package_code`, `mxik_code`, `mark_code`. A paid transaction returns
`ofd_url` (goods receipt) and `ofd_url_commission` (fee receipt). PINFL and Visa /
Mastercard use their own item shapes; see their READMEs and
[lifecycle](../lifecycle/README.md#fiscal-receipts).

## Callback API (your billing URL)

Before Atmos confirms a `/merchant` payment it calls your billing system. Money is taken
only if you accept.

1. The billing URL is agreed with Atmos during integration (a resource URL).
2. Atmos sends `POST {store_id, transaction_id, transaction_time, amount, invoice, sign}`
   ([callback.json](schemas/callback.json)). `invoice` is the `account` you sent in
   `pay/create`; `amount` is tiyin.
3. Check `sign` = hash of `store_id + transaction_id + invoice + amount + api_key`, joined
   with no separators. Atmos issues the `api_key`. The docs do **not** name the hash:
   `python3 scripts/sign.py atmos.callback body.json` (`ATMOS_API_KEY` from the
   environment) tries md5, sha1 and sha256 and reports which matches. Compare in constant
   time.
4. Match `invoice` and `amount` to the order, then answer **HTTP 200**
   `{"status": 1, "message": "Successfully"}`. To refuse, answer `{"status": 0, "message":
   "<reason>"}`. Anything other than 200 with `status` 1 means no debit.
5. Accept calls only from the Atmos address published at
   https://docs.atmos.uz/en/#callback-api; take it from that page, do not hard-code a copy.

Retries, the answer timeout and duplicate handling are not documented
([lifecycle](../lifecycle/README.md#retries-and-idempotency)). The Visa / Mastercard
bind-by-owner flow sends a different callback, see [mps](../mps/README.md#card-linking-by-the-owner).

## Sandbox

Test cards, the OTP `111111` and the widget and payment-page test hosts are in
[`../sandbox/README.md`](../sandbox/README.md).
