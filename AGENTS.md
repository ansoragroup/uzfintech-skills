# AGENTS.md

This repository is a set of agent skills. Codex, Claude Code and other agents can read it
directly.

## Using the skills

- Read the provider's `skills/<provider>/SKILL.md` first: `uzum` (Uzum Bank), `alif`
  (alifpay), `click`, `paynet`, `payme` (Paycom), `multicard`. Follow the pointers in that
  file to `references/<product>/README.md`, `schemas/`, `examples/` and `checklists/`.
- Answer contract questions from those files. When a fact is missing, say so and link the
  `Source:` URL. Do not guess.
- To validate an implementation, walk through the matching checklist and mark each item
  pass, fail or n.a. with a file:line citation.

## Changing this repository

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. The rules that matter most:

1. Do not paste vendor documentation prose verbatim. Write notes in your own words, state
   normative facts, and use trimmed schemas that carry `source_url` and `fetched`.
2. Keep raw downloads in `cache/`, which is git-ignored. Never commit cache contents.
3. Examples use placeholders only. Never use real credentials, merchant or service ids,
   order numbers, phones, card data, names, domains or IPs, and never copy vendor sample
   values into `examples/`.
4. Keep every value the vendor publishes for its sandbox (test hosts, test cards, OTP and
   3-DS codes, test PINFL and phones, scenarios, sample payloads) exactly, in
   `skills/<provider>/references/sandbox/README.md`. Use it for tests and fixtures. Never
   copy pre-filled credentials from vendor Postman collections.
5. Run the anonymization scan in CONTRIBUTING.md before every push.
6. `scripts/sync` must stay python3 standard library only.
