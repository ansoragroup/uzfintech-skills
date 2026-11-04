# Checklist: Kapital API payment orders (SendPaymentIBK, CheckPayments2)

Contracts: [`../references/kapital-api/README.md`](../references/kapital-api/README.md),
[`../references/purpose-codes/README.md`](../references/purpose-codes/README.md). Also run
[`common.md`](common.md) and [`purpose-codes.md`](purpose-codes.md).

## Before the call
- [ ] Each order gets a new `uniq` (and `num`) that is stored with the order **before** `SendPaymentIBK` is called and is never reused (`kapitalbank.unique-doc-number`).
- [ ] `purp_code` is a **new** code accepted today by `scripts/purpose_codes.py check` (`kapitalbank.old-purpose-codes-rejected`).
- [ ] `purpose` holds the code, the contract number and date (when there is one), the goods, works or services, and the payment type, built with `purpose_codes.py details` (`kapitalbank.payment-details-content`).
- [ ] Budget and treasury payees are checked first with `GetBudjetAcc` or `GetNalogAcc`, and their codes come from the bank, not from the commercial table (`kapitalbank.check-budget-account-first`).
- [ ] MFOs are 5 digits and accounts 20 digits (`purpose_codes.py account`); the vendor sample's 19-digit `acc_dt` is not copied.
- [ ] The `amount` unit has been confirmed with the bank in writing; the code does not assume sum or tiyin (`kapitalbank.amount-units-unstated`).
- [ ] `anor` is chosen on purpose: `0` СЭП (9:00–17:00, open-balance days) or `1` Anor (24/7); `GetOperDays` is checked for `anor: 0` (`kapitalbank.oper-day-dating`).
- [ ] `signs[]` carries the ЭЦП made as the bank's connection instruction prescribes; the vendor `"string"` values are not sent (`kapitalbank.payment-needs-signature`).

## After the call
- [ ] Success is judged from `error`, not from `result`; the order is then read back with `CheckPayments2` by `uniq`.
- [ ] A timeout or lost reply leads to `CheckPayments2` by `uniq`; a new order is sent only when the first is not found (`kapitalbank.poll-status-not-resend`).
- [ ] Status polling batches at most 100 `uniqs` or `general_ids` per call and backs off.
- [ ] States `55` (draft), `53`, `54`, `56` are stored with `state_name`, `err` and `err_msg`; nothing is treated as final until the bank confirms which states are final.
- [ ] At `54`, `branch` and `general_id` are stored; a missing `uniq` after a deleted draft is handled.
- [ ] The text the bank stored in `purpose` is read back from `GetDoc1C` (the bank may clean and complete it).
- [ ] There is no recall method in the API; the runbook says how to stop a wrong order through the bank.
