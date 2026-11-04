# Fiscal testing: where receipts can be tested, and sample data

Hand-written notes. A receipt registered on a production fiscal module is a real tax
record, even when the payment was a test. Test fiscalization only where a provider offers a
test host, and mock the provider's fiscal replies everywhere else. Warning
[`fiscal.test-fiscalization-only-in-tests`](../lifecycle/README.md#warn-without-being-asked).

- Source: the provider sandbox pages linked in each row; the two Tasnif replies below
- Fetched: 2026-11-04

## Test fiscalization per provider

| Provider | Test fiscalization | What the provider's sandbox page gives |
|---|---|---|
| [Uzum Fiscalization](../../../uzum/references/sandbox/README.md#fiscalization) | **yes**: test host `https://test-ofd.ipt-merch.com`, test key and test SPIC values from the Uzum manager | the receipts Uzum expects to see on the test host before go-live (sale, refund, discount and voucher variants) |
| [Uzum Checkout](../../../uzum/references/sandbox/README.md) | test terminal; the minimum test plan includes an auto-fiscalization cart that does not match `amount` (`3059`); whether the test terminal registers receipts is not stated | the Checkout test plan |
| [Payme](../../../payme/references/sandbox/README.md) | test host `test.paycom.uz`; whether it registers receipts is not stated | vendor `detail` and `SetFiscalData` sample values |
| [Alif](../../../alif/references/sandbox/README.md) | dev host `api-dev.alifpay.uz`; whether it registers receipts is not stated | receipt items with sample `spic` values |
| [Multicard](../../../multicard/references/sandbox/README.md) | dev host; whether it registers receipts is not stated | `ofd` items with sample `mxik` / `package_code` |
| [Click](../../../click/references/sandbox/README.md) | none documented for fiscalization | `submit_items`, `submit_qrcode` and `get_ofd_data` sample values |
| [Octo](../../../octo/references/sandbox/README.md) | no test fiscal object; `test: true` coverage of `fiscal-data` not stated | `basket` item and `fiscal-data` reply samples |
| [Atmos](../../../atmos/references/sandbox/README.md) | no sandbox host documented | one `ofd_items` sample line |
| [Paynet](../../../paynet/references/sandbox/README.md) | nothing published about receipts | - |

## Rules for tests

- Never point tests, CI or staging at a production fiscal module or a production
  fiscalization endpoint. Octo's missing `test: true` moves real money
  (`octo.test-flag-real-money`); a forgotten switch on a fiscal call registers a real
  receipt.
- Where no test host exists, unit-test your receipt builder against the provider's sample
  items and stub the provider's fiscal reply; the first real receipt comes from the first
  real sale.
- Never use real customer phone numbers, real TIN / PINFL of other people, or scanned
  marking codes of goods you did not sell. Use the provider's sample values and the
  placeholder phone `998901234567`.
- Receipt links in fixtures use placeholders, as in
  [`../receipts/`](../receipts/README.md#the-receipt-link-ofdsoliquz).
- Re-check every MXIK in your fixtures with `scripts/mxik.py check`; the codes in vendor
  samples are not guaranteed to be valid today.

## Sample MXIK codes in vendor samples

Codes as printed in the provider samples (for building only; confirm on Tasnif before any
real use):

| Code | Where | Package code in the sample |
|---|---|---|
| `00702001001000001` | Payme `detail` (IKPU) | `"123456"` |
| `00305001001000000` | Octo `basket` | `"1425207"` |
| `08517001001000000` | Alif receipt item | - |
| `06401004002000000`, `06401002004000000` | Multicard `ofd` | `"1506113"`, `"1519041"` |
| `10107002001000000` | Multicard `ofd` (delivery service) | `"1209885"` |
| `02710001003000000` | Multicard partial refund | `1282118` (a number in that sample) |

The Payme code ends in `001`, so it is an identification code, not a base code (derived
from the digit levels).

## Tasnif replies (public classifier data)

Exact replies of the public Tasnif endpoints, saved unchanged on 2026-11-04 with `lang=ru`.
They contain classifier data only, no personal data. They are what
[`../../scripts/mxik.py`](../../scripts/mxik.py) `lookup --file` reads and what the
[`../mxik/`](../mxik/README.md) page describes.

| File | Request | What it shows |
|---|---|---|
| [`tasnif-by-mxik.ru.json`](tasnif-by-mxik.ru.json) | `GET https://tasnif.soliq.uz/api/cls-api/mxik/get/by-mxik?mxikCode=04016001002000000&lang=ru` | one code (Коврик для мыши) with level codes and two packages: `1342705` (`шт.`, `isUnitPackage` `"1"`) and `1659249` (`пакет` of 1 `шт.`, `parentCode` `1342705`) |
| [`tasnif-search.ru.json`](tasnif-search.ru.json) | `GET https://tasnif.soliq.uz/api/cls-api/elasticsearch/search?search=коврик&size=2&lang=ru` | the search envelope with 2 of `recordTotal` 118 items, no package codes; `label` / `useCard` as strings |

```text
scripts/mxik.py lookup --file references/sandbox/tasnif-by-mxik.ru.json
scripts/mxik.py lookup --file references/sandbox/tasnif-search.ru.json
```

The search results, the record count and the package lists change as the catalogue is
edited; do not assert them in tests that call the live endpoints.
