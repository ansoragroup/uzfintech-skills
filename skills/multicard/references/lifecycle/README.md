# Multicard: money lifecycle, deadlines and reversals

Read this when building or reviewing a Multicard integration, and raise these traps before
they cost money: callback answers that refund the payer, calls that must never be resent,
hold and invoice expiry, refunds and payouts, and who issues the fiscal receipt.

- Source: https://docs.multicard.uz/19729300e0 (success callback),
  https://docs.multicard.uz/19729301e0 (webhooks), https://docs.multicard.uz/4488547f0
  (payments guide), https://docs.multicard.uz/19729316e0 (refund),
  https://docs.multicard.uz/24802978e0 (partial refund), https://docs.multicard.uz/19729315e0
  (fiscal link), https://docs.multicard.uz/4488548f0 (hold guide),
  https://docs.multicard.uz/19729318e0 (create hold), https://docs.multicard.uz/19729320e0
  (charge hold), https://docs.multicard.uz/19729296e0 (create invoice),
  https://docs.multicard.uz/4488549f0 (payouts guide), https://docs.multicard.uz/19729323e0
  (create payout), https://docs.multicard.uz/9655813d0 (tax receipt model),
  https://docs.multicard.uz/9655483d0 (store model), https://docs.multicard.uz/4488545f0
  (bind form) (Russian pages), plus the references linked in each row
- Fetched: 2026-11-03

## Warn without being asked

1. **`multicard.callback-reject-refunds`**: when writing the `callback_url` handler → answer
   HTTP 200 `{"success": true}`. Any other status, or `success` not `true`, cancels the
   payment and refunds the payer. A timeout or HTTP 500 leaves the funds blocked and the
   callback may come again; a repeat for the same `uuid` gets the same success answer.
   [common](../common/README.md#success-callback-your-callback_url)
2. **`multicard.never-resend-money-calls`**: when confirm, hold charge, scanpay or a payout
   times out, returns 5xx, `ERROR_DEBIT_UNKNOWN`, `ERROR_CALLBACK_TIMEOUT` or
   `ERROR_UNKNOWN` → poll `GET /payment/{uuid}` or `GET /payment/credit/{uuid}`; never
   resend. [payments](../payments/README.md#gotchas)
3. **`multicard.payout-irreversible`**: when adding payouts (`POST /payment/credit`) → no
   cancel or reversal endpoint is documented, so treat a payout as final. Cards: Uzcard and
   Humo only; `kyc_data` above 10 000 000 UZS (1 000 000 000 tiyin), else
   `400 ERROR_FIELDS`. [payouts](../payouts/README.md#gotchas)
4. **`multicard.draft-is-not-a-sale`**: when code marks orders paid → `POST /payment` and
   `POST /payment/invoice` move no money. Fulfil only on a verified success callback or a
   `success` status; the return URL is not proof. [invoice](../invoice/README.md#flow)
5. **`multicard.debit-available-less`**: when sending `debit_available: true` → Multicard
   may debit less than `amount`; check `payment_amount` and `total_amount` before
   fulfilling. [payments](../payments/README.md#methods)
6. **`multicard.hold-expiry-minutes`**: when using holds → `expiry` is in **minutes**,
   1..43200 (30 days); after it the funds return to the card. Every later call takes the
   **payment** uuid. Charge must be below the held amount and carries `ofd`; cancelling a
   non-active hold answers `403 ERROR_PAYMENT_APPLIED`. [hold](../hold/README.md#gotchas)
7. **`multicard.partial-refund-new-receipt`**: when adding partial refunds → Multicard must
   enable them on the terminal. `DELETE /payment/{uuid}/partial` needs `refund_amount`
   (tiyin) and `ofd`; the vendor says `ofd` fiscalizes a NEW receipt and the old one is
   cancelled. Not refundable: `404 ERROR_NOT_FOUND`. https://docs.multicard.uz/24802978e0
8. **`multicard.one-fiscalizer`**: when issuing receipts → read the store's
   `tax_registration`. With `1` Multicard fiscalizes (`tax`, `refund_tax`): never issue a
   second receipt. With `0` you fiscalize and send the link by `PATCH /payment/{uuid}/fiscal`.
   [reports](../reports/README.md#store-fiscal-settings)
9. **`multicard.invoice-ttl`**: when creating invoices → `ttl` is in seconds (default 1
   day); an expired invoice answers `400 ERROR_TRANS_NOT_READY`, so create a new one. The
   invoice uuid is not the payment uuid. [invoice](../invoice/README.md#gotchas)
10. **`multicard.webhook-5-retries`**: when consuming status webhooks → answer any 2xx or it
    is repeated 5 times. The sign rule conflicts on the vendor page; re-read
    `GET /payment/{uuid}` before acting. [common](../common/README.md#status-webhooks-optional)
11. **`multicard.bind-15-min`**: when binding cards → the bind session lives 15 minutes; the
    bind callback is unsigned and resent every 60 s, 5 attempts. Confirm with
    `GET /payment/card/bind/{session_id}`. [cards](../cards/README.md#bind-callback)
12. **`multicard.otp-codes`**: when handling SMS codes → wrong `400 ERROR_WRONG_OTP`, expired
    `423`, already sent `429`. The validity period is not documented.
    [cards](../cards/README.md#errors)
13. **`multicard.token-24h`**: when calling the API → the `POST /auth` token lives 24 hours;
    cache it, refresh before `expiry` and once on `401`. [common](../common/README.md#auth)
14. **`multicard.split-cap`**: when sending `split` → the parts must not exceed the amount
    minus the commission; read `commission_amount` from the answer.
    [payments](../payments/README.md#split-payments)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Auth token | 24 hours (`expiry`, GMT+5) | every call answers `401` | [common](../common/README.md#auth) |
| Unpaid invoice | `ttl` seconds, default 1 day | cancelled; `GET` answers `400 ERROR_TRANS_NOT_READY` | https://docs.multicard.uz/19729296e0 |
| Hold | `expiry` minutes, 1..43200 (30 days) | funds return to the card automatically | https://docs.multicard.uz/19729318e0 |
| Bind session (`form_url`) | 15 minutes | create a new link | [cards](../cards/README.md#gotchas) |
| Bind callback delivery | every 60 s, 5 attempts | poll `GET /payment/card/bind/{session_id}` | [cards](../cards/README.md#bind-callback) |
| SMS code (payment, hold, card) | not documented | `423` | [cards](../cards/README.md#errors) |
| Your answer to the success callback | not documented | timeout or HTTP 500: funds stay blocked, callback may repeat | [common](../common/README.md#success-callback-your-callback_url) |
| Status webhook | answer any 2xx | repeated 5 times | [common](../common/README.md#status-webhooks-optional) |
| Refund after payment | not documented | `404 ERROR_NOT_FOUND` | https://docs.multicard.uz/19729316e0 |
| Payout without `kyc_data` | up to 10 000 000 UZS | `400 ERROR_FIELDS` | [payouts](../payouts/README.md#errors) |
| Fiscal link after payment or refund | not documented | | https://docs.multicard.uz/19729315e0 |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| `draft` payment never confirmed | nobody; no money moved | no cancel call documented | n/a | n/a | none | [payments](../payments/README.md#gotchas) |
| You cannot fulfil after the debit | you, in the callback answer | non-200 or `{"success": false, "message"}` → Multicard refunds | no | once | not documented | [common](../common/README.md#success-callback-your-callback_url) |
| Unpaid invoice | you, or `ttl` | `DELETE /payment/invoice/{uuid}`; a paid invoice answers `400` | n/a | once | none | [invoice](../invoice/README.md#errors) |
| Full refund of a `success` payment | you | `DELETE /payment/{uuid}` → `revert`, `refund_time` | no | once (`revert` is final) | `1`: read `refund_tax` (how it is created is not described); `0`: your refund receipt, then `PATCH .../fiscal` `is_refund: true` | https://docs.multicard.uz/19729316e0 |
| Partial refund | you, after Multicard enables it | `DELETE /payment/{uuid}/partial {refund_amount, ofd, card_pan}` | yes, `refund_amount` in tiyin | not documented | `ofd` makes a new receipt; the old one is cancelled | https://docs.multicard.uz/24802978e0 |
| Release a hold | you; automatic at `expiry` | `DELETE /payment/hold/{uuid}`; not active → `403 ERROR_PAYMENT_APPLIED` | n/a | once | none (derived) | [hold](../hold/README.md#errors) |
| Capture a hold | you | `PUT /payment/hold/{uuid}/charge {amount, split, ofd}` | `amount` below the held amount | once (derived) | from the `ofd` on charge | https://docs.multicard.uz/19729320e0 |
| Refund a charged hold | you | `DELETE /payment/{uuid}` | as a full refund | as above | as above | [hold](../hold/README.md#gotchas) |
| Payout sent by mistake | you | no reversal endpoint documented | n/a | n/a | not documented | [payouts](../payouts/README.md#methods) |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Success callback | may repeat after a timeout or HTTP 500; count not documented | not documented | payment `uuid` | same `{"success": true}` again; fulfil once | [common](../common/README.md#success-callback-your-callback_url) |
| Status webhook | 5 repeats unless 2xx | not documented | `uuid` + `status` (derived) | ignore a status you already applied | https://docs.multicard.uz/19729301e0 |
| Bind callback | every 60 s, 5 attempts | not documented | `payer_id` = your `session_id` | save the token once | [cards](../cards/README.md#bind-callback) |
| `PUT /payment/{uuid}` confirm (you call) | n/a | n/a | payment `uuid` | already confirmed: `400 ERROR_FIELDS`; unknown outcome: poll | [payments](../payments/README.md#errors) |
| `PUT /payment/hold/{uuid}/charge` (you call) | n/a | n/a | payment `uuid` | never repeat; poll `GET /payment/{uuid}` | [hold](../hold/README.md#gotchas) |
| `PUT /payment/{uuid}/scanpay` (you call) | n/a | n/a | invoice `uuid` | on a timeout, `ERROR_DEBIT_UNKNOWN` or 500, read the invoice | [invoice](../invoice/README.md#scanpay-paymego-clickpass-and-similar) |
| `POST /payment/credit` payout (you call) | n/a | n/a | `invoice_id`; duplicate rejection not documented | `ERROR_UNKNOWN` or timeout: poll `GET /payment/credit/{uuid}` | [payouts](../payouts/README.md#gotchas) |
| `POST /payment`, `POST /payment/invoice` | n/a | n/a | `invoice_id`; duplicate rejection not documented | safe to repeat only before confirm (derived: no money moved) | [payments](../payments/README.md#methods) |

## Fiscal receipts

- **Who**: the store's `tax_registration` decides. `1`: Multicard fiscalizes the sale from
  `ofd`. `0`: you fiscalize. `2` / `3`: Multicard fiscalizes only the on-top (`up`) or
  merchant-paid (`down`) commission, so the goods receipt is yours (derived). Read it with
  get-store. [reports](../reports/README.md#store-fiscal-settings)
- **Products**: invoices require `ofd` on create; payments accept it; holds take it on
  charge, not on create; partial refunds require it. No receipt is documented for payouts
  or card binding.
- **Multicard receipts**: sale in `tax`, refund in `refund_tax` (`receipt`, `f_num`,
  `fm_num`, `qr_url`, `is_refund`). With `1` never register a second receipt yourself.
  https://docs.multicard.uz/9655813d0
- **Your receipts**: send the link with `PATCH /payment/{uuid}/fiscal {url, is_refund}`;
  after a refund issue a refund receipt linked to the sale, not above the sale total, and
  send it with `is_refund: true` (derived from the field). https://docs.multicard.uz/19729315e0
- **`ofd` item fields**: `qty`, `price` (unit, tiyin), `total` (`qty x price` before
  discounts, tiyin), `mxik`, `package_code`, `name`, `vat`, `tin`, `mark` (one per unit
  for marked goods). Store defaults: `tax_mxik`, `tax_package_code`,
  `tax_commission_recipient_tin`. [common](../common/README.md#fiscal-items-ofd)
- **Partial refund**: the vendor says `ofd` is the data for a NEW receipt and the OLD one is
  cancelled; which items it should list is unclear (see below).

## Not documented — ask the provider

- How long after payment a full or partial refund is allowed, how many partial refunds one
  payment allows, and whether a full refund works after a partial one.
- Whether partial-refund `ofd` lists the refunded items or the items kept; what the call
  returns.
- Whether `revert` creates `refund_tax` automatically when `tax_registration` is `1`.
- Deadline for the fiscal link (`PATCH /payment/{uuid}/fiscal`), and whether a refund link
  is required for `0`.
- Success callback retry count, interval and answer timeout; how long funds stay blocked.
- SMS code validity for payments, holds and card binding.
- Whether charging less than the held amount releases the rest; the hold status after
  `expiry`.
- A payout cancel or reversal; duplicate handling for a repeated `invoice_id`.
- The correct status-webhook sign rule (md5 vs SHA1 on the same page).
