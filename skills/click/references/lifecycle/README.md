# Click: money lifecycle, deadlines and reversals

Read this when building or reviewing a Click integration, and raise these traps before
they cost money: what Complete may answer after the debit, the reversal month window,
retries, one-time codes and tokens, and who issues the fiscal receipt.

- Source: https://docs.click.uz/en/shop-api/requests, https://docs.click.uz/en/shop-api/errors,
  https://docs.click.uz/en/merchant-api/requests, https://docs.click.uz/en/merchant-api/fiscalization,
  https://docs.click.uz/en/merchant-api/click-pass, https://docs.click.uz/en/additional/get-info,
  https://docs.click.uz/en/additional/shop-split, https://docs.click.uz/en/click-button/,
  https://docs.click.uz/en/additional/telegram-payments, plus the references linked in each
  row
- Fetched: 2026-11-03

## Warn without being asked

1. **`click.complete-after-debit`**: when writing the Complete handler → once Prepare
   succeeded and Click debited the payer, Complete must not answer an error except `-4`
   (already paid) or `-9` (cancelled). Click retries erroneous answers, then the payment goes
   to manual investigation. If you cannot deliver, answer success and then call
   `DELETE payment/reversal/:service_id/:payment_id`.
   [shop-api](../shop-api/README.md#after-click-has-debited-the-payer)
2. **`click.negative-error-cancels`**: when Complete arrives with `error < 0` → cancel,
   release the reservation and answer `-9`, even after an earlier success (Postman scenario
   8 expects `-9`, not `-4`). Never mark the order paid on it.
   [shop-api](../shop-api/README.md#test-scenarios-postman-generator)
3. **`click.reversal-month-window`**: when the task adds refunds → `payment/reversal` works
   only for a successful online-card payment of the **current reporting month**; a previous
   month's payment only on the **first day** of the next month. Full amount only; UZCARD may
   still reject. Plan another refund path. [merchant-api](../merchant-api/README.md#reversal)
4. **`click.idempotent-retries`**: when writing any SHOP API handler → Click repeats requests
   after timeouts and errors; key on `click_trans_id`. Advanced / Split Shop: unique per
   (`click_paydoc_id`, `attempt_trans_id`), but book the payment on `click_paydoc_id`.
   [shop-api](../shop-api/README.md#gotchas), [advanced-shop](../advanced-shop/README.md#gotchas)
5. **`click.soums-vs-tiyin`**: when handling amounts → SHOP API, Merchant API, CLICK Pass and
   links use **soums** (float; the link wants `N.NN`); fiscalization uses integer **tiyin**.
   Hash the raw `amount` string; compare in integer tiyin. [common](../common/README.md#units)
6. **`click.one-fiscal-receipt`**: when fiscalizing → use either `submit_items` (Click
   fiscalizes) or `submit_qrcode` (your own receipt), never both, only after a successful
   payment. Read `GET payment/ofd_data/:service_id/:payment_id` before any second submit.
   [fiscalization](../fiscalization/README.md#operations)
7. **`click.no-refund-receipt-api`**: when refunds meet fiscal receipts → Click documents no
   refund-receipt method and does not say whether a reversal cancels a `submit_items`
   receipt. Ask Click before going live. [fiscalization](../fiscalization/README.md#gotchas)
8. **`click.return-url-not-proof`**: when a link, button or widget returns the payer →
   `return_url`, the posted `status` and the widget callback can be forged or lost. Proof is
   your accepted Complete or `payment/status_by_mti`.
   [payment-button](../payment-button/README.md#gotchas)
9. **`click.reserve-own-timeout`**: when Prepare reserves goods → the docs set no
   Prepare-to-Complete deadline; release the reservation on your own timeout.
   [shop-api](../shop-api/README.md#gotchas)
10. **`click.status-1-not-final`**: when charging a card token or CLICK Pass →
    `payment_status` `1` is not final; poll `payment/status` until `2` or negative, and
    after a timeout poll before charging again. [merchant-api](../merchant-api/README.md#fields)
11. **`click.pass-confirm-30s`**: when CLICK Pass runs in confirmation mode →
    `click_pass/confirm` must arrive within **30 seconds** or Click cancels the payment;
    `otp_data` is single-use. [click-pass](../click-pass/README.md#flow)
12. **`click.check-status`**: when answering Advanced Shop `check` → `0` makes Click retry,
    `1` makes Click cancel, `2` marks success. Answer `0` only while truly processing.
    [advanced-shop](../advanced-shop/README.md#fields)
13. **`click.telegram-10s`**: when a Telegram bot sells through Click → answer
    `answerPreCheckoutQuery` within 10 s or Telegram cancels; mark paid only on
    `successful_payment`; `prices` are tiyin; refunds and chargebacks are the bot owner's.
    [telegram](../telegram/README.md#rules)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Prepare → Complete | not documented | release the reservation on your own timeout | [shop-api](../shop-api/README.md#gotchas) |
| `sign_time` age | not documented | | [shop-api](../shop-api/README.md#prepare-action--0) |
| `payment/reversal` | current reporting month; a previous month only on day 1 of the next month | reversal refused; refund by another path | [merchant-api](../merchant-api/README.md#reversal) |
| CLICK Pass confirmation mode | 30 seconds | Click cancels the payment | [click-pass](../click-pass/README.md#flow) |
| CLICK Pass `otp_data` | one use | send right after the scan; never reuse | [click-pass](../click-pass/README.md#gotchas) |
| Card token SMS code (`sms_code`) | not documented | | [card-tokens](../card-tokens/README.md#flow) |
| One-time token (`temporary = 1`) | one payment | Click deletes it | [card-tokens](../card-tokens/README.md#flow) |
| Merchant API `Auth` timestamp | seconds; allowed skew not documented | 401 | [merchant-api](../merchant-api/README.md#gotchas) |
| Unpaid `invoice/create` | lifetime not documented; status `-99` = Deleted | treat negative status as "will not be paid" | [merchant-api](../merchant-api/README.md#fields) |
| `payment/status_by_mti` lookup | the `YYYY-MM-DD` date the payment was made | payment not found | [merchant-api](../merchant-api/README.md#fields) |
| Fiscal data submit | only after `payment_status = 2` or an accepted Complete; deadline not documented | | [fiscalization](../fiscalization/README.md#gotchas) |
| Telegram `pre_checkout_query` | 10 seconds | Telegram cancels the payment | [telegram](../telegram/README.md#rules) |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Payment fails on Click's side after Prepare | Click | Complete with `error < 0`; you cancel and answer `-9` | n/a | every repeat gets `-9` | none (derived: not paid) | [shop-api](../shop-api/README.md#complete-action--1) |
| Click cancels after you accepted Complete | Click | Complete with `error < 0`; cancel, answer `-9` | n/a | every repeat gets `-9` | not documented | [shop-api](../shop-api/README.md#test-scenarios-postman-generator) |
| You cannot deliver after the debit | you | answer Complete success, then `DELETE payment/reversal/:service_id/:payment_id` | no | not documented | not documented | [shop-api](../shop-api/README.md#after-click-has-debited-the-payer) |
| Refund of a paid order (SHOP API, invoice, link, card token, CLICK Pass) | you | `DELETE payment/reversal/:service_id/:payment_id` | no; partial reversal is only in the previous docs | not documented | Click: no refund-receipt method; own register: issue your own refund receipt | [merchant-api](../merchant-api/README.md#reversal), [common](../common/README.md#doc-caveats) |
| Advanced Shop attempt failed on your side | you (answer) | `check` with `status: 1` → Click cancels | n/a | per attempt | none (derived) | [advanced-shop](../advanced-shop/README.md#fields) |
| CLICK Pass not confirmed | Click, automatically | no call; 30 s pass | n/a | n/a | none (derived) | [click-pass](../click-pass/README.md#flow) |
| Unpaid invoice | not documented | no cancel method documented; status `-99` Deleted | n/a | n/a | none | [merchant-api](../merchant-api/README.md#fields) |
| Refuse at checkout (Telegram) | you | `answerPreCheckoutQuery` `ok=false` + `error_message` | n/a | n/a | none | [telegram](../telegram/README.md#flow) |
| Telegram payment after `ok=true` | bot owner | not documented on the Click page | | | not documented | [telegram](../telegram/README.md#gotchas) |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| SHOP API Prepare | yes, after timeouts and errors; count not documented | not documented | `click_trans_id` | same answer; already paid `-4`; cancelled `-9` | [shop-api](../shop-api/README.md#gotchas) |
| SHOP API Complete | yes, after erroneous answers, then manual investigation | not documented | `click_trans_id` + `merchant_prepare_id` | repeat after success `-4`; after cancel `-9`; `error < 0` after success `-9` | [shop-api](../shop-api/README.md#test-scenarios-postman-generator) |
| Advanced / Split prepare and confirm | yes, with a new `attempt_trans_id` | not documented | (`click_paydoc_id`, `attempt_trans_id`); book on `click_paydoc_id` | never book one `click_paydoc_id` twice | [advanced-shop](../advanced-shop/README.md#gotchas) |
| Advanced `check` | Click asks; your `0` makes Click retry the payment | not documented | `click_paydoc_id` + `attempt_trans_id` | answer from your ledger | [advanced-shop](../advanced-shop/README.md#fields) |
| Advanced `compare` | Click asks for a period | not documented | `click_paydoc_id` keys | include payments that came through retries | [advanced-shop](../advanced-shop/README.md#gotchas) |
| `card_token/payment` (you call) | n/a | n/a | `transaction_parameter`, unique per charge | no duplicate rejection documented; on a timeout poll `payment/status` before charging again | [card-tokens](../card-tokens/README.md#gotchas) |
| `click_pass/payment` (you call) | n/a | n/a | `transaction_id` | on a timeout poll `payment/status` before charging again | [click-pass](../click-pass/README.md#gotchas) |
| `submit_items` / `submit_qrcode` (you call) | n/a | n/a | `payment_id` | read `get-ofd-data` before resubmitting | [fiscalization](../fiscalization/README.md#gotchas) |

## Fiscal receipts

- **Who**: Click fiscalizes a payment when you send its items with
  `POST payment/ofd_data/submit_items`. If your own register or OFD provider made the
  receipt, send its link with `POST payment/ofd_data/submit_qrcode`. One or the other per
  payment. [fiscalization](../fiscalization/README.md#operations)
- **Products**: SHOP API, Advanced / Split Shop, invoices, card tokens, CLICK Pass and
  payment links all produce a Click `payment_id`, so all use these calls (derived). For
  Telegram payments the Click page says nothing about fiscal receipts.
- **Sale fields** (tiyin, PascalCase): `Name`, `SPIC` (IKPU), `PackageCode`, `Price` (line
  total), `GoodPrice` (unit), `Amount` (quantity), `VAT`, `VATPercent`, `CommissionInfo`
  (`TIN` or `PINFL`), plus `received_ecash` / `received_cash` / `received_card` that should
  add up to the payment total. [fiscalization](../fiscalization/README.md#submit-items-fields)
- **Timing**: only after `payment_status = 2` or a Complete you accepted. No deadline is
  documented.
- **Refund**: no refund-receipt call exists. With `submit_items` do not issue your own
  receipt for the sale or the refund until Click says how reversals are fiscalized. With
  your own register, issue a refund receipt there linked to the sale; reversal is full only,
  so it equals the sale total. Click documents no time limit for it.
- **Before a second submit**: read `GET payment/ofd_data/:service_id/:payment_id`
  (`paymentId`, `qrCodeURL` are camelCase).

## Not documented — ask the provider

- SHOP API retry count and interval, your answer timeout, and how many erroneous Complete
  answers lead to manual investigation.
- The Prepare-to-Complete deadline and the accepted `sign_time` age.
- Partial reversal in the current API, and how many reversals one payment allows.
- Whether a reversal makes Click issue a refund receipt for a `submit_items` payment, and
  how a refund receipt is reported for a `submit_qrcode` payment.
- Whose `TIN` / `PINFL` goes into `CommissionInfo`, and whether Click checks the
  `received_*` sum.
- Lifetime of the card token SMS code and of an unpaid `invoice/create`; a cancel method
  for invoices.
- Whether Telegram payments also reach the SHOP API of the same `service_id`, and how they
  are refunded and fiscalized.
- The allowed clock skew for the Merchant API `Auth` timestamp.
