# Click: sandbox, test tools and vendor sample values

Hand-written notes for testing a Click integration: the playground, the Postman generator
with its 15 scenarios, Telegram test mode, how to get credentials, and the sample values
used on the Click pages. The values here are test or sample data, never real credentials.

- Source: https://docs.click.uz/en/testing/playground, https://docs.click.uz/en/testing/postman,
  https://docs.click.uz/en/merchant-api/requests, https://docs.click.uz/en/merchant-api/click-pass,
  https://docs.click.uz/en/merchant-api/fiscalization, https://docs.click.uz/en/click-button/,
  https://docs.click.uz/en/additional/get-info, https://docs.click.uz/en/additional/shop-split,
  https://docs.click.uz/en/additional/telegram-payments
- Fetched: 2026-11-03

## What Click publishes for testing

| Item | Published? | Details |
|---|---|---|
| Separate sandbox / test API host | **no** | The Merchant API pages show only `https://api.click.uz/v2/merchant/...`. The payment link and widget use `https://my.click.uz`. Neither has a test twin in the docs |
| Test cards, OTP / SMS codes | **no** | The card and SMS code in the card-token samples illustrate the format. Click does not say they work anywhere |
| Test phones | **no** | Phones in the samples are illustrative |
| Test `service_id` / `merchant_id` / `secret_key` | **no** | Click issues them per service. Both test tools take your own |
| SHOP API test tools | **yes** | The browser playground and the Postman generator. Both call **your** server |
| Telegram test provider | **yes** | The `@CLICKtest` bot gives a test `provider_token` (see below) |

So "sandbox" for Click means pointing Click's test tools at your own staging endpoints with
your own service credentials. Inbound SHOP API traffic can be fully simulated this way.
Outbound Merchant API calls (invoices, status, reversal, card tokens, fiscalization,
CLICK Pass) have no documented test environment, so mock them with the sample values below.

## Getting credentials (steps)

1. Be registered as a legal entity or an individual entrepreneur.
2. Sign a payment-acceptance agreement with one of the banks connected to CLICK and hand over
   the documents the bank asks for. The Telegram page lists the banks and documents.
3. On registration Click issues `merchant_id`, `service_id`, `merchant_user_id` and
   `secret_key`. The bank issues the login and password for the merchant account.
4. Give Click the URLs of your Prepare and Complete handlers.
5. Put `service_id` and `secret_key` into the playground or the Postman generator and aim
   them at a staging copy of those handlers.

The docs do not mention a separate test service or test `secret_key`. Ask your Click manager
whether one can be issued before you test against a live service.

## Playground

`https://docs.click.uz/en/testing/playground` signs and sends Prepare and Complete from the
browser straight to your URLs.

| Field | Default |
|---|---|
| Secret Key | empty (a password field; required) |
| Service ID | empty, placeholder `12345` (required) |
| URL Prepare / URL Complete | empty, placeholders `https://your-server.com/payment/prepare` and `.../payment/complete` |
| `merchant_trans_id` | generated: `txn_<epoch ms>_<6 base36 chars>`, with a regenerate button |
| `amount` | `10000` (must be > 0) |
| `click_trans_id` | random 9-digit number (placeholder `123456789`) |
| `click_paydoc_id` | random 9-digit number (placeholder `987654321`) |
| `error` | `0` |
| `error_note` | `Success` |
| `sign_time` | not editable: the browser's local time at send, `YYYY-MM-DD HH:mm:ss` |

- Buttons:
  - **Prepare** sends `action=0` and remembers `merchant_prepare_id` from the response.
  - **Complete** sends `action=1` with that id. It refuses to run before a Prepare.
  - **Prepare → Complete** runs both and stops if the Prepare response has no
    `merchant_prepare_id`.
- Each request is a `POST` with `Content-Type: application/x-www-form-urlencoded`. The page
  shows the request it sent and the HTTP status and body it got back. It also shows a
  `sign_string` preview with the secret masked.
- The signature is computed in the browser, so the secret never leaves the page.
- CORS: the requests come from the browser, so your endpoint must allow the
  `https://docs.click.uz` origin (or use a CORS browser extension). Do this on staging only;
  the page warns that production must keep CORS properly restricted.
- The generated `merchant_trans_id` does not exist in your system. A correct Prepare answers
  `-5` until you type in a real test order or account.
- To test a cancellation, set `error` to a negative value before Complete. Expect `-9`.

## Postman generator

`https://docs.click.uz/en/testing/postman` builds a Postman collection (schema v2.1.0) with
15 scenarios.

Prerequisites:
- Postman;
- a running server with Prepare and Complete;
- your `service_id` and `secret_key`.

### Form

| Field | Page example / default | Becomes variable |
|---|---|---|
| Service ID | placeholder `12345` | `service_id` |
| Secret Key | empty | `secret_key` |
| click_trans_id | `134` ("any test number") | `click_trans_id` |
| click_paydoc_id | `1344` | `click_paydoc_id` |
| amount | `1000` (any amount except `300`) | `amount` |
| merchant_trans_id | `user12344` (must exist in your system) | `merchant_trans_id` |
| sign_time | now (date and minutes) | `sign_time`, exported as `YYYY-MM-DD HH:mm:00` |
| URL Prepare / URL Complete | placeholders `https://your-server.com/prepare`, `.../complete` | `prepare_url`, `complete_url` |

The collection also gets these variables, all starting empty:
- `merchant_prepare_id`, which you fill by hand;
- `prepare_sign_string` and `complete_sign_string`, which the scripts fill.

**Generate collection** builds the JSON. **Download Postman JSON** saves it as
`Click SHOP API service_<service_id>.json`, and the collection is named
`Click SHOP API — service <service_id>`.

Import it with File → Import. To view the variables, right-click the collection, choose
Edit, and open the Variables tab. The downloaded file contains `secret_key` in plain text:
never commit or share it.

### Requests

Every request:
- is a `POST` to `{{prepare_url}}` (action 0) or `{{complete_url}}` (action 1);
- has `Content-Type: application/x-www-form-urlencoded`;
- sends these fields: `click_trans_id`, `service_id`, `click_paydoc_id`, `merchant_trans_id`,
  `merchant_prepare_id` (Complete only), `amount`, `action`, `sign_time`, `error` (`0` unless
  overridden), `error_note` (`Success`) and `sign_string`.

A pre-request script signs each request with Postman's `CryptoJS.MD5`, using the collection
variables:

```
Prepare : md5(click_trans_id + service_id + secret_key + merchant_trans_id + amount + "0" + sign_time)
          -> prepare_sign_string
Complete: md5(click_trans_id + service_id + secret_key + merchant_trans_id + merchant_prepare_id
              + amount + "1" + sign_time) -> complete_sign_string
```

Scenarios 1 and 4 have no script. They send a fixed, wrong `sign_string`.

The request names and descriptions in the collection are in Russian. Each description ends
with the expected error code.

### The 15 scenarios

| # | Request (English gloss) | Call | Inputs that differ from the variables | `sign_string` | Expected `error` |
|---|---|---|---|---|---|
| 1 | Prepare: invalid signature | Prepare | none | fixed `84bde13caa55fe3fb68f7afc663be7ce` | `-1` |
| 2 | Prepare: user/order not found | Prepare | none (see note 1) | Prepare script | `-5` |
| 3 | Prepare: success | Prepare | none | Prepare script | `0` |
| 4 | Complete: invalid signature | Complete | none | fixed `38e46c75d7d386a99354d3d2ceb351ad` | `-1` |
| 5 | Complete: wrong amount | Complete | `amount=300` | Complete script over `300` | `-2` |
| 6 | Complete: success | Complete | none | Complete script | `0` |
| 7 | Complete: repeated confirmation | Complete | none | Complete script | `-4` |
| 8 | Complete: cancel a confirmed payment | Complete | `error=-5017` | Complete script | `-9` |
| 9 | Prepare: success (prepare_id setup) | Prepare | none | Prepare script | `0` |
| 10 | Complete: transaction not found | Complete | `merchant_prepare_id=999999999` | Complete script over `999999999` | `-6` |
| 11 | Complete: success (prepare_id OK) | Complete | none | Complete script | `0` |
| 12 | Prepare: success (cancel setup) | Prepare | none | Prepare script | `0` |
| 13 | Complete: cancel payment | Complete | `error=-5017` | Complete script | `-9` |
| 14 | Complete: repeated cancel | Complete | `error=-5017` | Complete script | `-9` |
| 15 | Complete: confirm a cancelled payment | Complete | none (`error=0`) | Complete script | `-9` |

### Run order

Do not use "Run Collection". The Complete requests need a `merchant_prepare_id` that you
copy by hand.

1. Run 1, 2 and 3. Copy `merchant_prepare_id` from the response to 3 into the variable.
2. Run 4 to 7, then 8. The page's step list skips 8, but its scenario table includes it.
3. Run 9 and copy its `merchant_prepare_id`. Run 10, which uses `999999999` on its own. Put
   the id from 9 back into the variable, then run 11.
4. Run 12, copy its `merchant_prepare_id`, then run 13, 14 and 15.

For each request, read Response → Body. A passing answer looks like this (vendor sample
values):

```json
{"error": 0, "error_note": "Success", "click_trans_id": 134, "merchant_trans_id": "user12344", "merchant_prepare_id": 12345}
```

The page names the field `error_code`, but the JSON key is `error`.

### Notes the page does not spell out

1. **Scenario 2.** It sends exactly the same inputs as scenario 3, so a correct server cannot
   answer both `-5` and `0`. For scenario 2 only, point `merchant_trans_id` at an order or
   account that does not exist (edit the request body or the variable). Restore it before 3.
   The script re-signs automatically.
2. **One transaction for everything.** All 15 requests reuse one `click_trans_id`,
   `merchant_trans_id` and `sign_time`. Scenarios 9 and 12 then expect a fresh Prepare to
   succeed on the same ids after 6 paid them and 8 cancelled them. That only works for an
   account top-up model, where `merchant_trans_id` is a payable account. A one-off order, or
   a handler that is idempotent on `click_trans_id`, will rightly answer `-4` or `-9` there.
   In that case, set a new unpaid `merchant_trans_id` and a new `click_trans_id` before
   steps 3 and 4.
3. **`sign_time` is frozen at generation.** If your handler rejects old `sign_time` values
   (the docs set no window), update the variable before running.
4. **Scenario 5 tests the amount check, not the signature.** It signs `300`, so the signature
   is valid and only the amount differs from the order. Answer `-2`, not `-1`.

## Telegram Payments test mode

1. In `@BotFather`, send `/mybots`, pick the bot and open Bot Settings → Payments → CLICK
   Uzbekistan.
2. Choose **Connect CLICK Terminal Test**. This opens the test bot `@CLICKtest`.
3. Press Start, then Authorize. `@BotFather` then lists the connected provider with its test
   token.
4. Use that token as `provider_token` in `sendInvoice`.

Live mode is **Connect CLICK Terminal Live** → `@CLICKTerminal`. It asks for the merchant
login issued by the bank and returns a token containing `:LIVE:`; the page's sample is
`123:LIVE:XXXX`. Click does not publish test cards or the test token format for
`@CLICKtest`.

## Vendor sample values

These values are from the request and response samples on the Click pages. Use them in
mocks, fixtures and unit tests that replay Click's shapes. They are illustrative only: none
is documented as working against a live Click host, and they are not real credentials.

| Product / call | Values | Page |
|---|---|---|
| SHOP API (Postman) | `click_trans_id` `134`, `click_paydoc_id` `1344`, `merchant_trans_id` `"user12344"`, `amount` `1000`, `merchant_prepare_id` `12345`, wrong amount `300`, unknown prepare id `999999999`, Click error `-5017` | testing/postman |
| SHOP API (playground) | `amount` `10000`, `click_trans_id` `123456789`, `click_paydoc_id` `987654321`, `merchant_trans_id` `txn_<ms>_<rand>` | testing/playground |
| Advanced / Split Shop | `service_id` `123`, `click_paydoc_id` `123`, `attempt_trans_id` `345`, `merchant_prepare_id` / `merchant_confirm_id` `12345`, `sign_time` `"2020-03-04 17:00:00"`, `amount` `1000`, `branch_id` `123`; compare range `"2020-03-03 00:00:00"` to `"2020-03-04 00:00:00"`; split `cntrg_id` `123` / `450` and `321` / `550`; error `-250` | additional/get-info, additional/shop-split |
| Merchant API `invoice/create` | `service_id` `12345`, `amount` `10000`, `phone_number` `"998901234567"`, `merchant_trans_id` `"order_123"` → `invoice_id` `1234567`; invoice status `-99` `"Deleted"` | merchant-api/requests |
| Merchant API status / reversal | `payment_id` `1234567`, `payment_status` `1`; `status_by_mti` returns `merchant_trans_id` `"user123"` | merchant-api/requests |
| `card_token/request` | `card_number` `"8600123412341234"`, `expire_date` `"0526"`, `temporary` `1` → `card_token` `"3B1DF3F1-7358-407C-B57F-0F6351310803"`, `phone_number` `"+998*******97"` | merchant-api/requests |
| `card_token/verify` | `card_token` `"token"`, `sms_code` `123456` → `card_number` `"8600 55** **** 3244"` | merchant-api/requests |
| `card_token/payment` | `card_token` `"token"`, `amount` `10000`, `transaction_parameter` `"order_123"` → `payment_id` `598761234`, `payment_status` `1` | merchant-api/requests |
| CLICK Pass `payment` | `service_id` `12345`, `otp_data` `"1234567415821"`, `amount` `500`, `cashbox_code` `"KASSA-1"`, `transaction_id` `"12345"` → `payment_id` `1234567`, `payment_status` `1`, `confirm_mode` `1`, `card_type` `"private"`, `processing_type` `"UZCARD"`, `card_number` `"860002******8331"`, `phone_number` `"998221234567"` | merchant-api/click-pass |
| Fiscalization | `service_id` `12345`, `payment_id` `987654321`, `received_card` `100000` (tiyin); `qrcode` `"https://ofd.soliq.uz/epi?t=EZ000000000030&r=123456789&c=20221028171340&s=854971301623"`; `get-ofd-data` returns `paymentId` `1946296773` | merchant-api/fiscalization |
| Payment button | `merchant_id` `46`, `merchant_user_id` `4`, `service_id` `36`, `transaction_param` `"user23151"`, `amount` `1000`, `return_url` `"merchant-website"`, `card_type` `"uzcard/humo"` (send `uzcard` or `humo`); the PHP sample uses `merchant_id` `20` and `service_id` `31` | click-button |
| Telegram | live token sample `123:LIVE:XXXX` | additional/telegram-payments |

Sample-specific caveats:

- `"8600123412341234"` and `sms_code` `123456` are format samples. A real
  `card_token/request` with them will fail.
- In `card_token/verify` and `card_token/payment`, the literal `"token"` stands for the
  `card_token` returned by `request`.
- `"uzcard/humo"` is not a valid `card_type`. Tests should send one value.
