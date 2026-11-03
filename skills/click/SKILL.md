---
name: click
description: Exact API contracts for Click (CLICK Uzbekistan, click.uz) payment products - SHOP API Prepare/Complete webhooks with the sign_string MD5 signature, Advanced Shop and Split Shop (getinfo/prepare/confirm/check/compare), Merchant API at api.click.uz/v2/merchant (invoice/create, payment/status, status_by_mti, payment/reversal), card tokens (card_token/request, verify, payment), fiscalization (payment/ofd_data submit_items / submit_qrcode), CLICK Pass QR payments, the my.click.uz payment link and button, the pay-by-card checkout.js widget, mobile deeplinks and Telegram Payments via CLICK Terminal. Use when building, reviewing, debugging or testing any Click / my.click.uz / CLICK SuperApp integration - signatures and the Auth header, request/response fields, soum vs tiyin units, error codes, idempotency, reversal rules and the Postman test scenarios - or when validating an implementation against the contract.
---

# Click integrations

A router. Answer contract questions from the files referenced below, not from memory.
Each product folder has a `README.md` with hand-written notes, `schemas/` holding trimmed JSON
Schemas that carry their source URL and fetched date, and `examples/` holding anonymized
bodies. Examples show **bodies only**; headers and auth are in the README. Start with
[references/common/](references/common/README.md) for credentials, both auth schemes, units
and error handling.

## Products

| Product | Who calls whom | Auth | Reference |
|---|---|---|---|
| SHOP API | **Click calls you** (Prepare `action=0`, Complete `action=1`), form-urlencoded | `sign_string` MD5 with `SECRET_KEY` | [references/shop-api/](references/shop-api/README.md) |
| Advanced Shop / Split Shop | **Click calls you** (getinfo, prepare, confirm, check, compare), JSON | `sign_string` MD5 over `params` | [references/advanced-shop/](references/advanced-shop/README.md) |
| Merchant API | you call Click: invoices, payment status, reversal | `Auth: merchant_user_id:sha1(ts+secret):ts` | [references/merchant-api/](references/merchant-api/README.md) |
| Card tokens | you call Click: save a card, charge it | same `Auth` header | [references/card-tokens/](references/card-tokens/README.md) |
| Fiscalization | you call Click: OFD receipt data for a payment | same `Auth` header | [references/fiscalization/](references/fiscalization/README.md) |
| CLICK Pass | POS calls Click (payer shows a QR in the CLICK app) | same `Auth` header | [references/click-pass/](references/click-pass/README.md) |
| Payment link / button / widget / deeplink | payer is sent to `my.click.uz`; the result arrives via the SHOP API | none (public parameters) | [references/payment-button/](references/payment-button/README.md) |
| Telegram Payments | your bot calls the Telegram Bot API; Click is the provider | Telegram `provider_token` | [references/telegram/](references/telegram/README.md) |
| Sandbox and test data | playground and Postman generator (15 scenarios) call your server; Telegram test mode; vendor sample values | your own service credentials | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | deadlines, cancel / reverse / refund, retries, OTP and hold lifetimes, fiscal receipts | n/a | [references/lifecycle/](references/lifecycle/README.md) |

## Which product?

| The user wants to... | Product |
|---|---|
| be payable from the CLICK app, my.click.uz or USSD by order / account number | SHOP API |
| collect several payer fields, show details before paying, or let Click reconcile | Advanced Shop |
| split one payment between several counterparties | Split Shop |
| send a bill to a payer's phone (the payer confirms in CLICK) | Merchant API `invoice/create` + SHOP API |
| check, find or refund a payment | Merchant API (`payment/status`, `status_by_mti`, `payment/reversal`) |
| save a card and charge it later (subscriptions, one-click) | Card tokens |
| register a fiscal receipt for a Click payment | Fiscalization |
| charge in a shop by scanning the payer's CLICK app QR | CLICK Pass |
| put a "Pay with CLICK" link or button on a site, or open CLICK from an app | Payment link / button / deeplink (+ SHOP API) |
| take card payments in a pop-up on the site | Pay-by-card widget (+ SHOP API) |
| sell inside a Telegram bot | Telegram Payments |

## Cross-product rules

- Amounts are **soums** (a number that may have decimals) everywhere except fiscalization,
  which uses integer **tiyin**. The payment link wants `N.NN`. Store integer tiyin and
  convert at the edge.
- Two auth schemes: inbound handlers verify `sign_string` (MD5 over raw values with
  `SECRET_KEY`); outbound calls send `Auth: merchant_user_id:sha1(timestamp + secret_key):timestamp`
  with the timestamp in **seconds**.
- Inbound handlers answer `error` and `error_note` as JSON with HTTP 200. Merchant API
  responses carry `error_code` instead and use HTTP codes for transport and auth failures.
- `payment_status`: `< 0` error, `0` created, `1` processing, `2` success. Only `2` is paid.
- Only SHOP API Complete (or a status call) proves a payment. Redirects, widget callbacks and
  `invoice/create` do not.
- Refunds go through `payment/reversal`: full amount, current month only (or day 1 of the
  next month), online cards only.
- Click repeats inbound requests. Make handlers idempotent on `click_trans_id`
  (SHOP API) or `click_paydoc_id` (Advanced / Split).

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the deadline or
consequence, and the fix. Every window, refund path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `click.complete-after-debit`: after the debit Complete may answer only success, `-4` or
  `-9`. If you cannot deliver, answer success, then call `payment/reversal`.
- `click.negative-error-cancels`: Complete with `error < 0` → cancel, answer `-9`, even after
  an earlier success. Never mark the order paid on it.
- `click.reversal-month-window`: `payment/reversal` is full only, for the current reporting
  month; a previous month's payment only on day 1 of the next. Plan another refund path.
- `click.idempotent-retries`: Click repeats Prepare and Complete after timeouts and errors;
  key on `click_trans_id` (Advanced Shop: book on `click_paydoc_id`).
- `click.one-fiscal-receipt`: `submit_items` or `submit_qrcode`, never both, only after the
  payment; read `payment/ofd_data` before any second submit.
- `click.no-refund-receipt-api`: no refund-receipt method is documented; ask Click how a
  reversal is fiscalized before going live.
- `click.status-1-not-final`: card token and CLICK Pass `payment_status` `1` is not final;
  poll `payment/status` before charging again.
- `click.pass-confirm-30s`: CLICK Pass confirmation mode cancels the payment after 30 s;
  `otp_data` is single-use.

## Top gotchas

1. SHOP API: hash the **raw** `amount` string. Re-formatting it (`1000.0` vs `1000.00`)
   breaks `sign_string`. Complete adds `merchant_prepare_id` between `merchant_trans_id` and
   `amount`.
2. SHOP API: a Complete with `error < 0` always cancels and returns `-9`, even after an
   earlier success. After Prepare succeeded and money was taken, Complete must not answer
   any other error; refund with reversal instead.
3. SHOP API: `merchant_prepare_id` / `merchant_confirm_id` are ints. The Postman page says
   `error_code`; the JSON key you return is `error`.
4. Advanced Shop numbers actions differently (0 getinfo, 1 prepare, 2 confirm), and its
   signature concatenates `params` values in body order. Use an order-preserving parser.
5. Merchant API: a 200 can carry a non-zero `error_code`. There is no catalogue of those
   codes. A millisecond timestamp in `Auth` gives 401.
6. Card tokens: `expire_date` is `MMYY`; the token is usable only after `verify`; the vendor
   `request` example omits `Auth`, but send it.
7. Fiscalization: item keys are PascalCase, money is tiyin, `Price` is the line total, and
   `get-ofd-data` answers in camelCase.
8. CLICK Pass: with confirmation mode on, confirm within **30 seconds** or Click cancels.
   `otp_data` is single-use.
9. Payment link: `card_type` is `uzcard` or `humo`, not the vendor sample's `uzcard/humo`.
10. Telegram: the Click page misspells `answerPreCheckoutQuery` and `successful_payment`.

## Validate an implementation

Work through the matching checklist and mark each item pass, fail or n.a. with a file:line
citation:

- [checklists/common.md](checklists/common.md) (every product)
- [checklists/shop-api.md](checklists/shop-api.md)
- [checklists/advanced-shop.md](checklists/advanced-shop.md) (Advanced and Split Shop)
- [checklists/merchant-api.md](checklists/merchant-api.md) (invoices, status, reversal, card tokens)
- [checklists/fiscalization.md](checklists/fiscalization.md)
- [checklists/click-pass.md](checklists/click-pass.md)
- [checklists/payment-button.md](checklists/payment-button.md) (link, button, widget, deeplink)
- [checklists/telegram.md](checklists/telegram.md)

Then compare the real request and response shapes with `schemas/` and `examples/`. For the
SHOP API, also run the 15 Postman generator scenarios. Their exact inputs and run order are
in [references/sandbox/](references/sandbox/README.md).

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only. Secrets come from environment variables, never from
arguments, and print as `<SECRET>`.

```sh
python3 scripts/sign.py --list     # click.prepare, click.complete, click.advanced, click.auth
python3 scripts/sign.py click.prepare body.txt     # checks sign_string; CLICK_SECRET_KEY
python3 scripts/validate.py --list [text]
python3 scripts/validate.py shop-api/prepare body.txt [--part result]
```

`sign.py` prints the exact string it signed and, given a received value, `MATCH` or
`MISMATCH`. `validate.py` prints `OK` or `INVALID` with JSON paths; form values
are coerced to the numbers the schema names. Both exit 1 on a
mismatch. Run them before you call a signature, header or payload correct, and quote their
output.

## Answering rules

- Reply in the user's language, but never translate method names, fields, headers, codes
  or enum values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation. Code uses
  the sandbox values and runs as written.
- With several providers in one task, work each one from its own SKILL.md, then compare.
  Never carry a rule (units, auth, retries) over from another provider.
- Lifecycle: before you finish an answer that creates, confirms, cancels, refunds, retries
  or fiscalizes a payment, check "Warn without being asked" and
  [references/lifecycle/](references/lifecycle/README.md). State the deadline, whether the
  step can be undone and what happens to the fiscal receipt, with the warning ID, even if
  nobody asked. For an item under "Not documented", say so and send the user to the
  provider.
- Quote field names, types and codes exactly as they appear in the reference files. If a
  fact is not there, say the contract does not specify it and point to the vendor page
  listed as `Source:`.
- Where a README flags a vendor inconsistency, give both readings and say which one is safer.
- For tests, mocks and examples, use the sandbox data and vendor sample values in
  [references/sandbox/](references/sandbox/README.md). Click publishes no test cards, OTPs
  or sandbox host, so never present a sample card or SMS code as working test data.
- Never use real merchant credentials (a real `merchant_id`, `service_id`,
  `merchant_user_id`, `secret_key`, cabinet login or live bot token), and never invent
  credentials. Use placeholders such as `<SERVICE_ID>` and `<SECRET_KEY>`.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them; say they come from the merchant's agreement.
  Fee fields in API answers (`commission`, `fee`, `commission_amount`) are fine to explain.
- Upstream docs: https://docs.click.uz/en/ . Freshness: each README carries `Fetched:`.
  Run `scripts/sync --check` to compare against upstream.
