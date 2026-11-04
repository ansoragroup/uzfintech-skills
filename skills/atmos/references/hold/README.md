# Atmos Holding (freeze an amount on an Uzcard / Humo card, capture or release it later)

Hand-written notes. Transport, auth, error codes and `ofd_items`:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/). Visa / Mastercard holds are a separate API:
[`../mps/README.md`](../mps/README.md#holding).

- Source: https://docs.atmos.uz/en/#holding, https://docs.atmos.uz/en/#create-a-hold-request,
  https://docs.atmos.uz/en/#confirm-holding-request,
  https://docs.atmos.uz/en/#create-a-request-for-multiple-holding,
  https://docs.atmos.uz/en/#confirm-application-for-multiple-holding,
  https://docs.atmos.uz/en/#withdraw-the-held-amount,
  https://docs.atmos.uz/en/#holding-cancellation,
  https://docs.atmos.uz/en/#request-for-holding-operation-data
- Fetched: 2026-11-04
- Needs: a Bearer token ([auth](../common/README.md#auth)), `store_id`, and either a card
  token ([`../cards/`](../cards/README.md)) or the card number and expiry (SMS flow, PCI DSS
  scope).

## Flow

```
POST /hold/create {card_token | card_number + card_expiry, store_id, account, amount, duration, payment_details?}
   └─> hold_id                               (SMS sent only when no token is used)
PUT  /hold/apply/{hold_id} {otp}             (otp = SMS code, or 111111 with a token)
   └─> hold_id, hold_till                    funds frozen until hold_till
then, before hold_till, one of:
   capture: POST   /hold/{hold_id} {amount?, ofd_items?}  -> store_transaction, success_trans_id, ofd_url
   release: DELETE /hold/{hold_id} {send_cancel_sms}
GET /hold/{hold_id}  -> store_transaction (state at any time)
```

Multiple hold: `POST /hold/multiple/create {card_token, duration, items[]}` returns a
`parent_id`; `PUT /hold/multiple/apply/{parent_id} {otp}` returns one `hold_id` per item.
Each item is then captured or released on its own with `POST` / `DELETE /hold/{hold_id}`.

## Methods

| Method | Endpoint | Params (`*` required) | Result |
|---|---|---|---|
| hold-create | `POST /hold/create` | `store_id*`, `account*`, `amount*`, `duration*` (minutes), `card_token` or `card_number` + `card_expiry` (`YYmm`), `payment_details` | `hold_id` |
| hold-apply | `PUT /hold/apply/{id}` | path `id*` (hold_id), `otp*` | `hold_id`, `hold_till`, `card_token`, `card_pan` |
| hold-multiple-create | `POST /hold/multiple/create` | `card_token`, `duration*`, `items*[] {store_id, account, amount, payment_details}` | `parent_id`, `items[]` |
| hold-multiple-apply | `PUT /hold/multiple/apply/{id}` | path `id*` (parent_id), `otp*` | `parent_id`, `items[] {result, hold_id, hold_till}` |
| hold-capture | `POST /hold/{id}` | path `id*`, `amount` (not above the held amount), `ofd_items` (sample only) | `store_transaction`, `ofd_url`, `ofd_url_commission` |
| hold-cancel | `DELETE /hold/{id}` | path `id*`, `send_cancel_sms*` | `status`, `processing` |
| hold-get | `GET /hold/{id}` | path `id*` | `store_transaction` |

## Errors

| Code | Meaning | What to do |
|---|---|---|
| `STPIMS-ERR-142` | hold not confirmed | the cardholder did not enter the code, or `apply` failed: create a new hold |
| `STPIMS-ERR-143` | hold not removed | read `GET /hold/{id}`, retry the `DELETE` later |
| `STPIMS-ERR-144` | hold time expired | too late to capture; charge again with a normal payment |
| `STPIMS-ERR-145` | not in the error table; the vendor sample returns it with "hold cancelled" as the **successful** answer to `DELETE` | treat it as released, then confirm with `GET /hold/{id}` |

Other codes: [`../common/README.md`](../common/README.md#error-codes-resultcode).

## Gotchas

- `duration` is in **minutes**. Capture before `hold_till` from the `apply` answer; after
  it you get `STPIMS-ERR-144` and the money is released. The longest allowed duration is
  not published; ask Atmos.
- Creating a hold freezes nothing. Only `PUT /hold/apply/{id}` does.
- The path id goes in the URL (`/hold/apply/{id}`), not in the body. The vendor HTTP line
  prints `{id}}`; it is a typo.
- Capture may take a **smaller** `amount`; it must not exceed the held amount. Leaving it
  out captures the whole hold (derived). Whether the rest is released at once is not
  stated.
- The capture table lists only `amount`, but the sample also sends `ofd_items`. Send the
  fiscal lines for the amount you capture (derived, see
  [lifecycle](../lifecycle/README.md#fiscal-receipts)). The sample's item amount does not
  add up to its capture amount; do not copy it.
- `send_cancel_sms` is marked required on `DELETE`; always send `true` or `false`.
- `DELETE` with a body: some HTTP clients drop it. Check yours sends it.
- `hold_till` comes without a time zone (for example `2026-11-04T13:00:00.000`); assume
  Tashkent time (UTC+5) only after confirming with Atmos.
- There is no documented refund for a captured `/hold` transaction. The capture answer
  carries a `success_trans_id` like `pay/apply`, so `pay/reverse` is the likely route;
  confirm with Atmos before you rely on it.
- Multiple hold: the table has only `card_token`, so it looks token-only; the note above it
  says card number and expiry also work. Each `items[]` entry may name a different
  `store_id`.

## Examples

[`examples/`](examples/): hold-create, hold-apply, hold-multiple-create,
hold-multiple-apply, hold-capture, hold-cancel (request and response each), hold-get
(response).
