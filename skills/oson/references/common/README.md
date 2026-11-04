# Oson API: sources, transport, auth, statuses, errors

Hand-written notes. Applies to every Oson product in this skill. Invoice methods:
[`../invoice/`](../invoice/README.md); the notification you receive:
[`../notify/`](../notify/README.md).

- Source: Oson's own open-source shop plugins on GitHub (`github.com/Osonuz`), read at
  the commits below; there is no public API reference:
  - https://github.com/Osonuz/Woocommerce-gateway-oson/blob/43ff85efb26c2284bfca7b186026ee0f3d011613/plugin.php
    and `inc/ic_exchanger_class.php` (WooCommerce, 2022-06-16)
  - https://github.com/Osonuz/Webasyst-Shop-Script-Plugin/blob/ea43f49aa0a9ff801d4e3a5d5a74f386b7e35ae3/oson/lib/osonPayment.class.php
    and `oson/lib/config/settings.php` (Webasyst Shop-Script, 2022-01-06)
  - https://github.com/Osonuz/OpenCart-Plugin/blob/b68320637c9dbd61f47359487921c036a466719d/upload/catalog/controller/extension/payment/osongw.php
    and `README.md` (OpenCart 3, 2021-12-03)
  - https://github.com/Osonuz/OSON-modul-for-1C-Bitriks/blob/04c8fc3cc8fd2f920913b1b8a989d9f18711e137/oson.payment/lib/api.php
    and `oson.payment/install/public/sale_payment/oson.payment/.description.php`
    (1C-Bitrix, 2021-04-21)
- Fetched: 2026-11-04
- Spec: none. `https://oson.uz/docs/`, which the Bitrix module cites as the API
  documentation, answers 404. Every contract in this skill is **reconstructed from the
  plugins' code**: field names and the signature formula are exact, but required fields,
  types, limits and error codes are what the plugins send and read, not a published
  contract. Warning [`oson.unverified-contract`](../lifecycle/README.md).

## Transport

| Item | Value |
|---|---|
| Base URL | `https://api.oson.uz/api/` (WooCommerce default, OpenCart README "в данный момент", Webasyst); the older Bitrix module calls `https://core.oson.uz:8443/api/` instead. Keep it in configuration. Warning [`oson.host-from-config`](../lifecycle/README.md) |
| Methods | `POST invoice/create`, `POST invoice/status` (Bitrix adds a trailing `/`) |
| Format | JSON body; headers `Content-Type: application/json` and `token: <token>` (WooCommerce and OpenCart also send `Accept: application/json`) |
| Auth | the `token` header (Webasyst also repeats `token` in the body) plus `merchant_id` in the body |
| Amounts | decimal **major units** of `currency` (soum for `UZS`), not tiyin. Warning [`oson.amount-major-units`](../lifecycle/README.md) |
| Currency | every plugin sends `UZS`; Webasyst also lists RUB, USD and EUR as shop currencies but sends the order total as `UZS` without converting it. Bitrix makes `currency` a setting (default `UZS`) |
| Ids | your id `transaction_id` (string, unique per invoice); Oson's id `bill_id` (an integer in every sample the plugins store) |
| Payment page | `pay_url` from `invoice/create`; redirect the payer there |
| Cabinet | `https://business.oson.uz/` (WooCommerce README: registration there is required) |
| Timeouts | WooCommerce and OpenCart use 5 s connect and total timeouts (a client choice, not a provider rule) |

## Auth

Two values from the Oson business cabinet (or from Oson by e-mail):

| Plugin label | Field | Where it goes |
|---|---|---|
| "Id магазина", "ID поставщика", `OSON_MERCHANT_ID` | `merchant_id` | JSON body of every call |
| "Ключ магазина", "Секретный ключ", `OSON_AUTH_KEY`, `token` | `token` | `token` HTTP header; also the secret in the notification `signature` |

Server-side only. The token is the signing secret for notifications too, so a leaked
token lets anyone forge a `PAID` notification.

## Statuses

The `status` string in the `invoice/create` and `invoice/status` replies and in the
notification. Spelled exactly as the plugins compare it.

| Status | Meaning (derived from how the plugins react) | Final? |
|---|---|---|
| `REGISTRED` | invoice created, waiting for the payer (spelled without the second E) | no |
| `ON_PROGRESS` | payment in progress | no |
| `PAID` | paid; the only success status | yes |
| `DECLINED` | declined or cancelled | yes |
| `PAY_ERROR` | payment failed | yes |
| `EXPIRED` | `lifetime` ran out before payment | yes |

- Fulfil only on `PAID`. The OpenCart plugin treats `ON_PROGRESS` as paid; do not copy
  that. Warning [`oson.on-progress-not-paid`](../lifecycle/README.md).
- WooCommerce and Bitrix react only to `PAID` and `DECLINED`; handle `PAY_ERROR` and
  `EXPIRED` as failures too (OpenCart and Webasyst do).
- Whether a final status can still change is not documented.

## Errors

| Reader | Error fields it reads | Notes |
|---|---|---|
| WooCommerce | `error_code`, `message` | anything other than `status: REGISTRED` after create is an error |
| Webasyst | `error_code`, `message` | a truthy `error_code` is an error |
| Bitrix | `message` | shown when `pay_url` is missing |
| OpenCart | `errno`, `errstr` | treats `errno > 0` as an error |

- No error code list is published. Log `error_code` and `message` as they come and show
  the payer a neutral message.
- Whether errors come with a non-200 HTTP status is not documented; parse the body in
  every case.
- Two plugins (WooCommerce, OpenCart) turn TLS verification off; never copy that. Warning
  [`oson.tls-verify`](../lifecycle/README.md).
