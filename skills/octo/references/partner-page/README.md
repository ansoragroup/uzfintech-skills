# Octo payment via the partner's site (you collect the card, Octo processes it)

Hand-written notes. Transport, auth, `test`, envelope, statuses and error codes:
[`../common/README.md`](../common/README.md). Payment creation, two-stage capture and the
status check are the same calls as in [`../payment-page/`](../payment-page/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://help.octo.uz/payment-via-partner-web.html,
  https://help.octo.uz/payment-via-partner-web/one-stage.html,
  https://help.octo.uz/payment-via-partner-web/two-stage.html,
  https://help.octo.uz/payment-confirm-pay.html, https://help.octo.uz/confirm-pay/token.html,
  https://help.octo.uz/payment-via-partner-web/methods/verification-info.html,
  https://help.octo.uz/payment-via-partner-web/methods/check-sms-key.html,
  https://help.octo.uz/otp-resend.html, https://help.octo.uz/payment-via-web/one-stage.html (OTP
  limit) (Russian pages)
- Fetched: 2026-11-04
- Needs: a **PCI DSS certificate**. Octo allows this flow only for partners that may accept
  card data themselves. Without one, use the Octo page
  ([`../payment-page/`](../payment-page/README.md)) or pay with a token
  ([`../cards/`](../cards/README.md)).

## Flow

```
POST /prepare_payment {...}                     ─> data.octo_payment_UUID   (server, with secret)
POST /pay/{octo_payment_UUID} {pan, exp, method, cvc2, cardHolderName, email?}
                         or {card_token, method, email?}
   └─> data {id, uuid, status, redirectUrl, details{cardInfo, transType}}
Uzcard / Humo (SMS OTP on your page):
   GET /verificationInfo/{octo_payment_UUID}    ─> data {verifyId, phone (masked), secondsLeft}
   POST /check_sms_key {smsKey, paymentId = data.id, verifyId}
      └─> data status succeeded (one-stage; a two-stage hold waits for capture, derived)
   resend: POST /check_pan {pan, expDate, paymentId} ─> new verifyId, secondsLeft 120
Visa / Mastercard:
   pay returns redirectUrl to the issuer OTP form; show it to the payer; the result
   arrives as a notification, then check the status
two-stage: POST /set_accept as on the Octo page
```

## Methods

| Method | Endpoint | Params (`*` required) | Result (`data`) |
|---|---|---|---|
| pay-card | `POST /pay/{octo_payment_UUID}` | `pan*`, `exp*` (YYMM), `method*` (`bank_card`, `uzcard`, `humo`), `cvc2*`, `cardHolderName*`, `email` | transaction object |
| pay-token | `POST /pay/{octo_payment_UUID}` | `card_token*`, `method*`, `email` | transaction object |
| verification-info | `GET /verificationInfo/{octo_payment_UUID}` | path only | `verifyId`, `phone`, `secondsLeft` |
| check-sms-key | `POST /check_sms_key` | `smsKey*`, `paymentId*` (int, `data.id`), `verifyId*` (int) | transaction object |
| check-pan | `POST /check_pan` | `pan*`, `expDate*` (YYMM), `paymentId*` | `verifyId`, `phone`, `secondsLeft` |

- `email` is required on `pay` when `prepare_payment` carried a `user_data` block.
- `cvc2` is marked required; the Uzcard sample sends `""`. Send the real code for
  `bank_card` and an empty string for Uzcard and Humo (derived from the samples).
- Transaction object (trimmed in [`schemas/pay-card.json`](schemas/pay-card.json)): `id`
  (integer `paymentId`), `uuid`, `merchantTransId` (your `shop_transaction_id`),
  `initialSum`, `totalSum`, `transferSum`, `refundedSum`, `currency`, `createTime`,
  `expireTime`, `peyedTime` (vendor spelling; epoch **milliseconds**), `autoCapture`,
  `isTest`, `redirectUrl`, `details.cardInfo{first6, last4, issuerCountryCode, cardHolder}`,
  `status`, `riskLevel`, `bankCode`, `cardInputType` (`merchant_site` or `octo_page`),
  `fiscalDetails{status, errorCode, message}`.

## OTP rules

- Three wrong OTP entries cancel the payment; you must create a new one. The one-stage
  page states this for Uzcard; the Humo limit is not printed, so apply the same rule to
  both (derived). Warning [`octo.otp-three-tries`](../lifecycle/README.md).
- `verificationInfo` never returns an error for an expired code: it answers `error: 0`
  with `secondsLeft: 0`. Treat `0` as "expired or not active" and offer a resend.
- `check_pan` resends the code and gives a new `verifyId` with `secondsLeft: 120`. Its
  resend limit is `error: 17`. The number of allowed resends is not printed.
- `check_sms_key` and `check_pan` carry no shop secret; they are bound to `paymentId`.
  Call them from your server anyway, so that the PAN and the code never pass through
  third-party scripts (derived).

## Errors

| Case | Answer |
|---|---|
| wrong shop pair on `prepare_payment` | `error: 2`, `errMessage: "Wrong secret"` |
| resend limit | `check_pan`: `error: 17`, "maximum number of SMS resends" (Russian text) |
| processing decline | network code in `error` ([`../common/`](../common/README.md) error ranges) |
| code expired | `verificationInfo`: `error: 0`, `secondsLeft: 0` |

## Gotchas

- You are in PCI DSS scope: never log `pan`, `exp` or `cvc2`, never store them, and mask
  them in error reports (derived).
- `paymentId` is the integer `data.id` from `pay`, not `octo_payment_UUID`.
- `createTime` and `expireTime` are epoch milliseconds although the table says UNIX
  timestamp; divide by 1000 before comparing with seconds.
- `redirectUrl` changes meaning: before payment it is the OTP form, after `check_sms_key`
  it is a status page. Do not treat its presence as success.
- `totalSum` and `transferSum` are amounts; the fee breakdown is merchant specific and
  is not covered here.
- After `check_sms_key` returns `succeeded`, still wait for the notification or re-check
  the status before you ship ([`../common/`](../common/README.md)).

## Examples

[`examples/`](examples/): pay-card request/response, pay-token request,
verification-info response, check-sms-key request/response, check-pan request/response.
