# Checklist: Atmos Card linking

Contract: [`../references/cards/README.md`](../references/cards/README.md). Also run
[`common.md`](common.md).

## Link
- [ ] `bind-card/init` runs only on PCI DSS certified systems (full PAN and expiry pass through your server).
- [ ] `expiry` is sent as `YYmm`; `card_number` is 16 digits.
- [ ] `bind-card/confirm` sends the `transaction_id` from init and the SMS code; `STPIMS-ERR-098` lets the cardholder retry.
- [ ] The masked `phone` from init is shown so the cardholder knows where the code went.

## Store and use
- [ ] Only `card_id`, `card_token`, the masked `pan` and `expiry` are stored, mapped to your own customer id.
- [ ] `balance`, `card_holder` and the full PAN are not logged or stored (derived).
- [ ] `list-cards` is used only for reconciliation; customers see only their own cards from your mapping.
- [ ] Charges with the token go through `pay/create` → `pay/pre-apply {card_token}` → `pay/apply {otp: "111111"}`.

## Remove
- [ ] `remove-card` sends both `id` (`card_id`) and `token` (`card_token`), and the mapping is deleted in the same step.
- [ ] Charge errors on a saved card (blocked, expired) prompt the customer to link the card again.
