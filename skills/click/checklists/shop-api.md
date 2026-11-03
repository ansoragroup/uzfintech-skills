# Checklist: Click SHOP API (Prepare / Complete)

Contracts: [`../references/common/README.md`](../references/common/README.md) and
[`../references/shop-api/README.md`](../references/shop-api/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] Both endpoints accept `POST` with `application/x-www-form-urlencoded` over HTTPS.
- [ ] Every answer is JSON with `error` (int) and `error_note`, sent with HTTP 200.
- [ ] Prepare answers carry `click_trans_id`, `merchant_trans_id`, `merchant_prepare_id`;
  Complete answers carry `merchant_confirm_id` instead.
- [ ] `merchant_prepare_id` and `merchant_confirm_id` are integers.

## Prepare (action = 0)
- [ ] Checks run in order: signature (`-1`), action (`-3`), order exists (`-5`), amount
  (`-2`), already paid (`-4`) or cancelled (`-9`).
- [ ] The signature uses `click_trans_id + service_id + SECRET_KEY + merchant_trans_id + amount + action + sign_time`.
- [ ] The amount is compared in tiyin after parsing the raw string.
- [ ] The attempt is stored and the goods are reserved before `error: 0` is returned.
- [ ] `click_trans_id` and `click_paydoc_id` are stored with the attempt.
- [ ] A repeated Prepare for the same `click_trans_id` returns the same `merchant_prepare_id`.

## Complete (action = 1)
- [ ] The signature includes `merchant_prepare_id` between `merchant_trans_id` and `amount`.
- [ ] An unknown `merchant_prepare_id` returns `-6`.
- [ ] An incoming `error < 0` cancels the attempt, releases the reservation and returns `-9`,
  even after an earlier success (Postman scenario 8).
- [ ] `error = 0` marks the order paid once and returns `merchant_confirm_id`.
- [ ] A repeated Complete for a paid attempt returns `-4`; for a cancelled one `-9`.
- [ ] After a successful Prepare, Complete never returns another error; a failed delivery is
  refunded with `payment/reversal` instead.

## Operations
- [ ] Reservations without a Complete are released by your own timeout.
- [ ] All 15 Postman generator scenarios pass with a test amount other than 300.
- [ ] The Playground works against the endpoint (CORS allows docs.click.uz) or is not used.
