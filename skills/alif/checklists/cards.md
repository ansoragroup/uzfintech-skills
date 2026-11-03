# Checklist: Alif Cards, Hold, Monitoring and Summary

Contracts: [`../references/cards/README.md`](../references/cards/README.md),
[`../references/hold/README.md`](../references/hold/README.md),
[`../references/monitoring/README.md`](../references/monitoring/README.md),
[`../references/summary/README.md`](../references/summary/README.md). Also run [`common.md`](common.md).

## Cards
- [ ] `getCardToken` sends `phone` for Humo cards (required) and handles `1110` (phone mismatch) and `1104` (SMS off).
- [ ] The token is used only after `confirmCardToken` succeeds; OTP errors `1100` / `1101` / `1106` are handled.
- [ ] Only `token`, `masked_pan`, `bank_name` and `holder_name` are stored; PAN and expiry are discarded.
- [ ] `matchCardPIN` `false` on Humo is not treated as fraud by itself.
- [ ] `getCardType` `1005` means the scheme is unsupported (Uzcard / Humo only).

## Hold
- [ ] `hold` uses a client-unique `id` (persisted first), a tiyin `amount` and a confirmed token.
- [ ] On a timeout or any error, `getHold {id}` is called before acting; `1108` retries use a new `id`.
- [ ] Holds are charged (`pay` with `method {type: HOLD, id}`) or dismissed before expiry: Humo 10 days, Uzcard 30 days.
- [ ] The local state records why a hold became `dismissed: true` (charged, released or expired).

## Monitoring (`/history`)
- [ ] `from_date` / `to_date` are `YYYY-MM-DD`; Humo ranges stay within the last 3 months; ranges never exceed 1 year.
- [ ] Direction comes from `type`, not from the sign of `amount`; an unknown `merchant` field is tolerated.

## Summary (`/getSummary`)
- [ ] `from` / `to` are `YYYY-MM`; `to` is before the current month; Uzcard `from` is at least 2 months back; the range is at most 1 year.
- [ ] Missing months or types are read as zero.
