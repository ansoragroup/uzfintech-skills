# Payme Subscribe API (cards and receipts you call)

Hand-written notes. Transport, auth, errors and testing:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://developer.help.paycom.uz/protokol-subscribe-api/ and
  https://developer.help.paycom.uz/metody-subscribe-api/ (Russian pages)
- Fetched: 2026-11-03
- Direction: **you call Payme.** JSON-RPC 2.0 `POST` to
  `https://checkout.paycom.uz/api` (test: `https://checkout.test.paycom.uz/api`).

## Auth

| Caller | Header | Methods |
|---|---|---|
| Front end (browser, app) | `X-Auth: <CASHBOX_ID>` | `cards.create`, `cards.get_verify_code`, `cards.verify` |
| Back end only | `X-Auth: <CASHBOX_ID>:<CASHBOX_KEY>` | `cards.check`, `cards.remove`, every `receipts.*` |

The cashbox key never leaves your server. The methods are independent: any one can be used
without the others.

## Flow

```
card binding (front end)              payment (back end)
cards.create ──> token (verify:false)  receipts.create {amount, account, detail?} ──> receipt._id (state 0)
cards.get_verify_code ──> SMS sent     receipts.pay {id, token} ──> state 4 (paid)
cards.verify {code} ──> verify:true    receipts.check / receipts.get ──> state
store token on your back end           receipts.cancel ──> state 21 (queued) ──> 50 (cancelled)

invoice by SMS: receipts.create ──> receipts.send {id, phone}
hold:           receipts.create {hold:true} ──> receipts.pay {hold:true} ──> state 5
                ──> receipts.confirm_hold (state 4)  or  receipts.cancel
```

Receipt states `1` and `3` mean "creating / closing the transaction in the merchant
billing". When the cashbox also has a Merchant API Endpoint URL, paying a receipt runs the
Merchant API calls against your server (derived from the state table and the protocol
interaction page; test each protocol separately).

## Methods

| Method | Params (`*` required) | Result |
|---|---|---|
| `cards.create` | `card*{number*, expire*}` (`MMYY`), `account`, `save`, `customer` | `card{number, expire, token, recurrent, verify}` |
| `cards.get_verify_code` | `token*` | `sent`, `phone` (masked), `wait` (ms) |
| `cards.verify` | `token*`, `code*` | `card{...}` with `verify: true` |
| `cards.check` | `token*` | `card{...}` |
| `cards.remove` | `token*` | `success` |
| `receipts.create` | `amount*`, `account*`, `description`, `detail`, `hold` | `receipt` |
| `receipts.pay` | `id*`, `token*`, `payer{id, phone, email, name, ip}`, `hold` | `receipt` |
| `receipts.send` | `id*`, `phone*` | `success` |
| `receipts.cancel` | `id*` | `receipt` (state `21`) |
| `receipts.check` | `id*` | `state` |
| `receipts.get` | `id*` | `receipt` |
| `receipts.get_all` | `count*` (max 50), `from*`, `to*`, `offset*` | **bare array** of receipts |
| `receipts.set_fiscal_data` | `id*`, `fiscal_data*{receipt_id*, qr_code_url*, status_code, message, terminal_id, date, fiscal_sign}` | `success` |
| `receipts.confirm_hold` | `id*` | `receipt` (state `4`) |

- `save: true` gives a reusable token (`recurrent: true`). `save: false` gives a one-time
  token that Payme deletes after payment.
- `receipts.pay` `payer` is optional anti-fraud data.
- `receipts.set_fiscal_data` details: [`../fiscalization/`](../fiscalization/README.md).

## Receipt states

| State | Meaning | Final? |
|---|---|---|
| `0` | created, waiting for payment | no |
| `1` | first checks; creating the transaction in the merchant billing | no |
| `2` | debiting the card | no |
| `3` | closing the transaction in the merchant billing | no |
| `4` | **paid** | yes (can still be cancelled) |
| `5` | held (funds blocked) | no |
| `6` | hold command received, moving to `5`; contact Payme if it sticks | no |
| `20` | paused for manual handling | no |
| `21` | queued for cancel | no |
| `30` | queued for closing in the merchant billing | no |
| `50` | cancelled | yes |

## Receipt object

`_id` (24-char id), `create_time`, `pay_time`, `cancel_time` (ms, `0` when not happened),
`state`, `type`, `external`, `operation`, `category`, `error`, `description`, `detail`,
`amount` (tiyin), `currency` (`860`), `commission`, `account[{name, title, value, main}]`,
`card{number, expire}` or `null`, `merchant{_id, name, organization, address, business_id,
epos{merchantId, terminalId}, date, logo, type, terms}`, `meta{source, owner}` or `null`,
`processing_id`. The hold example also returns `sensitive_data: []`.

## Hold

- Set `hold: true` in **both** `receipts.create` and `receipts.pay`. The receipt moves to
  state `5`.
- Capture: `receipts.confirm_hold {id}` captures the whole held amount (state `4`). There
  is no partial-capture parameter.
- Release: `receipts.cancel {id}`.
- Uzcard releases a hold automatically after 30 days. Humo allows confirm or cancel within
  30 days; after that only confirm.
- Payme staff must enable holds on the cashbox, and holds can be tested only in production.

## Card form and security rules

- Show "Powered by Payme" in the app; Payme may disconnect the service if the API is misused.
- The card form: inputs have **no `name` attribute**, and the `<form>` has **no `action`**.
  The form shows the Payme logo, a link to the Payme offer, and a note that card data is
  not passed to the merchant and stays on the Payme server.
- Never store the raw card number or expiry. Store only the token and the masked `number`.
- Vendor recommendation: ask the user to set a payment PIN when saving a token, ask for it
  before each token payment, and delete the token after 3 wrong PINs.

## Gotchas

- Responses carry `"jsonrpc": "2.0"`; some vendor examples return `"id": null` or omit `id`.
  Match responses by your own request bookkeeping, not only by `id`.
- `receipts.get_all` returns a bare array as `result`, not `{receipts: [...]}`.
- Subscribe API error codes are not documented on the doc site. Branch on `error.code`
  and log `error.message`; never assume the Merchant API code table applies.
- The `cards.check` vendor example sends the front-end header (`X-Auth: <id>`), but the
  method list puts `cards.check` on the back end. Send `id:key` from your server.
- The `receipts.create` example response shows `detail.discount{title, price}` at receipt
  level; the request table does not document it.
- `expire` is `MMYY` in `cards.create`; responses format it differently (`MM/YY` in `card`,
  4 digits in `receipt.card`). Display it as returned.
- In receipts, `account[].title` and `merchant.type` may be a plain string or a localized
  object (`{ru, uz, en}`), and `account[].value` may be a number. Parse both shapes.
- `hold` is missing from the `receipts.create` and `receipts.pay` parameter tables; only the
  hold page documents it.

## Examples

[`examples/`](examples/): `cards-create`, `cards-get-verify-code`, `cards-verify`,
`receipts-create`, `receipts-pay`, `receipts-check` (request and response), plus
`receipts-get-all`, `receipts-set-fiscal-data` and `receipts-confirm-hold` requests.
