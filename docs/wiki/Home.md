# uzfintech-skills

**English** · [Русский](Home.ru.md) · [Oʻzbekcha](Home.uz.md) · [简体中文](Home.zh-CN.md)

Agent skills for the payment APIs of Uzbekistan: **Uzum Bank, Alif, Click, Paynet, Payme,
Multicard, Atmos, Octo, Oson and Kapitalbank**, plus a fiscal receipt skill shared by all of
them and a router skill for choosing and comparing providers. An agent that loads them
answers from exact contract notes, checks signatures and payloads with two small scripts,
and warns about deadlines, reversals and fiscal receipts before they turn into production
incidents.

## Start here

| I want to... | Page |
|---|---|
| install the skills in Claude Code, Codex, Cursor or another agent | [Install](Install.md) |
| check a signature, an auth header or a payload | [Tools](Tools.md) |
| know how an agent should use the skills and what a good answer looks like | [Agent guide](Agent-guide.md) |
| see the time windows, cancel / refund rules and receipt rules per provider | [Lifecycle](Lifecycle.md) |
| measure whether the skills make answers better | [Evals](Evals.md) |
| fix a fact or add a product or provider | [Contributing](Contributing.md) |
| find a quick answer | [FAQ](FAQ.md) |

## Providers

| Skill | Provider | What it covers |
|---|---|---|
| [`uzum`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzum/SKILL.md) | Uzum Bank | Merchant API webhooks, Checkout, Fiscalization, FastPay, Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Nasiya, PaymentHub |
| [`alif`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/alif/SKILL.md) | Alif (alifpay) | Checkout, Alif Nasiya instalments, Payments, Cards, Hold, Monitoring, Summary, legacy API map |
| [`click`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/click/SKILL.md) | Click | SHOP API, Advanced / Split Shop, Merchant API, card tokens, Fiscalization, CLICK Pass, payment button, Telegram Payments |
| [`paynet`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/paynet/SKILL.md) | Paynet | Internet acquiring for Humo and Uzcard |
| [`payme`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/payme/SKILL.md) | Payme (Paycom) | Merchant API, Subscribe API, Checkout, Fiscalization |
| [`multicard`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/multicard/SKILL.md) | Multicard | Invoices, card binding, payments, refunds, holds, payouts, reports |
| [`atmos`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/atmos/SKILL.md) | Atmos | Uzcard / Humo payments and reversals, payment page and widget, card linking, holds, withdrawal by PINFL, Visa / Mastercard (MPS / IPS), Callback API |
| [`octo`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/octo/SKILL.md) | Octo | Payment page (one-stage / two-stage), own card form, card tokens, full and partial refunds, fiscalization |
| [`oson`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/oson/SKILL.md) | Oson | Invoice API and signed payment notification, rebuilt from Oson's open-source shop plugins |
| [`kapitalbank`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/kapitalbank/SKILL.md) | Kapitalbank | Kapital API for legal entities (payment orders, status, statements, account checks, exchange rates, invoices), CBU payment purpose codes |
| [`fiscal`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/fiscal/SKILL.md) | All providers | MXIK (IKPU) and package codes, VAT and benefit fields, marking, receipt types, per-provider receipt fields |
| [`uzfintech`](https://github.com/ansoragroup/uzfintech-skills/blob/main/skills/uzfintech/SKILL.md) | All providers | Router: choose and compare providers, cross-provider cheatsheet (units, auth, callbacks, refunds, holds, fiscalization, test hosts), UzQR notes |

Start with `uzfintech` when the task is to choose or compare providers.

## What is inside a skill

```
skills/<provider>/
  SKILL.md                 router: products, decision table, rules, gotchas, warnings
  references/<product>/    README.md notes, schemas/*.json, examples/*.json
  references/sandbox/      vendor test hosts, cards, OTP codes, scenarios, kept exactly
  references/lifecycle/    deadlines, cancel / reverse / refund, retries, fiscal receipts
  checklists/*.md          review items: pass, fail or n.a. with a file:line citation
  scripts/sign.py          signatures and auth headers
  scripts/validate.py      JSON Schema check of request and response bodies
```

The notes are written from public developer documentation. Every reference names its source
page and the date it was fetched. The vendor documentation stays the authority.
