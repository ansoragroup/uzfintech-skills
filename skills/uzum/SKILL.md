---
name: uzum
description: Exact API contracts for Uzum Bank (Uzbekistan) payment products - Merchant API webhooks (check/create/confirm/reverse/status), Uzum Checkout (acquiring, card binding), Fiscalization (OFD receipts), FastPay and Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Uzum Nasiya (BNPL) and PaymentHub (JSON-RPC BaaS). Use when building, reviewing, debugging or testing any Uzum / Apelsin / uzumcheckout / uzumnasiya integration - endpoints, auth headers and signatures, request/response schemas, units, error codes, state machines, idempotency, polling and reconciliation - or when validating an implementation against the contract.
---

# Uzum Bank integrations

A router. Answer contract questions from the files referenced below, not from memory.
Each product folder has a `README.md` with hand-written notes, `schemas/` holding trimmed JSON
Schemas that carry their source URL and fetched date, and `examples/` holding anonymized
bodies. Most products also have a generated `endpoints.md`. Examples show **bodies only**;
headers and auth are in the product README.

## Products

| Product | Who calls whom | Auth | Reference |
|---|---|---|---|
| Merchant API | **Uzum calls you** (`/check`, `/create`, `/confirm`, `/reverse`, `/status`) | Basic (your credentials) | [references/merchant/](references/merchant/README.md) |
| Checkout | you call Uzum; Uzum calls back (unsigned) | `X-Terminal-Id` + `X-API-Key` (+ `X-Operation-Id`) | [references/checkout/](references/checkout/README.md) |
| Fiscalization | you call the OFD gateway | `X-API-Key` | [references/fiscalization/](references/fiscalization/README.md) |
| FastPay | POS calls Uzum (payer shows QR) | `user_id:sha1(ts+secret):ts` | [references/fastpay/](references/fastpay/README.md) |
| Dynamic QR | POS calls Uzum (merchant shows QR) | same as FastPay | [references/dynamicqr/](references/dynamicqr/README.md) |
| CrossBorder | you call Uzum (IPSec in prod) | Basic | [references/crossborder/](references/crossborder/README.md) |
| Remit Core | you call Uzum; Uzum calls back | `X-Api-Key` | [references/remitcore/](references/remitcore/README.md) |
| Ratekeeper | you call Uzum | `X-API-Key` | [references/ratekeeper/](references/ratekeeper/README.md) |
| Nasiya (BNPL) | you call Uzum Nasiya; buyer signs in a WebView | Bearer | [references/nasiya/](references/nasiya/README.md) |
| PaymentHub | you call Uzum (JSON-RPC 2.0) | Basic | [references/paymenthub/](references/paymenthub/README.md), [methods](references/paymenthub/methods.md), [errors](references/paymenthub/errors.md) |
| Sandbox | test hosts, test cards, 3-DS code, test phones and PANs, scenarios with expected codes, vendor samples | test credentials from your Uzum manager | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | deadlines, cancel / reverse / refund, retries, OTP and hold lifetimes, fiscal receipts | n/a | [references/lifecycle/](references/lifecycle/README.md) |

## Which product?

| The user wants to... | Product |
|---|---|
| be payable from the Uzum Bank app by account / order number (Uzum pushes payments) | Merchant API |
| take card payments on a website or app (hosted form, iframe, saved cards, two-step) | Checkout |
| register a fiscal receipt for a payment (OFD / soliq) | Fiscalization (or Checkout auto-fiscalization) |
| charge in a shop by scanning the payer's Uzum app QR | FastPay |
| show a QR on a terminal or screen for the payer to scan | Dynamic QR |
| send or receive money across borders by card / phone | Remit Core (newer) or CrossBorder |
| get a conversion rate / limits for a transfer | Ratekeeper |
| sell on installments (buy now, pay later) | Nasiya |
| pay utilities by card token, pay out to cards, or transfer to accounts by requisites | PaymentHub |
| test any of the above (test hosts, cards, scenarios, samples) | [sandbox](references/sandbox/README.md) |

## Cross-product rules

- Amounts are integer **tiyin** (1 UZS = 100) everywhere except where a README says otherwise
  (Nasiya does not state its unit).
- Times are Unix **milliseconds** in Merchant API, FastPay and PaymentHub. Fiscalization uses
  a Tashkent local `date_time` string.
- The HTTP status rarely carries the result. Checkout, FastPay, Ratekeeper and PaymentHub
  return business errors inside a 200 body. Merchant API webhooks must answer **400** with
  a string `errorCode`.
- Idempotency keys: Merchant `transId`, Checkout `X-Operation-Id`, Fiscalization
  `operation_id`, FastPay `order_id` / `transaction_id`, CrossBorder `externalTransferId` /
  `externalPaymentId`, Remit Core `externalTransferId`, PaymentHub `ext_id`. Persist them
  before the call.
- None of the callbacks are signed. Confirm every callback by reading the state back
  (`getOrderStatus`, `get_status`, `receipt.check.id`) before fulfilling.
- Production hosts for Checkout, PaymentHub, Remit Core and Ratekeeper are issued at
  onboarding. Keep every host in config.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the deadline or
consequence, and the fix. Every window, refund path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `uzum.merchant-lost-confirm`: after a 5xx or timeout on `/confirm`, Uzum polls `/status` up
  to 10 times. Commit before you answer, so `/status` says `CONFIRMED`; a repeated `/confirm`
  gets `10016`. `CREATED` expires after 30 minutes.
- `uzum.fiscal-receipt-24h`: a Fiscalization `date_time` must be within 24 h after the paid
  confirm and not in the future (422). Send it at payment time, not from a nightly batch.
- `uzum.fiscal-refund-needs-sale`: `/v2/refund_receipt` needs the sale `payment_id` and an
  already fiscalized sale receipt; each refund takes a new `operation_id`.
- `uzum.checkout-operation-id`: one `X-Operation-Id` per Checkout money call, stored first. On
  `3028` read `getOperationState`; a fresh id can refund twice.
- `uzum.checkout-stale-authorized`: TWO_STEP `AUTHORIZED` needs `complete` or `reverse`;
  ONE_STEP cannot be reversed (`3036`), only refunded. Hold expiry is not published.
- `uzum.merchant-no-refund-api`: Merchant API has no outbound refund. Uzum calls `/reverse`
  for the whole transaction; repeats get `10018`.
- `uzum.paymenthub-never-recreate`: a PaymentHub timeout, `30`, `57` or `-31615` means poll
  `receipt.check.id`. Never recreate or re-confirm; only `state 4` is paid.
- `uzum.crossborder-no-refund`: a credited CrossBorder transfer cannot be returned;
  `cancel_debit` only undoes a FROM_UZ debit whose onward credit failed.

## Top gotchas

1. Merchant API: `errorCode` is a **string**, `data` values are `{"value": ...}` objects, and
   `/status` must reflect a confirm whose HTTP response was lost (Uzum polls up to 10 times).
   Expire `CREATED` after 30 minutes.
2. Checkout: callbacks are unsigned, so call `getOrderStatus`. `orderNumber` reuse returns `3027`.
   ONE_STEP payments are refunded, not reversed (`3036`). With auto-fiscalization the cart
   total must equal `amount` (`3059`).
3. Fiscalization: HTTP **202 is pending**, not failure. Amounts go **before** discount, and
   the receipt must be sent within 24 h. A refund reuses the sale `payment_id`.
4. FastPay: SHA-1 hex of `timestamp + secret` with the timestamp in ms. Requests older than
   50 s fail with 403. `DUPLICATED` means "look up the earlier sale"; `operation.is.inProcess`
   means poll `status`.
5. CrossBorder: omit optional fields (never `""` or `null`). Confirm within 20 minutes.
   `PENDING` has no callback.
6. Remit Core: `2000` is async success-in-progress; never re-register. Use the field name
   `paymentInstrumentType`, and send countries as alpha-3.
7. Nasiya: `phone` is an **int** in `check-status` and a **string** in the SMS endpoints.
   `contract_id` is under `data.paymart_client`.
8. PaymentHub: wire error codes are **negative** (`-31613`). Result wrapping differs per
   method. Only `state 4` means paid, and `30` / `57` / `-31615` mean poll. Never recreate a
   receipt.

## Validate an implementation

Work through the matching checklist and mark each item pass, fail or n.a. with a file:line
citation:

- [checklists/merchant.md](checklists/merchant.md)
- [checklists/checkout.md](checklists/checkout.md)
- [checklists/fiscalization.md](checklists/fiscalization.md)
- [checklists/fastpay.md](checklists/fastpay.md) (FastPay and Dynamic QR)
- [checklists/crossborder.md](checklists/crossborder.md) (CrossBorder, Remit Core and Ratekeeper)
- [checklists/nasiya.md](checklists/nasiya.md)
- [checklists/paymenthub.md](checklists/paymenthub.md)

Then compare the real request and response shapes with `schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only. Secrets come from environment variables, never from
arguments, and print as `<SECRET>`.

```sh
python3 scripts/sign.py --list     # uzum.fastpay (FastPay, Dynamic QR), uzum.basic
python3 scripts/sign.py uzum.fastpay -f merchant_service_user_id=<USER> --expect '<Authorization>'  # UZUM_SECRET_KEY
python3 scripts/validate.py --list [text]
python3 scripts/validate.py webhook-confirm body.json [--part response]
```

`sign.py` prints the exact string it signed and, given a received value, `MATCH` or
`MISMATCH`. `validate.py` prints `OK` or `INVALID` with JSON paths. Both exit 1 on a
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
- For tests, fixtures and sandbox examples use the exact vendor test data in
  [references/sandbox/](references/sandbox/README.md) (test cards, 3-DS code, test phones,
  scenario inputs) and keep it out of production code paths.
- For credentials and merchant data use placeholders: `https://merchant.example.com`,
  `<BASIC_USER>`, `<API_KEY>`, `"100001"`. Never invent or copy a real credential, and never
  copy the pre-filled login, password or key from a vendor Postman collection.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them; say they come from the merchant's agreement.
  Fee fields in API answers (`commission`, `fee`, `commission_amount`) are fine to explain.
- Upstream docs: https://developer.uzumbank.uz/ . Freshness: each README carries `Fetched:`.
  Run `scripts/sync --check` to compare against upstream.
