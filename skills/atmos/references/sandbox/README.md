# Atmos sandbox and test data

Hand-written notes with the exact test values Atmos publishes. Use them in tests, fixtures
and examples on the test setup Atmos gives you; never hard-code them in production code
paths. Transport, auth and errors: [`../common/README.md`](../common/README.md).

- Sources: https://docs.atmos.uz/en/#sandbox, https://docs.atmos.uz/en/#test-cards,
  https://docs.atmos.uz/en/#error-debug-test-cards (cards and OTP),
  https://docs.atmos.uz/en/#html-widget and https://docs.atmos.uz/en/#payment-page (test
  widget and payment page)
- Fetched: 2026-11-04

## Environments

| What | Test | Production |
|---|---|---|
| API base URL | **not published** | `https://apigw.atmos.uz` |
| Token | not published | `POST https://apigw.atmos.uz/token` |
| HTML widget script | `http://cdn.pays.uz/checkout/js/v1.0.1/test-checkout.js` | `https://cdn.pays.uz/checkout/js/v1.0.1/checkout.js` |
| Payment page | `http://test-checkout.pays.uz/invoice/get` | `https://checkout.pays.uz/invoice/get` |

The docs name no separate sandbox API host. They say operations with the test cards "do not
involve the deduction of real funds", which suggests the test cards are accepted on the
host and credentials Atmos assigns for testing (derived). Ask Atmos which base URL and
which `consumer_key` / `consumer_secret` to use for tests, and keep the base URL in
configuration per environment. The two test hosted URLs are plain `http://`.

## Test cards and OTP

Copied exactly from https://docs.atmos.uz/en/#test-cards. The page prints the expiry as
`MM/YY`; the API wants `YYmm` (third column, derived).

| PAN | Expiry (as published) | `expiry` in the API |
|---|---|---|
| `9860090101014364` | 02/28 | `2802` |
| `9860090101893213` | 02/28 | `2802` |
| `9860090101842392` | 02/28 | `2802` |
| `9860090101469915` | 02/28 | `2802` |
| `5614688715378807` | 03/29 | `2903` |

Error card, from https://docs.atmos.uz/en/#error-debug-test-cards:

| PAN | Expiry (as published) | `expiry` in the API | Published behaviour |
|---|---|---|---|
| `8600492986215602` | 03/20 | `2003` | card expired |

| Item | Value |
|---|---|
| OTP for every test card | **`111111`** ("The default OTP for all test cards is - 111111") |
| Card scheme | not stated; BIN `9860` is Humo, BIN `8600` is Uzcard (derived) |

`111111` is also the fixed `otp` for token payments and token holds on production
([payments](../payments/README.md#gotchas)). Do not read the token-flow value as proof
that you are on a test setup.

## Test credentials (how to get them)

1. Ask Atmos (your manager or integration support) for test access. The docs give no
   self-service cabinet; they list `consumer_key` and `consumer_secret` as data you
   "obtain from ATMOS".
2. Ask for a test `store_id` (and `terminal_id` if your store has several terminals), and
   register your billing URL for the [Callback API](../common/README.md#callback-api-your-billing-url)
   on that store, with the `api_key` that signs the callbacks.
3. Products that Atmos switches on per merchant must be requested for testing too: card
   linking, holds, multi-payments, partial reversal, PINFL withdrawal and Visa / Mastercard
   (MPS) with its `apikey` (derived from the "enabled by Atmos" notes).
4. Production credentials are issued separately after the test integration is accepted
   (derived).

The vendor samples carry no real credential: they print `<access_token>`,
`Base64(consumer-key:consumer-secret)`, `store_id` `"XXXX"` and similar placeholders.

## Sandbox scenarios (derived)

The docs do not list sandbox scenarios. These runs use only the published test data:

| Goal | Steps | Expected |
|---|---|---|
| token | `POST /token` with your test `consumer_key:consumer_secret` | `{access_token, token_type: "Bearer", expires_in}` |
| pay by SMS code | `pay/create` → `pay/pre-apply {card_number, expiry: "2802"}` with a test card → `pay/apply {otp: "111111"}` | your billing URL gets the callback; answer `{"status": 1}`; `store_transaction.confirmed` `true`, `success_trans_id` set |
| link a card | `partner/bind-card/init {card_number, expiry}` → `bind-card/confirm {otp: "111111"}` | `data.card_token`, `data.card_id` |
| pay by token | `pay/create` → `pay/pre-apply {card_token}` → `pay/apply {otp: "111111"}` | as above |
| full refund | `pay/reverse {transaction_id: <success_trans_id>}` | `result.code` `OK` |
| partial refund | `create-reverse-partial` → `confirm-reverse-partial` with `ofd_items` → `get-reverse-partial` | reverted and left amounts add up to the original |
| expired card | `pay/pre-apply` with `8600492986215602`, `expiry` `"2003"` | an error; the exact `STPIMS-ERR-*` code is not published (record what you get) |
| wrong code | `pay/apply` with any code other than `111111` on the SMS flow | `STPIMS-ERR-098` (derived from the error table) |
| billing refuses | answer the callback with `{"status": 0}` | no debit; `apply` fails (derived) |
| lost answer | drop the connection during `pay/apply` | your code calls `pay/get` and never applies again |
| hold | `hold/create {duration: 10}` → `PUT /hold/apply/{id} {otp: "111111"}` → capture or `DELETE` | `hold_till` set, then a captured `store_transaction` or a released hold |

Your billing URL must be reachable from the internet for callbacks to arrive (derived).
Check the callback `sign` with your **test** `api_key`.

## Ready-made sandbox bodies

Link a test card (PCI DSS scope):

```json
{"card_number": "9860090101014364", "expiry": "2802"}
```

Pre-apply with a test card (SMS flow; `transaction_id` from `pay/create`):

```json
{"card_number": "9860090101014364", "expiry": "2802", "store_id": "<STORE_ID>", "transaction_id": 1}
```

Confirm an SMS payment, a card link or a hold:

```json
{"otp": "111111"}
```

## Vendor sample values

Most Atmos samples print placeholders (`XXXX`, `00000`, `<card-id>`, `000000000`), not
values. The few concrete ones, copied exactly; use them only in mocks and parsers:

| Call | Values | Page |
|---|---|---|
| `pay/create` | `amount` `5000000`, `account` `"12345"`, `store_id` `"XXXX"`, `lang` `"ru"`; one `ofd_items` line `amount` `10000` with `details` keys `quantity`, `package_code`, `mxik_code`, `mark_code` | `#transaction-creating` |
| `pay/create` answer | `transaction_id` `111111`, `success_trans_id` `null`, `card_id` `null` | `#transaction-creating` |
| multi-payment answer | `transaction_id` `[111111, 222222]` | `#multitransaction-creating` |
| token answers | `expires_in` `3600` in the text, `2525` and `1234` in the samples | `#authorization-in-api`, `#token-update` |

Sample-specific caveats:

- Several samples are not valid JSON (numbers with leading zeros such as `00000`). Do not
  paste them into a parser test as they are.
- Every sample OTP is `111111`, as a string in most samples and as a number in the
  `pay/apply` sample. Send a string of digits (derived) and keep leading zeros.

## Not published

- A sandbox API host, and test `consumer_key` / `consumer_secret`, `store_id`, `terminal_id`,
  callback `api_key` or MPS `apikey`.
- Visa / Mastercard test cards and any 3DS test page or test outcome: MPS cannot be tested
  with the cards above (they are local Humo / Uzcard cards).
- A test PINFL, passport or contract for [withdrawal by PINFL](../pinfl/README.md).
- Error cards other than the expired one (insufficient funds, blocked card, wrong code
  behaviour) and the `STPIMS-ERR-*` code each one returns.
- A way to trigger or replay a callback, and the address it comes from in test.
- Hold durations, limits and amount caps that apply in test.

## Do not put in tests or docs

- Your own `consumer_key`, `consumer_secret`, `api_key`, MPS `apikey` and tokens, test or
  production: load them from configuration.
- The callback source address from the vendor page: read it there when you configure a
  firewall; do not copy it into code comments or fixtures.
- Real payer data: use `998901234567`, `SAMPLE HOLDER` and masks like `986009******4364`.
