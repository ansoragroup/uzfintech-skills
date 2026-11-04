# Tasnif code card: packages, history, pictures

Hand-written notes. Hosts, reply shapes and error shapes:
[`../common/`](../common/README.md). What a package code is and where it goes on a receipt:
[fiscal `mxik/`](../../../fiscal/references/mxik/README.md) and
[fiscal `receipt-line/`](../../../fiscal/references/receipt-line/README.md).

- Source: the site https://tasnif.soliq.uz/ (a code's card), the clients in
  [`../common/`](../common/README.md#sources), and the probes in
  [`../sandbox/`](../sandbox/README.md)
- Fetched: 2026-11-04

All paths below are under `https://tasnif.soliq.uz/api/cls-api`.

## Endpoints

| Purpose | Request | Reply shape | Sample |
|---|---|---|---|
| The card with package codes | `GET /mxik/get/by-mxik?mxikCode=<17 digits>&lang=ru` | bare object | [`by-mxik-gtin.ru.json`](../sandbox/by-mxik-gtin.ru.json); fiscal skill: [`tasnif-by-mxik.ru.json`](../../../fiscal/references/sandbox/tasnif-by-mxik.ru.json) |
| Names in all languages, status, dates, package names | `GET /integration-mxik/get/history/<17 digits>` | envelope, `data` object | [`history.json`](../sandbox/history.json), [`history-not-found.json`](../sandbox/history-not-found.json) |
| Picture file names | `GET /integration-mxik/references/get/mxik/picture-names?mxik_code=<17 digits>` | bare array | [`picture-names.json`](../sandbox/picture-names.json) |
| One picture | `GET /integration-mxik/references/get/file/<file name>` | `application/octet-stream` (a PNG of about 410 KB in the probe) | not saved |

## The card: `mxik/get/by-mxik`

One object without an envelope: the level codes and names, `mxikName`, `attributeName`,
`shortName`, `internationalCode` (barcode), `label`, `useCard`, `lgotaId` / `lgotaName`,
`unitCode` / `unitName`, `units`, `myProduct`, `mnnName` and `packages[]`.

| Package field | Notes |
|---|---|
| `code` | the package code, **a number** in the reply; store it as a string (`tasnif.codes-as-strings`) |
| `name` | the label on the card, for example `шт.`, `1 шт.` or `шт. (пакет) 190 грамм` |
| `mxikCode` | the code the package belongs to |
| `parentCode`, `parentValue` | the package this one contains, and how many of it; `null` / the amount for a base package |
| `containerCode`, `containerName`, `containerNamePl`, `containerNamePl2` | the container (`пакет`) and its plural forms; `null` for a plain unit |
| `unitId`, `unitName` | the unit (`шт.`, `грамм`) |
| `isUnitPackage` | `"1"` on base packages in the samples, `"2"` on a container of another package |
| `type`, `childNames`, `childValues`, `children`, `childrenValue` | the containment chain; `&&`-separated in the `*Names` / `*Values` strings |
| `categoryID`, `categoryName`, `checkUser` | not documented |
| `createdAt` | `dd.MM.yyyy HH:mm:ss` text |
| `createdBy` | **who added the package**: a staff member's full name, a hex id or `USER`. Personal data: do not log, store or show it (`tasnif.personal-data`). The sample replaced a name with `USER` |

An unknown code answers **HTTP 403** with `text/plain` `MXIK ma'lumotlari topilmadi`
("MXIK data not found"), not JSON.

Which package to put on a receipt is the seller's choice among the card's packages; see
[fiscal `fiscal.package-code-required`](../../../fiscal/references/lifecycle/README.md#warn-without-being-asked).

## History: `integration-mxik/get/history/{mxik}`

The envelope with one `data` object:

| Field | Notes |
|---|---|
| `mxikCode` | the code |
| `groupNameUz` / `Ru` / `Lat` ... `subPositionNameUz` / `Ru` / `Lat` | level names; `...Uz` in Cyrillic, `...Lat` `null` in the probe |
| `brandName`, `attributeNameUz` / `Ru` / `Lat`, `description` | as on the card |
| `isActive` | `"1"` for the probed code. By its name, whether the code is still in use (derived); treat anything else as "check on the site" |
| `status` | `0` in the probe; meaning not documented |
| `createdAt`, `updatedAt` | `dd.MM.yyyy HH:mm:ss` text, for example `29.04.2022 14:47:09` |
| `updatedBy` | `null` in the probe; may hold a person, treat like `createdBy` |
| `packageNames[]` | `{code, mxikCode, nameUz, packageType, nameRu, nameLat}`; `code` is a number |
| `id` | a 32-character hex string that **changed on every call**; never key or compare on it (`tasnif.history-id-unstable`) |
| `pkey`, `parentPkey` | `null` in the probe |

`lang` changes nothing in this reply. An unknown code is HTTP 200 with
`{"success": false, "code": 0, "reason": "Mxik code not found!", "data": null}`.

This is the call for a scheduled re-check of stored codes: compare `isActive`, `updatedAt`
and the `packageNames[].code` set with what you stored, and send any change to a person
(`tasnif.codes-change`).

## Packages: card and history can differ

For `04016001002000000` on 2026-11-04 the card listed packages `1342705` (`шт.`) and
`1659249` (`1 шт.` in a `пакет`), history listed the same two codes with different names
(`шт.` and `пакет=1 шт.`), and the point-of-sale `cl-api` information listed only
`1342705`. Take the package list from the card and cross-check it with the point-of-sale
reply for the seller (`tasnif.package-lists-differ`, [`../pos/`](../pos/README.md)).

## Pictures

1. `GET /integration-mxik/references/get/mxik/picture-names?mxik_code=<code>` returns a
   JSON array such as `["04016001002000000_1.png", "04016001002000000_2.png", ...]`, or an
   empty array. One client also sends `lang=uz_latn`.
2. `GET /integration-mxik/references/get/file/<file name>` returns the bytes as
   `application/octet-stream`; set your own `Content-Type` from the extension.

Download pictures once and serve your own copy; do not hot-link them into a storefront.
Who owns the pictures and whether you may reuse them is not stated anywhere.
