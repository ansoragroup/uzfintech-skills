# Changelog

All notable changes to this project. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

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

[0.2.0]: https://github.com/ansoragroup/uzfintech-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ansoragroup/uzfintech-skills/releases/tag/v0.1.0
