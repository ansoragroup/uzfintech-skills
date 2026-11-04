---
name: tasnif
description: Public JSON endpoints of Tasnif, the Uzbek product and service classifier (tasnif.soliq.uz, MXIK / IKPU / SPIC codes), as the official site and point-of-sale software call them, because the tax committee publishes no API reference - text, sub-position and barcode (GTIN) search, the code card with package codes, code history with package names in three languages, product pictures, group-to-class lists, the per-seller point-of-sale check (cl-api information with permitted, cashSale, usePackage) and the txkm VAT-payer check, with the reply and error shapes, caching rules and the gaps. Use when building or reviewing a catalogue import, a barcode-to-MXIK lookup, a product-code picker or a scheduled re-check of stored codes against Tasnif, or when explaining what a Tasnif reply means.
---

# Tasnif (MXIK / IKPU) catalogue lookups

This file is a router. Answer from the files referenced below, not from memory.

The tax committee keeps the national catalogue of goods and services on
https://tasnif.soliq.uz/. The site and many point-of-sale programs read it through
unauthenticated `GET` endpoints. **No API reference, terms of use or rate limits are
published.** Every endpoint here was taken from the site's own calls and from open-source
clients pinned to commits in [references/common/README.md](references/common/README.md),
then probed once, politely, on 2026-11-04. Say so when you answer
(`tasnif.not-official-api`).

What goes on a receipt line (code and package code as strings, VAT, marking) is the
[fiscal skill](../fiscal/SKILL.md). This skill is about finding and checking codes.

## Pages

| Page | What | Reference |
|---|---|---|
| Common (all endpoints) | hosts, `cls-api` and `cl-api`, three reply shapes, `lang`, error shapes, caching, sources | [references/common/](references/common/README.md) |
| Search | text search, `by-params` by text or barcode (GTIN), sub-position search, group to classes | [references/search/](references/search/README.md) |
| Code card | `by-mxik` card with packages, `history` with package names, pictures | [references/code/](references/code/README.md) |
| Point of sale | `cl-api` information per TIN or terminal, txkm VAT-payer check, partner-only marking endpoints | [references/pos/](references/pos/README.md) |
| Sandbox | saved replies for every probed endpoint, placeholders | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle | no SLA, not-found shapes, package mismatches, retries, receipts, open questions | [references/lifecycle/](references/lifecycle/README.md) |

## Which page?

| The user wants to... | Use |
|---|---|
| find a code by product name | Search: `elasticsearch/search` or `mxik/search/by-params?text=` |
| find a code by barcode (EAN-13 / GTIN) | Search: `mxik/search/by-params?gtin=`, then a person confirms the hit |
| get the package codes of a code | Code card: `mxik/get/by-mxik` (or `history`) |
| check that a stored code still exists | Code card: `integration-mxik/get/history/{mxik}` (`isActive`, `updatedAt`) |
| show product pictures | Code card: `picture-names`, then `references/get/file/<name>` |
| build a category picker | Search: `class/short-info?groupCode=` |
| check a code for one seller or till | Point of sale: `cl-api` `get/information` with `tin` / `terminalId` |
| check whether a TIN is a VAT payer | Point of sale: txkm `is-vat/<TIN>` |
| validate a marking code (Data Matrix) | partner-only, not covered: [Point of sale](references/pos/README.md#partner-only-endpoints) |
| put the code on a receipt | [fiscal skill](../fiscal/SKILL.md) |
| test | [Sandbox](references/sandbox/README.md): saved replies, no test host exists |

## Rules that apply everywhere

- Read-only `GET`, no auth. Never send cookies, cabinet tokens or E-IMZO data.
- Keep both base URLs in configuration: `https://tasnif.soliq.uz/api/cls-api` (catalogue)
  and `https://tasnif.soliq.uz/api/cl-api` (point of sale).
- An MXIK is a 17-digit **string**. The package `code` arrives as a number; store it as a
  string too.
- Decide found or not found from the body, never from the HTTP status alone.
- Resolve codes when a product is created or edited, store them, re-check on a schedule.
  Never call Tasnif from checkout, payment or receipt code.
- Cache every reply, send one request at a time, back off on errors.
- Choosing a code, a VAT rate or a benefit is a tax decision. The skill reads the
  catalogue; the merchant's accountant chooses.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the consequence and
the fix. Details and sources are in
[references/lifecycle/README.md](references/lifecycle/README.md).

- `tasnif.not-official-api`: undocumented endpoints with no SLA; they can change or close
  without notice. Keep a manual fallback.
- `tasnif.no-checkout-calls`: a Tasnif outage must not stop a sale; look codes up in the
  catalogue workflow, never at checkout.
- `tasnif.check-body-not-status`: an unknown code is HTTP 403 text, 200 `success:false` or
  200 with an empty list, depending on the endpoint.
- `tasnif.codes-as-strings`: MXIK and package codes lose leading zeros as numbers.
- `tasnif.package-lists-differ`: the point-of-sale list can be shorter than the card's;
  take the package from the card and cross-check.
- `tasnif.barcode-hit-needs-review`: a GTIN hit is the catalogue's link, not proof; no hit
  does not mean no code.
- `tasnif.permitted-needs-seller`: `permitted` is `false` without `tin` / `terminalId`, and
  its meaning is not documented.
- `tasnif.history-id-unstable`: the `history` `id` changes on every call; key by
  `mxikCode`.
- `tasnif.throttle-and-cache`: no published limits; crawling can get you blocked.
- `tasnif.codes-change`: codes are edited and deactivated; re-check stored codes.
- `tasnif.no-tax-advice`: `lgota*`, `percent` and `cashSale` are data, not advice.
- `tasnif.personal-data`: TINs and the staff names in `createdBy` stay out of logs, code
  and fixtures.

## Top gotchas

1. Three reply shapes: the envelope `{success, code, reason, data, ...}`, a Spring page
   inside the envelope (`data.content[]`, `data.totalElements`), and a bare object or
   array (`by-mxik`, `picture-names`).
2. The envelope `code` is not a status you can trust: `200` with reason `OK`, `0` with
   `ok` on a GTIN hit, `-1` on no hit, `null` on `class/short-info`. Read `success` and the
   data.
3. Search results carry no package codes (`packages: null`); load the code card.
4. `class/search` fails on both APIs (403 on `cls-api`, 404 on `cl-api`); use
   `class/short-info`.
5. Without `lang`, `class/short-info` answers in Uzbek Cyrillic; `history` returns Uzbek
   and Russian names whatever you send (the `*Lat` fields were `null`).
6. Flags change type between endpoints (`label` `"0"` in search, `0` on the card); compare
   them as text.
7. `history` dates are `dd.MM.yyyy HH:mm:ss` text, `cl-api` dates are epoch milliseconds.

## Validate an implementation

Run [checklists/catalogue.md](checklists/catalogue.md). Mark each item pass, fail or n.a.
with a file:line citation, then compare the parsing code with the saved replies in
[references/sandbox/](references/sandbox/README.md).

## Tools: run them, do not compute by hand

`scripts/tasnif.py` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) is
python3, standard library only. Offline by default: it prints the exact URL and never
touches the network unless you pass `--online` (one `GET`).

```sh
python3 scripts/tasnif.py search "коврик" [--via by-params|subposition] [--size 5] [--online]
python3 scripts/tasnif.py gtin 4607001771555 [--online]
python3 scripts/tasnif.py code 04016001002000000 [--online]
python3 scripts/tasnif.py history 04016001002000000 [--online]
python3 scripts/tasnif.py info 04016001002000000 [--tin <TIN>] [--terminal-id <ID>] [--online]
python3 scripts/tasnif.py classes 040 [--online]
python3 scripts/tasnif.py pictures 04016001002000000 [--online]
python3 scripts/tasnif.py vat <TIN> [--online]
python3 scripts/tasnif.py code --file reply.json      # summarize a saved reply
python3 scripts/tasnif.py --selftest
```

Exit codes: 0 found, 1 not found or invalid input, 2 usage error, network error or an
unexpected reply (unknown: retry later). The
17-digit structure check (lost leading zeros, barcode in the code field) is
`scripts/mxik.py check` in the fiscal skill. The shared `sign.py` and `validate.py` hold
nothing for Tasnif: it has no signatures and no schemas.

## Answering rules

- Reply in the user's language, but never translate paths, fields or flag values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation. Code uses
  placeholders and runs as written.
- Say the endpoints are undocumented and were observed on the given date. Quote paths and
  fields exactly as the references give them. If a fact is not there, say Tasnif does not
  publish it.
- Lifecycle: before you finish an answer that stores, imports or re-checks codes, check
  "Warn without being asked" and [references/lifecycle/](references/lifecycle/README.md).
- Design for Tasnif being down: cache, a background job, a manual entry path. Never put a
  live Tasnif call in a request path.
- Never use a real TIN, PINFL or a person's name. Use `<TIN>` and placeholders, and drop
  `createdBy` from anything you save.
- Which code, VAT rate or benefit applies is the accountant's decision. Point to the
  catalogue and the [fiscal skill](../fiscal/SKILL.md); do not decide it.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare the
  saved replies with the live endpoints.
