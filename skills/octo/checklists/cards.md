# Checklist: Octo card tokenization

Contract: [`../references/cards/README.md`](../references/cards/README.md). Also run
[`common.md`](common.md) and [`partner-page.md`](partner-page.md) (paying with a token).

## Bind
- [ ] Tokenization is enabled for the shop, and the shop may receive card data (the bind call and its callback carry the full PAN).
- [ ] `bind_card` sends `shop_transaction_id`, `pan`, `exp` (YYMM), `phone`, `method`, `return_url` and a public HTTPS `bind_notify_url` on every call.
- [ ] Uzcard / Humo binds confirm the OTP with `POST /bind_card/check_sms_key` (`smsKey`, `paymentUUID`, `verifyId`); the reply is not expected to carry a token.
- [ ] `error: 20` reuses the stored token instead of binding again.
- [ ] The payer is told that a small verification debit is made and refunded.

## Bind callback
- [ ] `shop_transaction_id` is matched to a binding you started; unknown ids get an error answer.
- [ ] The token is stored first, then the handler answers HTTP `200`; repeats get the same answer (`octo.bind-callback-ack`).
- [ ] Only `active` tokens are offered for payment; `failed` ends the binding.
- [ ] The raw `pan` and `exp` from the body are never logged; only `card_token`, the masked number and the needed expiry are stored.

## Use and remove
- [ ] Token purchases call `prepare_payment`, then `POST /pay/{uuid}` with `card_token` and `method`.
- [ ] Removing a card calls `block_card_token`; codes `5` and `6` update your token record instead of failing.
