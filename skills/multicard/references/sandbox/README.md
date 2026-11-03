# Multicard sandbox and test data

Hand-written notes with the exact test values Multicard publishes. Use them in tests,
fixtures and examples against the sandbox host only; never send them to production, and
never hard-code them in production code paths. Transport, auth and errors:
[`../common/README.md`](../common/README.md).

- Sources: https://docs.multicard.uz/4736405f0 (intro: hosts, test card, sandbox OTP),
  https://docs.multicard.uz/19729295e0 (auth), https://docs.multicard.uz/19729296e0 and
  https://docs.multicard.uz/19729297e0 (`short_link`), and the method pages named in
  "Vendor sample values" (Russian pages)
- Fetched: 2026-11-03

## Environments

| What | Sandbox | Production |
|---|---|---|
| API base URL | `https://dev-mesh.multicard.uz/` | `https://mesh.multicard.uz/` |
| Token | `POST https://dev-mesh.multicard.uz/auth` | `POST https://mesh.multicard.uz/auth` |
| Invoice `short_link` | not returned (production only) | returned |

Paths, bodies and answers are the same on both hosts. Keep the base URL, `application_id`
and `secret` in configuration per environment; a token from one host is not valid on the
other (derived).

## Test card and OTP

| Item | Value |
|---|---|
| Test card PAN | `8600533364098829` (Uzcard BIN 8600) |
| Expiry | `2806`, already in the API's `yymm` form (June 2028); on the hosted forms enter `06/28` (derived) |
| Sandbox OTP (SMS code) | **`111111`** |

The docs publish **one** test card. No test phone number, PINFL, second card or per-card
error behaviour is documented. `otp_length` in `GET /payment/application` tells you how many
digits the code field must accept.

## Test credentials (how to get them)

1. Ask Multicard (your account manager or partner support) to register an application for
   the sandbox. They issue an `application_id` and a `secret`; the docs give no self-service
   cabinet.
2. Ask for at least one sandbox cashbox (`store_id` and store `uuid`). Read its settings with
   `GET /payment/store/{uuid}` ([`../reports/`](../reports/README.md)): `tax_registration`
   decides whether you must send `ofd`.
3. Features that Multicard switches on per account must be requested for the sandbox too:
   acceptless debit of bound cards, partial refunds, holds, payouts and split recipients
   (derived from the "enabled by Multicard" notes on each page).
4. Production credentials are issued separately after the sandbox integration is accepted
   (derived).

The auth example on the vendor page carries an `application_id` / `secret` pair. Do not reuse
it; use your own sandbox credentials.

## Sandbox scenarios (derived)

The docs do not list sandbox scenarios. These runs use only the published test data:

| Goal | Steps | Expected |
|---|---|---|
| token | `POST /auth` with your sandbox `application_id` and `secret` | `{token, role, expiry}`; reuse the token until `expiry` |
| hosted invoice | `POST /payment/invoice`, open `checkout_url`, pay with the test card, OTP `111111` | success callback to `callback_url` with a valid `sign`; `GET /payment/invoice/{uuid}` shows `success` |
| bind by hosted form | `POST /payment/card/bind`, open `form_url`, enter the test card | bind callback with `card_token`; `GET /payment/card/bind/{session_id}` returns the card |
| bind by API (PCI DSS) | `POST /payment/card {pan: "8600533364098829", expiry: "2806", user_phone}`, then `PUT /payment/card/{card_token} {otp: "111111"}` | card `active` |
| pay by token | `POST /payment` with the token, then `PUT /payment/{uuid} {otp: "111111"}` (or an empty body when `otp_hash` is `null`) | payment `success`, then refund with `DELETE /payment/{uuid}` -> `revert` |
| wrong OTP | confirm with any code other than `111111` | `400 ERROR_WRONG_OTP` |
| hold | `POST /payment/hold` -> confirm with `111111` -> charge or cancel | hold `active`, then payment `success` or hold `canceled` |
| payout | `POST /payment/credit` to the test card (or its token) with `confirmable: true` -> `PUT /payment/credit/{uuid} {otp: "111111"}` | payout `success`; wallet balance drops |
| lost answer | drop the connection during a confirm call | your code polls `GET /payment/{uuid}` and never sends a second confirm |
| duplicate order id | create two invoices or payments with the same `invoice_id` | not documented; record what the sandbox does and guard against it in your own code |

Your `callback_url` must be reachable from the internet for the sandbox to deliver callbacks
(derived). Verify the `sign` with your **sandbox** `secret`.

## Ready-made sandbox bodies

Bind by API (PCI DSS only) on `https://dev-mesh.multicard.uz/`:

```json
{"pan": "8600533364098829", "expiry": "2806", "user_phone": "998901234567"}
```

Confirm a payment, a bound card, a hold or a payout:

```json
{"otp": "111111"}
```

`998901234567` is a placeholder; Multicard publishes no test phone. If the sandbox checks
the phone against the card's SMS banking, ask Multicard which number the test card uses.

## Vendor sample values

Copied exactly from the request and response samples on the Multicard pages (ids below are
pages under `https://docs.multicard.uz/`). Use them in mocks, fixtures and unit tests that
replay Multicard's shapes. They are illustrative: none is documented as a live object on
`dev-mesh`.

| Call | Values | Page |
|---|---|---|
| `POST /auth` | -> `role` `"dev"`, `expiry` `"2023-03-18 16:40:31"`; `400` messages `"application_id required"`, `"You must supply a secret"`, `"Invalid Credentials"` | `19729295e0` |
| create-invoice | `store_id` `6`, `amount` `500000`, `invoice_id` `"123"`, `lang` `"ru"`; `ofd` items `{qty 1, price 2500000, mxik "06401004002000000", total 25000000, package_code "1506113", name "кроссовки men's low shoes"}` and `{qty 1, price 2500000, mxik "06401002004000000", total 2500000, package_code "1519041", name "кроссовки t.ace 2332 white black"}` -> `uuid` `"f6339f31-6a09-11f0-9a1b-00505680eaf6"`, `short_link` `"https://l.multicard.uz/1m1e12"`, `checkout_url` `"https://app.rhmt.uz/invoice/f6339f31-6a09-11f0-9a1b-00505680eaf6"`, `added_on` `"2025-07-26 15:19:06"` | `19729296e0` |
| get / delete invoice, scanpay | path `uuid` `527b7ead-b587-11f0-af7c-005056b4367d` (get), `1efd8630-b886-11f0-af7c-005056b4367d` (delete), `023874cd-b588-11f0-af7c-005056b4367d` (scanpay, body `code` `"50512"`) | `19729297e0`, `19729298e0`, `19729299e0` |
| success callback (you receive) | `store_id` `6`, `amount` `20000`, `invoice_id` `"2024864028760"`, `billing_id` `"20241214242009869794410864028760"`, `payment_time` `"2024-12-14 14:36:31"`, `ps` `"uzcard"`, `card_token` `"6225f3c93f7a880142782fa4"`, `uuid` `"e60d8ebc-b9fe-11ef-b159-005056b4367d"`, `receipt_url` `"https://dev-checkout.multicard.uz/check/e60d8ebc-b9fe-11ef-b159-005056b4367d"`, `sign` `"553b4292b0f1d8e0e18e6daeb3af3761"` (32 hex, md5) | `19729300e0` |
| status webhook (you receive) | same `uuid`, `amount` `200000`, `invoice_id` `"test"`, `status` `"progress"`, `refund_time` `null`, `receipt_url` `null`, `sign` `"5fe1289fbe9cf1834de72789f6629e5f23184974"` (40 hex, SHA1) | `19729301e0` |
| create-bind-link | `store_id` `6` -> `session_id` `"67f8dd24e9800"`, `form_url` `"https://dev-checkout.multicard.uz/card/67f8dd24e9800"`; missing field -> `ERROR_FIELDS` | `19729302e0` |
| get-bind-status, get-card, confirm-card | path `69089f9d03f26` (bind status) or `6225f3c93f7a880142782fa4` (card token); confirm body `otp` `"112233"` -> card `id` `55`, `application_id` `1`, `card_pan` `"409784******3066"`, `card_token` `"6225f3c93f7a110142782fa4"`, `phone` `"998901234567"`, `holder_name` `"AAAA BBBBB"`, `pinfl` `null`, `ps` `"uzcard"`, `status` `"active"`, `added_on` `"2022-04-21 14:36:29"`, `card_status` `{"code": 0}`, `sms_inform` `true`; wrong or expired code -> `ERROR_WRONG_OTP` | `19729304e0`, `19729305e0`, `19729309e0` |
| check-pinfl | `pinfl` `"12345678901234"` -> `data` `false`; empty or not 14 digits -> `ERROR_FIELDS` | `19729306e0` |
| create-payment by token | `card.token` `"6225f3c93f7a880142782fa4"`, `amount` `50000`, `store_id` `6`, `invoice_id` `"test"`; `ofd` items as in create-invoice with `price` = `total` `60000000` and `55700000` | `19729310e0` |
| create-payment by app | `payment_system` `"payme"`, `amount` `50000`, `store_id` `6`, `invoice_id` `"test"`, `billing_id` `1122334455`; `ofd` items add `vat` `12` | `19729313e0` |
| create-payment with split | `amount` `100000`, `store_id` `6`, `invoice_id` `"test"`; second `ofd` item `{qty 1, vat 0, price 10000, mxik "10107002001000000", total 10000, package_code "1209885", name "доставка заказа с маркетплейса"}`; `split` parts of `type` `"account"` with `amount` `88000` and `10000` | `19729312e0` |
| confirm-payment | path `83e73262-b626-11f0-af7c-005056b4367d`, body `otp` `"50112"`, `debit_available` `false` | `19729314e0` |
| refund-payment-partial | path `375b518e-b622-11f0-af7c-005056b4367d`; body empty, or `refund_amount` `22244100` with `ofd` item `{name "Бензин марки A80", mxik "02710001003000000", package_code 1282118, price 795000, qty 1, total 1605900}` | `24802978e0` |
| hold | create `card.token` `"6225f3c93f7a880142782fa4"`, `amount` `10000000`, `store_id` `15`, `invoice_id` `"18177"`, `expiry` `43200` -> `id` `753967`, `status` `"draft"`, `expiry` `"2025-03-08 23:12:15"`, `added_on` `"2025-03-07 23:12:15"`; confirm `otp` `"1122"` -> `"active"`; charge `amount` `100000`; cancel -> `"canceled"`; cancelling a hold that is not active -> `ERROR_PAYMENT_APPLIED` | `19729318e0`, `19729319e0`, `19729320e0`, `19729322e0` |
| payout | create `amount` `10000`, `store_id` `6`, `invoice_id` `"112233"`, `confirmable` `true` -> `id` `11351395`, `uuid` `"a81b7b62-6d86-11f0-9a1b-00505680eaf6"`, `status` `"draft"`, `commission_type` `"up"`, `total_amount` `10000`; confirm `otp` `"112233"` -> `status` `"success"`, `payment_time` `"2025-07-31 01:51:12"` | `19729323e0`, `19729324e0` |
| get-payment-history | `store_id` `"6"`, `offset` `0`, `limit` `100`, `only_status` `"success"`, `start_date` `"2025-03-01 00:00:00"`, `end_date` `"2025-03-02 00:00:00"` | `19729328e0` |

Sample-specific caveats:

- The OTPs in the samples (`112233`, `1122`, `50112`) are format samples. The sandbox code is
  `111111`.
- The create-invoice sample breaks `total = qty x price` on its first item, and the partial
  refund sample breaks it too; compute `total` yourself.
- The samples that carry a full card number, a payer phone, a holder name, KYC data, TINs or
  split recipient ids are left out here (see below).

## Do not put in tests or docs

- Your `application_id`, `secret` and JWTs, sandbox or production: load them from
  configuration.
- The auth sample credentials, merchant TIN, bank account, store data and the person shown
  in the vendor KYC example: they may be real.
- The full card numbers, payer phone, card holder name, processing merchant / terminal ids
  and split recipients in the payment, card and payout samples: they may belong to real
  people or accounts. Use the test card above, `998901234567` and `<RECIPIENT_UUID>`.
- Multicard's callback source IP: read it from the vendor page when you configure a firewall.
