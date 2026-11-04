# Checklist: CBU purpose codes and "Детали платежа" (UZS payment orders, every Uzbek bank)

Contract: [`../references/purpose-codes/README.md`](../references/purpose-codes/README.md).
Mark each item pass / fail / n.a. and cite the file and line that proves it.

## Codes
- [ ] No old code is sent from 26.05.2026: hard-coded values, saved templates, seed data and ERP mappings were checked with `scripts/purpose_codes.py check` (`kapitalbank.old-purpose-codes-rejected`).
- [ ] Old codes that map to several new ones (`00513`, `00512`, `00545`, `00525`, `00535`, `00693`, `00532`, `00518`, `00668`) are mapped per goods by a person, not by a one-to-one table (`kapitalbank.one-old-code-many-new`).
- [ ] Codes are stored and compared as 5-character strings; integer values such as MT940 `platPurposeCode` are left-padded before comparison.
- [ ] Budget, treasury, salary and loan payments do not use the commercial table; their codes come from the bank (`kapitalbank.check-budget-account-first`).

## "Детали платежа"
- [ ] The text names the code, the goods, works or services, and the payment type (`kapitalbank.payment-details-content`).
- [ ] When there is a contract, its number **and** date are both in the text (`DD.MM.YYYY`).
- [ ] The goods name is written by you, not copied from the table (some table names contain Latin look-alike letters).
- [ ] `purpose_codes.py details` returns `OK` for a sample of real orders.
- [ ] Whether the bank wants the code repeated inside the text has been confirmed (not documented).
