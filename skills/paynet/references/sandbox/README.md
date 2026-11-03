# Paynet: sandbox, test data and vendor sample values

Hand-written notes on testing a Paynet acquiring integration: what Paynet publishes for
testing, the sample values on its pages, how to use them in mocks, and what to ask Paynet.
The flow, fields and error table are in [`../acquiring/README.md`](../acquiring/README.md)
and [`../common/README.md`](../common/README.md).

- Source: https://pay-docs.paynet.uz/acquiring-humo-uzcard,
  https://pay-docs.paynet.uz/online-payment-confirmation,
  https://pay-docs.paynet.uz/payment-status-check,
  https://pay-docs.paynet.uz/payment-cancellation,
  https://pay-docs.paynet.uz/general-principles
- Fetched: 2026-11-03

## What Paynet publishes for testing

**No test data.** The public docs have no sandbox, test cards or test credentials. The
integration guide Paynet sends to merchants has none either.

| Item | Published? |
|---|---|
| Sandbox / test API host | **no**. Even the production base URL is issued privately |
| Test Humo / Uzcard cards (PAN, expiry) | **no** |
| Test OTP / SMS codes | **no** |
| Test phones | **no** |
| Test `service_id` / `secret_key` / `merchantId` | **no** |
| Cards or amounts that force a given error | **no** |
| Postman collection, playground, mock server | **no** |
| Request and response samples | **yes**, see below. They are illustrative and not documented as working anywhere |

## Getting access (steps)

1. Register the payment instrument with Paynet. Paynet issues `service_id` and `secret_key`
   (for the Basic header), your `merchantId` and the base URL.
2. Ask for a separate test environment and test credentials, and get the answers to the
   open questions below in writing.
3. Keep test and production credentials in separate secrets. Make the base URL and the
   `status` / `reverse` paths configurable (see the path note in the acquiring README).

Until Paynet answers, test against a local mock built from the samples below. Do not send
real payments with real cards as a test.

## Vendor sample values

These values come from the public samples. Use them in mocks, fixtures and unit tests that
replay Paynet's shapes. Never send the sample card to a live Paynet host. Where the table
says "your", use the values Paynet issued to you, or a placeholder.

| Call | Values |
|---|---|
| authorize request | `pan` `"1234567812345678"`, `expiry` `"2708"`, `amount` `150 000` (see the note below), `orderId` `"ORD-001234"`, `comment` `"Оплата подписки"` ("subscription payment"), `currency` `"UZS"`, `merchantId`: your own (placeholder `<MERCHANT_ID>`) |
| authorize response | `status` `0`, `message` `"Success"`, `data.transactionId` `"TXN-20260106-0001"`, `data.orderId` `"ORD-001234"`, `data.ttlSeconds` `120`, `data.phoneMask` `"+998 ** *** ** 45"` |
| confirm request | `transactionId` `"TXN-20260106-0001"`, `otp` `"123456"` |
| confirm response | `status` `0`, `message` `"Success"`, `data.transactionId` `"TXN-20260106-0001"`, `data.orderId` `"ORD-001234"`, `data.paymentId` `"PAY-987654"` |
| status response | as confirm, plus `data.status` `"SUCCESS"` |
| reverse response | as confirm, plus `data.status` `"CANCELLED"` |
| authorize / confirm error | `status` `400`, `message` `"Payment failed"`, `error.code` `"INSUFFICIENT_FUNDS"`, `error.message` `"Not enough balance to complete the transaction"`, `error.provider` `"HUMO"`, `error.providerCode` `"51"`, `error.providerMessage` `"Insufficient funds"`, `error.retryable` `false`, `error.details` `{"availableBalance": "50 000", "requiredAmount": "150 000"}` |
| status / reverse not found | `status` `9005`, `message` `"Transaction not found"`, `data` `null`, `error.code` `"TRANSACTION_NOT_FOUND"`, `error.message` `"Transaction with id <uuid> was not found"`; `provider`, `providerCode`, `providerMessage` and `details` are `null`, and `retryable` is `false` |

Notes on the samples:

- `"amount": 150 000` is not valid JSON. Amounts are integer tiyin, so a fixture should say
  `150000`. The page does not say whether the sample means 150 000 tiyin or 150 000 UZS.
- `"1234567812345678"` and `"123456"` show the format only. Paynet does not say they are
  test card or test OTP values.
- `"2708"` is `YYMM` (August 2027).
- The `status` field of the error envelope is `400` in one sample and the numeric error
  code `9005` in the other. Branch on `error.code`, not on `status`.
- The Basic header in a test must be built from your own test `service_id:secret_key`, or a
  placeholder such as `base64("<SERVICE_ID>:<SECRET_KEY>")`. Never copy a header from a
  document.

## Mock scenarios built from the samples

A mock Paynet server (or recorded fixtures) should cover at least these paths. The error
codes and their actions are in the common README.

| # | Call sequence | Mock answer | Expected merchant behaviour |
|---|---|---|---|
| 1 | authorize → confirm `123456` → status | `TXN-20260106-0001`, then `PAY-987654`, then `SUCCESS` | order paid; `paymentId` stored |
| 2 | authorize (sample card) | the `INSUFFICIENT_FUNDS` sample | final failure; no confirm screen |
| 3 | authorize → confirm wrong OTP | `OTP_INVALID` (1007) | ask for the code again with the same `transactionId` |
| 4 | authorize → wait past `ttlSeconds` → confirm | `OTP_EXPIRED` (1008) | start a new authorize |
| 5 | authorize → confirm | `-10012` `UNKNOWN_TRANSACTION_STATE`, then status `SUCCESS` | poll status; never repeat confirm |
| 6 | confirm times out | no response, then status `SUCCESS` or `FAILED` | poll status; mark the order paid only on `SUCCESS` |
| 7 | after 1 → reverse | `CANCELLED` | order cancelled; refund the payer in your system |
| 8 | status / reverse with an unknown id | the `TRANSACTION_NOT_FOUND` sample | do not change the order; check your id |
| 9 | reverse on a payment over 1 month old | an error (code not documented) | cancellation is impossible; refund by other means |

Scenarios 3 to 6 and 9 are not in Paynet's samples. Build those bodies from the error table
and the envelope in the common README.

## Open questions for Paynet

- Is there a sandbox or test host, and what is its base URL?
- Test Humo and Uzcard cards: PAN, expiry and the OTP that test mode accepts.
- Which test cards or amounts trigger `INSUFFICIENT_FUNDS`, `OTP_INVALID`, `OTP_EXPIRED`,
  `OTP_ATTEMPTS_EXCEEDED` and `-10012`?
- Test phones: does test mode send a real SMS, or accept a fixed code?
- Test `service_id` / `secret_key` / `merchantId`, and whether they are separate from
  production.
- Does `reverse` work in test mode, and which error does it return after one month?
- Must test traffic come from allow-listed IPs?
- The field description says the amount is in tiyin. What does the sample `150 000` mean?
