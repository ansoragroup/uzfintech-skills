# Checklist: Kapital API statements and accounts (GetDoc1C, GetMT940, GetAcc1C, GetAccounts)

Contract: [`../references/kapital-api/README.md`](../references/kapital-api/README.md). Also
run [`common.md`](common.md).

## Statements
- [ ] `GetDoc1C` sends `sid`, `branch` and `account`; the `date` format has been confirmed with the bank (the sample sends `"2026-03-04"`, other pages use `dd.MM.yyyy`).
- [ ] A statement with `fin: 0` is treated as incomplete and fetched again after the day closes (`kapitalbank.oper-day-dating`).
- [ ] Entries are de-duplicated across repeated fetches by document id and number.
- [ ] `dir` is read as `1` incoming, `2` outgoing; the document `state` uses the GetDoc1C mapping, not the CheckPayments2 one.
- [ ] Incoming payments are matched on `purpose`, amount and payer, not on `purp_code` alone (it may be `null`).
- [ ] `GetMT940` parsing accepts the text with real line breaks and with the escaped `\\n` of the sample, and also the sub-field shape.

## Accounts
- [ ] `GetAcc1C` / `GetAccounts` send a 5-character `branch` and a 20-digit `account`.
- [ ] `val` and account `state` are parsed as free values (the sample prints `"000"` and `2`).
- [ ] The amount unit of balances and turnovers has been confirmed with the bank (`kapitalbank.amount-units-unstated`).
