# Checklist: Multicard Cards

Contract: [`../references/cards/README.md`](../references/cards/README.md). Also run
[`common.md`](common.md).

## Hosted bind form
- [ ] `POST /payment/card/bind` sends `store_id`, `redirect_url`, `redirect_decline_url`, and `callback_url` and `phone` (needed for Humo).
- [ ] `session_id` is stored before the redirect; a new link is created after the 15-minute session expires.
- [ ] The bind callback (unsigned) is matched to an issued `session_id` via `payer_id` and confirmed with `GET /payment/card/bind/{session_id}` before the token is saved.
- [ ] The bind callback handler answers HTTP 200 and tolerates repeats every 60 s (5 attempts).

## Bind API (PCI DSS only)
- [ ] add-card, check-pinfl and check-card-by-pan run only on PCI DSS certified systems; otherwise only the hosted form is used.
- [ ] `expiry` is sent as `yymm`; `user_phone` is sent (required for Humo).
- [ ] confirm-card handles `ERROR_WRONG_OTP` (retry), `423` (code expired: restart) and `429` on add-card (wait).

## Card management
- [ ] Only `card_token` and the masked `card_pan` are stored; PAN, expiry, CVC and OTP are never stored or logged.
- [ ] A card is used for payments only in status `active` (and `card_status.code` `0`).
- [ ] `pinfl` ownership checks are applied where required; `check-pinfl` `null` (unknown) is not treated as a match.
- [ ] Removing a card calls `DELETE /payment/card/{card_token}` and removes the token from your vault.
