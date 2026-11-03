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

## When a rule is not published

Each lifecycle page ends with "Not documented — ask the provider". When the docs do not set
a deadline (for example, Click sets no Prepare-to-Complete limit), the agent says so and
suggests asking the provider rather than inventing a number.
