---
name: atmos
description: Exact API contracts for the Atmos payment gateway (Uzbekistan, apigw.atmos.uz; partner.atmos.uz is not in the public docs) - OAuth2 client-credentials Bearer token (1 h), Uzcard / Humo payments by SMS code or card token (pay/create, pre-apply, apply), multi-payments, full and partial reversals, the hosted payment page and HTML widget, card linking (bind-card init / confirm, card tokens for recurring charges), holds (single and multiple), withdrawal by PINFL, Visa / Mastercard acquiring (MPS / IPS invoices, card binding with 3DS, bind-by-owner, recurring template charges, holds), fiscal ofd_items (IKPU), the Callback API to your billing URL with its sign, and the published test cards and OTP. Use when building, reviewing, debugging or testing an Atmos integration - STPIMS-ERR codes, tiyin amounts, success_trans_id vs transaction_id, polling on unknown outcomes - or when validating an implementation against the contract.
---

# Atmos integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json`: trimmed JSON Schemas with `params` (body), `path` and `result`,
  carrying the source URL and fetched date;
- `examples/`: anonymized bodies.

Examples are bodies only. The host, the token call, the three answer envelopes, the
`STPIMS-ERR-*` codes, the Callback API and its `sign`, and `ofd_items` are in
[references/common/README.md](references/common/README.md); read it first. Test cards, the
OTP and the test widget / payment page are in [references/sandbox/](references/sandbox/README.md).

## Products

| Product | Methods | Reference |
|---|---|---|
| Common (all products) | `POST /token`, `/revoke`, envelopes, `STPIMS-ERR-*` codes, Callback API `sign`, `ofd_items`, `store_transaction` | [references/common/](references/common/README.md) |
| Payments (Uzcard / Humo) | pay-create, pay-pre-apply, pay-apply, pay-otp-resend, pay-get, pay-reverse, create / confirm / get-reverse-partial, bulk-pay-create / pre-apply / apply; payment page, HTML widget | [references/payments/](references/payments/README.md) |
| Card linking | bind-card-init, bind-card-confirm, list-cards, remove-card | [references/cards/](references/cards/README.md) |
| Holding | hold-create, hold-apply, hold-multiple-create / apply, hold-capture, hold-cancel, hold-get | [references/hold/](references/hold/README.md) |
| Withdrawal by PINFL | pinfl-create, pinfl-confirm, pinfl-check, pinfl-cancel, pinfl-update-cards, pinfl-cards-check | [references/pinfl/](references/pinfl/README.md) |
| Visa / Mastercard (MPS / IPS) | invoice create / get, card-bind link (by owner), card bind with 3DS, get / unbind card, pre-create, create / create-bind, apply, create-template (recurring), get by id / ext_id, hold / apply / cancel / return | [references/mps/](references/mps/README.md) |
| Sandbox and test data | 5 test cards, 1 expired-card case, OTP `111111`, test widget and payment page, what is not published | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | deadlines, cancel / reverse / refund, retries, hold and token lifetimes, fiscal receipts | [references/lifecycle/](references/lifecycle/README.md) |

Every call goes to `https://apigw.atmos.uz` with JSON bodies and
`Authorization: Bearer <access_token>` from `POST /token` (Basic
`consumer_key:consumer_secret`). MPS calls also send `apikey: <API_KEY>`.

## Which product?

| The user wants to... | Use |
|---|---|
| take an Uzcard / Humo payment without touching card data | Payments: pay-create → payment page or HTML widget → billing callback → pay-get |
| take an Uzcard / Humo payment from their own form (PCI DSS) | Payments: pay-create → pay-pre-apply `card_number` + `expiry` → pay-apply with the SMS code |
| save an Uzcard / Humo card and charge it later | Card linking: bind-card-init → bind-card-confirm → `card_token`; Payments with `card_token` and `otp` `111111` |
| split one card debit across several accounts of the store | Payments: bulk-pay-create → bulk-pay-pre-apply → bulk-pay-apply |
| refund fully or partly | Payments: pay-reverse with `success_trans_id`; create- then confirm-reverse-partial |
| block funds now, capture later | Holding: hold-create → hold-apply → capture or cancel (Visa / Mastercard: MPS hold) |
| debit a person's cards under a contract, without card data | Withdrawal by PINFL: create → confirm |
| take Visa / Mastercard | MPS: invoice page, or pre-create → create-bind → 3DS → apply |
| charge a saved Visa / Mastercard without the payer | MPS: create-template on a 3DS-verified card |
| answer the billing callback | [common](references/common/README.md#callback-api-your-billing-url) + `sign.py atmos.callback` |
| fiscalize (tax receipt) | `ofd_items` (IKPU); Atmos returns `ofd_url` |
| test (cards, OTP, scenarios) | [sandbox](references/sandbox/README.md) |

## Rules that apply everywhere

- Amounts are integer **tiyin** (1 UZS = 100) in every product.
- Cache the Bearer token for `expires_in` (3600 s by the text); on `401` get a new one and
  retry once. Send `Bearer` once, not `Bearer Bearer`.
- Three envelopes: `result.code` (`OK` / `STPIMS-ERR-*`) for `/merchant`, `/partner`,
  `/hold`; `code` `"200"` / negative for `/ppa`; `status.code` `0` / negative for `/mps`.
  Branch on the HTTP status first.
- Creating a payment, hold or PINFL debit moves no money; apply / confirm does, and on
  `/merchant` only after your billing URL answers `200 {"status": 1}`.
- On a timeout, a 5xx, `STPIMS-ERR-118`, `STPIMS-ERR-065` or `INFO-202`, read the object
  until a final state. Never resend a money-moving call.
- `consumer_secret`, `api_key`, MPS `apikey` and card data stay on the server. Store the
  card token and the masked PAN only.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the deadline or
consequence, and the fix. Every window, refund path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `atmos.callback-ack`: check `sign`, match `invoice` and `amount`, answer HTTP 200
  `{"status": 1}`; any other answer means no debit.
- `atmos.apply-no-resend`: apply / capture / confirm timed out or unknown → `pay/get`,
  `GET /hold/{id}`, `get/ext_id` or `check`; never apply again.
- `atmos.paid-check`: paid = `confirmed` `true` + `success_trans_id`; `pay/get` can say
  `STPIMS-ERR-092` for a paid transaction; a redirect is not proof.
- `atmos.reverse-success-id`: `pay/reverse` takes `success_trans_id`, not the draft
  `transaction_id`.
- `atmos.partial-reverse-confirm`: nothing is refunded until `confirm-reverse-partial` with
  `ofd_items`.
- `atmos.token-otp`: card-token flows send the fixed `otp` `111111`; it is not a sandbox
  code, and `otp-resend` is SMS-only.
- `atmos.card-token-merchant`: tokens belong to the merchant; `list-cards` returns every
  card, so keep your own customer mapping.
- `atmos.pci-card-data`: sending `card_number` + `expiry` or `pan` + `cvc2` is PCI DSS
  scope; otherwise use the payment page, widget or bind-by-owner.
- `atmos.hold-expiry`: `duration` is minutes; capture before `hold_till` or get
  `STPIMS-ERR-144`.
- `atmos.access-token-1h`: cache the Bearer token, renew before `expires_in`.
- `atmos.mps-final-status`: fulfil only on `status` `4`; re-query `0`-`3`, treat `8` / `9`
  as pending.
- `atmos.mps-3ds-verified`: `create/template` needs a card with `verified_state`
  `VERIFIED`, else `-201`.
- `atmos.pinfl-ext-id-unique`: `ext_id` is unique for ever (`-302`); `cancel` only before
  `confirm`; no refund documented.
- `atmos.fiscal-items`: send `ofd_items` with the IKPU; Atmos returns `ofd_url`.

## Top gotchas

1. `transaction_id` (draft) and `success_trans_id` (paid) are different numbers; refunds
   take the second.
2. The callback `sign` is `store_id + transaction_id + invoice + amount + api_key` with no
   separators, but the hash is not named: run `sign.py atmos.callback` to find it.
3. `expiry` is `YYmm` on `/merchant`, `/partner` and `/hold` (`2802` for 02/28); MPS labels
   it `MMYY` while its samples read `YYMM`.
4. The resend path is `otp-resend` in the HTTP line and `retry-otp` in the sample.
5. Hold `duration` is minutes; `DELETE /hold/{id}` carries a body; the docs return
   `STPIMS-ERR-145` as the successful release answer.
6. No refund is documented for a normal MPS payment, a captured `/hold` or a confirmed
   PINFL debit.
7. The MPS transaction table calls statuses `8` and `9` final although they are pending.
8. Several vendor samples are not valid JSON (`00000`) or print `Bearer Bearer`.
9. No sandbox host or test credentials are published; ask Atmos.
10. `partner.atmos.uz` is not described in the public docs; card linking lives at
    `https://apigw.atmos.uz/partner/...`.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then the product checklist:

- [checklists/payments.md](checklists/payments.md) (payments, refunds, multi-payments, hosted page)
- [checklists/cards.md](checklists/cards.md)
- [checklists/hold.md](checklists/hold.md)
- [checklists/pinfl.md](checklists/pinfl.md)
- [checklists/mps.md](checklists/mps.md) (Visa / Mastercard)

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only. Secrets come from environment variables, never from
arguments, and print as `<SECRET>`.

```sh
python3 scripts/sign.py --list     # atmos.basic, atmos.callback
python3 scripts/sign.py atmos.callback body.json   # md5 / sha1 / sha256; ATMOS_API_KEY
python3 scripts/sign.py atmos.basic -f consumer_key=<KEY>  # Basic header; ATMOS_CONSUMER_SECRET
python3 scripts/validate.py --list [text]
python3 scripts/validate.py pay-create body.json [--part result]
```

`sign.py` prints the exact string it signed and, given a received value, `MATCH` or
`MISMATCH`. `validate.py` prints `OK` or `INVALID` with JSON paths. Both exit 1 on a
mismatch. Run them before you call a signature, header or payload correct, and quote their
output.

## Answering rules

- Reply in the user's language, but never translate method names, fields, headers, codes
  or enum values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation.
- With several providers in one task, work each one from its own SKILL.md, then compare.
  Never carry a rule (units, auth, retries) over from another provider.
- Lifecycle: before you finish an answer that creates, confirms, cancels, refunds, retries
  or fiscalizes a payment, check "Warn without being asked" and
  [references/lifecycle/](references/lifecycle/README.md). State the deadline, whether the
  step can be undone and what happens to the fiscal receipt, with the warning ID. For an
  item under "Not documented", say so and send the user to Atmos.
- Quote endpoints, fields, types and codes exactly as they appear in the references. If a
  fact is not there, say the docs do not specify it and link the `Source:` page.
- For tests use the data in [references/sandbox/](references/sandbox/README.md). Never use
  real merchant credentials or real people's data; use placeholders such as `<API_KEY>`,
  `<CARD_TOKEN>` and `<STORE_ID>`.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them. Fee fields in API answers (`commission`,
  `ofd_url_commission`) are fine to explain.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
