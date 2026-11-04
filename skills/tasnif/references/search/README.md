# Tasnif search: by text, by barcode, by sub-position, by group

Hand-written notes. Hosts, reply shapes and error shapes:
[`../common/`](../common/README.md). Every search result lacks package codes; load the
card in [`../code/`](../code/README.md) for them.

- Source: the site https://tasnif.soliq.uz/, the clients in
  [`../common/`](../common/README.md#sources), and the probes in
  [`../sandbox/`](../sandbox/README.md)
- Fetched: 2026-11-04

All paths below are under `https://tasnif.soliq.uz/api/cls-api`.

## Endpoints

| Purpose | Request | Reply shape | Sample |
|---|---|---|---|
| Full-text search (the site's search box) | `GET /elasticsearch/search?search=<text>&size=<n>&page=<n>&lang=ru` | envelope, `data[]`, `recordTotal` | [`elasticsearch-search.ru.json`](../sandbox/elasticsearch-search.ru.json) |
| Search by name | `GET /mxik/search/by-params?text=<text>&size=<n>&page=<n>&lang=ru` | page in the envelope | [`by-params-text.ru.json`](../sandbox/by-params-text.ru.json) |
| Search by barcode | `GET /mxik/search/by-params?gtin=<barcode>&lang=ru` | page in the envelope | [`by-params-gtin.ru.json`](../sandbox/by-params-gtin.ru.json), [`by-params-gtin-not-found.ru.json`](../sandbox/by-params-gtin-not-found.ru.json) |
| Search sub-positions | `GET /mxik/search-subposition?search_text=<text>&page=<n>&size=<n>&lang=ru` | page in the envelope | [`search-subposition.ru.json`](../sandbox/search-subposition.ru.json) |
| Classes of a group | `GET /class/short-info?groupCode=<3 digits>&lang=ru` | envelope, `data[]` | [`class-short-info.ru.json`](../sandbox/class-short-info.ru.json), [`class-short-info.json`](../sandbox/class-short-info.json) (no `lang`) |

`page` starts at 0. URL-encode the text (Cyrillic is common).

The three text searches do not search the same thing. On 2026-11-04 `коврик` gave
`recordTotal` 118 in `elasticsearch/search` (the fiscal skill's
[sample](../../../fiscal/references/sandbox/tasnif-search.ru.json)), `totalElements` 158 in
`by-params?text=` and 14 in `search-subposition`. Do not compare counts between them, and
do not assert counts in tests that call the live endpoints.

## `elasticsearch/search`

Envelope `{success, code: 200, reason: "success", data[], recordTotal, errors}`. Each item:

| Field | Notes |
|---|---|
| `mxikCode`, `name` | the code and its name in `lang` |
| `fullName` | Uzbek Cyrillic, Russian, Uzbek Latin names and the code in one upper-case string |
| `groupCode` ... `brandCode`, `groupName` ... `brandName` | the levels, see [`../common/`](../common/README.md#code-structure-in-the-replies) |
| `attributeName`, `internationalCode` | the product attribute; `internationalCode` is the barcode when the catalogue has one |
| `label`, `useCard`, `usePackage`, `nonChangeable` | strings (`"0"`, `"1"`); on the card some are numbers |
| `unitsName`, `recommendedUnitsName` | unit names as one comma-separated string, for example `шт. (сет/ассорти), шт. (порция)` |
| `lgotaId`, `lgotaName` | a tax benefit linked to the code, `null` in the probes; meaning not documented |
| `categoryCode`, `categoryName` | for example `18`, `Услуги` |
| `surveyCategoryId`, `description`, `mnnName`, `property`, `packageName`, `categoryUnitId`, `categoryUnitName`, `recommendedCategoryUnitName` | not documented; `description` held a number-like string (`"2829788"`) in the probe |

No package codes: `packageName` was `null`.

## `mxik/search/by-params`

Takes `text` or `gtin`, plus `lang`, `size` and `page`. The reply is a page in the envelope:
read `data.content[]`, `data.totalElements` and `data.last`.

Each item has the level codes and names, `mxikCode`, `mxikName`, `attributeName`,
`internationalCode`, `label` (a number here), `myProduct`, `unitCode` / `unitName`,
`commonUnitCode` / `commonUnitName`, `units` and `packages` (`null`). A `gtin` search also
echoes `text`, `lang`, `page`, `size` and `download` in each item.

| Case | `success` | `code` | `reason` | `content` |
|---|---|---|---|---|
| `text=` | `true` | `200` | `OK` | the hits |
| `gtin=` with a hit | `true` | `0` | `ok` | one item; `internationalCode` equals the barcode |
| `gtin=` without a hit | `false` | `-1` | `not data found` | empty |

### Barcode to code

1. `GET /mxik/search/by-params?gtin=<barcode>&lang=ru`.
2. Hit: load the card (`/mxik/get/by-mxik`) for the package codes, show the code, its name
   and the packages to a person, and store what they confirm.
3. No hit: fall back to a text search on the product name and let a person pick.

A hit is the link the catalogue holds for that barcode; a product can still need a
different code, and many barcodes have no link at all. Warning
[`tasnif.barcode-hit-needs-review`](../lifecycle/README.md#warn-without-being-asked).
Check the barcode's own check digit before you call.

## `mxik/search-subposition`

`search_text`, `page`, `size`, `lang`. Same page shape and item fields as `by-params?text=`,
but it matches sub-positions (`subPositionName`). Useful for a picker that narrows by
category before the user chooses a code.

## `class/short-info`

`groupCode` (3 digits), optional `lang`. Envelope with `code: null`, `reason: null`;
`data[]` items are `{code, name, count}`: the 5-digit class code, its name and, by its
name, the number of codes in the class (derived). `recordTotal` is the number of classes
(17 for group `040`). Without `lang` the names are in Uzbek Cyrillic.

There is no endpoint in this skill that lists the groups themselves; take group codes from
the codes you already have, or from the site.

## Do not use

| Request | Result on 2026-11-04 |
|---|---|
| `GET /class/search?keyword=...` | 403 `text/plain` `Синф коди хато жўнатилган` |
| `GET https://tasnif.soliq.uz/api/cl-api/class/search?keyword=...` | 404 Spring error JSON ([sample](../sandbox/cl-api-class-search.json)); one client still calls it |
| `GET /mxik/search/dv-cert-number` | without a parameter: `{"success": false, "code": 400, "reason": "empty cert number"}` ([sample](../sandbox/dv-cert-number-empty.ru.json)); the parameter name is not known, and the clients that call it pass nothing usable. Which certificate it means is not documented |

## Seen in code, not probed

- `GET /mxik/search` (plain), in two clients.
- `GET /attribute/web-katalog?lang=&pageNo=&pageSize=&mnnName=&internalCode=` in one
  client. `mnnName` suggests the medicines catalogue (international non-proprietary
  names, derived).
- `GET https://api.tasnif.soliq.uz/api/v1/mxik/details`, named once in a mobile app;
  unverified.

Do not build on these without probing them yourself.
