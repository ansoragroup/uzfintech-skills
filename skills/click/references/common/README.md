# Click: credentials, the two auth schemes, units, errors, tooling

Hand-written notes. They apply to every Click product in this skill.

- Source: https://docs.click.uz/en/ (overview), https://docs.click.uz/en/merchant-api/requests,
  https://docs.click.uz/en/merchant-api/errors, https://docs.click.uz/en/shop-api/requests,
  https://docs.click.uz/en/testing/playground, https://docs.click.uz/en/testing/postman,
  https://docs.click.uz/en/additional/cms, https://docs.click.uz/en/additional/example.
  Russian pages have the same paths without `/en`.
- Fetched: 2026-11-03

## How the pieces fit

Click lets the payer pay from its own channels: the CLICK SuperApp, my.click.uz, USSD and the
Telegram bot. The merchant's site and app can send the payer there too. A service becomes
payable through all of these once the merchant's billing answers the **SHOP API**
(Prepare / Complete). Everything else either sends the payer to Click (payment link, button,
deeplink) or lets the merchant call Click (Merchant API).

| Direction | Products | Auth |
|---|---|---|
| **Click calls you** | SHOP API (form-urlencoded), Advanced Shop / Split Shop (JSON) | `sign_string` MD5 with `SECRET_KEY` in the body |
| **You call Click** | Merchant API (invoices, status, reversal), card tokens, fiscalization, CLICK Pass | `Auth: merchant_user_id:digest:timestamp` header |
| **Payer is sent to Click** | payment link / button, pay-by-card widget, mobile deeplink | none (public parameters) |
| **Telegram** | Telegram Payments via `CLICK Terminal` | Telegram `provider_token` |

## Credentials

Click issues these at registration:

| Name | Used by | Secret? |
|---|---|---|
| `merchant_id` | payment link, button, widget, deeplink | no |
| `service_id` | every product; one merchant can have several services | no |
| `merchant_user_id` | Merchant API `Auth` header | no |
| `secret_key` (`SECRET_KEY`) | SHOP API `sign_string` and the Merchant API digest | **yes** |

Keep `secret_key` server-side, encrypted at rest, and out of logs and client code.

## Auth scheme 1: SHOP API signature (Click -> you)

Click sends `sign_string` = lowercase hex `md5` of a plain string concatenation. You
recompute it and compare in constant time:

```
Prepare  (action=0): md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + amount + action + sign_time)
Complete (action=1): md5(click_trans_id + service_id + SECRET_KEY + merchant_trans_id + merchant_prepare_id + amount + action + sign_time)
Advanced / Split   : md5(click_paydoc_id + attempt_trans_id + service_id + SECRET_KEY + <params values in order> + action + sign_time)
```

Concatenate the values **exactly as received** (raw strings from the request). Do not
re-format `amount` (e.g. `1000.00` vs `1000`) before hashing. A mismatch is answered with
`error: -1`.

## Auth scheme 2: Merchant API header (you -> Click)

```
Auth: <merchant_user_id>:<digest>:<timestamp>
digest    = sha1(timestamp + secret_key), lowercase hex
timestamp = Unix time in seconds, 10 digits
```

Also send `Accept` and `Content-Type`. Both `application/json` and `application/xml` are
supported; use JSON. Base URL: `https://api.click.uz/v2/merchant/`. Generate a fresh
timestamp per request and keep the server clock in sync (NTP).

## Units

| Where | Amount unit |
|---|---|
| SHOP API, Advanced / Split Shop, Merchant API (`invoice/create`, `card_token/payment`, `click_pass/payment`), payment link | **soums**, as a number that may have decimals (`float`; the link wants `N.NN`) |
| Fiscalization (`submit_items`: `Price`, `VAT`, `received_*`, ...) | integer **tiyin** (1 soum = 100 tiyin) |

Store money as integer tiyin internally and convert at the edge. Compare SHOP API amounts
in tiyin, after parsing, to avoid float errors.

## Errors

- SHOP API / Advanced Shop: the **merchant** returns `error` (int) and `error_note`. See the
  table in [`../shop-api/README.md`](../shop-api/README.md). A negative `error` *sent by
  Click* means the payment failed on Click's side: cancel it and answer `-9`.
- Merchant API: the body has `error_code` (int, `0` = success) and `error_note`. Transport
  and auth problems use HTTP status codes:

| HTTP | Meaning |
|---|---|
| 200, 201 | OK |
| 400 | malformed or invalid request |
| 401 | not authorized (bad `Auth` header) |
| 403 | access denied |
| 404 | resource not found |
| 406 | unacceptable format (`Accept` / `Content-Type`) |
| 410 | resource gone |
| 500 | Click internal error |
| 502 | service unavailable / maintenance |

The docs publish no catalogue of non-zero `error_code` values for the Merchant API. Treat
any non-zero value as a failure and log `error_note`.

## Tooling and ready-made integrations

- **Playground** (https://docs.click.uz/en/testing/playground): sends signed Prepare and
  Complete requests to your endpoint from the browser. Your endpoint must allow CORS from
  docs.click.uz for it to work.
- **Postman generator** (https://docs.click.uz/en/testing/postman): builds a collection
  with 15 SHOP API scenarios. They are listed in the shop-api README.
- **Sandbox notes**: both tools, Telegram test mode, how to get credentials and the vendor
  sample values are in [`../sandbox/README.md`](../sandbox/README.md). Click publishes no
  sandbox host or test cards.
- **Server examples**: `github.com/click-llc/click-integration-php` and
  `github.com/click-llc/click-integration-django`.
- **CMS plugins** under `github.com/click-llc`: WooCommerce, OpenCart 3, 1C-Bitrix,
  Joomla VirtueMart and CS-Cart. A Drupal Ubercart archive is linked from the CMS page.
  The plugins implement the SHOP API for you.
- **Android SDK**: `github.com/click-llc/android-msdk`.

## Doc caveats

- docs.click.uz is a client-rendered single-page site. Old `?p=` article links now load the
  new site's start page, and robots.txt disallows crawling. Link the `/en/...` routes above.
- The previous documentation described partial reversal. The current pages do not, so do
  not rely on it.
