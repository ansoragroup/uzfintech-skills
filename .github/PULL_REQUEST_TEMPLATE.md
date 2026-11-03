## What changed

<!-- One topic per PR. -->

## Source

<!-- Link the vendor page for every changed fact. -->

## Checks

- [ ] `scripts/lint` prints `ok` for every check
- [ ] Examples use placeholders; sandbox data is copied exactly from the vendor
- [ ] No commission rates, payout shares, tariffs or settlement days
- [ ] Lifecycle facts (deadlines, cancel / refund, retries, receipts) are in `references/lifecycle/` and the `SKILL.md` warnings
- [ ] Translations updated, or an issue opened for them
- [ ] Eval run for changed behaviour: `claude plugin eval . --tag <provider>`
