# Contributing

Contributions are welcome: fixes, new products, and new providers. Read the content rules
first, because they are what keeps this repository publishable.

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
   note stale data (an expired test card) instead of dropping it. Sample credentials, tokens
   and card numbers printed in the request / response samples of public docs pages are kept
   there too, labeled as samples that the vendor does not document as working. Never copy
   logins, passwords or keys pre-filled in vendor Postman collections, real people's data, or
   material the vendor marks confidential.
6. **English content.** Error descriptions may stay in Russian where the upstream contract
   is Russian.
7. **SKILL.md stays a router.** Keep it under 180 lines and move detail into `references/`.
8. **No commercial terms.** Commission rates, payout percentages, settlement periods (T+1)
   and tariffs differ per merchant contract, so leave them out, even when a vendor page or
   an offer prints them. Fee fields in the API contract (`commission`, `fee`) stay.
9. **Lifecycle facts are kept and surfaced.** Every deadline, time window, cancel / reverse /
   refund rule, retry and idempotency rule, hold expiry, OTP lifetime and fiscal receipt rule
   goes into `skills/<provider>/references/lifecycle/README.md`, with its source. The ones
   that cost money or a tax problem when missed also get a line with a stable ID
   (`<provider>.<topic>`, for example `uzum.fiscal-receipt-24h`) in the `SKILL.md` block
   "Warn without being asked". Never rename an ID; add a new one instead. When the vendor
   does not document a window, list it under "Not documented, ask the provider" rather than
   guessing.
10. **Tools are shared.** `sign.py` and `validate.py` are edited only in `scripts/shared/`;
    `scripts/lint --fix` copies them into every skill. A new signature scheme needs a
    self-test vector.

## Adding a product to an existing provider

1. Add the source or sources to `sources.yaml`:

   ```yaml
   - id: <provider>-<product>-<lang>
     provider: <provider>          # folder under skills/
     product: <product>            # folder under references/
     kind: openapi | openapi-labels | html | file | markdown
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
   - `markdown` is a plain `.md` docs page (for example one listed in an `llms.txt`). The
     normalized text is hashed, and a change flags `refs` like `html`.
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
6. Add the product's deadlines, cancel / refund rules, retries and receipt rules to
   `references/lifecycle/README.md`, and a warning line to `SKILL.md` for each one that is
   costly to miss (content rule 9).
7. Add `checklists/<product>.md`.
8. Add the product to the provider's `SKILL.md` (products table, decision table, gotchas,
   checklist list).
9. Add an eval case in `evals/` for the most likely mistake (see `evals/README.md`).

## Adding a provider

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
3. Create `skills/<provider>/references/sandbox/README.md` (content rule 5) and
   `skills/<provider>/references/lifecycle/README.md` (content rule 9), and give both a row in
   the `SKILL.md` products table.
4. Add each product as described above.
5. Run `scripts/lint --fix` to copy the tools into `skills/<provider>/scripts/`, and add the
   provider's schemes to `scripts/shared/sign.py`.
6. Add a row to the skills table in `README.md` and its translations, and update the plugin
   descriptions in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
7. For providers without OpenAPI specs (HTML docs only), hand-write the schemas. Mark each one
   with `x-uzfintech-source` and track the pages as `kind: html`.

## Checks before a PR

```sh
scripts/lint --fix          # copy scripts/shared/*.py into every skill, then run every check
scripts/lint                # must print ok for every check; CI runs the same
scripts/sync --selftest     # YAML parser self-test, needs PyYAML
```

`scripts/lint` runs these checks; pick some with `--only scan,links`:

| Check | Fails when |
|---|---|
| `tools` | a skill's copy of a tool differs from `scripts/shared/`, `sign.py --selftest` fails, or `validate.py` crashes on a schema |
| `examples` | an `examples/<op>.request.json` or `<op>.response.json` does not validate against its schema |
| `frontmatter` | `SKILL.md` breaks the Agent Skills spec (name, description with "Use when") or is over 180 lines |
| `json` | a JSON file does not parse |
| `links` | a relative Markdown link is broken |
| `scan` | the anonymization scan below finds a hit, or a commercial rate appears |
| `i18n` | a README or wiki translation is missing, or Uzbek uses an apostrophe in oʻ / gʻ |
| `versions` | `plugin.json`, `marketplace.json` and `CHANGELOG.md` disagree |
| `lifecycle` | a skill has no `references/lifecycle/README.md` or is missing a section, `SKILL.md` has no "Warn without being asked" block, or a warning ID is used that the provider's lifecycle page does not define |

The `scan` check covers the anonymization rules. Outside `references/sandbox/` it fails on
secrets, card numbers, phones other than the placeholder, e-mails and IPv4 addresses, and
lists hash- or base64-shaped tokens for review (`--verbose` prints them all). Vendor test
data is expected in `references/sandbox/`, so the id, card and phone scans skip it, and a
secrets hit there must be a vendor sample value, never a working credential.

In `references/sandbox/`, check that every card, phone, id and code appears in the linked
vendor source. Also search for anything specific to your own company: product names, domains, merchant
and service ids, and order number ranges.

## Commits and PRs

- Use one topic per PR, and give each change a source: link the vendor page it came from.
- Changed behaviour gets an eval run: `claude plugin eval . --tag <provider>`.
- Update the README and wiki translations in the same PR, or open an issue for them.
  Uzbek uses the Latin script with U+02BB in oʻ / gʻ.
- For sync PRs opened by the workflow, re-read the flagged pages and update the
  hand-written `README.md` and checklists before merging.
