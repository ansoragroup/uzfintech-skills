# Changelog

All notable changes to this project. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-11-04

### Added

- `atmos` skill: Atmos payments for Uzcard / Humo (pay-create, pre-apply, apply,
  multi-payments, full and partial reversals, payment page, HTML widget), card linking,
  holds, withdrawal by PINFL, Visa / Mastercard (MPS / IPS), fiscal `ofd_items` and the
  Callback API, with the published test cards and OTP.
- `octo` skill: Octo acquiring for Visa / Mastercard / UnionPay and Uzcard / Humo, one-stage
  and two-stage payments (`prepare_payment`, `set_accept`), own card form, card tokens, full
  and partial refunds, fiscalization with registered basket items, `notify_url` signatures
  and the `test` flag.
- `oson` skill: Oson invoice API (`invoice/create`, `invoice/status`) and the signed payment
  notification, rebuilt from Oson's open-source shop plugins because Oson publishes no API
  reference, with the gaps listed (no sandbox, no test flag, no refund method).
- `kapitalbank` skill: the Kapital API for legal entities (APILogin, SendPaymentIBK,
  CheckPayments2, statements, account and payee checks, exchange rates, invoices) and the
  CBU payment purpose codes and "Детали платежа" rules for UZS payment orders in any bank.
- `fiscal` skill: provider-neutral fiscal receipt rules (MXIK / IKPU from Tasnif, package
  codes, VAT and benefit fields, Asl Belgisi marking, receipt types) and one table of who
  registers the receipt and in which field at each provider.
- `uzfintech` router skill: choosing a provider for a task, comparing providers, a
  cross-provider cheatsheet (units, auth, callbacks, refunds, holds, fiscalization, test
  hosts) and UzQR notes.
- `sign.py` schemes `atmos.basic`, `atmos.callback`, `octo.notify` and `oson.notify` with
  self-test vectors, 17 schemes in all.
- `skills/kapitalbank/scripts/purpose_codes.py` for offline purpose code lookups and checks,
  and `skills/fiscal/scripts/mxik.py` for MXIK checks with an opt-in Tasnif lookup.
- Eval cases for Atmos, Octo, Oson, Kapitalbank and the fiscal skill, 20 in all.

### Changed

- The Alif skill description mentions Alif Nasiya instalments.
- README, wiki, `AGENTS.md`, `llms.txt` and the plugin descriptions list the new providers
  and the router skill.

## [0.2.0] - 2026-11-03

### Added

- `sign.py` and `validate.py` in every skill: deterministic signature, auth-header and
  payload checks, python3 standard library only. 13 signature schemes with self-test vectors.
- `references/lifecycle/` for every provider: deadlines and time windows, cancel / reverse /
  refund rules, retries and idempotency, fiscal receipt rules, and a "Warn without being
  asked" block with stable IDs inlined in each `SKILL.md`.
- Answering rules in every `SKILL.md`: output per channel, one provider at a time, exact
  names, sandbox data only, no commercial terms, proactive lifecycle warnings.
- Behaviour evals for `claude plugin eval` in `evals/`, including cases that pass only when
  the agent raises a lifecycle warning nobody asked for.
- `scripts/lint`: tools in sync, examples valid against their schemas, Agent Skills
  frontmatter, links, anonymization scan, translations, versions, and every warning ID
  defined on its lifecycle page.
- CI on every PR, and a workflow that publishes `docs/wiki/` to the GitHub wiki.
- A Lifecycle wiki page that compares windows, refunds and receipts across providers.
- README and wiki in English, Russian, Uzbek and Simplified Chinese; `llms.txt`,
  `SECURITY.md`, issue and PR templates.

### Changed

- `SKILL.md` limit raised from 150 to 180 lines to fit the tools and warnings.

### Fixed

- Uzum Merchant API: repeated `/create`, `/confirm` and `/reverse` answer `10010`, `10016`
  and `10018` as the vendor table says; `10012` / `10013` belong to `/create` only.
- Uzum Fiscalization: `price` is the unit price, `operation_id` is new per receipt and reused
  only on a retry, and the 500 retry pauses follow the vendor.
- Uzum Remit Core: `/v1/cancel` is DEBIT only and only from `SUCCESS`.

## [0.1.0] - 2026-11-03

### Added

- Skills for Uzum Bank, Alif, Click, Paynet, Payme and Multicard: contract notes, trimmed
  schemas, anonymized examples, vendor sandbox data and checklists.
- `scripts/sync` and a weekly workflow that tracks upstream specs and pages.
- Claude Code plugin and marketplace manifests.

[0.3.0]: https://github.com/ansoragroup/uzfintech-skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ansoragroup/uzfintech-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ansoragroup/uzfintech-skills/releases/tag/v0.1.0
