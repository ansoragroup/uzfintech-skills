# Click in Telegram bots (Telegram Payments with CLICK Terminal)

Hand-written notes. The one example is in [`examples/`](examples/). There is no Click API
here: the bot talks only to the Telegram Bot API, and Click is the payment provider behind
it.

- Source: https://docs.click.uz/en/additional/telegram-payments
- Fetched: 2026-11-03
- Direction: **your bot calls Telegram**, and Telegram calls Click. Your server never sees
  card data.

## Connect

1. Create the bot with @BotFather (`/newbot`). The username must end in `bot`.
2. In @BotFather: `/mybots` → your bot → **Bot Settings → Payments → CLICK Uzbekistan**.
3. Pick the mode:

| Mode | Telegram bot | Login | Token |
|---|---|---|---|
| Test | @CLICKtest | press Start, then Authorize | a test `provider_token` |
| Live | @CLICKTerminal | the merchant cabinet login and password issued by the bank, then pick a `service_id` | a `provider_token` that contains `:LIVE:` |

Start in test mode. Treat the LIVE token as a secret: keep it in your secret store, never in
the repository or the bot's code.

Requirements for LIVE: the merchant is a legal entity or an individual entrepreneur with a
payment-acceptance agreement with one of the banks connected to Click. Fees are set in that
agreement and differ per merchant. The document list varies by bank; ask Click or the bank.

## Flow

```
user writes to the bot
bot ── sendInvoice(chat_id, title, description, payload, provider_token, currency, prices) ──> Telegram
user presses Pay
Telegram ── Update.pre_checkout_query ──> bot
bot ── answerPreCheckoutQuery(ok=true | ok=false + error_message) within 10 s ──> Telegram
Telegram charges through Click
Telegram ── Update.message.successful_payment ──> bot  (mark the order paid here)
```

## Rules

- Invoices go only to users who have written to the bot. They cannot be sent to groups or
  channels.
- One bot may use several `provider_token` values, for example one per `service_id`.
- Answer `pre_checkout_query` within **10 seconds**, or Telegram cancels the payment. Check
  stock and price there; on `ok=false` send a message the user understands.
- Mark the order paid only on `successful_payment`. Match it by the `invoice_payload` you
  set, and store `telegram_payment_charge_id` and `provider_payment_charge_id`.
- Amounts in `prices` are integers in the smallest currency unit, as the Bot API requires
  (tiyin for `UZS`).

## Before going LIVE

- Two-factor authentication on the Telegram account that owns the bot.
- `/terms`: the bot shows terms the user must accept before buying.
- `/support`: the bot tells users how to reach you; Telegram support does not handle these
  purchases.
- Backups of payment data, and a process for refunds and chargebacks; the bot owner bears
  them.

## Gotchas

1. The Click page names the update `success_payment` and the method `answerPrecheckoutQuery`.
   The Bot API names are `successful_payment` and `answerPreCheckoutQuery`.
2. The page does not say whether these payments also reach a SHOP API handler of the same
   `service_id`. Treat `successful_payment` as the bot's proof of payment, and ask Click
   before relying on Prepare / Complete for them.
3. The test and live tokens differ. Switching to LIVE means replacing the token in config,
   not changing code.
4. `pre_checkout_query` is your last chance to refuse. After `ok=true`, a failure on your
   side means a refund.

## Examples

- [`send-invoice.request.json`](examples/send-invoice.request.json): a `sendInvoice` body
  with a placeholder `provider_token`.
