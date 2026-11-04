# Oson invoice (`invoice/create`, `invoice/status`): payment page by link

Hand-written notes. Transport, auth, statuses and errors:
[`../common/README.md`](../common/README.md). The notification Oson sends you:
[`../notify/README.md`](../notify/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/) (built from what the plugins send and read; no vendor sample exists).

- Source: https://github.com/Osonuz/Woocommerce-gateway-oson/blob/43ff85efb26c2284bfca7b186026ee0f3d011613/plugin.php
  (lines 389-420), https://github.com/Osonuz/OpenCart-Plugin/blob/b68320637c9dbd61f47359487921c036a466719d/upload/catalog/controller/extension/payment/osongw.php,
  https://github.com/Osonuz/OSON-modul-for-1C-Bitriks/blob/04c8fc3cc8fd2f920913b1b8a989d9f18711e137/oson.payment/lib/api.php,
  https://github.com/Osonuz/Webasyst-Shop-Script-Plugin/blob/ea43f49aa0a9ff801d4e3a5d5a74f386b7e35ae3/oson/lib/osonPayment.class.php
- Fetched: 2026-11-04
- Spec: none; reconstructed from plugin code. Warning
  [`oson.unverified-contract`](../lifecycle/README.md).
- Needs: `merchant_id` and `token` from the cabinet (`https://business.oson.uz/`).

## Flow

```
POST invoice/create {merchant_id, transaction_id, user_account, amount, currency,
                     comment, phone, lang, lifetime, return_url, notify_url?}
   └─> {status REGISTRED, transaction_id, bill_id, pay_url}
       store bill_id next to your transaction_id, redirect the payer to pay_url
payer pays on Oson ─> notification to your notify URL ({transaction_id, bill_id, status, signature})
payer comes back to return_url ─> POST invoice/status {merchant_id, transaction_id}
   └─> {status, transaction_id, bill_id, pay_url}
fulfil only on PAID, confirmed by a verified notification or by invoice/status
```

## Methods

| Method | Endpoint | Params (as the plugins send them) | Result (as the plugins read it) |
|---|---|---|---|
| create | `POST invoice/create` | `merchant_id`, `transaction_id`, `user_account`, `amount`, `currency`, `comment`, `phone`, `lang`, `lifetime`, `return_url`, `notify_url` (OpenCart only) | `status` (`REGISTRED` on success), `transaction_id`, `bill_id`, `pay_url`; on failure `error_code`, `message` |
| status | `POST invoice/status` | `merchant_id`, `transaction_id` | `status`, `transaction_id`, `bill_id`, `pay_url`; on failure `error_code`, `message` |

Every plugin sends all of the create fields, so treat them all as required until Oson
says otherwise. No plugin sends anything else (no basket, no fiscal fields, no card data).

## Fields

| Field | What the plugins put there | Notes |
|---|---|---|
| `merchant_id` | the shop id from the cabinet | in every call |
| `transaction_id` | your unique invoice id: WooCommerce `uniqid()`, Webasyst `time()_order_app_merchant`, Bitrix the bare order id | the key for `invoice/status` and the notification. Make it unique per attempt. Warning [`oson.unique-transaction-id`](../lifecycle/README.md) |
| `user_account` | the order id (WooCommerce, OpenCart) or the customer id (Bitrix) | free text from your side |
| `amount` | WooCommerce: `ceil()` of the total (whole soum); Bitrix: a string with two decimals; OpenCart and Webasyst: the raw order total | major units, not tiyin. Warning [`oson.amount-major-units`](../lifecycle/README.md) |
| `currency` | `UZS` | |
| `comment` | "Payment order #<id>" or similar | shown to the payer (derived) |
| `phone` | the payer's phone; Bitrix strips the `+` | send digits only, `998XXXXXXXXX` (derived from Bitrix) |
| `lang` | two letters: `ru`, `uz`, `en` | Bitrix default `ru` |
| `lifetime` | `30` (WooCommerce, OpenCart, Webasyst) or `14400` (Bitrix default) | the unit is not stated. Warning [`oson.lifetime-unit`](../lifecycle/README.md) |
| `return_url` | the page the payer comes back to | Bitrix appends `?ORDER_ID=<id>`; check the status there, never trust the redirect |
| `notify_url` | your notification URL | only OpenCart sends it; the others rely on the URL set in the cabinet. Send it and also set it in the cabinet (derived) |
| `bill_id` (result) | Oson's invoice id | an integer in the WooCommerce and OpenCart tables, VARCHAR(255) in Webasyst; store it as a string |
| `pay_url` (result) | the Oson payment page | redirect the payer there; do not build it yourself |

## Rules

- Success of `invoice/create` is `status: "REGISTRED"` with a non-empty `pay_url`. Anything
  else is an error: show a neutral message and log `error_code` and `message`.
  Warning [`oson.registred-spelling`](../lifecycle/README.md).
- `REGISTRED` and `ON_PROGRESS` are not paid. Ship only on `PAID`. Warnings
  [`oson.on-progress-not-paid`](../lifecycle/README.md),
  [`oson.status-before-shipping`](../lifecycle/README.md).
- Call `invoice/status` when the payer returns and before you ship when no verified
  notification arrived. No plugin polls on a schedule; if you poll, back off (derived).
- There is no cancel, refund or partial-capture method in any plugin. Warning
  [`oson.no-refund-api`](../lifecycle/README.md).
- Keep the host in configuration: `https://api.oson.uz/api/` for current plugins,
  `https://core.oson.uz:8443/api/` in the older Bitrix module. Warning
  [`oson.host-from-config`](../lifecycle/README.md).
