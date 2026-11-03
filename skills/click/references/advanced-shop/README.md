# Click Advanced Shop and Split Shop (JSON webhooks with free-form params)

Hand-written notes. Schemas are in [`schemas/`](schemas/) and bodies in
[`examples/`](examples/). Credentials are in [`../common/README.md`](../common/README.md).
The classic form-encoded protocol is in [`../shop-api/README.md`](../shop-api/README.md).

- Source: https://docs.click.uz/en/additional/get-info (Advanced Shop),
  https://docs.click.uz/en/additional/shop-split (Split Shop)
- Fetched: 2026-11-03
- Direction: **Click calls you**, POST with `Content-Type: application/json; charset=utf-8`.
  You answer in JSON.

## When to use which

| Protocol | Use it when |
|---|---|
| SHOP API | the payer enters one id (`merchant_trans_id`) and pays an amount |
| Advanced Shop | the payment needs several fields (`contract`, `full_name`, `region`, ...), you want to show the payer details before paying (getinfo), and Click should check and reconcile with you (check, compare) |
| Split Shop | as Advanced, and one payment must be split between several counterparties registered at Click |

Agree with Click which protocol each `service_id` uses before you build the handler.

## Actions

**`action` numbers differ from the SHOP API.** Here `0` is getinfo, `1` prepare and `2`
confirm; in the SHOP API `0` is Prepare and `1` is Complete.

| `action` | Name | Advanced | Split | Purpose |
|---|---|---|---|---|
| 0 | getinfo | yes (optional) | yes (optional) | show the payer details before paying; no signature |
| 1 | prepare | yes | yes | validate the payment and return bank details; Split adds `split` |
| 2 | confirm (complete) | yes | yes | the payment went through; record it |
| 3 | check | yes | not documented | Click asks for the outcome of an attempt |
| 4 | compare | yes | not documented | Click asks for your payment registry for a period |

## Signature

```
sign_string = md5(click_paydoc_id + attempt_trans_id + service_id + SECRET_KEY + <params values> + action + sign_time)
```

`<params values>` is every value of the `params` object, concatenated in the order they
appear in the request body. getinfo and compare carry no signature in the docs.

## Fields

Requests:

| Field | Type | In | Notes |
|---|---|---|---|
| `click_paydoc_id` | int / bigint | 1, 2, 3 | Click's payment id |
| `attempt_trans_id` | int / bigint | 1, 2, 3 | a new value for every retry; the pair with `click_paydoc_id` is unique |
| `service_id` | int | all | your service |
| `action` | int | all | see the table above |
| `merchant_prepare_id` | varchar (Advanced) / bigint (Split) | 2, 3 | the value you returned from prepare |
| `params` | object | 0, 1, 2, 3 | `"key": "value"` payment fields; the amount travels here as `amount` |
| `sign_time` | varchar | 1, 2, 3 | `YYYY-MM-DD HH:mm:ss` |
| `sign_string` | varchar | 1, 2, 3 | MD5 hex |
| `from_date`, `till_date` | varchar | 4 | `YYYY-MM-DD HH:mm:ss` |

Responses always carry `error` (int) and `error_note`. Per action:
- getinfo: `params` with the details to show (keys are yours).
- prepare: `click_paydoc_id`, `attempt_trans_id`, optional `merchant_prepare_id`, `params`
  (for example the branch and settlement account), and for Split `split`.
- confirm: `click_paydoc_id`, `attempt_trans_id`, optional `merchant_confirm_id`, `params`.
- check: `click_paydoc_id`, `attempt_trans_id`, `params`, and `status`:

| `status` | Meaning | What Click does |
|---|---|---|
| 0 | not processed yet | retries the payment |
| 1 | processing failed | cancels the payment |
| 2 | processed | marks the payment successful |

- compare: `requests`, an object keyed by `click_paydoc_id`, each value holding
  `click_paydoc_id` and `params`.

Split `split` items: `cntrg_id` (int, the counterparty id at Click) and `amount` (float).
The amounts must add up to the payment amount. The docs warn that the item field names may
differ, so confirm them with Click for your service.

## Standard `params` keys

Click defines these keys; use them instead of inventing your own where they fit:
`account`, `act_num`, `address`, `amount`, `apart_num`, `birthday`, `branch_id`,
`caller_id`, `card_num`, `category`, `contract`, `credit_id`, `cross_phone`, `date`, `email`,
`full_name`, `house_num`, `internet_package`, `invoice`, `login`, `order_num`,
`payment_account`, `payment_mfo`, `phone_num`, `property_id`, `receipt_num`, `region`,
`security_code`, `service_type`, `TIN`, `transit_account`, `transit_mfo`.

## Error codes you return

The same as the SHOP API (`0`, `-1` ... `-9`), with `-5` reading "User does not exist by
params" (no match for the `params` you received). The examples also show custom codes such
as `-250` "Subscriber not found". As in the SHOP API, a negative `error` from Click means
cancel and answer `-9`.

## Gotchas

1. Signature order follows the request body. Parse JSON with an order-preserving map, and
   beware of JavaScript objects, which move integer-like keys to the front.
2. Concatenate `params` values exactly as sent. A number `1000` and a string `"1000"` give
   the same text, but `1000.0` does not. Keep the raw values.
3. Idempotency is per `(click_paydoc_id, attempt_trans_id)`. A retry has a new
   `attempt_trans_id` for the same `click_paydoc_id`, so do not book the payment twice
   across attempts: key the payment itself on `click_paydoc_id`.
4. `merchant_prepare_id` is a string in Advanced Shop and a bigint in Split Shop. Accept
   both on input.
5. The request tables list no `error` field, yet the error page says Click can send a
   negative one. Handle it if it appears.
6. `check` drives Click's decision. Answer `0` only while you are truly still processing;
   `1` makes Click cancel the payment.
7. Answer `compare` from your ledger for the exact window, including payments that came
   through retries.

## Examples

- [`getinfo.request.json`](examples/getinfo.request.json) /
  [`getinfo.response.json`](examples/getinfo.response.json)
- [`prepare.request.json`](examples/prepare.request.json) /
  [`prepare.response.json`](examples/prepare.response.json)
- [`prepare-split.response.json`](examples/prepare-split.response.json)
- [`confirm.request.json`](examples/confirm.request.json) /
  [`confirm.response.json`](examples/confirm.response.json)
- [`check.request.json`](examples/check.request.json) /
  [`check.response.json`](examples/check.response.json)
- [`compare.request.json`](examples/compare.request.json) /
  [`compare.response.json`](examples/compare.response.json)
- [`error.response.json`](examples/error.response.json)
