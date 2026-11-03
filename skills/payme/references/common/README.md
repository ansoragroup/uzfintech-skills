# Payme (Paycom) API: transport, auth, errors, sandbox

Hand-written notes. Applies to every Payme product in this skill.

- Source: https://developer.help.paycom.uz/ (start page), https://developer.help.paycom.uz/nastroyka-vzaimodeystviya/,
  https://developer.help.paycom.uz/protokol-merchant-api/ and its subpages,
  https://developer.help.paycom.uz/protokol-subscribe-api/,
  https://developer.help.paycom.uz/vzaimodeystvie-protokolov-merchant-api-i-subscribe-api/,
  https://developer.help.paycom.uz/pesochnitsa/ (Russian pages)
- Fetched: 2026-11-03
- Vendor names: the docs say "Payme Business"; hosts and SDK packages still use `paycom`.

## Two protocols

| Protocol | Who sends requests | Use it for |
|---|---|---|
| Merchant API | **Payme calls your Endpoint URL** | hosted checkout payments with full control over transactions, guaranteed cancel, split ("receivers") |
| Subscribe API | **you call Payme** | card binding (tokens), one-click and recurring payments from your own form, invoices by SMS, holds |

Both are JSON-RPC 2.0 over HTTPS `POST` with named params only. A cashbox may use both;
test each protocol separately.

## Transport

| Item | Merchant API (inbound) | Subscribe API (outbound) |
|---|---|---|
| URL | your Endpoint URL, set in the cashbox settings | prod `https://checkout.paycom.uz/api`, test `https://checkout.test.paycom.uz/api` |
| Auth | `Authorization: Basic base64(<login>:<CASHBOX_KEY>)` | `X-Auth: <CASHBOX_ID>` (front-end methods) or `X-Auth: <CASHBOX_ID>:<CASHBOX_KEY>` (back end) |
| Source check | requests come only from a fixed Payme IP list: https://developer.help.paycom.uz/protokol-merchant-api/skhema-vzaimodeystviya/ | n.a. |
| Content type | `Content-Type: text/json; charset=UTF-8` (derived: parse the body whatever the header says) | JSON body |
| TLS | v1, v1.1 or v1.2 must be supported; vendor recommends ssl session cache 1 MB, ssl session timeout >= 10 min, keepalive timeout 10 min | standard HTTPS |
| HTTP status | **always 200**; any other status is read as `-32400` | 200 with `result` or `error` |
| Amounts | integer **tiyin** (1 UZS = 100) | same |
| Times | Unix epoch **milliseconds** (13 digits) | same |

Merchant API Basic auth: the login is issued by Payme technical staff; the password is the
cashbox key (36 characters). The sandbox uses `TEST_KEY` instead of the key. Wrong
credentials must answer `-32504`.

## Keys and ids

| Value | Where |
|---|---|
| Cashbox id (Merchant ID) | merchant cabinet: business -> "Кассы" -> context menu -> copy ID (https://developer.help.paycom.uz/poisk-klyucha-i-id-kassy-v-lichnom-kabinete/poisk-id-kassy/) |
| Key and test key | cashbox -> "Настройки" -> "Инструменты разработчика" (https://developer.help.paycom.uz/poisk-klyucha-i-id-kassy-v-lichnom-kabinete/poisk-klyucha-parolya-ot-kassy/) |

Keep the key and the test key in secrets, never in a browser or app bundle.

## Request, response and error envelope

- Request: `{"method": "<Name>", "params": {...}, "id": <integer>}`. Subscribe requests also
  carry `"jsonrpc": "2.0"` in the vendor examples.
- Success: `{"result": {...}, "id": <same id>}`.
- Error: `{"error": {"code": <int>, "message": ..., "data": ...}, "id": <same id>}`.
  In the Merchant API `message` is a **localized object** `{"ru", "uz", "en"}` shown to the
  payer; `data` holds extra detail (an `account` field name, or the unknown method name).
  `SetFiscalData` errors use a plain-string `message`.

Common JSON-RPC errors (the Merchant API answers them; method-specific codes are in each
product README):

| Code | Meaning | Retry? (derived) |
|---|---|---|
| `-32300` | request method is not `POST` | no |
| `-32700` | JSON parse error | no |
| `-32600` | required RPC fields missing or of the wrong type | no |
| `-32601` | method not found; put the requested method name in `data` | no |
| `-32504` | not enough privileges (failed Basic auth) | no |
| `-32400` | system (internal) error: database, file system, undefined behaviour | Payme decides; your handler must be safe to repeat |

## Delivery and retries (Merchant API)

- Payme repeats `CreateTransaction` and `PerformTransaction` with the same params when the
  response is lost. The sandbox sends `CreateTransaction`, `PerformTransaction` and
  `CancelTransaction` twice and requires identical answers.
- If your server stays silent for long, the payment is paused and handled manually by
  Payme staff.
- A transaction left in state `1` is cancelled after **43 200 000 ms (12 h)**.

## Sandbox (Merchant API)

- Web address: https://test.paycom.uz. Enter the Merchant ID (cashbox id) and `TEST_KEY`;
  the cashbox must have the Endpoint URL set.
- Choose the account type in the tests: **accumulative** (many payments, e.g. a phone
  balance) or **one-time** (one payment, e.g. a shop order).
- Scenario 1, create and cancel an unconfirmed transaction: wrong auth (`-32504`), wrong
  amount (`-31001` from CheckPerform and Create), unknown account (`-31050..-31099`),
  `CheckPerformTransaction` (`allow: true`), `CreateTransaction` plus its repeat,
  `CheckTransaction`, a new `CreateTransaction` while the order waits for payment
  (`-31008`), `CancelTransaction` of state `1`, `CheckTransaction`.
- Scenario 2, create, perform and cancel a performed transaction: `CheckPerformTransaction`,
  `CreateTransaction` (plus repeat), `PerformTransaction` (plus repeat), `CheckTransaction`,
  `CancelTransaction`, `CheckTransaction`.
- Run scenario 1 first (it includes the security checks). Test checkout initialization in
  the sandbox first, then in production. Receipt URL: sandbox `https://test.paycom.uz`,
  production `https://checkout.paycom.uz`.
- Testing against production adds load; Payme blocks accounts tied to misbehaving
  applications.

## Testing the Subscribe API

- Use the test merchant cabinet: create a business, add a "Виртуальный терминал" cashbox,
  and ask Payme technical staff for its key. Send requests to
  `https://checkout.test.paycom.uz/api`.
- The test-cabinet login, the test cards with their SMS code and the scenarios per card are
  in [`../sandbox/README.md`](../sandbox/README.md). Keep them out of production code paths.
- Holds can be tested only in production (see [`../subscribe/`](../subscribe/README.md)).

## Other integration paths (summary)

- Android SDK: `uz.paycom:payment`; start `PaymentActivity` with extras `EXTRA_ID` (cashbox
  id), `EXTRA_AMOUNT`, `EXTRA_SAVE`, `EXTRA_LANG` (`RU` / `UZ`);
  `PaycomSandBox.setEnabled(true)` targets the test platform. The result returns
  `number`, `expire`, `token`, `recurrent`, `verify`; pay the token from your back end with
  `receipts.create` + `receipts.pay`. Source: https://developer.help.paycom.uz/integratsiya-s-mobilnym-prilozheniem/
- Telegram bot: BotFather -> Payments -> Paycom provider with a separate cashbox; answer
  `answerPreCheckoutQuery` within 10 s. Source: https://developer.help.paycom.uz/telegram-bot/
- CMS plugins (WooCommerce, OpenCart, Magento, JoomShopping, VirtueMart, 1C-Bitrix,
  Webasyst, CS-Cart) already implement the Merchant API and are tested with the same
  sandbox scenarios. Source: https://developer.help.paycom.uz/plaginy-dlya-cms/
- Server examples (PHP, Java / Kotlin) are linked from
  https://developer.help.paycom.uz/primer-realizatsii-servera/.
- Brand assets (logo, colour) for the "Powered by Payme" label:
  https://developer.help.paycom.uz/resursy/
