---
name: octo
description: Exact API contracts for the Octo payment gateway (Uzbekistan, secure.octo.uz) - acquiring of Visa / Mastercard / UnionPay and Uzcard / Humo cards, one-stage and two-stage payments through prepare_payment and set_accept, the Octo payment page or the partner's own card form (PCI DSS) with Uzcard / Humo SMS OTP, card tokenization (bind_card, bind_notify_url token callback, pay by card_token, block_card_token), full and partial refunds, fiscalization with registered basket items (spic, package_code, nds, inn / pinfl) and fiscal-data receipts, notify_url notifications signed with sha1 over unique_key, the status check, and the test flag (no separate sandbox host). Use when building, reviewing, debugging or testing an Octo integration - octo_shop_id / octo_secret in the JSON body, {error, data} envelope, major-unit amounts, hold windows, callback answers, refund limits - or when validating an implementation against the contract.
---

# Octo integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json`: trimmed JSON Schemas with `params` (body) and `result` (the
  content of `data`), carrying the source URL and fetched date;
- `examples/`: anonymized bodies.

Examples are bodies only. The host, the shop pair in the body, the `test` flag, the
`{error, data}` envelope, statuses, notifications and their `signature`, basket items and
error codes are in [references/common/README.md](references/common/README.md); read it
first. What Octo publishes for testing (and what it does not) is in
[references/sandbox/](references/sandbox/README.md).

## Products

| Product | Methods | Reference |
|---|---|---|
| Common (all products) | auth pair, `test` flag, envelope, statuses, `notify_url` notification and `signature`, basket item, error codes | [references/common/](references/common/README.md) |
| Payment page (Octo collects the card) | prepare-payment (one-stage / two-stage), check-status, set-accept (capture / cancel), capture-callback you receive | [references/payment-page/](references/payment-page/README.md) |
| Partner page (your card form, PCI DSS) | pay-card, pay-token, verification-info, check-sms-key, check-pan (OTP resend) | [references/partner-page/](references/partner-page/README.md) |
| Cards (tokenization) | bind-card, bind-check-sms-key, bind-callback you receive, block-card-token | [references/cards/](references/cards/README.md) |
| Refunds | refund (full or partial, limits) | [references/refunds/](references/refunds/README.md) |
| Fiscal | basket items in prepare-payment, fiscal-data (receipt) | [references/fiscal/](references/fiscal/README.md) |
| Sandbox and test data | `test: true` on the production host, how to get credentials, what is not published, test runs, vendor sample values | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | ttl, hold windows, capture and bind callbacks, OTP limits, refunds, retries, fiscal receipts | [references/lifecycle/](references/lifecycle/README.md) |

Every call goes to `https://secure.octo.uz` as `POST` JSON with `octo_shop_id` and
`octo_secret` in the body. Test payments use the same host with `test: true`.

## Which product?

| The user wants to... | Use |
|---|---|
| send the payer to an Octo page (Visa, Mastercard, UnionPay, Uzcard, Humo) | Payment page: prepare-payment -> `octo_pay_url`, then notification + status check |
| charge right away | prepare-payment with `auto_capture: true` |
| block funds now, capture or release later | prepare-payment with `auto_capture: false` -> set-accept `capture` or `cancel` |
| collect card data on their own page (PCI DSS certified) | prepare-payment -> Partner page: pay-card -> OTP (Uzcard / Humo) or `redirectUrl` (Visa / Mastercard) |
| save a card for one-click or recurring payments | Cards: bind-card -> OTP -> token in the bind callback |
| charge a saved card | prepare-payment -> Partner page: pay-token |
| refund a paid order fully or partly | Refunds: refund |
| cancel an unpaid or held payment | let `ttl` expire, or set-accept `cancel` for a hold |
| issue a tax receipt | Fiscal: registered `basket` items + `user_data`, then fiscal-data |
| learn the outcome after a lost reply | check-status (three-field prepare-payment) |
| test (test flag, credentials, sample payloads) | [sandbox](references/sandbox/README.md) |

## Rules that apply everywhere

- Amounts are decimal **major units** of `currency` (`1000.0` UZS), not tiyin.
- The shop pair goes in the body of server calls only; it never reaches a browser or app.
- Every answer is `{error, data}`; check `error == 0` and read `data.*`. A body without
  `error` is a failure.
- `test` is optional and its absence means real money; set it from configuration.
- Fulfil only after a verified notification **and** a status check that says `succeeded`
  (or `waiting_for_capture` for a hold). `return_url` proves nothing.
- On a timeout, run the status check with the same `shop_transaction_id` before you try
  again.
- Store `card_token` and the masked PAN only; never log PAN, expiry, CVC2 or OTP.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the deadline or
consequence, and the fix. Every window, refund path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `octo.test-flag-real-money`: `test` is optional and there is no sandbox host; a missing
  flag makes a real payment. Set it explicitly from configuration.
- `octo.hold-auto-cancel`: an uncaptured two-stage hold is cancelled by Octo (30 minutes on
  the two-stage pages, 30 / 7 days on the cancel page); capture with `set_accept` in time.
- `octo.capture-callback-answer`: answer the amount-confirmation callback with `capture` or
  `waiting_user_action` in `accept_status`, or Octo keeps resending it.
- `octo.notify-verify-status`: verify the notification `signature` (sha1 over `unique_key`,
  not `octo_secret`) and re-check the status before you ship.
- `octo.cancel-only-holds`: `set_accept` `cancel` works only on a hold; a `succeeded`
  payment needs `/refund`.
- `octo.refund-limits`: refunds only for `succeeded`, at least 1 USD equivalent, at most
  10 mln UZS per call, total up to the payment; `error: 22` otherwise.
- `octo.unique-shop-ids`: `shop_transaction_id` and `shop_refund_id` are unique per attempt
  and stored before the call; they are the only key after a lost reply.
- `octo.ttl-minutes`: `ttl` is minutes from creation; an expired payment cannot be paid and
  needs a new one.
- `octo.otp-three-tries`: three wrong Uzcard / Humo OTPs cancel the payment; `check_pan`
  resends until `error: 17`.
- `octo.bind-callback-ack`: store the token, then answer the bind callback HTTP 200; after
  three failed retries Octo cancels the token.
- `octo.fiscal-registered-items`: basket items must be registered with Octo first, or
  `prepare_payment` fails with `error: 403`.

## Top gotchas

1. The status check is `prepare_payment` with only `octo_shop_id`, `octo_secret` and
   `shop_transaction_id`; extra fields look like a new payment.
2. The notification `signature` uses `unique_key` from Octo's technical team; the docs say
   notifications are not signed with your secret and the separator is not printed.
3. The `auto_capture` default is printed both ways (`false` and `true`); always send it.
4. The partner flow uses the integer `data.id` as `paymentId` in `check_sms_key`, not
   `octo_payment_UUID`; its times are epoch **milliseconds**.
5. The card token comes only in the `bind_notify_url` callback, which also carries the raw
   PAN. `bind_notify_url` is marked optional, but without it you never get the token.
6. `fiscal-data` takes `payment_uuid`, not `octo_payment_UUID`, and a wrong pair answers
   `error: 1` there and `error: 2` everywhere else.
7. Code `500` means a format error on Humo and `verification_record_not_found` on Uzcard.
8. `user_data` is optional, but once sent it needs `user_id`, `phone` and `email`; the
   fiscal page needs it for the receipt.
9. Several samples use real-looking card numbers and `dev-pay.octo.uz` links; none is
   documented as a test card or a test host.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then the product checklist:

- [checklists/payment-page.md](checklists/payment-page.md) (one-stage, two-stage, status)
- [checklists/partner-page.md](checklists/partner-page.md) (card form, OTP)
- [checklists/cards.md](checklists/cards.md) (tokenization)
- [checklists/refunds.md](checklists/refunds.md) (refunds, hold release)
- [checklists/fiscal.md](checklists/fiscal.md) (basket items, receipts)

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only. Secrets come from environment variables, never from
arguments, and print as `<SECRET>`.

```sh
python3 scripts/sign.py --list     # octo.notify
python3 scripts/sign.py octo.notify notification.json   # OCTO_UNIQUE_KEY
python3 scripts/validate.py --list [text]
python3 scripts/validate.py prepare-payment body.json [--part result]
```

`sign.py` prints the exact string it signed and, given a received value, `MATCH` or
`MISMATCH`. `validate.py` prints `OK` or `INVALID` with JSON paths; trim a reply to
`{error, data}` first (`jq '{error, data}'`). Both exit 1 on a mismatch. Run them before
you call a signature or payload correct, and quote their output.

## Answering rules

- Reply in the user's language, but never translate method names, fields, codes or enum
  values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation. Code uses
  `test: true` and placeholders, and runs as written.
- With several providers in one task, work each one from its own SKILL.md, then compare.
  Never carry a rule (units, auth, retries) over from another provider.
- Lifecycle: before you finish an answer that creates, confirms, cancels, refunds, retries
  or fiscalizes a payment, check "Warn without being asked" and
  [references/lifecycle/](references/lifecycle/README.md). State the deadline, whether the
  step can be undone and what happens to the fiscal receipt, with the warning ID, even if
  nobody asked. For an item under "Not documented", say so and send the user to the
  provider.
- Quote endpoints, fields, types and codes exactly as they appear in the references. If a
  fact is not there, say the docs do not specify it and link the `Source:` page.
- For tests and examples use `test: true` and the notes in
  [references/sandbox/](references/sandbox/README.md). Octo publishes no test cards or test
  OTP; never pay with the sample card numbers. Never use real merchant credentials, keys,
  tokens or real people's data; use placeholders such as `<OCTO_SECRET>` and `<CARD_TOKEN>`.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them; say they come from the merchant's agreement.
  Amount fields in API answers (`total_sum`, `transfer_sum`, `refunded_sum`) are fine to
  explain.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
