# Checklist: Atmos Withdrawal by PINFL

Contract: [`../references/pinfl/README.md`](../references/pinfl/README.md). Also run
[`common.md`](common.md).

## Before a debit
- [ ] A signed contract with the person exists and its number is sent as `contract_number`; proof of consent is kept.
- [ ] `pinfl` is validated as 14 digits; `passport_series`, `passport_number` and the full name match the contract.
- [ ] `ext_id` is generated once per debit, stored before the call and never reused.

## Create, confirm, cancel
- [ ] `create` answers are read on `code` `"200"` (string or number) and negative codes; `available_balance` is not logged or stored.
- [ ] Money is treated as moved only after `confirm` returns `SUCCESS`; the taken amount is the sum of `details[].amount`.
- [ ] `cancel` is used only before `confirm`.
- [ ] A lost `create` or `confirm` answer leads to `check` with the same `ext_id`, never to a new `ext_id`.
- [ ] `partial_debit: true` is sent only when the contract allows a partial debit.
- [ ] `ofd_items` and `epos`, when sent, carry every inner field.

## Errors
- [ ] `-302` (ext_id used) leads to `check`; `-109` leads to `update-cards-list` → `cards/check/{ext_id}` → a new transaction; `-103` is not retried.
- [ ] `update-cards-list` use was agreed with Atmos.
- [ ] `details[]` card masks are shown only to the cardholder.
