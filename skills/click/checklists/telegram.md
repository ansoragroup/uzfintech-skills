# Checklist: Click in Telegram bots

Contract: [`../references/telegram/README.md`](../references/telegram/README.md). Mark each
item pass / fail / n.a. and cite the file and line that proves it.

## Setup
- [ ] The `provider_token` comes from config or a secret store; the LIVE one (`:LIVE:`) is
  never committed.
- [ ] Test (@CLICKtest) and live (@CLICKTerminal) tokens are switched by config only.

## Payment flow
- [ ] `sendInvoice` goes only to private chats with users who wrote to the bot.
- [ ] `prices` amounts are integer tiyin for `UZS`.
- [ ] `pre_checkout_query` is answered within 10 seconds, after checking stock and price,
  with a readable `error_message` on `ok=false`.
- [ ] The order is marked paid only on `successful_payment`, matched by `invoice_payload`.
- [ ] `telegram_payment_charge_id` and `provider_payment_charge_id` are stored.
- [ ] The code uses the Bot API names (`answerPreCheckoutQuery`, `successful_payment`).

## Before LIVE
- [ ] The bot owner's account has two-factor authentication.
- [ ] `/terms` and `/support` commands exist.
- [ ] A refund and chargeback process exists.
