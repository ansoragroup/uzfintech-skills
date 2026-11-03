# Multicard Hold (block funds on a bound card, then charge or release)

Hand-written notes. Transport, auth, errors, statuses, `ofd` and `split`:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://docs.multicard.uz/4488548f0 (guide), https://docs.multicard.uz/19729318e0,
  https://docs.multicard.uz/19729319e0, https://docs.multicard.uz/19729320e0,
  https://docs.multicard.uz/19729321e0, https://docs.multicard.uz/19729322e0 (Russian pages)
- Fetched: 2026-11-03
- Needs: a bound card token ([`../cards/`](../cards/README.md)).

## Flow

```
POST /payment/hold {card{token}, amount, store_id, invoice_id, expiry, split?}
   └─> hold {id, status draft, expiry, payment{uuid, otp_hash, checkout_url}}  ─> SMS to payer
       store data.payment.uuid: every later call uses it
PUT /payment/hold/{payment.uuid} {otp}   (or redirect to payment.checkout_url)
   └─> hold status active, payment status hold: funds blocked
then, before expiry, one of:
   PUT /payment/hold/{payment.uuid}/charge {amount?, split?, ofd?}  ─> payment success
   DELETE /payment/hold/{payment.uuid}                              ─> hold canceled
after expiry the funds return to the card automatically
```

With acceptless debit enabled for your account and a previously bound card, confirm with
an empty body.

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| create-hold | `POST /payment/hold` | `card*{token*}`, `amount*`, `store_id*`, `invoice_id*`, `expiry*` (minutes, 1..43200 = 30 days), `split` | hold |
| confirm-hold | `PUT /payment/hold/{uuid}` | `otp*` (empty body for acceptless) | hold |
| charge-hold | `PUT /payment/hold/{uuid}/charge` | `amount` (below the held amount; omit to charge all), `split`, `ofd` | payment |
| get-hold | `GET /payment/hold/{uuid}` | path `uuid` | hold |
| cancel-hold | `DELETE /payment/hold/{uuid}` | path `uuid` | hold (`canceled`) |

`{uuid}` is always the **payment** uuid (`data.payment.uuid`), not the hold `id`.

Hold object: `id`, `status`, `expiry`, `added_on`, `updated_on`, `payment` (the payment
object). Hold statuses seen in the examples: `draft`, `active`, `canceled`; the docs give no
full list.

## Errors

| Case | Answer |
|---|---|
| create: validation | `400 ERROR_FIELDS` |
| confirm: wrong or expired SMS code | `400 ERROR_WRONG_OTP` / `423` (as for payments) |
| charge: outcome unknown | `400 ERROR_DEBIT_UNKNOWN` or `ERROR_CALLBACK_TIMEOUT`: poll `GET /payment/{uuid}` until `success` or `error` |
| cancel: hold not active (charged or expired) | `403 ERROR_PAYMENT_APPLIED` (the text says 400) |

## Gotchas

- `expiry` is in **minutes**, not seconds; the maximum is 43200 (30 days). Charge before it
  runs out, or the funds go back to the payer.
- The charge schema marks `amount` required, but the text allows leaving it out to charge
  the whole hold and adding `split` and `ofd`. Send `amount` explicitly (derived).
- A charge amount must be **below** the held amount; you cannot charge more than you held.
- Pass `ofd` on charge when Multicard fiscalizes; the create call has no `ofd`.
- Never repeat a charge after a timeout or an unknown outcome; poll the payment.
- To release funds, cancel the hold. `DELETE /payment/{uuid}` is the refund call for
  completed payments ([`../payments/`](../payments/README.md)).

## Examples

[`examples/`](examples/): create-hold request/response, confirm-hold request/response,
charge-hold request/response, cancel-hold error.
