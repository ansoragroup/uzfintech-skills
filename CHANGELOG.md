# Changelog

All notable changes to this project. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `fiscal`: direct OFD integration with your own virtual fiscal module (ВФМ), from the
  ОФД's "Инструкция по интеграции" v6.5. Covers onboarding, the certificate and CMS
  signing, the `test.ofd.uz` endpoints (HTTPS and WebSocket), ReceiptInfo and its
  sub-objects, `ReceiptSeq`, refund, advance and credit receipts, the daily report, reply
  codes with a retry policy, commission sales, the txkm registration API and the `cl-api`
  methods. New warnings `fiscal.ofd-receipt-seq-per-vfm` and `fiscal.ofd-receipt-24h`.

### Changed

- `click`: field notes from a production SHOP API setup. Covers the cabinet's separate
  Prepare and Complete URL fields (branch on `action` and answer `-3` on a mismatch), the
  minimum and maximum amount for each service, and how mobile websites open the CLICK app:
  a same-tab navigation, with the status read again on `pageshow` and `visibilitychange`.
  The checklists gain matching items.

## [0.4.0] - 2026-11-04

### Added

- `tasnif` skill: MXIK (IKPU) catalogue lookups on tasnif.soliq.uz. Tasnif publishes no API
  reference, so the skill describes the public endpoints the site itself calls, as observed
  on the fetch date: search by text and by barcode (GTIN), the code card with package codes,
  history for re-checking stored codes, pictures, class lists, the point-of-sale `cl-api`
  check and the txkm VAT-payer check. Saved replies stand in for a test host, and the
  lifecycle page covers reply shapes, caching and codes that change without notice.
- `skills/tasnif/scripts/tasnif.py`: prints each Tasnif request offline, sends one `GET` only
  with `--online`, summarizes a saved reply with `--file`, and has a `--selftest`.
- Eval case `tasnif-barcode-to-mxik`, 22 in all.
- Three Tasnif entries in `sources.yaml`: the class list, picture names and the
  point-of-sale information reply.

### Changed

- The fiscal MXIK page and the `fiscal` and `uzfintech` skills link to the `tasnif` skill for
  searches, barcodes and re-checks.
- README, wiki, `AGENTS.md`, `llms.txt` and the plugin descriptions list the Tasnif skill.

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
- Eval cases for Atmos, Octo, Oson, Kapitalbank, the fiscal skill and the router, 21 in
  all.

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

[0.4.0]: https://github.com/ansoragroup/uzfintech-skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ansoragroup/uzfintech-skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ansoragroup/uzfintech-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ansoragroup/uzfintech-skills/releases/tag/v0.1.0
