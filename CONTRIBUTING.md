# Contributing

Contributions are welcome: fixes, new products, and new providers. Payme and Multicard are the
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
4. **Examples are fully anonymized.** In `examples/`, schemas and README snippets, use
   placeholders, never real or vendor-sample values:

   | Kind | Use |
   |---|---|
   | URLs / domains | `https://merchant.example.com/...` |
   | Credentials | `<BASIC_USER>`, `<BASIC_PASSWORD>`, `<API_KEY>`, `<CARD_TOKEN>` |
   | UUIDs | freshly generated (`python3 -c "import uuid; print(uuid.uuid4())"`) |
   | Phone | `+998901234567` / `998901234567`; masks like `+998*****4567` |
   | Order number | `"100001"` |
   | Card | `<CARD_PAN_16_DIGITS>`, masks like `860012******0000`; vendor test PANs live in `references/sandbox/` only |
   | People / companies | `SAMPLE HOLDER`, `Merchant Example` |
   | Merchant / service / terminal ids | small obvious values (`1`, `100`) or `<SERVICE_ID>` |

   Do not copy ids, receipts, names, tax numbers, accounts or amounts from vendor
   samples. Make up new ones.
5. **Vendor sandbox data is kept, exactly.** Every provider has
   `skills/<provider>/references/sandbox/README.md` with everything the vendor publishes for its
   test environment: test hosts, test cards with expiry, OTP / 3-DS codes, test PINFL and
   phones, scenario inputs with expected results, test-only methods and sample payloads. Copy
   the values exactly and link the source page or file. They are test data, not secrets, and
   integrations cannot be tested without them. Say so when the vendor publishes none, and
   note stale data (an expired test card) instead of dropping it. Never copy real merchant
   credentials, pre-filled logins, passwords or keys from vendor Postman collections, real
   people's data, or material the vendor marks confidential.
6. **English content.** Error descriptions may stay in Russian where the upstream contract
   is Russian.
7. **SKILL.md stays a router.** Keep it under ~150 lines and move detail into `references/`.

## Adding a product to an existing provider

1. Add the source or sources to `sources.yaml`:

   ```yaml
   - id: <provider>-<product>-<lang>
     provider: <provider>          # folder under skills/
     product: <product>            # folder under references/
     kind: openapi | openapi-labels | html | file
     lang: ru | en | uz
     url: https://...
     spa: docusaurus | bundle      # html only, when the page is rendered client-side
     refs: [skills/<provider>/references/<product>/README.md]   # files to re-review on change
   ```

   - `openapi` is the primary machine-readable spec. `scripts/sync` regenerates
     `schemas/openapi.min.json`, `schemas/ops/*.json` and `endpoints.md` from it.
   - `openapi-labels` is a second-language copy of the same spec, used for English summaries.
   - `html` is a documentation page. Only its text hash is tracked, and a change flags `refs`
     for human review.
   - `spa` is needed when the server returns the same empty shell for every page and the
     text is loaded by JavaScript. `docusaurus` hashes the route's content chunk, so each
     page is tracked on its own (Click). `bundle` hashes the text of every script on the
     page, so one content change flags all of that site's sources (Paynet). `scripts/sync`
     fails a page that has almost no text, or the same text as another page, so a missing
     `spa` shows up on the first run.
   - `file` is any other upstream asset (test-case PDF, Postman collection). Its raw bytes are
     hashed, and a change flags `refs` like `html`.
   - A changed source of any kind that lists `refs` is flagged, so list the sandbox README on
     every source it was written from.
2. Run `scripts/sync --only <id>[,<id>]` and check the generated files.
3. Write `references/<product>/README.md` with:
   - the source URL and fetched date;
   - direction (who calls whom), hosts, auth, units;
   - the flow or state machine, the error table, and gotchas;
   - an `Examples` section.
4. Add anonymized `examples/*.json`. Name them `<operation>.request.json` /
   `<operation>.response.json`, and keep bodies only, because headers belong in the README.
5. Add the product's test hosts, test cards, codes, scenarios and samples to
   `references/sandbox/README.md` (content rule 5).
6. Add `checklists/<product>.md`.
7. Add the product to the provider's `SKILL.md` (products table, decision table, gotchas,
   checklist list).

## Adding a provider (for example Payme or Multicard)

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
3. Create `skills/<provider>/references/sandbox/README.md` (content rule 5) and give it a row
   in the `SKILL.md` products table.
4. Add each product as described above.
5. Add a row to the skills table in `README.md`, and update the plugin descriptions in
   `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
6. For providers without OpenAPI specs (HTML docs only), hand-write the schemas. Mark each one
   with `x-uzfintech-source` and track the pages as `kind: html`.

## Checks before a PR

```sh
scripts/sync --selftest                                   # YAML parser self-test
find skills .claude-plugin -name '*.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
```

Anonymization scan. Outside `references/sandbox/` every command should print nothing; review
any hit by hand. Vendor test data is expected in `references/sandbox/`, so the id, card and
phone scans skip it, and a secrets hit there must be a vendor sample value, never a working
credential.

```sh
# secrets and tokens (sandbox files included: no pre-filled vendor credentials there either)
rg -n -i '(api[_-]?key|secret|token|password|authorization)"?\s*[:=]\s*"?[A-Za-z0-9+/=_-]{16,}' skills
rg -n -P '\b[A-Fa-f0-9]{32,}\b|\b[A-Za-z0-9+/]{24,}={0,2}(?=["\s])' skills -g '!**/references/sandbox/**'
# card numbers (16 digits) and phones other than the placeholder
rg -n -P '(?<!\d)(8600|9860|5614|4\d{3}|5[1-5]\d{2})\d{12}(?!\d)' skills -g '!**/references/sandbox/**'
rg -n -P '998\d{9}' skills -g '!**/references/sandbox/**' | rg -v '998901234567'
# e-mails and IPv4 addresses
rg -n -P '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}' skills
rg -n -P '\b\d{1,3}(\.\d{1,3}){3}\b' skills
```

In `references/sandbox/`, check that every card, phone, id and code appears in the linked
vendor source. Also search for anything specific to your own company: product names, domains, merchant
and service ids, and order number ranges.

## Commits and PRs

- Use one topic per PR, and give each change a source: link the vendor page it came from.
- For sync PRs opened by the workflow, re-read the flagged pages and update the
  hand-written `README.md` and checklists before merging.
