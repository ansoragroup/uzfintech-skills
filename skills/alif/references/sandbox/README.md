# Alif sandbox: hosts, test cards, test OTP / PINFL, test-only methods, vendor samples

Hand-written notes. Exact values published by Alif for the **sandbox only**. They move no real
money and do not work in production. Keep them in tests, fixtures and local configs, never in
production code paths.

- Sources: https://docs.alifpay.uz/#sandbox (ru, also `/uz/`, `/en/`), https://docs.alifpay.uz/checkout/,
  https://docs.alifpay.uz/payments/, https://docs.alifpay.uz/cards/; the same data appears on
  https://docs.alifpay.uz/v1/
- Fetched: 2026-11-03
- The environment switch ("Продуктивная" / "Песочница") is tabbed content. The sandbox host is
  rendered client-side only (Next.js chunk `/_next/static/chunks/246-*.js`), so a plain HTML
  fetch of the page does not show it.

## Environments

| Item | Sandbox | Production |
|---|---|---|
| API base URL | `https://api-dev.alifpay.uz/v2` | `https://api.alifpay.uz/v2` |
| Hosted checkout page | `https://checkout-dev.alifpay.uz/?invoice=<invoice_id>` | `https://checkout.alifpay.uz/?invoice=<invoice_id>` |
| `Token` header | sandbox token | production token |

- Get both tokens through https://alifpay.uz/ ("Получить API-токен"). The docs say each
  environment has its own token, so keep host and token paired in config.
- Vendor demo of the hosted page: https://checkout-dev.alifpay.uz/?invoice=id (pay with the cards
  below).
- The sandbox is an isolated replica of the API and is not connected to processing.

## Test cards (tokenization and charges)

| PAN | Behaviour |
|---|---|
| `1234111111111111` | valid card |
| `1234666666666666` | insufficient funds |
| `1234777777777777` | SMS notifications not enabled (`1104` / `SMS_NOTIFICATION_IS_OFF`) |
| `1234999999999999` | blocked card (`1107` / `BLOCKED_CARD`) |

- `exp`: any current date in `MMYY`. The docs print `06` + (current two-digit year + 1), so
  `0627` in 2026. Compute it in tests instead of hard-coding it.
- OTP for every test card (`confirmPayment`, `confirmCardToken`, legacy `confirmChargeOTP`):
  `111111`.
- Sandbox limit: one charge or hold is at most **5,000,000,000 tiyin**. A larger amount gets the
  insufficient-funds behaviour of the method used (status or error).
- `getCardToken` checks `phone` against the card's SMS-notification phone. A mismatch returns
  `1110`.

## Test PINFL (`matchCardPIN`, legacy `pinfl`)

| PINFL | Behaviour |
|---|---|
| `11111111111111` | valid PINFL |

## alif mobi QR test tokens (`method.type = MOBI_SHOW_QR`)

| `method.token` | Behaviour |
|---|---|
| `mock-success-card` | valid token |
| `mock-invalid-card` | invalid token |

A real QR / barcode token from the payer's alif mobi app is valid for 30 seconds.

## Test-only methods (sandbox host only)

| Method | Params | Result |
|---|---|---|
| `_payInvoiceWithMobi` (beta) | `invoice_id*` (string), `installment` (bool) | the invoice struct; simulates the payer paying the invoice in alif mobi, by instalment when `installment: true`, otherwise by card |
| `_completeInstallmentRefund` | `refund_id*` (string), `approve` (bool) | `{ok: true}`; moves a pending instalment refund to `DONE` (`approve: true`) or `FAILED` |

Vendor inconsistency: the `_completeInstallmentRefund` sample sends `{"id": ...}` and shows the
response `{"message": "success"}`, but the parameter table says `refund_id` and `{ok}`. Send
`refund_id`, and accept either response shape. Schemas:
[`../checkout/schemas/_payInvoiceWithMobi.json`](../checkout/schemas/_payInvoiceWithMobi.json),
[`../payments/schemas/_completeInstallmentRefund.json`](../payments/schemas/_completeInstallmentRefund.json).

## Vendor samples (copied exactly; use them in sandbox tests)

`POST https://api-dev.alifpay.uz/v2/getCardToken`

```json
{"pan": "1234111111111111", "exp": "0324", "phone": "998123456789"}
```

The sample `exp` `0324` has already passed. Use a current date (see above).

`POST https://api-dev.alifpay.uz/v2/matchCardPIN`

```json
{"token": "62d602f4-115d-46ce-a385", "pin": "11111111111111"}
```

`POST https://api-dev.alifpay.uz/v2/pay` (alif mobi QR)

```json
{"id": "035033da-4065-4c5b-adac", "amount": 7800000,
 "method": {"type": "MOBI_SHOW_QR", "token": "19458a75616ed275da27244b"}}
```

In the sandbox, put `mock-success-card` or `mock-invalid-card` in `method.token`.

`POST https://api-dev.alifpay.uz/v2/_payInvoiceWithMobi`

```json
{"invoice_id": "aa70817a-dfcf-4c6e-9332", "installment": true}
```

`POST https://api-dev.alifpay.uz/v2/_completeInstallmentRefund` (vendor sample; see the
inconsistency note above)

```json
{"id": "92f1b03a-acfc-41bb-91bc"}
```

Other sample values the vendor pages use, handy for fixtures:

| Field | Sample value |
|---|---|
| `phone` | `998123456789` |
| invoice `id` | `aa70817a-dfcf-4c6e-9332` (hosted page `https://checkout-dev.alifpay.uz/?invoice=aa70817a-dfcf-4c6e-9332`) |
| card `token` | `62d602f4-115d-46ce-a385` |
| receipt item 1 | `name` "Mug v556-3.25 (blue)", `spic` `08517001001000000`, `amount` 2, `price` 4000000 |
| receipt item 2 | `name` "Orbit White (XL)", `spic` `10399002001000000` |
| `Token` header | `Yml0Lmx5LzN4WW9XeWc=` (placeholder in the docs, not a working token) |

Vendor sample ids are truncated UUIDs. Real ids are full strings.

## Test plan (minimum)

| # | Scenario | Input | Expect |
|---|---|---|---|
| 1 | card payment with OTP | `pay` with `1234111111111111`, then `confirmPayment` `111111` | `SUCCEEDED` |
| 2 | wrong OTP | `confirmPayment` with any other code | `1100`, attempts end with `1106` |
| 3 | insufficient funds | `1234666666666666` | `INSUFFICIENT_FUNDS` / `1108` (retry needs a **new** `id`) |
| 4 | SMS off | `1234777777777777` | `1104` / `SMS_NOTIFICATION_IS_OFF` |
| 5 | blocked card | `1234999999999999` | `1107` / `BLOCKED_CARD` |
| 6 | over the sandbox limit | valid card, amount > 5,000,000,000 tiyin | insufficient-funds behaviour |
| 7 | tokenization | `getCardToken` + `confirmCardToken` `111111`, then `pay` with `TOKEN` | token works without OTP |
| 8 | phone mismatch | `getCardToken` with another phone | `1110` |
| 9 | PINFL | `matchCardPIN` with `11111111111111` | `{ok: true}` |
| 10 | alif mobi QR | `pay` `MOBI_SHOW_QR` with `mock-success-card` / `mock-invalid-card` | success / failure |
| 11 | hosted page | `invoice` on the sandbox host, pay on `checkout-dev` or with `_payInvoiceWithMobi` | webhook arrives, `getInvoice` agrees |
| 12 | instalment partial refund | `refundPaymentPartial`, then `_completeInstallmentRefund` `approve` true / false | `DONE` / `FAILED`, webhook to `webhook_url` |
| 13 | webhook signature | tamper with one byte of a received body | your HMAC check rejects it |
