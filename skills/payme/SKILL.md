---
name: payme
description: Exact API contracts for Payme (Paycom, Payme Business, Uzbekistan) payments - Merchant API JSON-RPC methods you implement (CheckPerformTransaction, CreateTransaction, PerformTransaction, CancelTransaction, CheckTransaction, GetStatement, SetFiscalData), transaction states and cancel reasons, the 12-hour timeout, Subscribe API card tokens and receipts (cards.*, receipts.*, holds), hosted checkout by GET link or POST form with button / QR, and fiscal receipt items (IKPU code, package_code, vat_percent). Use when building, reviewing, debugging or testing a checkout.paycom.uz / test.paycom.uz integration - Basic auth, X-Auth, JSON-RPC error codes -31001..-31099 and -32xxx, tiyin amounts, millisecond timestamps, idempotent retries, sandbox scenarios - or when validating an implementation against the contract.
---

# Payme (Paycom) integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json`: trimmed JSON Schemas with `params` and `result`, carrying the
  source URL and fetched date;
- `examples/`: anonymized bodies.

Examples are bodies only. The transport, Basic auth / `X-Auth` and the JSON-RPC error
envelope are in [references/common/README.md](references/common/README.md); read it first.
Test hosts, cards and scenarios are in [references/sandbox/](references/sandbox/README.md).

## Products

| Product | Methods | Reference |
|---|---|---|
| Common (all products) | two protocols, transport, auth, JSON-RPC errors `-32xxx`, keys, sandbox scenarios, SDK / Telegram / plugins | [references/common/](references/common/README.md) |
| Merchant API (Payme calls you) | `CheckPerformTransaction`, `CreateTransaction`, `PerformTransaction`, `CancelTransaction`, `CheckTransaction`, `GetStatement`, `SetFiscalData` (`ChangePassword` undocumented) | [references/merchant/](references/merchant/README.md) |
| Subscribe API (you call Payme) | `cards.create`, `cards.get_verify_code`, `cards.verify`, `cards.check`, `cards.remove`, `receipts.create`, `receipts.pay`, `receipts.send`, `receipts.cancel`, `receipts.check`, `receipts.get`, `receipts.get_all`, `receipts.set_fiscal_data`, `receipts.confirm_hold` | [references/subscribe/](references/subscribe/README.md) |
| Checkout | GET link, POST form, `Paycom.Button`, `Paycom.QR`, checkout errors `-316xx` | [references/checkout/](references/checkout/README.md) |
| Fiscalization | `detail` / `items` (`code` IKPU, `package_code`, `vat_percent`), `SetFiscalData`, `receipts.set_fiscal_data` | [references/fiscalization/](references/fiscalization/README.md) |
| Sandbox and test data | test hosts, test cards and SMS code `666666`, test cabinet login, `TEST_KEY`, Merchant API sandbox scenarios, vendor sample values | [references/sandbox/](references/sandbox/README.md) |

Merchant API: Payme sends JSON-RPC 2.0 `POST` to your Endpoint URL with
`Authorization: Basic base64(<login>:<CASHBOX_KEY>)`. Subscribe API: you send JSON-RPC 2.0
`POST` to `https://checkout.paycom.uz/api` with `X-Auth`.

## Which product?

| The user wants to... | Use |
|---|---|
| send the buyer to the Payme page and get paid into their billing | Checkout (GET or POST) + Merchant API methods |
| reconcile with Payme | Merchant API `GetStatement` (mandatory) |
| pass fiscal items (IKPU) for the tax receipt | `detail` in `CheckPerformTransaction`, `receipts.create` or the POST form |
| receive the fiscal receipt Payme registered | Merchant API `SetFiscalData` |
| pay from their own card form or app, or save a card | Subscribe `cards.create` -> `cards.get_verify_code` -> `cards.verify`, then `receipts.create` + `receipts.pay` |
| recurring or one-click payments | Subscribe with `save: true`, then `receipts.create` + `receipts.pay` per charge |
| send an invoice by SMS | `receipts.create` -> `receipts.send` |
| block funds now and capture later | `hold: true` in `receipts.create` and `receipts.pay`, then `receipts.confirm_hold` or `receipts.cancel` |
| refund | Merchant API: implement `CancelTransaction` (refunds from the cabinet need it); Subscribe: `receipts.cancel` |
| split a payment between cashboxes | Merchant API `receivers` in `CreateTransaction` |
| test against the sandbox (test cards, SMS code, scenarios, sample payloads) | [sandbox](references/sandbox/README.md) |

## Rules that apply everywhere

- Amounts are integer **tiyin** (1 UZS = 100). Times are Unix epoch **milliseconds**.
- Merchant API: answer **HTTP 200** for every outcome; errors go in `error` with a localized
  `message {ru, uz, en}`. Echo the request `id`.
- The Payme transaction `id` (24 chars) is the idempotency key. Repeats of
  `CreateTransaction`, `PerformTransaction` and `CancelTransaction` must return the stored
  answer unchanged.
- Fulfil only on `PerformTransaction` (state `2`) or a Subscribe receipt in state `4`.
  The checkout return URL is not proof of payment.
- The cashbox key stays on the server. Front ends use only `X-Auth: <CASHBOX_ID>` for the
  three card-binding methods.
- Never store raw card numbers or expiry; keep the token and the masked number.

## Top gotchas

1. The doc site swaps two pages: `/checkperformtransaction/` shows CheckTransaction and
   `/checktransaction/` shows CheckPerformTransaction.
2. State `1` older than **43 200 000 ms (12 h)** must be cancelled with reason `4`; a later
   `CreateTransaction` or `PerformTransaction` on it answers `-31008`.
3. `-31050..-31099` need a localized `message` and `data` = the `account` field name, or
   the sandbox fails.
4. A one-time account with a transaction already in state `1` must reject a new
   `CreateTransaction` with `-31008`.
5. `GetStatement` filters on the Payme `time`, inclusive, ascending, and lists only
   successful creates.
6. Unset times are `0`; `reason` is `null` until cancelled; `transaction` is a string.
7. Subscribe error codes are undocumented, `receipts.get_all` returns a bare array, and
   some examples have `"id": null`.
8. `detail.items[].price` is the unit price and `discount` the line total; `code` is the
   17-digit IKPU and `package_code` is required. In the POST form `detail` is base64 JSON.
9. `SetFiscalData` errors use a plain-string `message`; store a `CANCEL` call as a separate
   fiscal receipt.
10. Holds need `hold: true` in **both** create and pay, Payme staff must enable them, and
    they are testable only in production.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then the product checklist:

- [checklists/merchant.md](checklists/merchant.md)
- [checklists/subscribe.md](checklists/subscribe.md)
- [checklists/checkout.md](checklists/checkout.md)
- [checklists/fiscalization.md](checklists/fiscalization.md)

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Answering rules

- Quote method names, fields, types and codes exactly as they appear in the references. If
  a fact is not there, say the docs do not specify it and link the `Source:` page.
- For tests and examples use the sandbox data in
  [references/sandbox/](references/sandbox/README.md) (test cards, SMS code, test hosts,
  vendor sample values). Never use real merchant credentials, keys, tokens or real people's
  data; use placeholders such as `<CASHBOX_ID>`, `<CASHBOX_KEY>` and `<CARD_TOKEN>` for those.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
