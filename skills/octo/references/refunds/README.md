# Octo refunds (full or partial, after a succeeded payment)

Hand-written notes. Transport, auth, envelope and error codes:
[`../common/README.md`](../common/README.md). Releasing a two-stage hold is not a refund:
use `set_accept` with `cancel` ([`../payment-page/`](../payment-page/README.md)). Schema:
[`schemas/refund.json`](schemas/refund.json). Examples: [`examples/`](examples/).

- Source: https://help.octo.uz/refunds.html, https://help.octo.uz/cancel.html (Russian pages)
- Fetched: 2026-11-04
- Needs: the shop pair and the `octo_payment_UUID` of a payment in status `succeeded`.

## Flow

```
payment status succeeded (one-stage, or two-stage after capture)
POST /refund {octo_shop_id, shop_refund_id, octo_secret, octo_payment_UUID, amount}
   └─> data {octo_payment_UUID, refund_id, refund_time, status succeeded|pending|failed}
pending ─> re-check the payment status (refunded_sum) until it settles (derived)
```

## Method

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| refund | `POST /refund` | `octo_shop_id*`, `shop_refund_id*` (your id, unique per refund), `octo_secret*`, `octo_payment_UUID*`, `amount*` | `octo_payment_UUID`, `refund_id` (Octo id), `refund_time`, `status` |

## Limits

- Only payments in status `succeeded` can be refunded. A held two-stage payment
  (`waiting_for_capture`) is released with `set_accept` / `cancel` instead. Warning
  [`octo.cancel-only-holds`](../lifecycle/README.md).
- Each refund is at least **1 USD** or the UZS equivalent; smaller amounts are rejected.
- A single refund and the sum of all refunds may not exceed the original payment.
- One refund call may not exceed **10 mln UZS**; the number of refund calls is not
  limited, so a larger amount is split into several calls with distinct
  `shop_refund_id` values.
- These limits are printed on the page, but the time window after the payment is not.
  Warning [`octo.refund-limits`](../lifecycle/README.md).

## Errors

| Case | Answer |
|---|---|
| wrong shop pair | `error: 2`, `errMessage: "Wrong secret"` |
| amount below the minimum, above the rest, or above the per-call cap | `error: 22`, `errMessage: "Wrong amount to refund."` (example [`examples/error-wrong-amount.response.json`](examples/error-wrong-amount.response.json)) |
| payment not `succeeded` | not printed; expect a non-zero `error` (derived) |

## Gotchas

- Generate `shop_refund_id` once per refund intent and store it before the call, so a
  retry after a timeout reuses it. Octo describes it as a unique request id; what it
  answers to a repeated id is not printed (derived).
- `status: pending` is not final. Do not refund again; re-read the payment and compare
  `refunded_sum` (derived).
- `refund_time` is described as ISO 8601, but the sample prints `yyyy-MM-dd HH:mm:ss`.
  Parse both.
- Partial refunds keep the payment `succeeded`; track the running total yourself against
  `refunded_sum` so you never ask for more than the rest (derived).
- A refund of a fiscalized payment needs a return receipt; the refund page does not say
  whether Octo issues it ([`../fiscal/`](../fiscal/README.md)).

## Examples

[`examples/`](examples/): refund request/response (partial), error-wrong-amount response.
