# Alif Cards (Uzcard / Humo tokenization, PINFL match, card type)

Hand-written notes. Transport, auth, errors: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.alifpay.uz/cards/ (Russian page)
- Fetched: 2026-11-03
- Card schemes: Uzcard and Humo only.

## Flow

```
getCardToken {pan, exp, phone?} -> {token, masked_phone}   (SMS OTP sent to the holder)
confirmCardToken {token, otp}   -> {token, masked_pan, bank_name, holder_name}
token is now reusable: pay{method TOKEN}, hold, history, getSummary, matchCardPIN
```

## Methods

| Method | Params (`*` required) | Result |
|---|---|---|
| `getCardToken` | `pan*` (16 digits), `exp*` (`MMYY`), `phone` (`998NNNNNNNNN`; **required for Humo**) | `{token, masked_phone}` |
| `confirmCardToken` | `token*`, `otp*` | `{token, masked_pan, bank_name, holder_name}` |
| `matchCardPIN` | `token*` (confirmed), `pin*` (PINFL, 14 digits) | `{ok: bool}` |
| `getCardType` | `pan*` (prefix, 4..16 digits) | `{type: "HUMO" \| "UZCARD"}` or error `1005` |

## Errors you will see here

`1102` bad card data, `1103` expired, `1104` SMS notifications off, `1107` blocked,
`1110` `phone` differs from the card's SMS-notification phone, `1100` / `1101` / `1106` OTP
wrong / expired / attempts exhausted.

## Gotchas

- The token is unusable until `confirmCardToken` succeeds.
- `matchCardPIN` can return `false` for some Humo cards simply because the scheme has no
  PINFL on file; do not treat that as fraud by itself.
- Never log or store the PAN or expiry after tokenization; keep `token` and `masked_pan`.
- Sandbox test cards, OTP `111111` and PINFL `11111111111111`: [`../sandbox/README.md`](../sandbox/README.md).

## Examples

[`examples/`](examples/): getCardToken request/response, confirmCardToken request/response,
getCardType response.
