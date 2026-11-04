# Tasnif: hosts, reply shapes, errors, caching and sources

Hand-written notes. They apply to every endpoint in this skill. Search endpoints:
[`../search/`](../search/README.md). The code card, history and pictures:
[`../code/`](../code/README.md). Point-of-sale checks: [`../pos/`](../pos/README.md).
Saved replies: [`../sandbox/`](../sandbox/README.md).

- Source: the requests the site https://tasnif.soliq.uz/ makes, the open-source clients
  pinned in [Sources](#sources), and one probe of each endpoint (one request a second,
  `GET` only) whose replies are in [`../sandbox/`](../sandbox/README.md)
- Fetched: 2026-11-04
- Spec: none. No API reference, Swagger file, terms of use or rate limits were found on
  soliq.uz, tasnif.soliq.uz or lex.uz; `/api/cls-api/swagger-ui` answers 404. Paths,
  parameters and fields are exact; what a field means is derived from the replies and the
  clients unless a cell says otherwise. Warning
  [`tasnif.not-official-api`](../lifecycle/README.md#warn-without-being-asked).

## Hosts

| Base | What | Notes |
|---|---|---|
| `https://tasnif.soliq.uz/api/cls-api` | the catalogue: search, code card, history, pictures, classes | an older alias, `https://api-tasnif.soliq.uz/cls-api`, appears in client code (not probed) |
| `https://tasnif.soliq.uz/api/cl-api` | point of sale: `integration-mxik/get/information` per seller or till | alias `https://api-tasnif.soliq.uz/cl-api` in client code (not probed); unknown paths answer 404 in Spring's JSON error format |
| `https://txkm.soliq.uz/api/txkm-api` | cash-register service: VAT-payer check by TIN | a different service; see [`../pos/`](../pos/README.md) |

- No auth, no cookies, no API key. Send `Accept: application/json` and a `User-Agent` that
  names your product.
- There is no test host. The catalogue is the same for tests and production; use the
  saved replies for unit tests.
- Keep every base URL in configuration. Clients in the wild use both host forms.

## Reply shapes

Three shapes, depending on the endpoint. Parse each endpoint with its own shape.

| Shape | Looks like | Endpoints |
|---|---|---|
| Envelope | `{"success", "code", "reason", "data", "recordTotal", "errors"}` | `elasticsearch/search`, `class/short-info`, `integration-mxik/get/history/{mxik}`, `cl-api` information (adds `permitted`) |
| Page in the envelope | the envelope, with `data` as a Spring page: `content[]`, `totalElements`, `totalPages`, `number`, `size`, `first`, `last`, `empty`, `pageable` | `mxik/search/by-params`, `mxik/search-subposition` |
| Bare | a JSON object or array, no envelope | `mxik/get/by-mxik` (object), `references/get/mxik/picture-names` (array of file names) |

The envelope `code` and `reason` are not consistent between endpoints:

| Endpoint | `success` | `code` | `reason` |
|---|---|---|---|
| `elasticsearch/search`, `history` | `true` | `200` | `success` |
| `by-params?text=`, `search-subposition` | `true` | `200` | `OK` |
| `by-params?gtin=` with a hit | `true` | `0` | `ok` |
| `by-params?gtin=` without a hit | `false` | `-1` | `not data found` |
| `class/short-info` | `true` | `null` | `null` |
| `cl-api` information | `true` | `200` | `null` |

Decide on `success` and on the data (`data` not `null`, `content` or the list not empty),
never on `code` alone.

## Language

`lang` takes `ru` and `uz` in every client. What changes:

- Without `lang`, `class/short-info` names come in Uzbek Cyrillic; with `lang=ru`, in
  Russian.
- `history` returns `...Uz` and `...Ru` names whatever `lang` is; the `...Lat` fields were
  `null` in the probe, except the package `nameLat`.
- `by-params?gtin=` echoes `"lang": "uz"` in each item even when `lang=ru` was sent, and
  still returns Russian names.
- `uz_latn` appears in one client for `picture-names`; it was not probed.
- `elasticsearch/search` puts all three languages in one `fullName` string.

## Not found and errors

| Endpoint | Unknown code or empty input | HTTP | Body |
|---|---|---|---|
| `mxik/get/by-mxik` | unknown `mxikCode` | 403 | `text/plain`: `MXIK ma'lumotlari topilmadi` |
| `integration-mxik/get/history/{mxik}` | unknown code | 200 | `{"success": false, "code": 0, "reason": "Mxik code not found!", "data": null}` |
| `mxik/search/by-params?gtin=` | no hit | 200 | `success: false`, `code: -1`, empty `content` |
| `cl-api` information | unknown `mxikCode` | 200 | `success: true`, `data: []`, `recordTotal: 0` |
| `mxik/search/dv-cert-number` | no certificate number | 200 | `{"success": false, "code": 400, "reason": "empty cert number"}` |
| `cls-api` `class/search` | any request | 403 | `text/plain`: `Синф коди хато жўнатилган` (the class code is sent wrong) |
| `cl-api` `class/search` | any request | 404 | Spring error JSON: `timestamp`, `status`, `error`, `message`, `path` |

So a 403 can mean "no such code" on one endpoint and "bad request" on another, and a 200
can be a miss. Warning
[`tasnif.check-body-not-status`](../lifecycle/README.md#warn-without-being-asked).

Network failures, 5xx and HTML pages from a proxy are possible like on any public site;
treat anything that is not the expected JSON shape as "unknown, retry later", not as "no
such code".

## Code structure in the replies

The level codes in each reply are prefixes of the 17-digit code:

| Field | Digits | Example (`04016001002000000`) |
|---|---|---|
| `groupCode` | 3 | `040` |
| `classCode` | 5 | `04016` |
| `positionCode` | 8 | `04016001` |
| `subPositionCode` | 11 | `04016001002` |
| `brandCode` | 14 | `04016001002000` |
| `mxikCode` / `mxik` | 17 | `04016001002000000` |

What each level means and how to check a code offline:
[fiscal `mxik/`](../../../fiscal/references/mxik/README.md) and `scripts/mxik.py check` in
the fiscal skill.

## Politeness and caching

No limits are published. Warning
[`tasnif.throttle-and-cache`](../lifecycle/README.md#warn-without-being-asked).

- One request at a time per process, at most about one a second, with a timeout
  (20 s in `scripts/tasnif.py`).
- Cache card and history replies per code for at least a day; cache searches per query.
- On a timeout, 5xx or an unexpected body, back off (for example 1 min, 5 min, 30 min)
  and keep the last good value.
- Do not crawl the catalogue. For a full list, ask the tax committee for an export or
  use the site's own download, if it offers one for your account.

## Sources

The site was read on 2026-11-04. Every client below is pinned to the commit that was read;
none is published by the tax committee, and none was reviewed for licence or quality.

| Repository @ commit | File | Shows |
|---|---|---|
| [aslon1213/tasnifuz-search](https://github.com/aslon1213/tasnifuz-search/blob/8fb2a52153b1aef1b2e7cba5c759e5242696917e/tsuz_search/client.py) | `tsuz_search/client.py` | `elasticsearch/search`, `by-params`, `dv-cert-number`, `history` |
| [azabroflovski/mxik-js](https://github.com/azabroflovski/mxik-js/blob/58da9cca7e491122685a8e4bc8c493685ae43b42/packages/mxik/lib/http.ts) | `packages/mxik/lib/http.ts` | the `cls-api` base URL as the npm `mxik` default |
| [InomjonQurbonov/Bussines_task](https://github.com/InomjonQurbonov/Bussines_task/blob/9b277f9f4366e0e1f57626b6e3ab16b491ae361e/product_code/views.py) | `product_code/views.py` | `by-mxik`, `search-subposition` |
| [DilyorbekAbdujabborov/tg_store](https://github.com/DilyorbekAbdujabborov/tg_store/blob/eecd1c7387eba6afd7cc99489687171f97373ffb/server.js) | `server.js` | `elasticsearch/search`, `picture-names` |
| [abbouse/kitobchi-laravel](https://github.com/abbouse/kitobchi-laravel/blob/a593b220026a0bd4bfaa2f2a9153a2c5d4809bdd/scripts/ofd_ikpu_suggest.php) | `scripts/ofd_ikpu_suggest.php` | `by-params`, `search-subposition` |
| [sanedidi/super-market](https://github.com/sanedidi/super-market/blob/1fdaff0983cb50e45b2a773fda63094f69feb4cb/docs/api.md) | `docs/api.md` | `by-params`, `picture-names` |
| [hbncompany/uztools](https://github.com/hbncompany/uztools/blob/cd8ab09dbf39be29e69fc42739a85c3718b53a6c/lib/api_service.dart) | `lib/api_service.dart` | `by-params`, `dv-cert-number`; `lib/mxik_search_screen.dart` names an unverified `api.tasnif.soliq.uz/api/v1/mxik/details` |
| [pharmacosmos-dev/pharma-crm-backend](https://github.com/pharmacosmos-dev/pharma-crm-backend/blob/a935b83a975127fe22008e1c3433a6e4f7fc82cb/internal/controller/http/v1/helper.handler.go) | `internal/controller/http/v1/helper.handler.go` (lines 2218, 2244) | `picture-names` with `lang=uz_latn`, `references/get/file/<name>` |
| [jamshidbekml/webkassa](https://github.com/jamshidbekml/webkassa/blob/d1ecff912df3ade11e8db70b9a7edfecdcf712d5/src/api/shared/utils/get-category-name.ts) | `src/api/shared/utils/get-category-name.ts` | `class/short-info` |
| [taxirov/e-mall](https://github.com/taxirov/e-mall/blob/1cd327aef7901c4dc62e75272d27d9d861990843/src/lib/soliq.ts) | `src/lib/soliq.ts` | `attribute/web-katalog` (not probed) |
| [IsMaN-programmer/pos_terminal_v2](https://github.com/IsMaN-programmer/pos_terminal_v2/blob/24f08d5a31f3357313854908425973bdbc01c1eb/src/components/AdminStock.tsx) | `src/components/AdminStock.tsx` (lines 279, 288, 313, 369) | `history`, then `cl-api` information with `tin` and `terminalId`, the txkm VAT check, `permitted` read as `true`, `1` or `"true"` |
| [AbduxalilVoxidjonov/ishonchproject](https://github.com/AbduxalilVoxidjonov/ishonchproject/blob/a3fd043c3abc09c903ba28afde5b90cd2e29ef5c/fiskal/EPOS%20fiskallash%20integratsiya.md) | `fiskal/EPOS fiskallash integratsiya.md` | `cl-api` information in a fiscal module integration |
| [QANOT/qanot](https://github.com/QANOT/qanot/blob/2044d677327bf8d68d3fcac8176a8fde7f32e7d6/qanot/tools/local_ikpu.py) | `qanot/tools/local_ikpu.py` | `cl-api` `class/search?keyword=` (answered 404 on 2026-11-04) |
| [Farhod2521/FASTAPI-](https://github.com/Farhod2521/FASTAPI-/blob/36cc6a0e4d70fceb5973f80d4e938bec99237a7a/endpoints/app_main.py) | `endpoints/app_main.py` | `POST integration-kcm/kcm` (not probed) |

Some of these repositories commit credentials or internal addresses. Do not copy anything
from them except the public paths and field names recorded here.
