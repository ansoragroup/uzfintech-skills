# Tasnif at the point of sale: seller check, VAT-payer check, partner endpoints

Hand-written notes. These are the calls cash-register software makes when a product is set
up for a seller. Hosts and shapes: [`../common/`](../common/README.md). What goes on the
receipt itself: [fiscal skill](../../../fiscal/SKILL.md).

- Source: the clients in [`../common/`](../common/README.md#sources) (mainly
  `IsMaN-programmer/pos_terminal_v2` `src/components/AdminStock.tsx` and
  `AbduxalilVoxidjonov/ishonchproject`), and the probes in
  [`../sandbox/`](../sandbox/README.md)
- Fetched: 2026-11-04

## Endpoints

| Purpose | Request | Reply shape | Sample |
|---|---|---|---|
| A code for one seller or till | `GET https://tasnif.soliq.uz/api/cl-api/integration-mxik/get/information?mxikCode=<17 digits>&lang=ru[&tin=<TIN>][&terminalId=<ID>]` | envelope with `data[]` and `permitted` | [`information.ru.json`](../sandbox/information.ru.json), [`information-two-packages.ru.json`](../sandbox/information-two-packages.ru.json), [`information-not-found.ru.json`](../sandbox/information-not-found.ru.json) |
| Is a TIN a VAT payer | `GET https://txkm.soliq.uz/api/txkm-api/ccm-api/info/check/is-vat/<TIN>[?terminalId=<ID>]` | flat object | [`is-vat.json`](../sandbox/is-vat.json) |

Both are unauthenticated `GET`s. The `tin` / `<TIN>` is a taxpayer's identifier: use your
own merchant's TIN only, never log other people's, and use `<TIN>` in code samples and
fixtures (`tasnif.personal-data`). The probes used no `tin` for `information`.

## `cl-api` information

Envelope `{success, code: 200, reason: null, data[], recordTotal, errors, permitted}`.
Each `data[]` item:

| Field | Notes |
|---|---|
| `mxik`, `name`, `description`, `internalCode` | the code (named `mxik` here, not `mxikCode`) and its name |
| `label`, `usePackage`, `cashSale` | numbers (`0`, `1`). By their names: needs marking codes, sold by package code, may be sold for cash (derived; not documented) |
| `recipeBoxId` | `null` in the probes; not documented |
| `createdAt`, `updateAt` | epoch milliseconds (note the spelling `updateAt`) |
| `packages[]` | `{code, mxikCode, nameUz, packageType, nameRu, nameLat}`; `code` is a number |

`permitted` sits next to `data`, not inside it. It was `false` in every probe without `tin`
and `terminalId`. The client that reads it accepts `true`, `1` or `"true"`. What makes it
`true`, and whether a seller may sell a code when it is `false`, is not documented: show it
to the person setting up the product, do not block sales on it
(`tasnif.permitted-needs-seller`).

The package list here can be **shorter** than the card's: one package here, two on the
card for `04016001002000000`. Two packages (`1508539` and `1508540`, `услуга (сум)` and
`услуга (раз)`) for the service code `10406001002000000`. Warning
`tasnif.package-lists-differ`.

An unknown code is `success: true` with `data: []` and `recordTotal: 0`, so check the list,
not `success`.

Optional `text` / `search_text` parameters appear in one client; they were not probed.

## txkm VAT-payer check

```json
{"success": true, "reason": "So'rov bajarildi", "data": true, "percent": 12,
 "cashSaleAllowed": false, "fractionalSale": false, "baseCalculationAmount": 440000}
```

| Field | Notes |
|---|---|
| `data` | `true`: the TIN is registered as a VAT payer on the day of the call (by the client's use, derived) |
| `percent` | the VAT rate the service returns for that payer |
| `cashSaleAllowed`, `fractionalSale`, `baseCalculationAmount` | not documented |

`reason` is Uzbek ("request done"). The reply has no `code` and no `errors`.

Use it to pre-fill the VAT setting of a new seller and show it for confirmation. Status can
change; re-check it on a schedule, not per sale. The rate on each receipt line is the
accountant's decision (`tasnif.no-tax-advice`, fiscal `fiscal.vat-per-product`).

## Partner-only endpoints

Seen in code, not probed, and not usable without credentials from the tax committee or a
cash-register operator:

| Request | Auth in the clients | Purpose (from the client) |
|---|---|---|
| `GET https://tasnif.soliq.uz/api/cl-api/marking/validation-onkm` | a username and password in the client's configuration | validate a marking code |
| `https://tasnif.soliq.uz/api/cl-api/marking/*` | an `Authorization` token passed through | marking-code calls proxied by a POS backend |
| `POST https://tasnif.soliq.uz/api/cl-api/integration-kcm/kcm` | none seen | a construction-materials catalogue (KCM) |

For marking codes on receipts, see the
[fiscal skill](../../../fiscal/SKILL.md) (`fiscal.marked-goods-need-codes`). Do not reuse
credentials found in public repositories.
