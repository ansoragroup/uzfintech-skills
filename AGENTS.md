# AGENTS.md

This repository is a set of agent skills. Codex, Claude Code and other agents can read it
directly.

## Using the skills

- Read the provider's `skills/<provider>/SKILL.md` first: `uzum` (Uzum Bank), `alif`
  (alifpay), `click`, `paynet`, `payme` (Paycom), `multicard`. Follow the pointers in that
  file to `references/<product>/README.md`, `schemas/`, `examples/` and `checklists/`.
- With several providers in one task, work each from its own `SKILL.md`, then compare. Never
  carry units, auth or retry rules from one provider to another.
- Answer contract questions from those files. When a fact is missing, say so and link the
  `Source:` URL. Do not guess.
- Run `skills/<provider>/scripts/sign.py` and `scripts/validate.py` before calling a
  signature, auth header or payload correct, and quote their output. Secrets go in the
  environment variable that `sign.py --list` names, never in arguments.
- When a task creates, confirms, cancels, refunds, retries or fiscalizes a payment, read the
  `SKILL.md` block "Warn without being asked" and `references/lifecycle/README.md`. State the
  deadline, whether the step can be undone and what happens to the fiscal receipt, even when
  nobody asked.
- Use the vendor test data in `references/sandbox/` for tests and examples. Never invent test
  cards or hosts; say so when a provider publishes none.
- Do not state or estimate commission rates, payout shares or settlement terms. They come
  from each merchant's contract.
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
5. Keep deadlines, cancel / refund, retry and fiscal receipt rules in
   `references/lifecycle/README.md`, and the costly ones as stable-ID warnings in `SKILL.md`.
   Never rename a warning ID.
6. Edit the tools only in `scripts/shared/`, then run `scripts/lint --fix`.
7. Run `scripts/lint` before every push. Every check must print `ok`.
8. `scripts/sync`, `scripts/lint` and the tools stay python3 standard library only, 3.9+.
9. Change the English README or wiki page first, then its `ru`, `uz` and `zh-CN` versions.
