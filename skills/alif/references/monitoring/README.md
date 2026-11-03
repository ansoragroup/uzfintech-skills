# Alif Monitoring (card transaction history)

Hand-written notes. Transport, auth, errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.alifpay.uz/monitoring/ (Russian page)
- Fetched: 2026-11-03

## `POST /history`

| Param | Type | Rule |
|---|---|---|
| `id*` | string | unique request id |
| `token*` | string | confirmed card token |
| `from_date*` | string | `YYYY-MM-DD` |
| `to_date*` | string | `YYYY-MM-DD` |

Response: `{"txns": [txn, ...]}`. Transaction: `number` (string id), `type`, `time`
(ISO-8601), `amount` (tiyin), `merchant` (shown in the sample, not in the attribute list),
`city`, `street`, `mcc` (string), `currency` (`UZS`, `USD`, ...).

`type` values (shared with [summary](../summary/README.md)): `DEBIT`, `CREDIT`, `P2P_DEBIT`,
`P2P_CREDIT`, `DEBIT_REVERSAL`, `CREDIT_REVERSAL`, `P2P_DEBIT_REVERSAL`,
`P2P_CREDIT_REVERSAL`, `CASH_IN`, `CASH_OUT`, `REFILL_FROM_BANK_ACCOUNT`.

## Gotchas

- Humo: only the last three months are available, and the range must not exceed one year.
- `amount` is unsigned; the direction comes from `type`.
- No pagination is documented; keep ranges short.

## Examples

[`examples/`](examples/): history request/response.
