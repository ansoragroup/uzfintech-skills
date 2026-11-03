# Alif Hold (block funds on a tokenized card, charge later)

Hand-written notes. Transport, auth, errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.alifpay.uz/hold/ (Russian page)
- Fetched: 2026-11-03

## Flow

```
hold {id, amount, token} -> hold{dismissed: false}
  charge: pay {id: <new payment id>, amount, method: {type: HOLD, id: <hold id>}, receipt...}
  release: dismissHold {id}
  auto-release: 30 days (Uzcard), 10 days (Humo)
getHold {id} -> current state
```

## Methods

| Method | Params (`*` required) | Result |
|---|---|---|
| `hold` | `id*` (client-unique), `amount*` (tiyin), `token*` (confirmed card token) | hold struct |
| `dismissHold` | `id*` | hold struct |
| `getHold` | `id*` | hold struct |

Hold struct: `id`, `created_at` (ISO-8601), `amount` (tiyin), `dismissed` (bool).
`dismissed: true` means the funds were charged, released on request, or released on expiry.
The struct does not say which; track that yourself.

## Gotchas

- If `hold` times out, errors with `1003`, or returns any error from the common table, call
  `getHold {id}` before doing anything else; the hold may exist.
- `1108` insufficient funds: retry only with a **new** hold `id`.
- Charge the hold before the scheme's expiry (Humo 10 days, Uzcard 30 days).
- The hold `id` and the payment `id` are different identifiers.
- Sandbox cap: 5,000,000,000 tiyin per hold.

## Examples

[`examples/`](examples/): hold request/response, getHold response (dismissed), pay with
HOLD request.
