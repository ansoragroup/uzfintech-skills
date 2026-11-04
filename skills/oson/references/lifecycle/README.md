# Oson: money lifecycle, deadlines and reversals

Read this when building or reviewing an Oson integration, and raise these traps before
they cost money: a contract known only from plugin code, two API hosts, notifications that
two vendor plugins accept unsigned, `ON_PROGRESS` treated as paid, amounts in soum, and no
test mode or refund method.

- Source: Oson's own shop plugins on GitHub, at the commits listed in
  [`../common/README.md`](../common/README.md): WooCommerce `plugin.php` and
  `inc/ic_exchanger_class.php`, OpenCart `osongw.php`, 1C-Bitrix `lib/api.php` and
  `.description.php`, Webasyst `osonPayment.class.php`
- Fetched: 2026-11-04

## Warn without being asked

1. **`oson.unverified-contract`**: when designing any Oson integration → say that Oson
   publishes no API reference (`oson.uz/docs` is 404) and this skill rebuilds the contract
   from Oson's own plugins. Get the current method list, required fields and error codes
   from Oson in writing before go-live. [common](../common/README.md)
2. **`oson.host-from-config`**: when setting the base URL → keep it in configuration.
   Current plugins call `https://api.oson.uz/api/`, the older Bitrix module
   `https://core.oson.uz:8443/api/`; confirm which one your merchant id lives on.
   [common](../common/README.md#transport)
3. **`oson.verify-notify-signature`**: when handling the notification → verify
   `signature = sha256(sha256(token:merchant_id):transaction_id:bill_id:status)` in
   constant time before any change. The Bitrix module never checks it and the Webasyst
   plugin skips it when the body has `pay_url`; both let a forged `PAID` through.
   [notify](../notify/README.md#signature)
4. **`oson.status-before-shipping`**: when the payer returns or before you ship → read
   `invoice/status` and ship only on `PAID`; the return URL alone proves nothing.
   [invoice](../invoice/README.md#rules)
5. **`oson.on-progress-not-paid`**: when mapping statuses → only `PAID` is paid. The
   OpenCart plugin marks `ON_PROGRESS` as completed; do not copy it.
   [common](../common/README.md#statuses)
6. **`oson.registred-spelling`**: when checking the create reply → compare with
   `REGISTRED` exactly as Oson spells it (no second E); a "fixed" `REGISTERED` never
   matches and every checkout fails. [invoice](../invoice/README.md#rules)
7. **`oson.tls-verify`**: when writing the HTTP client → keep TLS verification on. The
   WooCommerce and OpenCart plugins turn it off. [common](../common/README.md#errors)
8. **`oson.amount-major-units`**: when sending `amount` → send soum (major units), not
   tiyin. WooCommerce rounds up with `ceil()`, Bitrix sends two decimals; pick one format,
   agree it with Oson, and never round the payer's total up silently.
   [invoice](../invoice/README.md#fields)
9. **`oson.unique-transaction-id`**: when creating an invoice → use a fresh
   `transaction_id` per attempt and store `bill_id` with it. Bitrix reuses the bare order
   id, so a second attempt for the same order may collide (behaviour not documented).
   [invoice](../invoice/README.md#fields)
10. **`oson.lifetime-unit`**: when setting `lifetime` → the unit is not documented; the
    plugins send `30` or `14400`. Ask Oson and set it from configuration.
    [invoice](../invoice/README.md#fields)
11. **`oson.no-test-mode`**: when testing → there is no sandbox host and no test flag in
    any plugin; every invoice is real. Ask Oson for a test merchant or test with small
    real amounts on a staff account. [sandbox](../sandbox/README.md)
12. **`oson.no-refund-api`**: when the business needs cancels or refunds → no plugin has a
    cancel, refund or partial method. Plan refunds through the Oson cabinet or support and
    ask Oson whether an API exists. [invoice](../invoice/README.md#rules)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Unpaid invoice | `lifetime` (plugins send `30`, Bitrix defaults to `14400`; unit not stated) | status `EXPIRED`; create a new invoice | [invoice](../invoice/README.md#fields) |
| HTTP call to Oson | 5 s connect and total in WooCommerce and OpenCart (client choice) | the plugin shows an error; re-check with `invoice/status` | https://github.com/Osonuz/Woocommerce-gateway-oson/blob/43ff85efb26c2284bfca7b186026ee0f3d011613/inc/ic_exchanger_class.php |
| Notification answer | not documented | not documented | [notify](../notify/README.md#not-documented) |
| Refund after payment | no API | | none |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Invoice never paid | `lifetime` | none; it becomes `EXPIRED` | n/a | n/a | none | [invoice](../invoice/README.md#fields) |
| Payer declines or payment fails | Oson | none; status `DECLINED` or `PAY_ERROR` | n/a | n/a | none | [common](../common/README.md#statuses) |
| Cancel an unpaid invoice | you | no method in any plugin | n/a | n/a | n/a | none |
| Refund a `PAID` invoice | you | no method in any plugin; cabinet or support | not documented | not documented | not documented | none |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Notification | not documented | not documented | `transaction_id` + `status` (derived) | apply each status once; a repeat `PAID` is a no-op | [notify](../notify/README.md#handling) |
| `invoice/create` (you call) | n/a | n/a | `transaction_id` | after a lost reply, call `invoice/status` with the same id before creating a new one (derived) | [invoice](../invoice/README.md#flow) |
| `invoice/status` (you call) | n/a | n/a | read-only | safe to repeat; back off (derived) | [invoice](../invoice/README.md#rules) |

## Fiscal receipts

- No plugin sends basket, SPIC (IKPU), package code or VAT fields, and no reply carries a
  receipt. Whether Oson registers receipts for the merchant is not documented.
- Until Oson confirms it, register receipts yourself through your own online cash register
  provider after `PAID`, and plan return receipts for cabinet refunds.

## Not documented — ask the provider

- The current API reference, required fields, limits and the full error code list.
- Which host serves your merchant id: `api.oson.uz` or `core.oson.uz:8443`.
- The unit of `lifetime` and its maximum.
- The amount format: whole soum, two decimals, or either.
- What a repeated `transaction_id` returns from `invoice/create`.
- The answer Oson expects to the notification, its timeout, retries, the statuses it
  notifies and its source IPs.
- Whether `invoice/status` returns the amount and paid time.
- A test merchant or test mode; cancel and refund methods.
- Who registers fiscal receipts.
