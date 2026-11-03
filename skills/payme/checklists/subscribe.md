# Checklist: Payme Subscribe API

Contract: [`../references/subscribe/README.md`](../references/subscribe/README.md). Also run
[`common.md`](common.md).

## Cards
- [ ] Card entry uses `cards.create` from the front end with `X-Auth: <CASHBOX_ID>` only; `expire` is sent as `MMYY`.
- [ ] Card form inputs have no `name` attribute and the `<form>` has no `action`; the form shows the Payme logo, the offer link and the card-data note.
- [ ] A token is used only after `cards.verify` returns `verify: true`; `cards.get_verify_code` `wait` is respected before resending.
- [ ] Only the token and masked `number` are stored; raw PAN and expiry never reach your server logs or database.
- [ ] `save: true` is used only for recurring or one-click flows; one-time tokens are not reused.
- [ ] `cards.check` and `cards.remove` run from the back end with `id:key`.

## Receipts
- [ ] `receipts.create` sends tiyin `amount`, the cashbox `account` fields and, when fiscalization is needed, `detail`.
- [ ] `receipts.pay` is called with the receipt `_id` and a verified token; the order is fulfilled only at state `4`.
- [ ] Non-final states (`1`, `2`, `3`, `5`, `6`, `20`, `21`, `30`) are polled with `receipts.check` or `receipts.get`, not treated as failure.
- [ ] `receipts.cancel` handles state `21` (queued) until `50` (cancelled).
- [ ] `receipts.get_all` parses a bare array, pages with `count` at most 50, and uses ms `from` / `to`.
- [ ] Receipt parsing accepts `account[].title` and `merchant.type` as a string or a localized object, and `account[].value` as a string or number.

## Hold
- [ ] `hold: true` is set in both `receipts.create` and `receipts.pay`; state `5` is treated as funds blocked, not paid.
- [ ] Holds are confirmed (`receipts.confirm_hold`, state `4`) or cancelled within 30 days; Humo holds older than 30 days can only be confirmed.

## Product rules
- [ ] "Powered by Payme" is shown in the app.
- [ ] Card PIN, if used, follows the vendor recommendation: delete the token after 3 wrong PINs.
