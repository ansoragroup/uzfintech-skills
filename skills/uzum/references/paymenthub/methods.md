# Uzum PaymentHub: methods

- Source: https://developer.uzumbank.uz/paymenthub/ (account, card, merchant, receipt pages)
- Fetched: 2026-11-03
- `*` = required. Amounts in tiyin, times in Unix ms. Full trees: `schemas/<method>.json`.
- **Wrapper** = the key inside `result` that holds the payload (`-` = payload is `result` itself).

## Account

| Method | Params | Wrapper | Result fields |
|---|---|---|---|
| `account.attached.list` | `type*` (1, 5, 6, 7, 12) | `accounts` (array) | `number`, `mfo`, `currency` |
| `account.balance` | `number*`, `mfo*` | `account` | `number`, `mfo`, `balance` (for requisite payments) |
| `account.transfer.balance` | `number*`, `mfo*` | `account` | `number`, `mfo`, `balance` (for account-to-card) |
| `account.check` | `number*`, `mfo*` (receiver) | `account` | `inn`, `name`, `valid` (bool) |
| `account.history` | `account{number*, mfo*}`, `page{page*, size*}`, `filter{from*, to*, type*}` (`CREDIT` / `DEBIT` / `null`) | - | `account{number, mfo, currency}`, `page{page, size, total_elements, total_pages}`, `total_debit`, `total_credit`, `open_balance`, `close_balance`, `documents[{doc_id, date_time, amount, details, corr_name, corr_mfo, corr_account, currency, corr_bank, corr_inn}]` |

## Card binding

| Method | Params | Wrapper | Result fields |
|---|---|---|---|
| `cards.add` (first send) | `number*` (PAN), `expire*` (`MMYY`), `sms{hash*, template*}`, `requester_phone`, `merchant_id*` | `card` | `id` (SMS confirmation id), `phone_mask` |
| `cards.add` (resend) | `id*` (from the first send), `sms{hash*}` | `card` | `id`, `phone_mask` |
| `cards.add.confirm` | `id*`, `code*` (OTP, valid 2 min) | `card` | `token`, `active`, `state`, `phone`, `balance`, `masked_pan`, `holder_name` |
| `cards.get` | `token*` | `card` | same as `cards.add.confirm` |
| `cards.get.receiver` | `number` (PAN) or `token` | `card` | `holder_name`, `card_state` (`ACTIVE` / `NOT ACTIVE`), `bank{code, name}` |

Card `state`: `0` active with SMS notifications, `-1` no SMS notifications, `-2` expired,
`-4` blocked, `-10` PIN tries exceeded, `-20` inactive. `requester_phone` mismatch gives
`-31608`. `sms.template` numbers come from the bank. `merchant_id` sets the partner name
shown in the SMS.

## Merchant (service catalogue for online payments)

| Method | Params | Wrapper | Result fields |
|---|---|---|---|
| `merchant.get.categories` | none | `categories` | `id`, `name` |
| `merchant.get.all` | none | `merchants` | service objects (below) |
| `merchant.get.by.category` | `category_id*` | `merchants` | service objects |
| `merchant.get.by.id` | `merchant_id*` | `merchant` | one service object |
| `merchant.info` | `merchant_id*`, `accounts[{key*, value*}]*` | `info` | `merchant_id`, `items[{title, type, key, value}]` |

Service object: `merchant_id`, `merchant_name`, `gateway_name`, `category_id`, `logo_url`,
`min_amount`, `max_amount`, `fields[{key, name, regex, type, send_on_pay, placeholder,
mask_type?, masks?}]`. `accounts[].key` comes from `fields[].key`. In `merchant.info`, an item
of type `SELECT` has `value` as an array of `{value, name}`; `STRING` has a plain string.

## Receipts: online payment by card (type 1)

| Method | Params | Wrapper | Result |
|---|---|---|---|
| `receipt.create` | `merchant_id*`, `ext_id`, `accounts[{key*, value*}]*`, `amount*` | `receipt` | receipt, `state 0` |
| `receipt.pay.by.card` | `id*`, `card{token*}` | `receipt` | receipt, `state 4` when paid |

Online receipt extras: `merchant{...}`, `account[{key, value}]`, `details[{title, type, key,
value}]`, `transaction_details{reference_number, credit_reference_number}`,
`ofd{url, terminal_id, fiscal_sign}`.

## Receipts: card to account by requisites (type 7)

| Method | Params | Wrapper | Result |
|---|---|---|---|
| `receipt.create.requisite` | `sender{token*}`, `ext_id*`, `amount*`, `payment_detail{number* (20-27 digits), name* (>= 3), sender_name* (>= 3), inn, mfo*, details* (>= 3)}` | - | receipt, `state 0` |
| `receipt.confirm.requisite` | `id*` | - | receipt, `state 30` (processing) or `4` |

Result: `sender{token, amount, currency, commission}`, `receiver{account, mfo, amount,
currency, commission}`, `details{name, sender_name, details, memorial}` (`memorial` is a
link to the payment-order PDF).

## Receipts: account to account by requisites (type 7)

| Method | Params | Wrapper | Result |
|---|---|---|---|
| `receipt.pay.requisite` | `amount*`, `ext_id*`, `sender{number*, mfo*}` (your account), `payment_detail{number* (20 or 25-27 digits), name*, details*, sender_name*, sender_type (HUMO / UZCARD; needed for fee calc), mfo, inn}` | `receipt` | receipt, `state 30` |

Order: `account.balance` -> `account.check` (receiver valid?) -> `receipt.pay.requisite` ->
poll `receipt.check.id`. Result: `sender{account, mfo, amount, currency, commission}`,
`receiver{...same}`, `details{name, sender_name, details, memorial, account_type}`.

## Receipts: account to card (type 6)

| Method | Params | Wrapper | Result |
|---|---|---|---|
| `receipt.account.create.transfer` | `amount*`, `ext_id*`, `account{number*, mfo*}` (from `account.attached.list {type: 6}`), `sender{id*, name*, document{nationality, type, series_number, birth_date, valid_to}}`, `receiver{number*}` (16-digit PAN), `description` (<= 254) | - | receipt, `state 0` |
| `receipt.account.confirm.transfer` | `id*` | - | receipt, `state 4` / `50` / `51` / `57` |

Result: `sender{account, mfo, amount, currency, commission}`, `receiver{masked_pan,
holder_name, amount, currency, commission}`. Document `type`: `Passport`, `IDCard`,
`ResidencePermit`; dates `yyyyMMdd`; `nationality` ISO alpha-2.

## Receipts: lookup, reconciliation, registry

| Method | Params | Wrapper | Result |
|---|---|---|---|
| `receipt.check.id` | `id*` (receipt id) | `receipt` | receipt for its type |
| `receipt.check.extId` | `id*` (**your `ext_id`**, still named `id`) | `receipt` | receipt for its type |
| `receipt.compare.payment` | `from*`, `to*`, `type*` (receipt type) | `compare` | `id`, `from`, `to`, `type` |
| `receipt.compare.check` | `id*` (from compare.payment) | `compare` | `bank[]`, `supplier[]`, `error[]` of `{ext_id, amount, id}` |
| `receipt.registry` | `page{number*, size*<=100}`, `create_time{from, to}` or `pay_time{from, to}`, `states[]`, `types[]*` | `registry` | `page`, `size`, `total_pages`, `total_items`, `items[]` |

Reconciliation runs in the background: `receipt.compare.check` returns `-31615` until it is
done. All three arrays empty = books match. `bank`: in the bank, missing on your side;
`supplier`: on your side, missing in the bank; `error`: amount mismatch.

Common receipt fields: `id`, `ext_id`, `state`, `create_date`, `pay_date`, `error`, `type`,
`description`, `amount`, `currency`, `commission`, plus `init_amount` (original amount for
partial refunds, from the models page).
