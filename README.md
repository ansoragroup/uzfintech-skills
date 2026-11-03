# uzfintech-skills

Agent skills for Uzbek payment provider APIs, for **Claude Code** and **Codex**.

The skills give exact contract answers and help validate an integration. They cover:
- endpoints, auth headers and signatures;
- request and response schemas, field types and units;
- error codes and state machines;
- idempotency rules and anonymized examples.

| Skill | Provider | Products |
|---|---|---|
| [`uzum`](skills/uzum/SKILL.md) | Uzum Bank | Merchant API (webhooks), Checkout, Fiscalization, FastPay, Dynamic QR, CrossBorder, Remit Core, Ratekeeper, Nasiya, PaymentHub |
| [`alif`](skills/alif/SKILL.md) | Alif (alifpay) | Checkout, Payments, Cards, Hold, Monitoring, Summary |

Payme and Click are planned. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Layout

```
skills/<provider>/
  SKILL.md                         router: products, decision table, gotchas, pointers
  references/<product>/README.md   hand-written contract notes (source URL + fetched date)
  references/<product>/schemas/    trimmed JSON Schemas derived from upstream specs
  references/<product>/examples/   anonymized request / response bodies
  checklists/<product>.md          implementation validation checklists
scripts/sync                       upstream sync (python3, stdlib only)
sources.yaml                       tracked upstream sources and their hashes
```

## Install

### Claude Code: plugin (recommended)

```
/plugin marketplace add ansoragroup/uzfintech-skills
/plugin install uzfintech@uzfintech-skills
```

Update it later with `/plugin marketplace update uzfintech-skills`.

### Claude Code: copy the skills

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
mkdir -p ~/.claude/skills
cp -R uzfintech-skills/skills/uzum uzfintech-skills/skills/alif ~/.claude/skills/
```

To install for one project only, use `<project>/.claude/skills/` instead.

### Codex: skills directory

```sh
git clone https://github.com/ansoragroup/uzfintech-skills
mkdir -p ~/.codex/skills
cp -R uzfintech-skills/skills/uzum uzfintech-skills/skills/alif ~/.codex/skills/
```

### Codex (or any agent): AGENTS.md

You can also vendor the repository, for example as a git submodule at
`vendor/uzfintech-skills`. Then add this to your project's `AGENTS.md`:

```md
## Payment provider contracts
For any Uzum Bank or Alif (alifpay) integration work, read
`vendor/uzfintech-skills/skills/uzum/SKILL.md` or `vendor/uzfintech-skills/skills/alif/SKILL.md`
first and follow its pointers. Answer contract questions from those files, and validate
changes with the matching `checklists/*.md`.
```

## Using it

Ask the agent things like:

- "What does Uzum Merchant `/confirm` send, and what must I answer on a retry?"
- "Verify an Alif webhook signature in Go."
- "Validate our Checkout integration against the Uzum checklist."

The agent loads the matching `SKILL.md` and then reads only the reference files it needs.

## Freshness

Every reference carries the source URL and the date it was fetched.
`.github/workflows/sync.yml` runs `scripts/sync` weekly and opens a PR when an upstream
spec or page changes. To run it locally:

```sh
scripts/sync --check            # report only; exit 1 when upstream changed
scripts/sync                    # regenerate OpenAPI-derived files, update sources.yaml
scripts/sync --report out.md    # also write a Markdown report
```

Raw downloads go to `cache/`, which is git-ignored.

## Disclaimer

This project is not affiliated with Uzum Bank or Alif. The notes are derived from the
public developer documentation. Vendor documentation is the authority, so confirm
production behaviour with your provider manager. Never commit real credentials or customer
data to this repository.

## License

[MIT](LICENSE)
