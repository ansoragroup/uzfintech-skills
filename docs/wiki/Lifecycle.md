# Lifecycle

**English** · [Русский](Lifecycle.ru.md) · [Oʻzbekcha](Lifecycle.uz.md) · [简体中文](Lifecycle.zh-CN.md)

Most costly payment bugs are not about a wrong field. They come from a step that runs too
late or twice: a refund attempted after its window has closed, a receipt sent after its
deadline, a webhook that fails during a deploy and quietly refunds the payer. This page
gathers those rules for every provider in one place.

Each skill keeps the full rules in `references/lifecycle/README.md`, and its `SKILL.md` lists
the costly ones under "Warn without being asked". An agent that loads the skill raises these
warnings on its own whenever a task creates, confirms, cancels, refunds, retries or
fiscalizes a payment.

## At a glance

| Provider | Windows that bite | Undoing a payment | Fiscal receipt |
|---|---|---|---|
| [Uzum Bank](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzum/references/lifecycle/README.md) | Fiscalization `date_time` within **24 h** after the confirmed payment, else 422. A Merchant API `CREATED` transaction older than 30 min counts as failed. | Merchant API: no outbound refund call, Uzum calls your `/reverse` for the whole amount. Checkout: TWO_STEP `reverse` before `complete`, otherwise `refund` up to `completedAmount` minus `refundedAmount`. ONE_STEP cannot be reversed (`3036`). | You fiscalize, except Checkout with auto-fiscalization on (ONE_STEP only, enabled by the manager). A refund receipt needs the sale already fiscalized. |
| [Alif](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/references/lifecycle/README.md) | Webhook retries for about **1 h**; with no HTTP 200 the payment is cancelled and refunded. Holds end after **10 days** (Humo) or **30 days** (Uzcard). | `refundPayment` and `refundInvoice` return the whole amount; partial refunds exist only for instalments. Errors also arrive as HTTP 200, so only `SUCCEEDED` means paid. | Alif registers it when you send `receipt` with `spic`. A refund receipt is registered only when a sale receipt exists. |
| [Click](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/references/lifecycle/README.md) | `payment/reversal` works in the **current reporting month**, and for last month's payments only on the **1st** of the next month. CLICK Pass confirm within **30 s**. | Reversal is full only, and UZCARD may still reject it. Plan another refund path. | Click fiscalizes from `submit_items`, or you send your own receipt link with `submit_qrcode`, one or the other. No refund-receipt call exists. |
| [Paynet](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/references/lifecycle/README.md) | `reverse` only within **1 month** of the payment. OTP lifetime comes from `ttlSeconds`. | `reverse`, then poll `status` (`CANCEL_PENDING` is not final). Lock the button against a second click. | Who registers the receipt is not published. Ask Paynet at onboarding. |
| [Payme](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/references/lifecycle/README.md) | A state `1` transaction is cancelled after **12 h** (43 200 000 ms, reason `4`). Holds: **30 days**. | A refund is a full `CancelTransaction` on a performed transaction (state `-2`, reason `5`). Answer `-31007` to refuse. | Payme fiscalizes from `detail` and sends `SetFiscalData` `PERFORM` / `CANCEL`. Store them as separate receipts and never register a second one yourself. |
| [Multicard](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/references/lifecycle/README.md) | Hold `expiry` in **minutes** (up to 30 days). Invoice `ttl` in seconds (default 1 day). Auth token lives **24 h**. | Full refunds; partial ones only when Multicard enables them on the terminal, and they fiscalize a new receipt. Payouts cannot be undone. | `tax_registration` on the store decides: `1` Multicard fiscalizes, `0` you do. |
| [Atmos](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/atmos/references/lifecycle/README.md) | Hold `duration` in **minutes**; capture before `hold_till` or get `STPIMS-ERR-144`. Bearer token lives **3600 s**. The billing callback must answer HTTP 200 `{"status": 1}`, or there is no debit. | `pay/reverse` takes the `success_trans_id`, not the draft `transaction_id`. A partial refund is `create-reverse-partial`, then `confirm-reverse-partial` with `ofd_items`. A PINFL debit can be cancelled only before `confirm`. No refund is documented for an MPS payment without a hold. | Send `ofd_items` with the IKPU; Atmos returns `ofd_url`, so it registers the receipt (derived). A refund receipt for a full reversal is not described. |
| [Octo](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/octo/references/lifecycle/README.md) | Two-stage hold: `set_accept` within **30 min** by the two-stage pages (the cancel page says up to 30 days Humo / Uzcard, 7 days Visa / Mastercard), or Octo cancels it. An unpaid payment ends after `ttl` minutes. Three wrong OTPs cancel the payment. | `set_accept` `cancel` works only on a hold. A `succeeded` payment goes back through `/refund`, full or partial, at least 1 USD equivalent and at most 10 mln UZS per call. | Octo registers it from `basket` items that your bank manager registered first, else `error: 403`; read it with `fiscal-data`. Return receipts are not described. |
| [Oson](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/oson/references/lifecycle/README.md) | Invoice `lifetime` unit is not documented (plugins send `30` or `14400`); after it the status is `EXPIRED`. | No cancel or refund method in any plugin; refunds go through the Oson cabinet or support. | No plugin sends receipt fields, and who registers the receipt is not documented. Register it yourself until Oson confirms. |
| [Kapitalbank](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/kapitalbank/references/lifecycle/README.md) | Old purpose codes are refused from **26.05.2026** (new codes in force from 06.05.2026). `anor: 0` (СЭП) runs 9:00–17:00 on open days, `anor: 1` (Anor) 24/7. A `fin: 0` statement is not final. | No recall method is published; ask the bank. A resent `SendPaymentIBK` is a second real order. | Not applicable: payment orders between legal entities are bank transfers. |

The [`fiscal`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/fiscal/references/lifecycle/README.md) skill compares receipt rules across
providers. Only Uzum Fiscalization publishes a deadline (24 h); Payme, Alif, Multicard,
Octo and Atmos publish none, so register right after the payment is confirmed.

## The warnings that cost the most

| ID | When it applies | What goes wrong |
|---|---|---|
| `uzum.fiscal-receipt-24h` | receipts sent from a queue, batch or retry loop | 422 "date_time should be within 24 hours"; a nightly batch is already too late for some payments |
| `uzum.merchant-lost-confirm` | `/confirm` and `/status` handlers | Uzum polls `/status` after a lost confirm and does not resend it; commit before you answer |
| `alif.webhook-1h-auto-refund` | webhook handlers, downtime, deploys | an hour without HTTP 200 cancels the payment and returns the money |
| `click.reversal-month-window` | refund features | after the 1st of the next month the reversal is no longer possible |
| `click.complete-after-debit` | Complete handlers | the payer is already debited; answer success (errors only `-4` / `-9`) and reverse if you cannot deliver |
| `paynet.reverse-1-month` | refund or cancel buttons | after one month `reverse` is impossible |
| `payme.create-timeout-12h` | order reservation, Create / Perform | Create or Perform after 12 h must get `-31008`; the order must be released |
| `payme.cancel-is-the-refund` | refund features | there is no amount parameter, so a refund is always the full payment |
| `multicard.callback-reject-refunds` | `callback_url` handlers | any answer other than HTTP 200 `{"success": true}` cancels and refunds the payment |
| `multicard.payout-irreversible` | payouts | no cancel or reversal endpoint exists |
| `atmos.callback-ack` | billing URL handlers | any answer other than HTTP 200 `{"status": 1}` means no debit |
| `atmos.apply-no-resend` | `pay/apply`, hold capture and confirm calls after a timeout or 5xx | a second money call; read the state with `pay/get` or `GET /hold/{id}` instead |
| `atmos.reverse-success-id` | refund features | `pay/reverse` with the draft `transaction_id` instead of `success_trans_id` |
| `octo.test-flag-real-money` | non-production environments | without `test: true` the payment on `secure.octo.uz` is real |
| `octo.hold-auto-cancel` | two-stage payments | no `set_accept` before the hold expires; Octo cancels it and the payer gets the money back |
| `oson.verify-notify-signature` | notification handlers | an unchecked signature lets a forged `PAID` through |
| `oson.no-refund-api` | refund features | no cancel or refund method; refunds go through the cabinet or support |
| `kapitalbank.old-purpose-codes-rejected` | UZS payment orders in any bank | an old purpose code after 26.05.2026 gets the order refused or delayed |
| `kapitalbank.poll-status-not-resend` | lost or unclear `SendPaymentIBK` answers | a resend creates a second real order |
| `fiscal.one-receipt-per-payment` | providers that register the receipt themselves | a second receipt for the same sale on your own fiscal module |

Every ID is defined on its provider's lifecycle page, and `scripts/lint` fails when a page,
a `SKILL.md` or this wiki mentions an ID that is not defined. IDs are never renamed or
translated.

## Retries and idempotency

The rules differ by provider, so never carry them across:

- **Uzum Merchant API:** a repeated `/create` gets `10010`, a repeated `/confirm` gets
  `10016`, a repeated `/reverse` gets `10018`. After a lost `/confirm`, Uzum polls `/status`.
- **Uzum Checkout:** `X-Operation-Id` is unique per operation. Persist it before the call; on
  `3028` read `getOperationState` instead of sending a new id.
- **Payme:** Create and Perform are repeated with the same params, and the sandbox sends each
  method twice. Return the stored answer for the same Payme `id`.
- **Click:** Prepare and Complete may come again for the same `click_trans_id`; answer the
  same way.
- **Multicard:** never resend a money call after a timeout, 5xx or `ERROR_DEBIT_UNKNOWN`. Poll
  the payment instead.
- **Paynet:** a retryable error means "check `status`", not "send again".
- **Atmos:** never resend `pay/apply`, a hold capture, an MPS apply or a PINFL confirm after a
  timeout, 5xx, `STPIMS-ERR-118`, `STPIMS-ERR-065` or `INFO-202`. Read `pay/get`,
  `GET /hold/{id}`, `get/ext_id` or `check` instead.
- **Octo:** `shop_transaction_id` and `shop_refund_id` are unique per attempt and stored
  before the call. After a lost reply, check the status with the three-field
  `prepare_payment` call.
- **Oson:** use a fresh `transaction_id` per attempt. After a lost reply, call
  `invoice/status` with the same id before creating a new invoice.
- **Kapitalbank:** store `uniq` before `SendPaymentIBK`. After a lost reply, ask
  `CheckPayments2` by `uniq` and resend only when the order is not found. There are no
  webhooks, so poll.

## When a rule is not published

Each lifecycle page ends with "Not documented — ask the provider". When the docs do not set
a deadline (for example, Click sets no Prepare-to-Complete limit), the agent says so and
suggests asking the provider rather than inventing a number.
