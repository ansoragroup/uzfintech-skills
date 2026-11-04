# Tasnif testing: saved replies and placeholders

Hand-written notes. Tasnif has **no test host**: the catalogue is the same data for tests
and production. Unit-test your parsers against the replies below, and keep live calls out
of CI.

- Source: one `GET` per request below to the public endpoints on 2026-11-04, one request a
  second; hosts and shapes in [`../common/`](../common/README.md)
- Fetched: 2026-11-04

## Saved replies

Each file is the reply body exactly as received, except where the row says otherwise.
Paths are under `https://tasnif.soliq.uz/api/cls-api` unless the row gives a full URL.

| File | Request | What it shows |
|---|---|---|
| [`elasticsearch-search.ru.json`](elasticsearch-search.ru.json) | `GET /elasticsearch/search?lang=ru&search=хлеб&size=1&page=0` | the envelope with one item and `recordTotal`; flags as strings, no package codes |
| [`by-params-text.ru.json`](by-params-text.ru.json) | `GET /mxik/search/by-params?text=коврик&lang=ru&size=2&page=0` | a Spring page in the envelope, `code` `200`, `reason` `OK`, `packages` `null` |
| [`by-params-gtin.ru.json`](by-params-gtin.ru.json) | `GET /mxik/search/by-params?gtin=4607001771555&lang=ru` | a barcode hit: `code` `0`, `reason` `ok`, `internationalCode` equal to the barcode, the request echoed in the item (`lang` `uz`) |
| [`by-params-gtin-not-found.ru.json`](by-params-gtin-not-found.ru.json) | `GET /mxik/search/by-params?gtin=0000000000000&lang=ru` | no hit: HTTP 200, `success` `false`, `code` `-1`, empty `content` |
| [`search-subposition.ru.json`](search-subposition.ru.json) | `GET /mxik/search-subposition?search_text=коврик&page=0&size=2&lang=ru` | the same page shape as `by-params?text=` |
| [`class-short-info.ru.json`](class-short-info.ru.json) | `GET /class/short-info?groupCode=040&lang=ru` | 17 classes `{code, name, count}` in Russian, `code` and `reason` `null` |
| [`class-short-info.json`](class-short-info.json) | `GET /class/short-info?groupCode=040` | the same classes in Uzbek Cyrillic (no `lang`) |
| [`by-mxik-gtin.ru.json`](by-mxik-gtin.ru.json) | `GET /mxik/get/by-mxik?mxikCode=00901001004004005&lang=ru` | the card of the barcode hit above: one package `1391155` (`шт. (пакет) 190 грамм`, `parentValue` 190 `грамм`). **Changed:** `createdBy` held a person's name and is replaced with `USER` |
| [`history.json`](history.json) | `GET /integration-mxik/get/history/04016001002000000` | names in Uzbek and Russian, `isActive` `"1"`, text dates, `packageNames` `1342705` and `1659249`; the `id` changes on every call |
| [`history-not-found.json`](history-not-found.json) | `GET /integration-mxik/get/history/99999999999999999` | HTTP 200, `success` `false`, `reason` `Mxik code not found!` |
| [`picture-names.json`](picture-names.json) | `GET /integration-mxik/references/get/mxik/picture-names?mxik_code=04016001002000000` | a bare array of three file names |
| [`information.ru.json`](information.ru.json) | `GET https://tasnif.soliq.uz/api/cl-api/integration-mxik/get/information?mxikCode=04016001002000000&lang=ru` | the point-of-sale reply: one package (`1342705`) where the card has two, epoch-millisecond dates, `permitted` `false` |
| [`information-two-packages.ru.json`](information-two-packages.ru.json) | the same with `mxikCode=10406001002000000` | a service code with two packages (`услуга (сум)`, `услуга (раз)`) |
| [`information-not-found.ru.json`](information-not-found.ru.json) | the same with `mxikCode=99999999999999999` | HTTP 200, `success` `true`, `data` `[]`, `recordTotal` `0` |
| [`cl-api-class-search.json`](cl-api-class-search.json) | `GET https://tasnif.soliq.uz/api/cl-api/class/search?keyword=коврик&page=0&size=2&lang=ru` | HTTP 404, Spring's error JSON |
| [`dv-cert-number-empty.ru.json`](dv-cert-number-empty.ru.json) | `GET /mxik/search/dv-cert-number?lang=ru` | HTTP 200, `success` `false`, `code` `400`, `empty cert number` |
| [`is-vat.json`](is-vat.json) | `GET https://txkm.soliq.uz/api/txkm-api/ccm-api/info/check/is-vat/<TIN>` | a VAT payer: `data` `true`, `percent`, three undocumented fields. The TIN is not saved |

Not saved, because they are not JSON:

| Request | Reply |
|---|---|
| `GET /mxik/get/by-mxik?mxikCode=99999999999999999&lang=ru` | HTTP 403, `text/plain`: `MXIK ma'lumotlari topilmadi` |
| `GET /class/search?keyword=коврик&page=0&size=2&lang=ru` | HTTP 403, `text/plain`: `Синф коди хато жўнатилган` |
| `GET /integration-mxik/references/get/file/04016001002000000_1.png` | HTTP 200, `application/octet-stream`, a PNG of 419777 bytes |

The fiscal skill keeps two more Tasnif replies:
[`tasnif-by-mxik.ru.json`](../../../fiscal/references/sandbox/tasnif-by-mxik.ru.json) (the
card of `04016001002000000` with both packages) and
[`tasnif-search.ru.json`](../../../fiscal/references/sandbox/tasnif-search.ru.json) (a text
search for `коврик`).

```text
scripts/tasnif.py gtin --file references/sandbox/by-params-gtin.ru.json
scripts/tasnif.py code --file references/sandbox/by-mxik-gtin.ru.json
scripts/tasnif.py history --file references/sandbox/history.json
scripts/tasnif.py info --file references/sandbox/information.ru.json
scripts/tasnif.py --selftest
```

## Rules for tests

- No test host exists. Unit tests read these files; an integration test that calls the
  live site runs by hand, rarely, one request at a time
  (`tasnif.throttle-and-cache`).
- The search results, record counts, package lists and dates change as the catalogue is
  edited. Do not assert them in tests that call the live endpoints; assert the shape.
- Never put a real TIN, PINFL, terminal ID or a person's name in a fixture. Use `<TIN>`
  and `<ID>`; replace `createdBy` and `updatedBy` with `USER` (`tasnif.personal-data`).
- The key order inside the Spring page objects (`pageable`, `sort`) changed between two
  identical calls. Compare parsed JSON, never raw bytes or hashes of a page reply.
- Do not key fixtures on the `history` `id`; it differs on every call
  (`tasnif.history-id-unstable`).
- Re-check every code in your fixtures with the fiscal skill's `scripts/mxik.py check`.
