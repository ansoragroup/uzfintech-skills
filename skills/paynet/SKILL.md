---
name: paynet
description: Exact API contracts for Paynet (Uzbekistan) internet acquiring - Humo and Uzcard card payments with an SMS OTP, host to host - authorize, confirm, status and reverse under /api/v1/payment-service/, Basic auth from service_id:secret_key, tiyin amounts, the status/message/data/error envelope, string error codes (OTP_INVALID, INSUFFICIENT_FUNDS, UNKNOWN_TRANSACTION_STATE -10012, ...) and transaction statuses (SUCCESS, CANCELLED, RETURN_PENDING, ...). Use when building, reviewing, debugging or testing a Paynet / pay-docs.paynet.uz acquiring integration, or when validating an implementation against the contract.
---

# Paynet integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

The product folder has:
- `README.md`: hand-written notes;
- `schemas/<operation>.json`: trimmed JSON Schemas with `params` and `result`, carrying the
  source URL and fetched date;
- `examples/`: anonymized bodies.

Examples are bodies only. Read the transport, the Basic header, the envelope and the error
table in [references/common/README.md](references/common/README.md) first.

## Products

| Product | Operations | Reference |
|---|---|---|
| Common | transport, Basic auth, envelope, error codes, transaction statuses, doc gaps | [references/common/](references/common/README.md) |
| Acquiring (Humo / Uzcard) | `authorize`, `confirm`, `status`, `reverse` | [references/acquiring/](references/acquiring/README.md) |
| Sandbox and test data | what exists for testing (no test data is published), vendor sample values, mock scenarios, open questions | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | deadlines, cancel / reverse / refund, retries, OTP and hold lifetimes, fiscal receipts | [references/lifecycle/](references/lifecycle/README.md) |

Every call goes from your server to Paynet, under
`<BASE_URL>/api/v1/payment-service/payment/`, with
`Authorization: Basic base64(service_id:secret_key)`. Paynet issues the base URL privately.

## Which operation?

| The user wants to... | Use |
|---|---|
| charge a Humo or Uzcard card number from their own form | `authorize` (OTP sent) -> `confirm` with the OTP |
| find out whether a payment went through | `status?value=<transactionId or paymentId>` |
| handle a timeout, `-10012` or `retryable: true` | `status`, polled until a final state |
| cancel a payment | `reverse` (at most 1 month after the payment) |
| take Visa / Mastercard, a hosted page, saved cards or webhooks | not in the public docs; ask Paynet |

## Rules that apply everywhere

- Amounts are integer **tiyin**. `expiry` is `YYMM`.
- Success is `status == 0` in the body. Failures carry `error` with a **string** `code`.
  Several constants share one number (`1007`, `1009`), so branch on `error.code`.
- `orderId` must be unique per authorize. Persist `transactionId` before the OTP screen.
- Only `data.status == "SUCCESS"` means paid. `UNKNOWN`, `CREATED`, `PENDING_CONFIRM` and
  `*_PENDING` are not final, so poll `status`.
- The server sees the raw PAN, which puts it in PCI DSS scope. Never log or store the PAN,
  expiry, OTP or `secret_key`.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the deadline or
consequence, and the fix. Every window, refund path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `paynet.reverse-1-month`: `reverse` works only within 1 month of the payment and cancels the
  whole amount. No refund method exists after that.
- `paynet.unknown-state-poll`: a `confirm` timeout, `-10012` or an unknown `error.code` is not
  a failure. Poll `status` to a final state; never repeat `confirm`.
- `paynet.retryable-means-status`: `retryable: true` means "read `status`", not "send it
  again". A repeated `confirm` can act twice.
- `paynet.no-webhooks-poll`: no callbacks are published. Later `CANCELLED` or `RETURNED` show
  up only through `status`, so reconcile on a schedule.
- `paynet.success-only-paid`: only `data.status` `SUCCESS` is paid. Top-level `status: 0`
  only means the call worked.
- `paynet.otp-ttl-from-response`: count the OTP down from `ttlSeconds` in the `authorize`
  response; never hardcode it. Expiry gives `1008`.
- `paynet.new-orderid-after-expiry`: after `1008`, `1009` or `1010` start a new `authorize`
  with a new `orderId` that maps back to your order.
- `paynet.fiscal-owner-unknown`: the docs do not say who issues the sale or reversal fiscal
  receipt. Store `confirm` `attributes` raw and ask Paynet before go-live.

## Top gotchas

1. The `status` and `reverse` paths are inconsistent on the public page (`/status/value=id`
   vs `/merchant/payment/status?value=`). Make them configurable and confirm them with Paynet.
2. The vendor request example has `"amount": 150 000`, which is not valid JSON. Send an
   integer.
3. The top-level `status` is a number (`0`, `400`, `9005`, ...). `data.status` is a string
   transaction state.
4. `retryable` means "check the status", not "send again". Never repeat `confirm` blindly.
5. The docs allow TLS 1.0 / 1.1. Keep your client at TLS 1.2 or higher.
6. No base URL, sandbox, test cards, webhooks or hosted page are published. Do not invent
   them; say the docs do not cover them. [references/sandbox/](references/sandbox/README.md)
   lists what to ask Paynet.

## Validate an implementation

Run [checklists/acquiring.md](checklists/acquiring.md). Mark each item pass, fail or n.a.
with a file:line citation, then compare the payloads with `schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only. Secrets come from environment variables, never from
arguments, and print as `<SECRET>`.

```sh
python3 scripts/sign.py --list     # paynet.basic
python3 scripts/sign.py paynet.basic -f service_id=<ID> --expect '<Authorization>'  # PAYNET_SECRET_KEY
python3 scripts/validate.py --list [text]
python3 scripts/validate.py authorize body.json [--part result]
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
- Quote field names, types and codes exactly as they appear in the references. If a fact is
  not there, say the docs do not specify it and link the `Source:` page.
- For tests, mocks and examples, use the sandbox data and vendor sample values in
  [references/sandbox/](references/sandbox/README.md). Paynet publishes no test cards or
  OTPs, so never present the sample PAN or OTP as working test data.
- Never use real merchant credentials (a real `service_id`, `secret_key`, `merchantId`,
  login or Basic header), and never invent credentials. Use placeholders such as
  `<SERVICE_ID>`, `<SECRET_KEY>` and `<MERCHANT_ID>`.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them; say they come from the merchant's agreement.
  Fee fields in API answers (`commission`, `fee`, `commission_amount`) are fine to explain.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream. pay-docs.paynet.uz is a single-page app, so a hash change may not track content;
  re-read the pages when in doubt.
