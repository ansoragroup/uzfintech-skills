# Contributing

**English** · [Русский](Contributing.ru.md) · [Oʻzbekcha](Contributing.uz.md) · [简体中文](Contributing.zh-CN.md)

Fixes, new products and new providers are welcome. The full rules are in
[CONTRIBUTING.md](https://github.com/ansoragroup/uzfintech-skills/blob/main/CONTRIBUTING.md).
This page is the short version.

## The rules that keep the repository publishable

1. **Your own words.** Write notes yourself. Field names, types, codes, limits, URLs and
   timeouts are facts and can be copied; paragraphs of vendor prose cannot.
2. **Every fact has a source.** Each README names its vendor page and fetched date; each
   schema carries `x-uzfintech-source`.
3. **Examples are anonymized.** Placeholders such as `<CARD_TOKEN>`, `100001`,
   `+998901234567`, `merchant.example.com`. Never real or vendor-sample ids, names or amounts.
4. **Sandbox data is kept exactly.** Test hosts, cards, OTP codes, test PINFL, scenarios and
   sample payloads go into `references/sandbox/README.md` as the vendor publishes them.
   Integrations cannot be tested without them.
5. **Lifecycle facts are kept.** Deadlines, cancel and refund rules, retry rules and fiscal
   receipt rules go into `references/lifecycle/README.md` with a stable warning ID.
6. **No commercial terms.** No commission rates, payout shares, tariffs or settlement days.
7. **`SKILL.md` stays a router**, under 180 lines. Detail goes into `references/`.

## Before you open a PR

```sh
scripts/lint --fix        # copies scripts/shared/*.py into every skill, then checks
scripts/lint              # tools, examples, frontmatter, json, links, scan, i18n, versions, lifecycle
scripts/sync --selftest   # needs PyYAML
```

`scripts/lint` must print `ok` for every check. CI runs the same commands on every PR.
If you changed behaviour, run the matching eval: `claude plugin eval . --tag <provider>`.

## Fixing a fact

1. Find the vendor page that says otherwise and link it in the PR.
2. Fix the reference README, the schema, the example and the checklist item together.
3. If `SKILL.md` repeats the fact (rules, gotchas, warnings), fix it there too.

## Translations

The README and every wiki page exist in English, Russian, Uzbek and Simplified Chinese.
Change the English page first, then update the three translations in the same PR, or open
an issue so a speaker can do it.

- Never translate API names, fields, headers, codes, enum values or warning IDs.
- Uzbek uses the Latin script and writes oʻ and gʻ with U+02BB (ʻ), not an apostrophe.
  `scripts/lint --only i18n` checks it. Write natural Uzbek, not word-for-word Russian.
- Chinese uses Simplified characters and keeps the product names as the vendors spell them.

## Commits and PRs

One topic per PR. The weekly sync workflow opens its own PR when an upstream spec or page
changes; re-read the flagged pages before merging it.
