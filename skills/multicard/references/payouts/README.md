# Multicard Payouts (credit Uzcard and Humo cards from your partner wallet)

Hand-written notes. Transport, auth, errors and statuses:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://docs.multicard.uz/4488549f0 (guide), https://docs.multicard.uz/19729323e0,
  https://docs.multicard.uz/19729324e0, https://docs.multicard.uz/19729325e0 (Russian pages)
- Fetched: 2026-11-03
- Direction: money leaves your partner deposit (wallet) and lands on a payer's Uzcard or
  Humo card. Check the balance first with `GET /payment/application`
  ([`../reports/`](../reports/README.md)).

## Flow

```
GET /payment/application ─> wallet_sum (+ wallet_overdraft) covers the amount?
POST /payment/credit {card{pan | token}, amount, store_id, invoice_id, confirmable, device_details, kyc_data?}
   confirmable false or omitted ─> one-step payout, data.status final or poll
   confirmable true             ─> data.uuid (store it), status draft
       PUT /payment/credit/{uuid} {otp}  ─> payout executes
on ERROR_UNKNOWN or a timeout: GET /payment/credit/{uuid} until success or error
```

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| create-payout | `POST /payment/credit` | `card*{pan | token}` (Uzcard or Humo), `amount*`, `store_id*` (**string** here), `invoice_id*`, `confirmable` (marked required; `false` or omitted = one step), `device_details*{ip*, user_agent*}`, `kyc_data` (above 10 000 000 UZS) | payment |
| confirm-payout | `PUT /payment/credit/{uuid}` | `otp*` | payment |
| get-payout | `GET /payment/credit/{uuid}` | path `uuid` | payment |

`kyc_data` (all fields are strings and all are required when the object is sent):
`last_name`, `first_name`, `middle_name`, `passport`, `pinfl`, `dob` (`YYYY-MM-DD`),
`passport_expiry_date`. It identifies the **card holder**, not you.

## Errors

| Case | Answer |
|---|---|
| wrong card number | `400 ERROR_CARD_NOT_FOUND` |
| more than 10 000 000 UZS without `kyc_data` | `400 ERROR_FIELDS` ("identification required") |
| outcome unknown, or a timeout | `400 ERROR_UNKNOWN`: poll `GET /payment/credit/{uuid}` until `success` or `error` |

## Gotchas

- Never resend a payout after `ERROR_UNKNOWN` or a timeout: poll. A blind retry with the
  same body can pay twice (derived).
- `store_id` is typed **string** on create-payout and integer elsewhere; send what each
  schema says.
- `kyc_data` is marked required in the schema but is needed only above 10 000 000 UZS
  (1 000 000 000 tiyin). The response returns `kyc_data` as a **JSON-encoded string**, not
  an object; parse it before reading.
- The threshold is in UZS while `amount` is in tiyin; compare in the same unit.
- `confirmable` is marked required but may be omitted; send `false` explicitly for a
  one-step payout.
- Payouts go to Uzcard and Humo cards only. A full PAN puts you in PCI DSS scope; prefer a
  bound card token.
- `kyc_data` is personal data: keep it out of logs, and store only what your KYC policy
  requires.

## Examples

[`examples/`](examples/): create-payout request/response, create-payout request with
`kyc_data`, confirm-payout request.
