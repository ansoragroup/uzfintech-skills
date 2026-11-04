# Atmos: money lifecycle, deadlines and reversals

Read this when building or reviewing an Atmos integration, and raise these traps before
they cost money: the billing answer that decides every debit, calls that must never be
resent, the two transaction ids, hold and token lifetimes, refunds, and fiscal lines.

- Source: https://docs.atmos.uz/en/#callback-api, https://docs.atmos.uz/en/#authorization-in-api,
  https://docs.atmos.uz/en/#transaction-verification,
  https://docs.atmos.uz/en/#retrieving-transaction-information,
  https://docs.atmos.uz/en/#transaction-cancellation,
  https://docs.atmos.uz/en/#creating-a-partial-reversal, https://docs.atmos.uz/en/#holding,
  https://docs.atmos.uz/en/#card-linking, https://docs.atmos.uz/en/#withdrawal-by-tin-pinfl,
  https://docs.atmos.uz/en/#visa-mastercard-acquiring, https://docs.atmos.uz/en/#holding-ips,
  https://docs.atmos.uz/en/#transaction-status-status, plus the references linked in each row
- Fetched: 2026-11-04

## Warn without being asked

1. **`atmos.callback-ack`**: when writing the billing URL handler → check `sign`, match
   `invoice` and `amount` to the order, then answer HTTP 200
   `{"status": 1, "message": "Successfully"}`. Any other status code or `status` means no
   debit. Accept calls only from the Atmos address on the vendor page. Retries and the
   answer timeout are not documented, so make the handler idempotent on `transaction_id`.
   [common](../common/README.md#callback-api-your-billing-url)
2. **`atmos.apply-no-resend`**: when `pay/apply`, `bulk/pay/apply`, a hold capture,
   `mps/pay/transaction/apply` or `ppa/transaction/confirm` times out, returns 5xx,
   `STPIMS-ERR-118`, `STPIMS-ERR-065` or `INFO-202` → read the state (`pay/get`,
   `GET /hold/{id}`, `mps/pay/get/ext_id`, `ppa/transaction/check`); never send the money
   call again. [payments](../payments/README.md#gotchas)
3. **`atmos.paid-check`**: when code marks orders paid → `pay/create` and `pay/pre-apply`
   move no money. Paid means `store_transaction.confirmed` `true` and a non-null
   `success_trans_id`; `pay/get` may answer `STPIMS-ERR-092` for a paid transaction, so do
   not decide on `result.code` alone. A widget or payment-page redirect is not proof.
   [payments](../payments/README.md#gotchas)
4. **`atmos.reverse-success-id`**: when adding refunds → `pay/reverse` takes the
   **`success_trans_id`** in its `transaction_id` field, not the draft `transaction_id`
   from `pay/create`. Store both ids on the order. [payments](../payments/README.md#methods)
5. **`atmos.partial-reverse-confirm`**: when adding partial refunds → nothing is refunded
   until `confirm-reverse-partial` with `ofd_items` for the refunded part; the first call
   only registers it. [payments](../payments/README.md#flow-one-payment)
6. **`atmos.token-otp`**: when charging a linked card → the token flow sends the fixed
   `otp` `111111` on `pay/apply` and `PUT /hold/apply/{id}`; it is not a sandbox code and
   no SMS is sent. `pay/otp-resend` belongs to the SMS flow only.
   [cards](../cards/README.md#gotchas)
7. **`atmos.card-token-merchant`**: when storing linked cards → the card token belongs to
   your merchant, not to a customer; `list-cards` returns every card of the merchant. Keep
   your own customer → `card_id` / `card_token` map and never list another customer's
   cards. [cards](../cards/README.md#gotchas)
8. **`atmos.pci-card-data`**: when the server sends `card_number` + `expiry`
   (`pay/pre-apply`, `bind-card/init`, `hold/create`) or `pan` + `cvc2` (MPS) → that is
   PCI DSS scope. Without the certificate use the payment page, the widget or MPS
   bind-by-owner. [payments](../payments/README.md#hosted-options-no-card-data-on-your-side)
9. **`atmos.hold-expiry`**: when using holds → `duration` is in **minutes**; creating a hold
   freezes nothing until `PUT /hold/apply/{id}`; capture before `hold_till` or get
   `STPIMS-ERR-144` and lose the reservation. The longest duration is not published.
   [hold](../hold/README.md#gotchas)
10. **`atmos.access-token-1h`**: when calling the API → the Bearer token lives 3600 seconds
    by the text (samples show other values): cache it, renew before `expires_in` runs out
    and once on `401`. Never request a token per call. [common](../common/README.md#auth)
11. **`atmos.mps-final-status`**: when handling Visa / Mastercard → fulfil only on `status`
    `4`; `0` to `3` are not final, query again; treat `8` and `9` as pending although the
    table calls them final. Invoices: trust `final` and `success`.
    [mps](../mps/README.md#gotchas)
12. **`atmos.mps-3ds-verified`**: when charging a saved Visa / Mastercard without the payer
    (`create/template`) → only a card with `verified_state` `VERIFIED` works; otherwise
    `-201`. Check `GET /mps/pay/card/{id}` after binding. [mps](../mps/README.md#gotchas)
13. **`atmos.pinfl-ext-id-unique`**: when debiting by PINFL → `ext_id` must be unique for
    ever (`-302`); money moves on `confirm`; `cancel` works only before it and no refund is
    documented. On a timeout call `check` with the same `ext_id`.
    [pinfl](../pinfl/README.md#gotchas)
14. **`atmos.fiscal-items`**: when selling goods or services → send `ofd_items` with the
    IKPU (`ofd_code`) on `pay/create` (and on hold capture, partial reversal, MPS, PINFL in
    their own shapes); the receipt link comes back as `ofd_url`. Without fiscal lines no
    receipt is issued (derived from the PINFL note). [common](../common/README.md#fiscal-items)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Bearer token | 3600 seconds by the text; read `expires_in` | `401` on every call | [common](../common/README.md#auth) |
| Hold (`/hold`) | `duration` minutes, chosen on create; ends at `hold_till` | `STPIMS-ERR-144`, reservation released | [hold](../hold/README.md#gotchas) |
| Hold maximum `duration` | not published | | https://docs.atmos.uz/en/#create-a-hold-request |
| MPS hold (`/mps-extend`) | not published | | [mps](../mps/README.md#holding) |
| MPS invoice | `expiration_time` minutes, or `expiration_date` `YYYY-MM-DDTHH:MM:SS`; default not stated | invoice unusable (derived) | https://docs.atmos.uz/en/#create-an-invoice-ips |
| SMS code (pay, hold, card link) | not documented | `STPIMS-ERR-098` or a new code with `pay/otp-resend` | [payments](../payments/README.md#errors) |
| Your billing answer | not documented | no debit (derived) | [common](../common/README.md#callback-api-your-billing-url) |
| Full or partial reversal after payment | not documented | `STPIMS-ERR-101` | [payments](../payments/README.md#errors) |
| PINFL cancel | until `confirm` | no documented way back | [pinfl](../pinfl/README.md#gotchas) |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Draft never applied (`pay/create` only) | nobody; no money moved | no cancel call documented | n/a | n/a | none | [payments](../payments/README.md#gotchas) |
| You cannot accept the payment | you, in the billing answer | `{"status": 0, "message": "<reason>"}` → no debit | no | once | none | [common](../common/README.md#callback-api-your-billing-url) |
| Full refund of a `/merchant` payment | you | `POST /merchant/pay/reverse {transaction_id: <success_trans_id>, reason}` | no | once (derived) | not described | https://docs.atmos.uz/en/#transaction-cancellation |
| Partial refund | you | `create-reverse-partial` → `confirm-reverse-partial {ofd_items}` | yes, `amount` in tiyin | not documented; `get-reverse-partial` shows what is left | `ofd_items` on confirm | https://docs.atmos.uz/en/#creating-a-partial-reversal |
| Release a hold | you; automatic at `hold_till` | `DELETE /hold/{id} {send_cancel_sms}` | n/a | once | none (derived) | [hold](../hold/README.md#errors) |
| Capture a hold | you | `POST /hold/{id} {amount?, ofd_items?}` | `amount` up to the held amount | once (derived) | `ofd_url` from the capture | [hold](../hold/README.md#methods) |
| Refund a captured `/hold` | you | not documented; `pay/reverse` with its `success_trans_id` is likely | unknown | unknown | unknown | [hold](../hold/README.md#gotchas) |
| MPS hold: release / capture / refund | you | `/mps-extend/<partner>/cancel`, `/apply`, `/return` (`status` 7) | not documented | once (derived) | from the hold `ofd_items` | [mps](../mps/README.md#holding) |
| MPS payment (no hold) | you | no cancel or refund documented | n/a | n/a | n/a | [mps](../mps/README.md#gotchas) |
| PINFL debit, not yet confirmed | you | `POST /ppa/transaction/cancel` → `CANCELED` | n/a | once | none | [pinfl](../pinfl/README.md#methods) |
| PINFL debit, confirmed | you | not documented | n/a | n/a | n/a | [pinfl](../pinfl/README.md#gotchas) |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Billing callback (you receive) | not documented | not documented | `transaction_id` (derived) | answer the same `status` again; fulfil once | [common](../common/README.md#callback-api-your-billing-url) |
| MPS bind-by-owner callback (you receive) | not documented | not documented | `card_id` (derived) | store the card once | [mps](../mps/README.md#card-linking-by-the-owner) |
| `pay/create` (you call) | n/a | n/a | none documented | safe to repeat before `apply` (no money moved); duplicate `account` may give `STPIMS-ERR-066` | [payments](../payments/README.md#methods) |
| `pay/apply`, `bulk/pay/apply` (you call) | n/a | n/a | `transaction_id` | never repeat; `pay/get` | [payments](../payments/README.md#gotchas) |
| `pay/reverse` (you call) | n/a | n/a | `success_trans_id` | `STPIMS-ERR-101`: read the transaction, retry later | [payments](../payments/README.md#errors) |
| Hold capture `POST /hold/{id}` | n/a | n/a | `hold_id` | never repeat; `GET /hold/{id}` | [hold](../hold/README.md#gotchas) |
| MPS create / pre-create (you call) | n/a | n/a | `ext_id` (UUID) | reuse gives `-10`; read with `get/ext_id` | [mps](../mps/README.md#gotchas) |
| PINFL create / confirm (you call) | n/a | n/a | `ext_id` | reuse gives `-302`; read with `check` | [pinfl](../pinfl/README.md#gotchas) |

## Fiscal receipts

- **Who**: Atmos returns the receipt link itself (`ofd_url` for the goods, and
  `ofd_url_commission` for the fee) when you send fiscal lines, so Atmos registers the
  receipt (derived). Do not register a second receipt for the same sale on your own
  fiscal module unless Atmos tells you to.
- **Products**: `/merchant` payments take `ofd_items` on `pay/create`; holds on capture
  (sample only); partial reversal requires them on `confirm-reverse-partial`; MPS takes
  `ofd_items` on `pre-create` and holds and `items` on invoices; PINFL takes `ofd_items`
  `{ofd_code, package_code, tin}` and returns `ofd_url` only if they were sent. No receipt
  is documented for card linking. [common](../common/README.md#fiscal-items)
- **Item fields** (`/merchant`): `ofd_code` (IKPU), `name`, `amount` (tiyin) and
  `details[]` with `quantity`, `package_code`, `mxik_code`, `mark_code`.
- **Refunds**: `pay/reverse` takes no fiscal lines; whether Atmos issues a refund receipt
  for a full reversal is not described. Partial reversal sends `ofd_items` for the
  refunded part (derived from the field).

## Not documented — ask the provider

- The sandbox API host and test credentials (see [sandbox](../sandbox/README.md#not-published)).
- Callback retries, interval and answer timeout; the hash used for `sign`.
- How long after payment a full or partial reversal is allowed, and how many partial
  reversals one payment allows; which `transaction_id` partial reversal takes.
- A refund for a captured `/hold`, a normal MPS payment and a confirmed PINFL debit.
- The maximum hold `duration`, the time zone of `hold_till`, and whether a smaller capture
  releases the rest at once.
- SMS code validity; the widget `key`; the MPS `expiry` format (`MMYY` label vs `YYMM`
  samples).
- Whether a full reversal creates a refund receipt.
