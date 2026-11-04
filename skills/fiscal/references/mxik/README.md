# MXIK (IKPU / SPIC): the product code on every receipt line

Hand-written notes. Every online fiscal receipt line in Uzbekistan names the goods or
service with a code from the Unified Electronic National Catalogue of Products (Goods and
Services), which the tax committee keeps on tasnif.soliq.uz. The same code has several
names, depending on the language and the provider:

| Name | Where you meet it |
|---|---|
| MXIK (Mahsulotlar va xizmatlarning identifikatsiya kodi) | Uzbek; Multicard `mxik`, Atmos `mxik_code` |
| IKPU (Идентификационный код продукции и услуг) | Russian; Payme calls `code` the IKPU, Atmos `ofd_code` |
| SPIC | Click `SPIC`, Uzum `spic` / `receiptParams.spic`, Alif `spic`, Octo `spic` |

- Source: https://tasnif.soliq.uz/ (the catalogue, a client-rendered site), the replies in
  [`../sandbox/`](../sandbox/README.md) (public classifier data), and the regulation on the
  catalogue: Cabinet of Ministers resolution No. 263 of 28.04.2025,
  https://lex.uz/ru/docs/7502311 (only its title and date were readable here)
- Fetched: 2026-11-04

## Structure (17 digits)

A full code has exactly 17 digits. The classifier's own reply returns every level as a
prefix of the full code, so the levels can be read straight from the digits:

| Level | Reply field | Digits | Example (`04016001002000000`) |
|---|---|---|---|
| Group | `groupCode` / `groupName` | 1-3 | `040` КАУЧУК, РЕЗИНА И ИЗДЕЛИЯ ИЗ НИХ |
| Class | `classCode` / `className` | 1-5 | `04016` |
| Position | `positionCode` / `positionName` | 1-8 | `04016001` |
| Sub-position | `subPositionCode` / `subPositionName` | 1-11 | `04016001002` Коврик для мыши |
| Brand | `brandCode` / `brandName` | 1-14 | `04016001002000` (no brand) |
| Full code | `mxikCode` / `mxikName` | 1-17 | `04016001002000000` |

- The last three digits carry attributes (`attributeName` in the reply; derived from the
  field name). A code whose brand and attribute digits are all zero (ends in `000000`) is a
  base code; a code with brand or attribute digits set identifies a specific product
  (derived from the reply levels).
- **The code is text, not a number.** Every goods code in the replies and vendor samples in
  this repository starts with `0` (`040`, `057`, `007`, `003`, `064`, `027`, `085`), so a
  database column, spreadsheet or JSON serializer that treats it as a number drops the
  leading zero and sends 16 digits. Every provider schema here types the field as a
  string. Warning [`fiscal.mxik-as-string`](../lifecycle/README.md#warn-without-being-asked).
- A 13-digit number is usually an EAN-13 barcode. Click has a separate `Barcode` field; no
  other provider here takes one.

Run `scripts/mxik.py check <code>` for the split and these hints. It never calls the
network.

## Finding the right code

1. Search the product by name on https://tasnif.soliq.uz/ and open its card.
2. Copy the full 17-digit code, the package codes listed on the card, and note the unit,
   the marking flag and any benefit (`lgota`) shown there.
3. Register it with the provider if the provider needs that first (Octo: through the bank
   manager; Multicard: optional store defaults `tax_mxik` / `tax_package_code`).
4. Keep code and package code per catalogue item in your own database, as strings.

Choosing the right code for a product is a tax and accounting decision. The skill shows
where the fields go; it does not choose the code. For a disputed or missing code, send the
user to the Tasnif site's own support or to their accountant.

## Public JSON endpoints (used by the site, not a documented API)

The Tasnif site loads its data from these unauthenticated `GET` endpoints. No official
description, Swagger file or terms of use for them was found on soliq.uz, tasnif.soliq.uz
or lex.uz (`/api/cls-api/swagger-ui` answers 404). **They are what the official site uses,
not a documented integration API, and may change without notice. Confirm codes in the site
UI before you rely on them**, and do not hammer them from production code; cache the
result per product.

Every endpoint (barcode search, history, pictures, the point-of-sale `cl-api` check, the
VAT-payer check), their reply and error shapes and the caching rules are in the
[tasnif skill](../../../tasnif/SKILL.md). This page keeps only what the receipt needs.

| Purpose | Request |
|---|---|
| Full-text search | `GET https://tasnif.soliq.uz/api/cls-api/elasticsearch/search?search=<text>&size=<n>&lang=ru` |
| One code with its packages | `GET https://tasnif.soliq.uz/api/cls-api/mxik/get/by-mxik?mxikCode=<17 digits>&lang=ru` |

Only `lang=ru` was checked here. Exact replies: [`../sandbox/`](../sandbox/README.md).

Search reply: `{success, code, reason, data[], recordTotal, errors}`. Each `data[]` item has
`mxikCode`, `name`, `fullName` (all languages in one string), the level codes and names,
`unitsName`, `label`, `useCard`, `usePackage`, `lgotaId` / `lgotaName`, `categoryName` and
more. The search reply has **no package codes**.

By-mxik reply: one object (no envelope) with the level codes and names, `mxikName`,
`label`, `useCard`, `lgotaId` / `lgotaName`, `unitCode` / `unitName`, and `packages[]`:

| Package field | Meaning (from the sample) |
|---|---|
| `code` | the package code (a number in this reply; providers want a string) |
| `name` | label shown on the card, for example `шт.` or `1 шт.` |
| `containerName` | container, for example `пакет`; `null` for the plain unit |
| `unitId` / `unitName` | the unit the package counts in |
| `parentCode` / `parentValue` | the package this one contains, and how many |
| `isUnitPackage` | `"1"` on the plain unit package in the sample, `"2"` on the container |

Flags whose meaning the site does not explain:

- `label`: by its name, whether the code needs marking codes (derived). `"0"` / `0` in the
  sample. Check the marking rules in [`../receipt-line/`](../receipt-line/README.md#marking-codes-asl-belgisi).
- `useCard`: meaning not documented. Do not infer anything from it.
- `usePackage`: by its name, whether the code is used with package codes (derived).
- Types differ between the two replies: search returns `label` and `useCard` as strings
  (`"0"`), by-mxik as numbers (`0`). Compare them as text.

`scripts/mxik.py lookup <code> --online` calls the by-mxik endpoint once and prints the
package list; without `--online` it only prints the URL. `--file reply.json` summarizes a
reply you saved.

## Third-party clients

Community libraries wrap these endpoints, for example the npm package `mxik`
(github.com/azabroflovski/mxik-js) and the PyPI package `tsuz-search`. They are not
published by the tax committee and were not reviewed for this skill; check their code and
licence before you depend on them, and expect them to break when the site changes.
