# Checklist: Kapital API go-live

Contracts: [`../references/kapital-api/README.md`](../references/kapital-api/README.md),
[`../references/sandbox/README.md`](../references/sandbox/README.md),
[`../references/lifecycle/README.md`](../references/lifecycle/README.md). Also run
[`common.md`](common.md) and the product checklists.

## Access
- [ ] The connection application was handed in at a branch and access was granted for the company's internet-banking login.
- [ ] The host, the paths and the signing method come from the bank's connection instruction and are in configuration (`kapitalbank.host-and-sandbox-not-published`).
- [ ] The login mode is agreed: IP restriction with the production egress IPs registered, or an SMS step that a person handles (`kapitalbank.sms-or-ip-restriction`).
- [ ] The ЭЦП certificate for `signs[]` is installed where the server signs, and its expiry is monitored (`kapitalbank.payment-needs-signature`).

## Written answers from the bank
- [ ] The `amount` unit (`kapitalbank.amount-units-unstated`).
- [ ] Which `CheckPayments2` states are final, and whether a `55` draft needs confirmation in internet banking.
- [ ] How to recall a wrong order, and the `sid` lifetime.
- [ ] Whether a test contour exists; if not, the first live order is a small amount between your own accounts (derived).

## Data
- [ ] Every stored purpose code and template passes `scripts/purpose_codes.py check` (`kapitalbank.old-purpose-codes-rejected`).
- [ ] Status polling and statement fetching run on a schedule, since no webhooks exist (`kapitalbank.poll-status-not-resend`).
