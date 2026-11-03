# Uzum CrossBorder (transfers to / from Uzbekistan, cross-border service payments)

Hand-written notes. Generated tables: [`endpoints.md`](endpoints.md); schemas:
[`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_crossborder.yaml (en labels: `en_crossborder.yaml`)
- Fetched: 2026-11-03
- Direction: partner (foreign money-transfer service) calls Uzum. No callbacks for transfers.

## Hosts and auth

| Env | Base URL | Notes |
|---|---|---|
| Production | `https://crossborder.transfer.uz` | from the `servers` block; reachable over an IPSec tunnel only |
| Test | `crossborder-transfer.ub.ufintech.uz` | from the Testing section; credentials from your Uzum manager |

HTTP Basic auth (`<BASIC_USER>:<BASIC_PASSWORD>`). **Omit optional fields entirely**: an
empty string or `null` for an optional field is a validation error (`10002`).

## Operations (`POST` unless noted)

| Group | Path | Purpose |
|---|---|---|
| To UZ | `/cbt/v1/transfer/check_credit` | register + feasibility check; returns `transferId`, rate, receiver card data |
| To UZ | `/cbt/v1/transfer/confirm_credit` | execute (status must be `APPROVED`) |
| To UZ | `/cbt/v1/transfer/receiver_banks` | banks with cards for a phone (`bankLabel` values) |
| To UZ | `/cbt/v1/transfer/card`, `/card_list` | card info by PAN / cards by phone |
| From UZ | `/cbt/v1/transfer/check_debit` | register debit from a UZ card and send OTP |
| From UZ | `/cbt/v1/transfer/resend_otp` | resend OTP |
| From UZ | `/cbt/v1/transfer/confirm_debit` | `{externalTransferId, code}` with the OTP |
| From UZ | `/cbt/v1/transfer/cancel_debit` | reverse a `SUCCESS` debit when your crediting failed |
| Common | `/cbt/v1/transfer/convert` | rate quote `{amount, currencyFrom, currencyTo, direction TO_UZ / FROM_UZ}` |
| Common | `/cbt/v1/transfer/status`, `/transfer_list` | status by `externalTransferId`; registry |
| Payments | `/cbt/v1/payment/service_list`, `check_service`, `check_payment`, `confirm_payment`, `status`, `payment_list` | pay UZ services (utilities, mobile) from abroad |
| Account | `GET /cbt/v1/partner/account/closing_balance`, `GET .../operations` | partner pre-funded account |

## Transfer state machine

```
check_* ──> REGISTERED ──> APPROVED ──confirm──> SUCCESS ──cancel_debit (FROM_UZ only)──> REVERSED
                │             │           └──> FAILED (error block carries 104xx reason)
                └──> PENDING (manual review: poll /transfer/status hourly until SUCCESS/FAILED)
```

Payment statuses: `REGISTERED`, `APPROVED`, `PENDING`, `SUCCESS`, `FAILED`.

## Key fields

- Amounts are **integers in minor units** (tiyin / kopecks / cents). Minimum 1 tiyin.
- `externalTransferId` / `externalPaymentId`: your unique id; reuse gives `10211` / `20201`.
- `check_credit`: `identificationType` `PHONE` | `CARD` | `TOKEN` with `identificationValue`;
  `bankLabel` required for `PHONE` (no default bank). `senderCurrencyCode`
  `UZS` | `RUB` | `USD` | `EUR` | `TJS`. Sender / receiver person data blocks.
- `check_debit`: `receiverAccount`, sender card (`senderCardToken` or PAN + expiry),
  sender person data (`residencyCode` 1 resident / 2 non-resident, identity document,
  `pinfl`), phone must match the card's SMS-notification phone (`10317`).
- OTP code format `[0-9a-zA-Z]{4,6}`; optional `smsHash` for Android auto-read.
- Errors: HTTP 200 with an `error {errorCode, errorMessage, errorDetails}` block, or
  non-200 with the same block.

## Limits (UZ-issued debit cards)

Single transfer 19,999,999 UZS; 9,999 USD equivalent per 30 days; 5 transfers per day;
150 per month (per receiver card for TO_UZ, per sender card for FROM_UZ). The single
limit can be raised on request.

## Error codes (`errorCode`)

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| 10001 | auth failed | 10002 | validation (see `errorDetails`) |
| 10005 | internal error | 10006 | method not in your contract |
| 10101 | internal Uzum service error | 10102 | not available with custom-rate scenario |
| 10201 / 10202 | sender / receiver blacklist | 10203 | receiver cards not found |
| 10208 | rate changed / amounts wrong | 10209 / 10210 | single / monthly amount limit |
| 10211 | transfer id already exists | 10212 | transfer not found |
| 10220 | not approved (wrong status) | 10221 | expired: confirm >= 20 min after check |
| 10222 | partner limits not set | 10224 | crediting error |
| 10225 | receiver bank mismatch | 10227 | reverse requires `SUCCESS` |
| 10228 | sender card scheme not HUMO / Uzcard / Visa Uzum | 10229 | reversal error |
| 10230 / 10231 | daily / monthly count limit | 10240 | no receiver banks for phone |
| 10301 | sender card not found | 10302 | processing unavailable, retry later |
| 10303 | sender bank mismatch | 10310 | OTP expired |
| 10311 | OTP wrong, attempts left | 10312 | OTP wrong, no attempts left (failed) |
| 10316 | debit error | 10317 | phone not linked to card |
| 10318 | card info unavailable | 10401-10407 | `FAILED` reasons from processing: blocked, expired, limit, antifraud, credit error, insufficient funds, debit error |
| 11001 | account not found | 11002 | statement period too long |
| 11003 | balance / statement rate limit, retry | | |
| 20101-20105 | service not found / inactive / unavailable / bad params | 20200 | payment forbidden |
| 20201 | payment id exists | 20202 | payment not found |
| 20203 | not approved | 20204 | expired (20 min) |
| 20205 | payment failed | 20206 | bad amount |
| 20207 / 20208 | client number not found / does not exist | 20209 | bad phone |
| 20210 | antifraud | 20211 | payer verification failed |

## Gotchas

- Confirm within **20 minutes** of the check (`10221` / `20204`).
- `PENDING` gets no callback: poll status hourly.
- Credited funds cannot be returned. `cancel_debit` exists only to undo a debit whose
  onward credit failed on your side.
- Cache `service_list`; it changes rarely. `minAmount` / `maxAmount` are tiyin.
- Test host in the Testing text differs from the `servers` block; keep both in config.
- Test scenarios (transfers to and from Uzbekistan, payments), test PANs and phones, OTP codes
  that trigger each debit error, mock `serviceId`s and the vendor sample:
  [`../sandbox/README.md`](../sandbox/README.md#crossborder-transfers-to-uzbekistan), DEBIT in
  [`../sandbox/README.md`](../sandbox/README.md#crossborder-transfers-from-uzbekistan-debit).

## Examples

[`examples/`](examples/): check_credit request/response, confirm_credit response, error.
