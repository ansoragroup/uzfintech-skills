# Checklist: Click Advanced Shop and Split Shop

Contracts: [`../references/common/README.md`](../references/common/README.md) and
[`../references/advanced-shop/README.md`](../references/advanced-shop/README.md). Mark each
item pass / fail / n.a. and cite the file and line that proves it.

## Setup
- [ ] Click has confirmed which protocol (SHOP API, Advanced or Split) the `service_id` uses.
- [ ] The handler branches on `action` with **Advanced** numbering: 0 getinfo, 1 prepare,
  2 confirm, 3 check, 4 compare.

## Signature
- [ ] JSON is parsed with an order-preserving map, and `params` values are concatenated in
  body order, as received.
- [ ] The string is `click_paydoc_id + attempt_trans_id + service_id + SECRET_KEY + <params values> + action + sign_time`.
- [ ] prepare, confirm and check reject a bad signature with `-1`.

## Actions
- [ ] getinfo returns the details to show in `params`, or `-5` when nothing matches.
- [ ] prepare validates `params` (including `amount`) and returns `merchant_prepare_id`.
- [ ] Split prepare returns `split` items whose `amount`s add up to the payment amount, and
  the item field names are confirmed with Click.
- [ ] confirm records the payment once, keyed on `click_paydoc_id`, across attempts.
- [ ] `merchant_prepare_id` is accepted as a string (Advanced) or a bigint (Split).
- [ ] A negative incoming `error`, if present, cancels and returns `-9`.
- [ ] check returns `status` 0 only while still processing, 1 for failed, 2 for done.
- [ ] compare returns every payment in `from_date`..`till_date`, keyed by `click_paydoc_id`.

## Idempotency
- [ ] Repeated requests with the same `(click_paydoc_id, attempt_trans_id)` give the same answer.
- [ ] A new `attempt_trans_id` for a known `click_paydoc_id` does not book a second payment.
