# Uzum Remit Core (international transfers: CREDIT to UZ cards, DEBIT from UZ cards)

Hand-written notes. Generated tables: [`endpoints.md`](endpoints.md); schemas:
[`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_remitcore.yaml (en labels: `en_remitcore.yaml`)
- Fetched: 2026-11-03
- Successor-style API to [CrossBorder](../crossborder/README.md) with a single
  register/process flow for both directions.

## Hosts and auth

| Env | Base URL |
|---|---|
| Test | `https://remit-core.ipt-merch.com` |
| Production | over an IPSec tunnel; address issued at onboarding |

Header `X-Api-Key: <uuid>` on every call. Ignore unknown response fields (the API adds
fields without versioning).

Test flow, error cases and the vendor `/v1/register` sample from the Postman collection:
[`../sandbox/README.md`](../sandbox/README.md#remit-core-credit-transfers).

## Operations (all `POST`)

| Path | Purpose |
|---|---|
| `/v1/register` | create transfer; status `REGISTERED` |
| `/v1/process` | execute a `REGISTERED` transfer |
| `/v1/confirm` | `{transferId, otp}` for DEBIT with `confirmationType = OTP` |
| `/v1/resend_otp` | `{transferId}` |
| `/v1/cancel` | `{transferId}`; DEBIT only (`8003` for CREDIT) |
| `/v1/get_status` | `{transferId}` or `{externalTransferId}` |
| `/v1/convert` | quote: amount, currencies, countries -> `exchangeRate`, `fee` |
| `/info/v1/get_banks` | `{phoneNumber, receiverCountry: "UZB"}` -> `banks[]` |
| `/info/v1/get_balance` | partner account balance |

## Flows

```
CREDIT: register -> process -> code 0 (SUCCESS) | 2000 (async: callback or get_status)
DEBIT:  register -> process -> 2001 confirmation required
                          OTP: confirm {otp} [resend_otp] ; 3DS: done outside Remit Core
                   -> SUCCESS / FAILED
cancel: DEBIT only, from SUCCESS -> CANCELLING -> CANCELLED | CANCELLING_FAILED
        (CREDIT cancel -> 8003; result may be async: 2000)
```

Statuses: `INIT`, `REGISTERED`, `PROCESSING`, `CONFIRMATION`, `CONFIRMING`, `SUCCESS`,
`FAILED`, `CANCELLING`, `CANCELLING_FAILED`, `CANCELLED`.

## register request

- `transferType` `CREDIT` | `DEBIT`; `externalTransferId` (yours, unique); `clientId`.
- `transferData{senderAmount?, receiverAmount?, senderCurrencyCode, senderCountry,
  receiverCountry, receiverCurrencyCode, reason?}`; amounts in minor units.
- `target`: `{paymentInstrumentType: CARD_PAN, cardPan}` (16-19 digits) or
  `{paymentInstrumentType: PHONE, phoneNumber, bankLabel}`.
- `source` (DEBIT): `{paymentInstrumentType: ACCOUNT, accountNumber}` or
  `{paymentInstrumentType: MASKED_CARD, maskedPan}`.
- Countries are ISO alpha-3 (`RUS`, `UZB`); currencies ISO alpha-3.
- `sender`, `receiver`: person data; `identityDocument.documentType` `ID`, `PASSPORT`,
  `FOREIGN_PASSPORT`, `RESIDENT_CARD`, `MILITARY_ID`, `DRIVER_LICENSE`, `OTHER`.

## Response envelope

`{code, message, result{status, transferId, externalTransferId, senderAmount,
senderCurrencyCode, senderName, receiverAmount, receiverCurrencyCode, receiverName,
receiverPaymentSystem, fee, exchangeRate, rrn, confirmationData?}}`.
`confirmationData{confirmationType OTP | 3DS, confirmationValue, extraFields{acsUrl, termUrl, paReq}}`.
HTTP 401 / 403 / 422 / 500 carry `{code, message, errors[{field, message}]}`.

## Callback

Uzum POSTs the `TransferResultInfo` (same shape as `result`) to the URL agreed at
onboarding after `process`, `confirm` or `cancel` answered `2000`. Any 2xx = delivered.

## Codes

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| 0 | success | 2000 | accepted async: wait callback / poll |
| 1001 | bad JSON / schema | 2001 | confirmation required |
| 1002 | missing fields | 2002 | repeated request |
| 1003 | format error (`errors[]`) | 1101 | missing header |
| 3001 | duplicate `externalTransferId` | 3003 | single amount limit |
| 3004 | daily amount limit | 3012 | monthly amount limit |
| 3013 / 3014 | daily / monthly count limit | 3017 | limits not configured |
| 3008 | OTP incorrect | 3018 | OTP attempts exceeded |
| 3040 | OTP expired | 3036 | confirm window expired |
| 3035 | confirm not possible in this status | 3038 | status does not allow the operation |
| 3010 | identification type not allowed | 3011 | person data missing |
| 3020 / 3021 | sender / receiver card not found | 3023 / 3024 | sender / receiver bank |
| 3030 / 3031 | sender / receiver stop-list | 3032 | phone mismatch |
| 3034 / 3039 | receiver / sender card type | 3037 / 3041 | credit / debit error |
| 3054 | transfer not found | 3055 | cancel failed, retry |
| 3060 | invalid account | 3102 | limit |
| 3103 | security reject | 5003 | rate changed |
| 8002 | access restricted | 8003 | cancel of CREDIT prohibited |
| 9000 | internal error | 9051 | external timeout |
| 9100 | external error | | |

## Limits (UZ cards) and BINs

Minimum 1 UZS; single 18,749,999 UZS; 9,999 USD per 30 days; 5 per day; 150 per month.
UZCARD BINs 5440, 5614, 6262, 6263, 6264, 8600; HUMO 4008, 4027, 4062, 4067, 4073, 4097,
4198, 4294, 4728, 4790, 5555, 9860; Visa (Uzum) 49169903.

## Settlement report

Daily CSV `Remit_Core_transfers_YYYYMMDD.csv`, `;`-separated, amounts in minor units;
`fee` can be negative.

## Gotchas

- `2000` is not an error; never re-register on it.
- Treat `2002` as "already in progress": poll `get_status`.
- Limits differ from CrossBorder (18,749,999 vs 19,999,999 UZS single).

## Examples

[`examples/`](examples/): register CREDIT request, process response, async callback,
error.
