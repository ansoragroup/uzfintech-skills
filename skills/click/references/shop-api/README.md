# Click SHOP API (Prepare / Complete webhooks)

Hand-written notes. Schemas are in [`schemas/`](schemas/) and bodies in
[`examples/`](examples/). Credentials, the signature rule and units are in
[`../common/README.md`](../common/README.md).

- Source: https://docs.click.uz/en/shop-api/, https://docs.click.uz/en/shop-api/requests,
  https://docs.click.uz/en/shop-api/errors, https://docs.click.uz/en/testing/postman
- Fetched: 2026-11-03
- Direction: **Click calls you.** You give Click two URLs on your billing server, one for
  Prepare and one for Complete (one URL that branches on `action` also works).

## Transport

| Item | Value |
|---|---|
| Method | `POST` from Click to your URLs, over HTTPS |
| Request body | `application/x-www-form-urlencoded`. Every value arrives as a string |
| Response body | JSON, with `error` (int) and `error_note` (string) always present |
| Auth | `sign_string` in the body: an MD5 hex digest that includes `SECRET_KEY` |
| Amount | `amount` is in **soums** and may carry decimals |
| Time | `sign_time` is `YYYY-MM-DD HH:mm:ss` |

The examples show the form fields as a JSON object for readability. On the wire they are
URL-encoded `key=value` pairs.

## Flow

```
payer pays in a CLICK channel (app, my.click.uz, USSD, Telegram, your link or button)
    │
    ▼
Prepare (action=0) ──> you: check sign, order, amount; reserve; return merchant_prepare_id
    │  error=0
    ▼
Click debits the payer
    │
    ▼
Complete (action=1, error=0)   ──> you: mark paid, return merchant_confirm_id
Complete (action=1, error<0)   ──> you: cancel the order, return -9
```

Invoices created with the Merchant API (`invoice/create`) are also paid through this flow:
the payer confirms the invoice in CLICK, then Click sends Prepare and Complete.

### Prepare (action = 0)

Request: `click_trans_id`, `service_id`, `click_paydoc_id`, `merchant_trans_id`, `amount`,
`action`, `error`, `error_note`, `sign_time`, `sign_string`.

```
sign_string = md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + amount + action + sign_time)
```

What to check, in this order:
1. The signature. On a mismatch, return `-1`.
2. `action` is `0`. Otherwise return `-3`.
3. The order, account or login in `merchant_trans_id` exists and can still be supplied.
   If not, return `-5`.
4. `amount` equals what is due. If not, return `-2`.
5. The order is not already paid (`-4`) or cancelled (`-9`).

Then store the attempt, **reserve the goods** so they cannot be sold twice, and return
`merchant_prepare_id` (your id for this attempt, an int).

### Complete (action = 1)

Request: the Prepare fields plus `merchant_prepare_id`, with `action = 1`.

```
sign_string = md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + merchant_prepare_id + amount + action + sign_time)
```

What to check: the signature (`-1`), `merchant_prepare_id` exists (`-6`), the amount
(`-2`), then the incoming `error`:
- `error < 0`: the payment failed on Click's side. Cancel the attempt, release the
  reservation and return `-9`.
- `error = 0`: mark the order paid and return `merchant_confirm_id`.

A repeated Complete for an attempt that is already paid returns `-4`. A Complete for an
attempt that is already cancelled returns `-9`.

### After Click has debited the payer

Once your Prepare succeeded and the money has been taken, your Complete answer **must not**
be an error, except `-4` (already paid) or `-9` (already cancelled). Click retries
erroneous answers and then hands the payment to manual investigation. If you cannot
deliver after all, answer success and then refund with
`DELETE payment/reversal/:service_id/:payment_id` from the Merchant API.

## Fields

Requests (form fields):

| Field | Type | Notes |
|---|---|---|
| `click_trans_id` | bigint | Click's id for this attempt. Echo it back |
| `service_id` | int | your service |
| `click_paydoc_id` | bigint | Click's payment number. Store it: the Merchant API `payment_id` is most likely this value, though the docs do not say so outright |
| `merchant_trans_id` | varchar | your order id, account or login, as the payer entered it |
| `merchant_prepare_id` | int | Complete only: the value you returned from Prepare |
| `amount` | float | soums |
| `action` | int | `0` Prepare, `1` Complete |
| `error` | int | `0` or a negative Click code |
| `error_note` | varchar | text for `error` |
| `sign_time` | varchar | `YYYY-MM-DD HH:mm:ss` |
| `sign_string` | varchar | MD5 hex, see above |

Responses (JSON): `click_trans_id`, `merchant_trans_id`, `merchant_prepare_id` (Prepare) or
`merchant_confirm_id` (Complete), `error`, `error_note`. The error page lists only `error`
and `error_note` for a failure, but echoing the ids does no harm.

## Error codes you return

| `error` | `error_note` (as documented) | When |
|---|---|---|
| 0 | Success | accepted |
| -1 | SIGN CHECK FAILED! | `sign_string` does not match |
| -2 | Incorrect parameter amount | amount differs from what is due |
| -3 | Action not found | `action` is not 0 or 1 |
| -4 | Already paid | the order or attempt is already completed |
| -5 | User does not exist | unknown `merchant_trans_id` |
| -6 | Transaction does not exist | unknown `merchant_prepare_id` |
| -7 | Failed to update user | your side could not save the change |
| -8 | Error in request from click | a required field is missing or malformed |
| -9 | Transaction cancelled | the attempt was cancelled, or Click sent `error < 0` |

Click's own `error` in the request is `0` for success or any negative value for a failure.

## Test scenarios (Postman generator)

The generator at https://docs.click.uz/en/testing/postman builds 15 requests against your
two URLs. Pick a test amount other than 300 (scenario 5 uses 300 as the wrong amount).
Expected answers:

| # | Request | Expected `error` |
|---|---|---|
| 1 | Prepare, bad signature | -1 |
| 2 | Prepare, unknown order | -5 |
| 3 | Prepare, valid | 0 |
| 4 | Complete, bad signature | -1 |
| 5 | Complete, amount 300 (signature valid) | -2 |
| 6 | Complete, valid | 0 |
| 7 | Complete again | -4 |
| 8 | Complete with `error=-5017` after success | -9 |
| 9 | Prepare, valid | 0 |
| 10 | Complete with `merchant_prepare_id=999999999` | -6 |
| 11 | Complete, valid | 0 |
| 12 | Prepare, valid | 0 |
| 13 | Complete with `error=-5017` | -9 |
| 14 | the same cancellation again | -9 |
| 15 | Complete after the cancellation | -9 |

Scenario 8 means a cancellation from Click wins over an earlier success: cancel and return
`-9`, not `-4`. The generator page calls the field `error_code`; your JSON must use `error`.

The exact inputs, signatures, run order and the generator's own inconsistencies are in
[`../sandbox/README.md`](../sandbox/README.md).

## Gotchas

1. Hash the **raw** strings from the form. Parsing `amount` to a float and printing it again
   (`1000.0`, `1000`) breaks the signature.
2. Compare money after parsing: convert `amount` to integer tiyin and compare it with the
   order total. Never compare floats directly.
3. `merchant_prepare_id` and `merchant_confirm_id` are ints. Do not return UUIDs or
   strings there.
4. Make both handlers idempotent on `click_trans_id`. Click repeats requests after timeouts
   and errors.
5. A negative `error` in a Complete always means cancel. Never mark the order paid on it.
6. Release the reservation when a Prepare is not followed by a successful Complete within
   your own timeout. The docs set no deadline.
7. The response must be JSON even for errors, with `error` as a number. Return HTTP 200.
   The docs define no other status code.
8. Restrict the endpoints to Click if you can. Click publishes no source IP list in the
   current docs, so the signature is the only documented protection.

## Examples

Requests are the form fields shown as JSON. `<MD5_HEX>` stands for the computed
`sign_string`.

- [`prepare.request.json`](examples/prepare.request.json) /
  [`prepare.response.json`](examples/prepare.response.json)
- [`complete.request.json`](examples/complete.request.json) /
  [`complete.response.json`](examples/complete.response.json)
- [`complete-cancel.request.json`](examples/complete-cancel.request.json) /
  [`complete-cancel.response.json`](examples/complete-cancel.response.json) (Click reports a
  failure, you answer `-9`)
- [`error.response.json`](examples/error.response.json) (bad signature)
