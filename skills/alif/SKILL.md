---
name: alif
description: Exact API contracts for Alif (alifpay, Uzbekistan) payments - Checkout invoices and hosted page, direct payments (card + OTP, card token, hold, alif mobi QR), Alif Nasiya instalments (buy now, pay later) through Checkout, refunds and partial instalment refunds, payouts / split payments, fiscal receipts, card tokenization (Uzcard / Humo), holds, card transaction history and monthly card summary, plus a legacy (original-version /purchase, /scoring, /pinfl) to current-API migration map. Use when building, reviewing, debugging or testing an api.alifpay.uz / checkout.alifpay.uz integration - endpoints, Token auth, webhook HMAC Signature verification, request/response schemas, tiyin amounts, error codes 1001-1110, payment statuses - or when validating an implementation against the contract.
---

# Alif (alifpay) integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json`: trimmed JSON Schemas with `params` and `result`, carrying the
  source URL and fetched date;
- `examples/`: anonymized bodies.

Examples are bodies only. The transport, the `Token` header and the error envelope are in
[references/common/README.md](references/common/README.md); read it first.

## Products

| Product | Methods | Reference |
|---|---|---|
| Common (all products) | transport, auth, error codes, webhook `Signature`, changelog | [references/common/](references/common/README.md) |
| Sandbox | `api-dev` / `checkout-dev` hosts, test cards, OTP, PINFL, QR test tokens, `_` methods, vendor samples, test plan | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | deadlines, cancel / reverse / refund, retries, OTP and hold lifetimes, fiscal receipts | [references/lifecycle/](references/lifecycle/README.md) |
| Checkout | `invoice`, `getInvoice`, `refundInvoice`, `sendInvoice`, `addInvoiceReceiptURL`, `chargeInvoiceHold`, `_payInvoiceWithMobi` | [references/checkout/](references/checkout/README.md) |
| Payments | `pay`, `confirmPayment`, `getPayment`, `refundPayment`, `applyPayouts`, `refundPaymentPartial`, `getRefund`, `registerReceipt`, `_completeInstallmentRefund` | [references/payments/](references/payments/README.md) |
| Cards | `getCardToken`, `confirmCardToken`, `matchCardPIN`, `getCardType` | [references/cards/](references/cards/README.md) |
| Hold | `hold`, `dismissHold`, `getHold` | [references/hold/](references/hold/README.md) |
| Monitoring | `history` | [references/monitoring/](references/monitoring/README.md) |
| Summary | `getSummary` | [references/summary/](references/summary/README.md) |
| Legacy (original version) | `purchase`, `confirmChargeOTP`, `getPurchase`, `refundPurchase`, `pinfl`, `scoring`; v1 -> v2 migration map | [references/legacy-v1/](references/legacy-v1/README.md) |

Every method is `POST https://api.alifpay.uz/v2/<method>` (sandbox:
`https://api-dev.alifpay.uz/v2/<method>`) with a JSON body and the header
`Token: <API_TOKEN>`. Branch auth (beta) uses `Store-Token` instead.

## Which product?

| The user wants to... | Use |
|---|---|
| send the buyer to a hosted payment page (card or alif mobi, instalments) | Checkout `invoice` -> redirect -> webhook -> `getInvoice` |
| charge a card number with an SMS OTP from their own UI | Payments `pay` `CARD` -> `confirmPayment` |
| save a card and charge it later without OTP | Cards `getCardToken` / `confirmCardToken`, then `pay` `TOKEN` |
| block funds now and capture later | Hold `hold`, then `pay` `HOLD` or `dismissHold` |
| split a payment to other merchants or release funds on delivery | `payouts` / `skip_payouts` + `applyPayouts` |
| refund | `refundInvoice` / `refundPayment` (full); `refundPaymentPartial` (instalment only) |
| register a fiscal receipt made by their own cash register | `registerReceipt`; for invoices, `addInvoiceReceiptURL` |
| score a card holder | `matchCardPIN`, `history`, `getSummary` |
| maintain or migrate code using `purchase` / `charge` / `ref` / `scoring` / `pinfl` | [legacy-v1](references/legacy-v1/README.md) migration map |
| test against the sandbox (cards, OTP, PINFL, QR tokens, simulated mobi / refund outcomes) | [sandbox](references/sandbox/README.md) |

## Rules that apply everywhere

- Amounts are integer **tiyin**. A payment or invoice must be 50,000..20,000,000,000 tiyin,
  computed as `sum(price x amount - discount)`: `price` is the unit price, `amount` is the
  quantity, and `discount` is the line total.
- Errors come back as **HTTP 200** with `{"error": {"code", "message"}}`. Branch on `code`
  (1001-1110; the table in common gives retry guidance). Non-200 means an auth or network
  failure.
- Payment, hold and refund `id`s are client-generated. Use a UUID, persist it first, and
  read the state back (`getPayment`, `getHold`, `getInvoice`) before any retry. On `1108`,
  retry only with a new `id`.
- Webhooks are verified with `Signature` = base64(HMAC-SHA256(secret, raw body)), compared in
  constant time. Answer HTTP 200 quickly: about an hour of failed delivery **cancels and
  refunds** the payment.
- Only `SUCCEEDED` means paid. `OTP_REQUIRED`, `PENDING`, `PENDING_REVERSAL` and `HELD` are
  not final, and `UNKNOWN_ERROR` must be read back.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the deadline or
consequence, and the fix. Every window, refund path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `alif.webhook-1h-auto-refund`: Alif retries a webhook for about an hour; with no HTTP 200
  the payment is cancelled and refunded. Verify, answer 200 at once, process later.
- `alif.persist-id-first`: you generate `id` for `pay`, `hold`, `refundPaymentPartial`; store
  it first. After a timeout or `1003` read back before any retry; `1108` needs a new `id`.
- `alif.error-is-http-200`: errors arrive as HTTP 200 with `{error:{code, message}}`. Only
  `SUCCEEDED` is paid; `UNKNOWN_ERROR` needs a read back.
- `alif.hold-expiry-10-30-days`: capture a `hold` before the scheme releases it (10 days Humo,
  30 days Uzcard). `dismissed: true` does not say why; track it yourself.
- `alif.refund-full-only`: `refundPayment` and `refundInvoice` return the whole amount.
  Partial refunds exist only for instalments (`refundPaymentPartial`, reviewed).
- `alif.refund-receipt-needs-sale-receipt`: Alif registers a refund receipt only if the sale
  had one (`receipt`, or invoice `receipt: true`).
- `alif.amount-equals-items`: the total must equal `sum(price x amount - discount)` in tiyin
  (`price` per unit, `discount` per line), else `1005`.
- `alif.otp-restart`: on `1100` ask for the code again; on `1101` (expired) or `1106` (no
  attempts left) start a new `pay` with a new `id`.

## Top gotchas

1. The `pay` request puts card fields flat in `method` (`{type, pan, exp}`). The response nests
   them under `method.payload`, with masked values.
2. The payment webhook doc describes a `payload` wrapper, but the changelog says the body is
   the bare payment struct. Accept both with `body.get("payload", body)`. `/pay` has no
   `webhook_url` parameter, so confirm the destination at onboarding.
3. `refundInvoice` returns receipt links as top-level `receipts`. `getInvoice` puts them in
   `payment.receipt.results`.
4. `TOKEN` with `force: true` cannot be combined with `payouts`. A `skip_payouts` payment can
   only be fully refunded until `applyPayouts` runs.
5. Holds auto-release after 30 days (Uzcard) or 10 days (Humo). `dismissed: true` does not say
   whether the hold was charged or released.
6. `getCardToken` needs `phone` for Humo cards. `matchCardPIN` can return `false` on Humo
   simply because the scheme has no PINFL on file.
7. `history`: Humo returns only the last 3 months, and the range is at most 1 year.
   `getSummary` takes `YYYY-MM` months, and `to` must be before the current month.
8. The current API replaced `/purchase`, `ref` and `charge` (2024-03-19). Do not build on
   the old names. To maintain or migrate old code, use [legacy-v1](references/legacy-v1/README.md).
9. Vendor docs have known flaws: `registerReceipt` swaps the latitude and longitude
   descriptions, and the `_completeInstallmentRefund` params disagree with its example.
   Sample ids are truncated, so do not validate ids as full UUIDs.
10. The sandbox is a **separate host** (`api-dev.alifpay.uz`, `checkout-dev.alifpay.uz`) with
    its own token. The docs say the two tokens are separate; keep host and token paired in config.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then the product checklist:

- [checklists/checkout.md](checklists/checkout.md)
- [checklists/payments.md](checklists/payments.md)
- [checklists/cards.md](checklists/cards.md), which covers cards, hold, monitoring and summary

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only. Secrets come from environment variables, never from
arguments, and print as `<SECRET>`.

```sh
python3 scripts/sign.py --list     # alif.webhook
python3 scripts/sign.py alif.webhook body.json --expect '<Signature>'   # ALIF_WEBHOOK_SECRET
python3 scripts/validate.py --list [text]
python3 scripts/validate.py confirmPayment body.json [--part result]
```

`sign.py` prints the exact string it signed and, given a received value, `MATCH` or
`MISMATCH`. `validate.py` prints `OK` or `INVALID` with JSON paths; a `{success, data}`
envelope is unwrapped. Both exit 1 on a
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
- Quote field names, types and codes exactly as they appear in the references. If a fact is
  not there, say the docs do not specify it and link the `Source:` page.
- For tests, fixtures and sandbox examples, use the exact vendor test data in
  [references/sandbox/](references/sandbox/README.md): cards, OTP `111111`, PINFL, QR test
  tokens, the `api-dev` host. Keep it out of production code paths.
- For credentials and merchant data, use placeholders (`<API_TOKEN>`, `<WEBHOOK_SECRET>`,
  `https://merchant.example.com`). Never invent or copy a real token.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them; say they come from the merchant's agreement.
  Fee fields in API answers (`commission`, `fee`, `commission_amount`) are fine to explain.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
