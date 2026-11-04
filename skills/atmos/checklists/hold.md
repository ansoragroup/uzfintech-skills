# Checklist: Atmos Holding

Contract: [`../references/hold/README.md`](../references/hold/README.md). Also run
[`common.md`](common.md).

## Create and confirm
- [ ] `hold/create` sends `store_id`, `account`, `amount` (tiyin), `duration` in **minutes**, and a `card_token` or `card_number` + `card_expiry` (`YYmm`, PCI DSS only).
- [ ] The hold is treated as active only after `PUT /hold/apply/{id}` returns `hold_till`; `otp` is the SMS code, or `111111` with a token.
- [ ] `hold_id` (and `parent_id` for a multiple hold) is stored on the order.

## Capture or release
- [ ] Capture (`POST /hold/{id}`) runs before `hold_till`; `STPIMS-ERR-144` is handled as "too late".
- [ ] A capture `amount` never exceeds the held amount, and `ofd_items` match the captured amount.
- [ ] A lost capture answer leads to `GET /hold/{id}`, never to a second capture.
- [ ] Release sends `DELETE /hold/{id}` with a body that carries `send_cancel_sms`, and the HTTP client really sends that body.
- [ ] `STPIMS-ERR-145` on release is treated as released and confirmed with `GET /hold/{id}`.
- [ ] `hold_till` is parsed with a confirmed time zone, not the server's local one.

## Refund
- [ ] A refund after capture was agreed with Atmos (no documented call); nothing assumes it works.
