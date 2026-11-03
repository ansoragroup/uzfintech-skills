# Payme sandbox and test data

Hand-written notes with the exact test values Payme publishes for its test environments.
Use them in tests, fixtures and examples. They work only on the test hosts below; never send
them to production, and never hard-code them in production code paths. Transport and auth:
[`../common/README.md`](../common/README.md).

- Sources: https://developer.help.paycom.uz/pesochnitsa/,
  https://developer.help.paycom.uz/protokol-subscribe-api/,
  https://developer.help.paycom.uz/vzaimodeystvie-protokolov-merchant-api-i-subscribe-api/,
  https://developer.help.paycom.uz/integratsiya-s-mobilnym-prilozheniem/testirovanie-v-pesochnitse/,
  https://developer.help.paycom.uz/poisk-klyucha-i-id-kassy-v-lichnom-kabinete/poisk-klyucha-parolya-ot-kassy/,
  https://developer.help.paycom.uz/integratsiya-s-mobilnym-prilozheniem/podklyuchenie-biblioteki/,
  https://developer.help.paycom.uz/telegram-bot/podklyuchenie-bota/, and the method and
  checkout pages named in "Vendor sample values" (Russian pages)
- Fetched: 2026-11-03

## Environments

| What | Test | Production |
|---|---|---|
| Merchant API sandbox (Payme calls your Endpoint URL) | `https://test.paycom.uz` | n.a. (live traffic) |
| Checkout GET / POST (receipt URL) | `https://test.paycom.uz` | `https://checkout.paycom.uz` |
| Subscribe API (JSON-RPC endpoint) | `https://checkout.test.paycom.uz/api` | `https://checkout.paycom.uz/api` |
| Merchant cabinet | `https://merchant.test.paycom.uz` (login page `/#/login`) | the production Payme Business cabinet |
| Android SDK | `PaycomSandBox.setEnabled(true)` | `PaycomSandBox.setEnabled(false)` (the default) |
| Telegram payments | BotFather -> Payments -> Paycom.Uz -> "Connect Paycom Test" (no registration) | "Connect Paycom Live" |

Each protocol is tested on its own: the Merchant API in the sandbox at `test.paycom.uz`, the
Subscribe API through a cashbox in the test cabinet.

## Test cards

Every card has expiry **03/99** (send `"0399"` as `card.expire` in `cards.create`). The SMS
code for every test card is always **`666666`**.

| PAN | Expiry | What it triggers |
|---|---|---|
| `8600 0609 2109 0842` | 03/99 | SMS informing is not connected on the card (verify-code flow fails) |
| `3333 3364 1580 4657` | 03/99 | card expired |
| `4444 4459 8745 9073` | 03/99 | card blocked |
| `8600 1434 1777 0323` | 03/99 | unknown system error |
| `8600 1343 0184 9596` | 03/99 | 10-second processing delay, then an error (use it to test your timeouts) |
| `8600 4954 7331 6478` | 03/99 | no special behaviour: a working card for the happy path |
| `8600 0691 9540 6311` | 03/99 | no special behaviour: a working card; the vendor's own Subscribe examples use it (masked `860006******6311`) |

Unspaced, as sent in a request: `8600060921090842`, `3333336415804657`, `4444445987459073`,
`8600143417770323`, `8600134301849596`, `8600495473316478`, `8600069195406311`.

The vendor examples write the same expiry as `"0399"` in requests, `"03/99"` in
`cards.check` answers and `"9903"` in one `receipts.get_all` answer. Send `"0399"` (MMYY)
and accept any of the three in answers (derived).

## Test credentials (how to get them)

No shared keys exist; every developer gets their own.

**Merchant API sandbox (`TEST_KEY`)**

1. In the Payme Business cabinet add a web cashbox. Payme then issues two keys for it:
   the key (live payments) and the test key (`TEST_KEY`, sandbox only).
2. Find both under cashbox -> "Настройки" -> "Инструменты разработчика". The Merchant ID is
   the cashbox id from the cashbox developer parameters (or "Скопировать ID" in the cashbox
   list).
3. Set the cashbox Endpoint URL to your billing endpoint; the sandbox calls it.
4. Open `https://test.paycom.uz`, enter the Merchant ID and `TEST_KEY`.

During sandbox runs Payme sends `Authorization: Basic base64(<login>:<TEST_KEY>)`; in
production the password is the live key (derived). Keep both in configuration, never in code.

**Subscribe API test cashbox**

1. Log in to `https://merchant.test.paycom.uz`: login = your own mobile phone number,
   password = **`qwerty`**, SMS code = **`666666`**.
2. Create a business, then add a cashbox of type "Виртуальный терминал".
3. Ask Payme technical support for that cashbox's key (password); the test cabinet does not
   show it.
4. The test cashbox id is in the browser address bar while the cashbox is open.
5. Send requests to `https://checkout.test.paycom.uz/api` with
   `X-Auth: <TEST_CASHBOX_ID>` (front-end card methods) or
   `X-Auth: <TEST_CASHBOX_ID>:<TEST_CASHBOX_KEY>` (back end).

## Merchant API sandbox scenarios

Pick the account type for each run: **accumulative** (pays many times, e.g. a phone
balance) or **one-time** (pays once, e.g. a shop order). The sandbox sends
`CreateTransaction`, `PerformTransaction` and `CancelTransaction` **twice**; the second
answer must equal the first.

Scenario 1 (run first; it holds the security checks): create and cancel an unconfirmed
transaction.

| Step | Your answer must be |
|---|---|
| "Неверная авторизация" (wrong Basic auth) on any method | error `-32504` |
| "Неверная сумма": a real order with a wrong amount | `-31001` from `CheckPerformTransaction` and `CreateTransaction` |
| "Несуществующий счёт": a valid amount with an unknown order | an error in `-31050..-31099` with a localized `message` and `data` = the account field name |
| `CheckPerformTransaction` with a real account and amount in tiyin | `result.allow: true` |
| `CreateTransaction` (one-time account, order awaiting payment), then its repeat | no error, identical answers (`state 1`) |
| `CheckTransaction` | no error |
| `CreateTransaction` with a **new** transaction id for the same waiting order | `-31008` |
| `CancelTransaction` of the state-`1` transaction, then `CheckTransaction` | no error; state `-1` |

Scenario 2: create, perform and cancel a performed transaction.

| Step | Your answer must be |
|---|---|
| `CheckPerformTransaction` | `allow: true` |
| `CreateTransaction` + repeat | no error, identical answers |
| `CheckTransaction` | no error |
| `PerformTransaction` + repeat | no error, identical answers (`state 2`) |
| `CheckTransaction` | no error |
| `CancelTransaction` + repeat, then `CheckTransaction` | no error; state `-2` |

CMS plugins are checked with the same two scenarios. Test checkout initialization (GET /
POST to `https://test.paycom.uz`) only after both scenarios pass, then repeat it in
production.

## Subscribe API scenarios (derived from the card table)

| Goal | Card | Expected outcome |
|---|---|---|
| bind and pay (happy path) | `8600495473316478` or `8600069195406311` | `cards.create` -> `cards.get_verify_code` -> `cards.verify` with `666666` -> `receipts.create` + `receipts.pay` reaches state `4` |
| SMS not connected | `8600060921090842` | an error during verification |
| expired card | `3333336415804657` | an error on `cards.create` or pay |
| blocked card | `4444445987459073` | an error |
| system error handling | `8600143417770323` | an error; your code must not mark the order paid |
| slow processing / timeout | `8600134301849596` | about 10 s of delay, then an error; check your HTTP timeout and that you do not double-charge |

The exact error codes for these cards are not documented (Subscribe error codes are
undocumented overall). Holds (`hold: true`) cannot be tested in the sandbox; test them in
production with small amounts.

## Ready-made sandbox bodies

`cards.create` against `https://checkout.test.paycom.uz/api` with `X-Auth: <TEST_CASHBOX_ID>`:

```json
{"id": 1, "method": "cards.create",
 "params": {"card": {"number": "8600495473316478", "expire": "0399"}, "save": true}}
```

`cards.verify` with the test SMS code:

```json
{"id": 3, "method": "cards.verify",
 "params": {"token": "<CARD_TOKEN_FROM_CARDS_CREATE>", "code": "666666"}}
```

## Vendor sample values

Copied exactly from the request and response samples on the Payme pages (paths below are
under `https://developer.help.paycom.uz/`). Use them in mocks, fixtures and unit tests that
replay Payme's shapes. They are illustrative: none is documented as a live object on the
test hosts.

| Call | Values | Page |
|---|---|---|
| Merchant API `CheckPerformTransaction` | `amount` `500000` -> `allow` `true` | `metody-merchant-api/checktransaction` |
| Merchant API `CreateTransaction` | `id` `"5305e3bab097f420a62ced0b"`, `time` `1399114284039`, `amount` `500000` -> `create_time` `1399114284039`, `transaction` `"5123"`, `state` `1`; chain payment `receivers` `[{"id": "5305e3bab097f420a62ced0b", "amount": 200000}, {"id": "4215e6bab097f420a62ced01", "amount": 300000}]` | `metody-merchant-api/createtransaction` |
| Merchant API `PerformTransaction` | same `id` -> `transaction` `"5123"`, `perform_time` `1399114284039`, `state` `2` | `metody-merchant-api/performtransaction` |
| Merchant API `CancelTransaction` | same `id`, `reason` `1` -> `transaction` `"5123"`, `cancel_time` `1399114284039`, `state` `-2` | `metody-merchant-api/canceltransaction` |
| Merchant API `CheckTransaction` | same `id` -> `create_time` `1399114284039`, `perform_time` `1399114285002`, `cancel_time` `0`, `transaction` `"5123"`, `state` `2`, `reason` `null` | `metody-merchant-api/checkperformtransaction` |
| Merchant API `GetStatement` | `from` `1399114284039`, `to` `1399120284000` -> one transaction with the values above | `metody-merchant-api/getstatement` |
| Merchant API `SetFiscalData` | receipt `id` `"61396aaed8b87a4c215ae556"`, `type` `"PERFORM"` or `"CANCEL"`; `fiscal_data` `receipt_id` `121` / `123`, `status_code` `0`, `message` `"accepted"`, `terminal_id` `"EP000000000025"`, `fiscal_sign` `"800031554082"`, `date` `"20220706221021"`; unknown receipt -> `-32001` | `metody-merchant-api/setfiscaldata` |
| fiscal `detail` (CheckPerformTransaction, `receipts.create`) | `receipt_type` `0`; shipping `title` `"Доставка до ттз-4 28/23"`, `price` `500000`; item `title` `"Помидоры"`, `price` `505000`, `count` `2`, `discount` `10000`, `code` (IKPU) `"00702001001000001"`, `units` `241092`, `vat_percent` `15`, `package_code` `"123456"` | `metody-merchant-api/checktransaction`, `metody-subscribe-api/receipts.create` |
| Subscribe `cards.create` / `cards.verify` / `cards.check` | request `id` `123`; card `8600069195406311`, `expire` `"0399"`, `save` `true` -> `number` `"860006******6311"`, `expire` `"03/99"`, `recurrent` `true`, `verify` `false` (then `true` after `cards.verify` with `"666666"`) | `metody-subscribe-api/cards.create`, `cards.verify`, `cards.check` |
| Subscribe `cards.get_verify_code` | -> `sent` `true`, `phone` `"99890*****31"`, `wait` `60000` | `metody-subscribe-api/cards.get_verify_code` |
| Subscribe `receipts.create` | `id` `4`, `amount` `500000`, `account` `{"order_id": "test"}`, the fiscal `detail` above -> `_id` `"62da73b0803aced907a52b46"`, `create_time` `1658483632482`, `pay_time` `0`, `state` `0`; discount line `"Скидка 5%"`, `price` `10000` | `metody-subscribe-api/receipts.create` |
| Subscribe `receipts.pay` / `receipts.check` / `receipts.cancel` | receipt `id` `"2e0b1bc1f1eb50d487ba268d"`; pay -> `state` `4`, `amount` `3500`; check -> `state` `4`; cancel -> `state` `21`, `amount` `2000`; account field `name` `"order_id"`; merchant `name` `"Online Shop LLC"` | `metody-subscribe-api/receipts.pay`, `receipts.check`, `receipts.cancel` |
| Subscribe `receipts.get_all` | `count` `2`, `from` `1636398000000`, `to` `1636398000000`, `offset` `0` -> `_id` `"618a5b9f1045eb4efde669a4"`, `amount` `100000`, `state` `4`, account fields `loan_id` and `transaction`, card `expire` `"9903"` | `metody-subscribe-api/receipts.get_all` |
| Checkout GET and payment button | `ac.order_id=197`, `a=500` (`amount` `500`), `lang` `ru`, button `colored` or `white`; URL shape `https://checkout.paycom.uz/base64(m=<MERCHANT_ID>;ac.order_id=197;a=500)` | `initsializatsiya-platezhey/otpravka-cheka-po-metodu-get`, `.../generatsiya-knopki-oplaty-i-qr-koda` |

Sample-specific caveats:

- The page slugs `checkperformtransaction` and `checktransaction` are swapped upstream: each
  serves the other method.
- The checkout samples carry a concrete merchant id, left out here; put your test cashbox
  id in `m` / `merchant`.
- `amount` `500` in the checkout sample is 5 UZS in tiyin.

## Do not put in tests or docs

- Live cashbox keys, `TEST_KEY` values and test cashbox keys: they are per account. Load them
  from configuration.
- The `X-Auth` keys, card tokens, merchant ids, the Merchant API `account.phone` value and
  the payer phone numbers shown in the vendor examples: they may belong to real accounts. Use
  `<TEST_CASHBOX_ID>`, `<CARD_TOKEN>`, `<MERCHANT_ID>` and `998901234567`.
- Payme's source IP list: read it from the vendor page when you configure a firewall.
