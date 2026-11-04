# uzfintech-skills

**English** · [Русский](README.ru.md) · [Oʻzbekcha](README.uz.md) · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-10%20providers-0a7c66.svg)](#providers)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757.svg)](#install)
[![Python 3.9+ stdlib](https://img.shields.io/badge/tools-python3%20stdlib-3776ab.svg)](#tools)

Agent skills for Uzbek payment provider APIs: **Uzum Bank, Alif, Click, Paynet, Payme,
Multicard, Atmos, Octo, Oson and Kapitalbank**, plus a fiscal receipt skill shared by all of
them and a router skill for choosing and comparing providers. They work in Claude Code,
Codex, Cursor and any other agent that reads `SKILL.md` files.

Models know these APIs only roughly. They mix up tiyin and sum, sign the wrong string and
invent error codes or sandbox cards. With these skills the agent answers from exact contract
notes and checks signatures and payloads with scripts instead of guessing. Each skill covers:

- endpoints, auth headers, signatures, units and state machines;
- trimmed JSON Schemas, error codes, idempotency and retry rules;
- anonymized request and response examples;
- vendor sandbox data, kept exactly: test hosts, test cards, OTP codes, scenarios;
- implementation checklists for reviewing an integration;
- `sign.py` and `validate.py`, two deterministic tools with no dependencies.

## Providers

| Skill | Provider | Products |
|---|---|---|
| [`uzum`](skills/uzum/SKILL.md) | Uzum Bank | Merchant API (webhooks), Checkout, Fiscalization, FastPay, Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Nasiya, PaymentHub |
| [`alif`](skills/alif/SKILL.md) | Alif (alifpay) | Checkout, Alif Nasiya instalments, Payments, Cards, Hold, Monitoring, Summary, legacy API migration map |
| [`click`](skills/click/SKILL.md) | Click | SHOP API, Advanced / Split Shop, Merchant API, card tokens, Fiscalization, CLICK Pass, payment link / button / widget, Telegram Payments |
| [`paynet`](skills/paynet/SKILL.md) | Paynet | Internet acquiring (Humo / Uzcard): authorize, confirm, status, reverse |
| [`payme`](skills/payme/SKILL.md) | Payme (Paycom) | Merchant API, Subscribe API (cards, receipts, holds), Checkout (GET / POST / button / QR), Fiscalization |
| [`multicard`](skills/multicard/SKILL.md) | Multicard | Invoices and scanpay, card binding, payments (token / card / app / split), refunds, holds, payouts, reports |
| [`atmos`](skills/atmos/SKILL.md) | Atmos | Payments (Uzcard / Humo: pay-create / pre-apply / apply, multi-payments, full and partial reversals, payment page, HTML widget), card linking, holds, withdrawal by PINFL, Visa / Mastercard (MPS / IPS), Callback API |
| [`octo`](skills/octo/SKILL.md) | Octo | Visa / Mastercard / UnionPay and Uzcard / Humo acquiring: payment page (one-stage / two-stage), own card form (PCI DSS), card tokens, full and partial refunds, fiscalization (basket, fiscal-data) |
| [`oson`](skills/oson/SKILL.md) | Oson | Invoice API (invoice/create with a pay_url, invoice/status) and the signed payment notification, rebuilt from Oson's open-source shop plugins |
| [`kapitalbank`](skills/kapitalbank/SKILL.md) | Kapitalbank | Kapital API for legal entities: APILogin, SendPaymentIBK payment orders, CheckPayments2, statements (GetDoc1C, GetMT940), account and payee checks, exchange rates, invoices; CBU payment purpose codes for UZS payment orders in any bank |
| [`fiscal`](skills/fiscal/SKILL.md) | All providers | Fiscal receipts: MXIK (IKPU) codes from Tasnif, package codes, VAT and benefit fields, Asl Belgisi marking, receipt types, who registers the receipt and in which field at each provider |
| [`uzfintech`](skills/uzfintech/SKILL.md) | All providers | Router: choose a provider for a task, compare providers, cross-provider cheatsheet (units, auth, callbacks, refunds, holds, fiscalization, test hosts), UzQR notes |

Start with `uzfintech` when the task is to choose or compare providers. It points to the
provider skill that holds the contract.

## Install

### Any agent: the `skills` CLI

```sh
npx skills add ansoragroup/uzfintech-skills
```

The [`skills`](https://github.com/vercel-labs/skills) CLI asks which agents to install to
(Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot and others) and whether to install
globally or for one project. Add `--skill payme` to install a single provider.

### Claude Code: plugin

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

Update with `/plugin marketplace update uzfintech-skills`. The plugin namespaces the skills
as `uzfintech:payme`, `uzfintech:click` and so on.

### Manual copy

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
cp -R uzfintech-skills/skills/* ~/.claude/skills/    # Claude Code, all projects
cp -R uzfintech-skills/skills/* ~/.codex/skills/     # Codex
```

For one project only, copy into `<project>/.claude/skills/` instead.

### Agents without skill support: AGENTS.md

Vendor the repository (for example as a git submodule at `vendor/uzfintech-skills`) and add
this to your project's `AGENTS.md`:

```md
## Payment provider contracts
For Uzbek payment provider work (Uzum Bank, Alif, Click, Paynet, Payme, Multicard, Atmos,
Octo, Oson, Kapitalbank), read `vendor/uzfintech-skills/skills/<provider>/SKILL.md` first and
follow its pointers. To choose or compare providers, start with
`vendor/uzfintech-skills/skills/uzfintech/SKILL.md`. Run its
`scripts/sign.py` and `scripts/validate.py` instead of computing signatures by hand, and
review changes against the matching `checklists/*.md`.
```

The [Install wiki page](docs/wiki/Install.md) covers updates, pinning a version and
troubleshooting.

## How it works

Each skill is split into a router and workers: a small router decides where to go, and the
work happens in focused places with only the context they need.

```
             your question
                   │
     ┌─────────────▼─────────────┐   ~140 lines, loaded when the description matches:
     │  skills/<provider>/       │   products, decision table, gotchas,
     │  SKILL.md   (router)      │   answering rules, tool commands
     └──────┬────────────┬───────┘
  slow path │            │ fast path
  (reading) │            │ (deterministic)
     ┌──────▼──────┐  ┌──▼───────────────────┐
     │ references/ │  │ scripts/sign.py      │  exact signed string, MATCH / MISMATCH
     │ checklists/ │  │ scripts/validate.py  │  OK / INVALID with JSON paths
     └─────────────┘  └──────────────────────┘
```

- **One provider per skill.** A multi-provider task loads each skill on its own and compares
  afterwards. A rule such as units, auth or retries never carries over from one provider to
  another. The `uzfintech` router helps choose and compare, then hands over to the provider
  skill. Receipt codes that every provider shares (MXIK, package codes, marking) live in the
  `fiscal` skill.
- **Fast path first.** Signatures, auth headers, checkout URLs and payload shapes are
  computed by code, never by the model. The agent runs the tool and quotes its output.
- **Inline and spill.** `SKILL.md` inlines only what is needed on every task. Contracts,
  schemas, examples, sandbox data and checklists stay in files that the agent reads on
  demand.
- **Stable IDs.** Signature schemes (`payme.basic`, `click.prepare`), schema names
  (`uzum/webhook-confirm`) and error codes are the same in every language and are never
  translated.
- **Output for the channel.** In chat the agent gives the conclusion first, in about 100
  words. In a PR or review it writes Problem, Change, Validation. It replies in your
  language but keeps API names as they are.
- **Warn without being asked.** Payment bugs hide in time windows and irreversible steps.
  Whenever a task creates, confirms, cancels, refunds, retries or fiscalizes a payment, the
  agent states the deadline, whether the step can be undone and what happens to the fiscal
  receipt, even if you did not ask. See [Lifecycle warnings](#lifecycle-warnings).

## Lifecycle warnings

Every skill has `references/lifecycle/README.md` with each provider's deadlines and time
windows, cancel / reverse / refund rules, retry and idempotency rules, hold and OTP lifetimes,
and fiscal receipt rules. The costly ones are inlined in `SKILL.md` under "Warn without being
asked", each with a stable ID. For example, `uzum.fiscal-receipt-24h`: an Uzum fiscal receipt
must carry a `date_time` within 24 hours of the payment, so a refund receipt cannot simply be
sent the next week.

The [Lifecycle wiki page](docs/wiki/Lifecycle.md) collects all of them in one table.

## Tools

Every skill ships `scripts/sign.py` and `scripts/validate.py`. They need only `python3`
(3.9+) and the standard library. Secrets come from environment variables and are printed
as `<SECRET>`.

```console
$ python3 skills/click/scripts/sign.py --list
click.prepare       SHOP API Prepare sign_string = md5(...)
                    fields: click_trans_id service_id merchant_trans_id amount action sign_time; secret: CLICK_SECRET_KEY
click.complete      SHOP API Complete sign_string = md5(...)
                    fields: click_trans_id service_id merchant_trans_id merchant_prepare_id amount action sign_time; secret: CLICK_SECRET_KEY
click.advanced      Advanced / Split Shop sign_string = md5(..., params values in body order, ...)
                    fields: click_paydoc_id attempt_trans_id service_id params action sign_time; secret: CLICK_SECRET_KEY
click.auth          Merchant API Auth: merchant_user_id:sha1(ts+secret):ts, ts in seconds
                    fields: merchant_user_id [timestamp]; secret: CLICK_SECRET_KEY

$ CLICK_SECRET_KEY=test-secret python3 skills/click/scripts/sign.py click.prepare body.txt \
    --expect d7696dbc2b950daf03e1191fbea5fbb3
input   12345100<SECRET>100011000.002026-11-03 10:00:00
value   24d6c366acd79c05457ddf0547d6d65c
MISMATCH, received d7696dbc2b950daf03e1191fbea5fbb3
```

The `input` line shows the bug. Click sent `amount=1000.00` and signed that string. Our
handler parsed the amount as a number and rebuilt it as `1000.0`, so `body.txt` no longer
holds what Click signed. Sign the raw values exactly as they arrived.

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string
```

`validate.py` unwraps JSON-RPC and `{success, data}` envelopes, reads form-urlencoded
bodies and skips `<PLACEHOLDER>` values. Both tools exit `0` on success, `1` on a mismatch
and `2` on a usage error, so you can use them in CI. See the
[Tools wiki page](docs/wiki/Tools.md) for every scheme.

Two skills add an offline tool of their own: `skills/kapitalbank/scripts/purpose_codes.py`
looks up and checks CBU payment purpose codes, and `skills/fiscal/scripts/mxik.py` checks
MXIK codes, with an opt-in Tasnif lookup.

## Try it

- "Click says our Prepare `sign_string` is wrong. Here is the request body."
- "Implement Payme Merchant API `CreateTransaction` with its `-31008` / `-31050` errors."
- "What does Uzum Merchant `/confirm` send, and what do I answer on a retry?"
- "Verify an Alif webhook signature in Go."
- "Which test cards and OTP codes does the Uzum Checkout sandbox use?"
- "Review our Multicard integration against the checklist."
- "Which providers can hold funds and capture later? Compare Atmos and Octo."
- "Our payment order still uses purpose code 00545. What replaces it?"
- "Payme sandboxida qaysi test kartalardan foydalanish mumkin?"

## Quality

| Check | Command | What it proves |
|---|---|---|
| Repository lint | `scripts/lint` | tools in sync and self-tested, every example valid against its schema, frontmatter within the spec, no broken links, anonymization scan, translations present, versions consistent, every warning ID defined on its lifecycle page |
| Parser self-test | `scripts/sync --selftest` | the bundled YAML parser agrees with PyYAML |
| Behaviour evals | `claude plugin eval . --runs 3` | an agent with the skill loads the right provider, quotes exact codes, runs the tools and refuses to invent sandbox data or commercial terms |

The 21 eval cases are in [`evals/`](evals/README.md). CI runs the lint on every PR.

## Freshness

Every reference carries its source URL and fetched date. Once a week,
`.github/workflows/sync.yml` runs `scripts/sync`, regenerates the OpenAPI-derived files and
opens a PR when an upstream spec or docs page changes. A person re-reads the flagged pages
before merging.

```sh
scripts/sync --check            # report only; exit 1 when upstream changed
scripts/sync                    # regenerate derived files, update sources.yaml
```

## Documentation

The [wiki](docs/wiki/Home.md) has the full guides:
[Install](docs/wiki/Install.md) · [Tools](docs/wiki/Tools.md) ·
[Agent guide](docs/wiki/Agent-guide.md) · [Lifecycle](docs/wiki/Lifecycle.md) ·
[Evals](docs/wiki/Evals.md) · [Contributing](docs/wiki/Contributing.md) · [FAQ](docs/wiki/FAQ.md)

## Contributing

Fixes, new products and new providers are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md):
it explains the content rules (no verbatim vendor prose, anonymized examples, sandbox data
kept exactly, no commercial terms) and the checks to run before a PR. Report security issues
as described in [SECURITY.md](SECURITY.md).

## Disclaimer

This project is not affiliated with any of the payment providers it covers. The notes are
derived from public developer documentation, and that documentation is the authority.
Confirm production behaviour with your provider. Commission rates and settlement terms
depend on each merchant's contract, so the skills do not state them. Never commit real
credentials or customer data.

## License

[MIT](LICENSE)
