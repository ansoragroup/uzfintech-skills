# Contributing

Contributions are welcome: fixes, new products, and new providers. Payme and Click are the
next planned providers. Read the content rules first, because they are what keeps this
repository publishable.

## Content rules

1. **No verbatim vendor prose.** Write notes in your own words. Normative facts are fine:
   field names, types, enums, codes, limits, URLs and timeouts. Copying paragraphs or whole
   pages is not.
2. **Schemas are trimmed derivatives.** Every schema file carries its upstream source URL and
   fetched date. OpenAPI-derived files use `x-uzfintech-source`, which `scripts/sync`
   writes. Hand-written schemas set `x-uzfintech-source: {source_url, fetched, note}`.
   Remove descriptions, examples and vendor marketing.
3. **Raw downloads stay out of git.** `scripts/sync` writes to `cache/`, which is ignored.
   Never commit it.
4. **Examples are fully anonymized.** Use placeholders, never real or vendor-sample values:

   | Kind | Use |
   |---|---|
   | URLs / domains | `https://merchant.example.com/...` |
   | Credentials | `<BASIC_USER>`, `<BASIC_PASSWORD>`, `<API_KEY>`, `<CARD_TOKEN>` |
   | UUIDs | freshly generated (`python3 -c "import uuid; print(uuid.uuid4())"`) |
   | Phone | `+998901234567` / `998901234567`; masks like `+998*****4567` |
   | Order number | `"100001"` |
   | Card | `<CARD_PAN_16_DIGITS>`, masks like `860012******0000`; **never** test PANs (link the vendor testing page) |
   | People / companies | `SAMPLE HOLDER`, `Merchant Example` |
   | Merchant / service / terminal ids | small obvious values (`1`, `100`) or `<SERVICE_ID>` |

   Do not copy ids, receipts, names, tax numbers, accounts or amounts from vendor
   samples. Make up new ones.
5. **English content.** Error descriptions may stay in Russian where the upstream contract
   is Russian.
6. **SKILL.md stays a router.** Keep it under ~150 lines and move detail into `references/`.

## Adding a product to an existing provider

1. Add the source or sources to `sources.yaml`:

   ```yaml
   - id: <provider>-<product>-<lang>
     provider: <provider>          # folder under skills/
     product: <product>            # folder under references/
     kind: openapi | openapi-labels | html
     lang: ru | en | uz
     url: https://...
     refs: [skills/<provider>/references/<product>/README.md]   # html: files to re-review on change
   ```

   - `openapi` is the primary machine-readable spec. `scripts/sync` regenerates
     `schemas/openapi.min.json`, `schemas/ops/*.json` and `endpoints.md` from it.
   - `openapi-labels` is a second-language copy of the same spec, used for English summaries.
   - `html` is a documentation page. Only its text hash is tracked, and a change flags `refs`
     for human review.
2. Run `scripts/sync --only <id>[,<id>]` and check the generated files.
3. Write `references/<product>/README.md` with:
   - the source URL and fetched date;
   - direction (who calls whom), hosts, auth, units;
   - the flow or state machine, the error table, and gotchas;
   - an `Examples` section.
4. Add anonymized `examples/*.json`. Name them `<operation>.request.json` /
   `<operation>.response.json`, and keep bodies only, because headers belong in the README.
5. Add `checklists/<product>.md`.
6. Add the product to the provider's `SKILL.md` (products table, decision table, gotchas,
   checklist list).

## Adding a provider (for example Payme or Click)

1. Create `skills/<provider>/SKILL.md` with frontmatter:

   ```yaml
   ---
   name: <provider>
   description: <what it covers and exactly when to trigger: product names, hosts, typical tasks>
   ---
   ```

   The description is what the agent matches on, so name the products, API hosts and tasks.
2. If the provider has cross-product rules (transport, error envelope, signatures), put them in
   `skills/<provider>/references/common/README.md`.
3. Add each product as described above.
4. Add a row to the skills table in `README.md`, and update the plugin descriptions in
   `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
5. For providers without OpenAPI specs (HTML docs only), hand-write the schemas. Mark each one
   with `x-uzfintech-source` and track the pages as `kind: html`.

## Checks before a PR

```sh
scripts/sync --selftest                                   # YAML parser self-test
find skills .claude-plugin -name '*.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
```

Anonymization scan. Every command should print nothing; review any hit by hand.

```sh
# secrets and tokens
rg -n -i '(api[_-]?key|secret|token|password|authorization)"?\s*[:=]\s*"?[A-Za-z0-9+/=_-]{16,}' skills
rg -n -P '\b[A-Fa-f0-9]{32,}\b|\b[A-Za-z0-9+/]{24,}={0,2}(?=["\s])' skills
# card numbers (16 digits) and phones other than the placeholder
rg -n -P '(?<!\d)(8600|9860|5614|4\d{3}|5[1-5]\d{2})\d{12}(?!\d)' skills
rg -n -P '998\d{9}' skills | rg -v '998901234567'
# e-mails and IPv4 addresses
rg -n -P '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' skills
rg -n -P '\b\d{1,3}(\.\d{1,3}){3}\b' skills
```

Also search for anything specific to your own company: product names, domains, merchant
and service ids, and order number ranges.

## Commits and PRs

- Use one topic per PR, and give each change a source: link the vendor page it came from.
- For sync PRs opened by the workflow, re-read the flagged pages and update the
  hand-written `README.md` and checklists before merging.
