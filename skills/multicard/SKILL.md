---
name: multicard
description: Exact API contracts for the Multicard payment gateway (Uzbekistan, mesh.multicard.uz) - Bearer JWT auth (24 h token), hosted invoices with checkout_url / QR scanpay, card binding by hosted form or PCI DSS API, token and card payments with OTP confirm, payments through Payme / Click / Uzum / other apps, holds, full and partial refunds, payouts to Uzcard / Humo cards with KYC, split payments, fiscal items (ofd: mxik IKPU, package_code, vat), success callbacks signed with md5, status webhooks, registries and the dev-mesh sandbox with its test card and OTP. Use when building, reviewing, debugging or testing a Multicard integration - {success, data|error} envelope, ERROR_* codes, tiyin amounts, GMT+5 times, polling on unknown outcomes - or when validating an implementation against the contract.
---

# Multicard integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json`: trimmed JSON Schemas with `params` (body), `path`, `query` and
  `result` (the content of `data`), carrying the source URL and fetched date;
- `examples/`: anonymized bodies.

Examples are bodies only. The base URLs, Bearer auth, the `{success, data | error}`
envelope, error codes, payment statuses, callback signatures, `ofd` and `split` are in
[references/common/README.md](references/common/README.md); read it first. Test hosts, the
test card and the sandbox OTP are in [references/sandbox/](references/sandbox/README.md).

## Products

| Product | Methods | Reference |
|---|---|---|
| Common (all products) | `POST /auth`, envelope, error codes, payment statuses, success callback `sign`, status webhooks, `ofd`, `split`, shared models | [references/common/](references/common/README.md) |
| Invoice (hosted page) | create-invoice, get-invoice, delete-invoice, scanpay; success callback and status webhook you receive | [references/invoice/](references/invoice/README.md) |
| Cards (binding) | create-bind-link, get-bind-status, get-card, check-pinfl, revoke-card; PCI DSS: add-card, confirm-card, check-card-by-pan; bind callback | [references/cards/](references/cards/README.md) |
| Payments (own page, refunds) | create-payment by token / card data / split / app (`payment_system`), confirm-payment, send-fiscal-link, refund-payment, refund-payment-partial, get-payment | [references/payments/](references/payments/README.md) |
| Hold | create-hold, confirm-hold, charge-hold, get-hold, cancel-hold | [references/hold/](references/hold/README.md) |
| Payouts | create-payout, confirm-payout, get-payout (Uzcard / Humo, `kyc_data` above 10 000 000 UZS) | [references/payouts/](references/payouts/README.md) |
| Reports | get-application (wallet), get-store (fiscal settings), get-merchant-account, get-payment-history, get-payout-history | [references/reports/](references/reports/README.md) |
| Sandbox and test data | `dev-mesh` host, the test card and its expiry, OTP `111111`, credential steps, test runs, vendor sample values | [references/sandbox/](references/sandbox/README.md) |

Every call goes to `https://mesh.multicard.uz/` (sandbox `https://dev-mesh.multicard.uz/`)
with JSON bodies and `Authorization: Bearer <JWT>` from `POST /auth {application_id, secret}`.

## Which product?

| The user wants to... | Use |
|---|---|
| send the payer to a Multicard payment page (cards and apps) | Invoice: create-invoice -> `checkout_url`, then the success callback |
| take payment from a QR shown in the payer's Payme / Click / Uzum app | Invoice: create-invoice + scanpay |
| save a card without PCI DSS | Cards: create-bind-link -> hosted form -> `card_token` |
| save a card from their own form (PCI DSS certified) | Cards: add-card -> confirm-card |
| charge a saved card (recurring, one-click) | Payments: create-payment with `card.token` -> confirm-payment |
| redirect to a payment app from their own page | Payments: create-payment with `payment_system` |
| block funds now, capture later | Hold: create -> confirm -> charge or cancel |
| refund fully or partly | Payments: `DELETE /payment/{uuid}` or `DELETE /payment/{uuid}/partial` |
| pay money out to a card | Reports: get-application (balance) -> Payouts: create-payout |
| split one payment between recipients | `split` on create-payment, create-hold or charge-hold |
| fiscalize (tax receipt) | `ofd` items; store `tax_registration` decides who registers the receipt |
| reconcile | Reports: get-payment-history, get-payout-history |
| test against the sandbox (test card, OTP, runs, sample payloads) | [sandbox](references/sandbox/README.md) |

## Rules that apply everywhere

- Amounts are integer **tiyin** (1 UZS = 100). Times are `Y-m-d H:i:s` in **GMT+5**.
- Cache the JWT for its 24-hour life; on `401` get a new one and retry once.
- Every answer except `/auth` is `{success, data}` or `{success: false, error{code,
  details}}`. Branch on the HTTP status **and** `error.code`.
- Creating a payment, hold or payout moves no money; the confirm step (or the hosted page)
  does. Fulfil only on `success` from a verified callback or a `GET`.
- On a timeout, a 5xx, `ERROR_DEBIT_UNKNOWN`, `ERROR_CALLBACK_TIMEOUT` or `ERROR_UNKNOWN`,
  poll the object until a final status. Never resend a money-moving call.
- `secret` and card data stay on the server. Store the `card_token` and the masked PAN only.

## Top gotchas

1. Verify the success callback `sign` = md5 of `{store_id}{invoice_id}{amount}{secret}`,
   then answer HTTP 200 `{"success": true}`. Any other answer **refunds the payer**.
2. The status webhook sign is documented two ways (md5 of `{uuid}{amount}{secret}` vs SHA1
   of `{uuid}{invoice_id}{amount}{secret}`); the bind callback is not signed at all.
3. `/auth` answers without the envelope and uses its own `400` error shape.
4. `ofd` is required on create-invoice; `price` is the unit price and `total` is
   `qty x price`. The vendor examples break that rule.
5. The invoice `uuid` and the payment `uuid` differ; holds are addressed by
   `data.payment.uuid`, not the hold `id`.
6. Hold `expiry` is in **minutes** (max 43200); invoice `ttl` is in **seconds**.
7. Several pages call `423`, `429` and `403` answers "400" in the text; a refund that is no
   longer possible answers `404 ERROR_NOT_FOUND`.
8. Fields marked required are sometimes optional (`callback_url`, `phone`, `user_phone`,
   `confirmable`, `kyc_data`); each product README says which.
9. Payout `store_id` is a string; `kyc_data` comes back as a JSON string.
10. `short_link` is returned only in production; the sandbox has one test card and no
    documented test phone.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then the product checklist:

- [checklists/invoice.md](checklists/invoice.md)
- [checklists/cards.md](checklists/cards.md)
- [checklists/payments.md](checklists/payments.md) (payments, refunds, holds)
- [checklists/payouts.md](checklists/payouts.md) (payouts, wallet, registries)

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Answering rules

- Quote endpoints, fields, types and codes exactly as they appear in the references. If a
  fact is not there, say the docs do not specify it and link the `Source:` page.
- For tests and examples use the sandbox data in
  [references/sandbox/](references/sandbox/README.md) (test card, OTP, sandbox host, vendor
  sample values). Never use real merchant credentials, keys, tokens or real people's data;
  use placeholders such as `<APPLICATION_ID>`, `<SECRET>` and `<CARD_TOKEN>` for those.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them; say they come from the merchant's agreement.
  Fee fields in API answers (`commission`, `fee`, `commission_amount`) are fine to explain.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
