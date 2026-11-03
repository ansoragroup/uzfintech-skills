# Alif Card summary (scoring: monthly totals by transaction type)

Hand-written notes. Transport, auth, errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.alifpay.uz/summary/ (Russian page)
- Fetched: 2026-11-03

## `POST /getSummary`

| Param | Type | Rule |
|---|---|---|
| `id*` | string | unique request id (was `ref` in the old version) |
| `token*` | string | confirmed card token |
| `from*` | string | `YYYY-MM`; for Uzcard at least two months before the current date |
| `to*` | string | `YYYY-MM`; included in full; must be **before** the current month |

The range must not exceed one year.

## Response

An object keyed by month (`YYYY-MM`). Each month maps transaction `type` (same list as
[monitoring](../monitoring/README.md)) to `{amount, count}` (`amount` in tiyin). A month with
no transactions is still present, with `{}`.

```json
{"2026-07": {"DEBIT": {"amount": 1000000, "count": 2}}, "2026-08": {}}
```

## Gotchas

- Do not assume every type key is present; missing type = zero.
- The old version used `YYYY-MM-DD` ranges and `ref`; requests in that format are rejected
  by the current method.

## Examples

[`examples/`](examples/): getSummary request/response.
