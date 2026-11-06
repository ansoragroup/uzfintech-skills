# Direct OFD integration (own virtual fiscal module, ВФМ)

Read this when a marketplace, payment system or e-commerce platform registers receipts
itself on the operator of fiscal data (ОФД, ofd.uz) instead of letting a payment provider
do it. The integrator gets a virtual fiscal module (ВФМ, `TerminalID`), signs every
receipt with its own certificate and sends it to the ОФД over HTTPS or WebSocket. If a
payment provider already registers the receipt, do not also send it here
(`fiscal.one-receipt-per-payment`).

- Source: ОФД "Инструкция по интеграции", version 6.5,
  https://docs.google.com/document/d/1YjRCRO3xaGNpSQ-jGxtNn_nPY-4Df47mpmtiKF05wbY/edit
- Swagger of the registration API: https://txkm.soliq.uz/api/txkm-api/swagger-ui.html#/
- Swagger of the classifier API: https://tasnif.soliq.uz/api/cl-api/swagger-ui/index.html?configUrl=/api/cl-api/v3/api-docs/swagger-config
- Fetched: 2026-11-06

The instruction names the parties ЭТП (electronic trading platform), ЭПС (electronic
payment system), ВК (virtual cash register), ОФД and ВФМ. Field names, codes and JSON
below are quoted from it; values are the instruction's own samples or placeholders.

## Onboarding

1. Send a letter to ofd.uz asking to connect.
2. Sign the contract with the ОФД.
3. The ОФД sends this instruction and the login and password for the txkm API; give the
   ОФД the IP addresses you will call from (they are whitelisted).
4. Get a **test** certificate ([registration](#registration-api-txkm)) and send test
   receipts to the test host: sale, refund, advance and credit.
5. Ask the ОФД for its conclusion (заключение) on the test results.
6. Pay the yearly fee for the production certificate through the Paynet ЭПС.
7. Send a letter to the Tax Committee.
8. Get the production certificate.
9. Start fiscalization.

## Certificate

Generate an RSA 2048 key and a PKCS#10 CSR; the instruction's example:

```sh
openssl req -new -newkey rsa:2048 -nodes -keyout user-etp.key -out user-etp.csr \
  -subj "/CN=OOO User1 Market/UID=user_1_id"
```

- The CSR goes into the registration request; the issued certificate's CN is the ВФМ
  number (`TerminalID`, 14 characters, for example `EZ000000000043`).
- A certificate is valid for **one year**. The renewed certificate is a **new ВФМ**, and
  `ReceiptSeq` starts again at 1.
- Keep the private key out of the repository and logs; it signs tax records.

## Signing

Every body (QRPaymentInfo, ReceiptInfo, DReportInfo) is a JSON file wrapped in an attached
CMS (PKCS#7) signature, DER, without certificates:

```sh
openssl cms -sign -nodetach -binary -in ReceiptInfo.json -text -outform der \
  -out ReceiptInfo.p7b -nocerts -signer user-etp.crt -inkey user-etp.key
```

The same command signs `QRPaymentInfo.json` and `DReportInfo.json`.

## Endpoints

### Test host (documented)

| Operation | Request |
|---|---|
| Payment notice (QRPaymentInfo) | `POST https://test.ofd.uz/emp/v2/QRPayment` |
| Receipt (ReceiptInfo) | `POST https://test.ofd.uz/emp/v3/receipt` |
| Receipt over WebSocket | `wss://test.ofd.uz/ws/emp/v3/receipt` |
| Daily report (DReportInfo) | `POST https://test.ofd.uz/emp/v3/dreport` |

```sh
curl --cacert test.ofd.uz-root.crt -H "Content-Type: application/octet-stream" \
  --data-binary @ReceiptInfo.p7b https://test.ofd.uz/emp/v3/receipt
```

- Body: the signed `.p7b`, `Content-Type: application/octet-stream`.
- `test.ofd.uz-root.crt`: the root certificate of the test host; the instruction says to
  save it from https://test.ofd.uz/ in the browser (lock icon). Pin it in the HTTP client.
- WebSocket: binary frames; each frame is a 16-byte `RequestId` followed by the signed
  receipt, and the reply echoes the same `RequestId`. Use it to match replies to receipts.
- The **production host is not in the instruction**; the ОФД gives it with the production
  certificate. Keep the host in configuration, never in code.

## QRPaymentInfo (payment notice)

| Field | Type | Notes |
|---|---|---|
| `PaymentId` | string(36) | `[A-Za-z0-9-]`, your payment ID |
| `PaidSum` | uint64 | tiyin |
| `DateTime` | string | `YYYY-MM-DD HH:MM:SS`, UTC+5 |
| `TIN` / `PINFL` | string(9) / string(14) | seller; PINFL for a sole proprietor |
| `PhoneNumber` | string(12) | `998901234567` |
| `Location` | object | `Latitude`, `Longitude`, optional |
| `SalePointAddress` | string(128) | |
| `IsRefund` | 0 / 1 | |
| `ReceiptInfo` | object | `TerminalID` (14), `ReceiptSeq` (16) of the receipt it belongs to |

Reply: `{"Code": 0, "Message": "accepted", "TerminalID": "...", "DateTime": "20220302113650", "PaymentId": "..."}`.

## ReceiptInfo (the receipt)

### Top level

| Field | Type | Notes |
|---|---|---|
| `ReceiptSeq` | uint64 | per ВФМ, starts at 1, +1 per receipt (refunds too); max `999999999999`, then a new CSR and certificate and restart at 1 |
| `IsRefund` | 0 / 1 | |
| `ReceiptType` | byte | `0` sale or refund, `1` advance, `2` credit |
| `AdvanceContractID` | string | required for advances and for the sale that closes them |
| `Items` | array | [items](#item) |
| `ReceivedCash`, `ReceivedCard` | uint64 | tiyin |
| `TotalVAT` | uint64 | tiyin |
| `Time` | string | `YYYY-MM-DD HH:MM:SS`, UTC+5 |
| `RefundInfo` | object | only when `IsRefund` is 1, absent otherwise |
| `SaleReceiptInfo` | object | required for `ReceiptType` 2 |
| `ConsumerInfo` | object | required for gas and electricity suppliers |
| `Location`, `TaxiInfo`, `ExtraInfo`, `MerchantInfo`, `PickupPointInfo`, `QRPaymentOnSiteInfo` | object | optional, by business type |

### Item

| Field | Type | Required | Notes |
|---|---|---|---|
| `Name` | string(63) | yes | the unit of measure at the end of the name |
| `Barcode` | string(13) | no | EAN-13 |
| `Labels` | string(21)[] | no | marking codes, up to 300 |
| `SPIC` | string(17) | yes | the MXIK, [mxik](../mxik/README.md) |
| `Units` | uint64 | no | |
| `PackageCode` | string(20) | yes | from the code's Tasnif card |
| `OwnerType` | byte | yes | "see the reference list"; the list is not in the instruction |
| `GoodPrice` | uint64 | yes | unit price |
| `Price` | uint64 | yes | line total before discounts |
| `Amount` | uint64 | yes | quantity × 1000 |
| `VAT` | uint64 | yes | VAT amount |
| `VATPercent` | byte | yes | from the seller's tax settings |
| `Discount`, `Other`, `Voucher` | uint64 | no | `Other`: other discounts, such as insurance |
| `CommissionInfo` | object | for commission sales | the principal's `TIN` (9) or `PINFL` (14), [commission](#commission-sales) |

Units: money fields (`Price`, `GoodPrice`, `VAT`, `Discount`, `Other`, `Voucher`,
`ReceivedCash`, `ReceivedCard`, `CashedOutFromCard`) are tiyin (× 100). `Amount` is ×
1000 in the item's unit: 1 шт = `1000`, 0.5 кг = `500`, 125 г = `125`, 1.5 л = `1500`.
The instruction checks sums and discounts against a formula that is published as an image
and is not in the text; the text keeps only its tolerance, `10000` (100 сум).

### Sub-objects

| Object | Fields |
|---|---|
| `RefundInfo` | `TerminalID` (14), `ReceiptSeq` (string), `DateTime` `YYYYMMDDHHMMSS`, `FiscalSign` (12; only for `ReceiptType` 0, empty otherwise) of the original receipt |
| `SaleReceiptInfo` | the same four fields of the original sale, all required |
| `ExtraInfo` | `PhoneNumber` (required), `Other` (14), `CashedOutFromCard`, `CardType` (`1` corporate, `2` personal, `3` social; required for card payments), `CardNumber` (masked `8600********1234`, required for social cards), `PPTID` (required for card payments) |
| `MerchantInfo` | `TIN`, `PINFL`, `Name` (32), `ContractDate`, `ContractNumber` (32) |
| `PickupPointInfo` | `Address` (64), `RegionCode`, `DistrictCode` |
| `ConsumerInfo` | `PINFL`, `AccountNumber` (32), `CadastralNumber` (64) |
| `TaxiInfo` | `TIN`, `PINFL`, `CarNumber` (8), `TripDetailsInfo` with start and end `TripAddressInfo` (`Location`, `Address` 256, `Name` 256, `ID` 63) and `AddressLang` `UZB` / `RUS` / `ENG` |
| `QRPaymentOnSiteInfo` | `QRCodeID` (63), `RegionCode`, `DistrictCode`, `VillageCode` |

Region and district codes come from the txkm `region` list.

### Refunds, advances and credit

- `TerminalID` + `ReceiptSeq` is the unique key of a receipt at the ОФД.
- A refund is a **new receipt** with the next `ReceiptSeq`, `IsRefund` 1 and `RefundInfo`
  of the original. Example from the instruction: after sales 1 to 6, receipt 7 refunds
  receipt 3.
- Advances (`ReceiptType` 1) of one deal share an `AdvanceContractID`; a sale
  (`ReceiptType` 0) with the same ID closes them. Credit payments (`ReceiptType` 2) carry
  the original sale in `SaleReceiptInfo`.

| `ReceiptSeq` | Type | `AdvanceContractID` | `SaleReceiptInfo` | What happens |
|---|---|---|---|---|
| 1, 2 | 0 | | | ordinary sales |
| 3, 5 | 1 | `AAAAAAAAAAA` | | first and second advance for product P3 |
| 6 | 0 | `AAAAAAAAAAA` | | sale that closes advances 3 and 5 |
| 12 | 0 | | | sale of P6 on credit |
| 13, 14, 16 | 2 | | receipt 12 | credit instalments |

### Reply

```json
{"Code": 0, "Message": "accepted", "TerminalID": "EZ000000000043", "ReceiptSeq": "14",
 "DateTime": "20220302113650", "FiscalSign": "852425411426",
 "QRCodeURL": "https://ofd.soliq.uz/epi?t=EZ000000000043&r=2&c=20220302113650&s=852425411426"}
```

- Store `TerminalID`, `ReceiptSeq`, `DateTime` and `FiscalSign`; a later refund or credit
  receipt needs them.
- `QRCodeURL` arrives JSON-escaped (`&`); a JSON parser unescapes it, string copying
  does not. It is the [receipt link](../receipts/README.md#the-receipt-link-ofdsoliquz).
- Advance and credit receipts get `FiscalSign` `""` and no `DateTime`.

## DReportInfo (daily report)

`ReportDate` `YYYY-MM-DD`, `TotalCount`, and `PurchaseReceipt`, `AdvanceReceipt`,
`CreditReceipt`; each has `Sale` (required) and `Refund` (optional), each of those
`Count`, `Cash`, `Card`, `VAT` in tiyin. Reply: `Code`, `Message`, `TerminalID`,
`ReportDate`. Build it from your stored accepted receipts of that day.

## Reply codes and retries

| `Code` | Meaning | What to do |
|---|---|---|
| 0 | accepted | store the reply |
| 1 | I/O error | resend the same receipt |
| 2, 3 | PKCS#7 format or structure | fix signing; do not resend unchanged |
| 4 | service error | retry later with the same `ReceiptSeq` |
| 5 | signature check failed | the certificate expired or is invalid; renew it |
| 6 | JSON structure | fix the builder |
| 10 | field values | fix the values (sums, codes, units) |
| 11 | postpone | resend later |
| 12 | record not found or expired | check the referenced receipt |
| 20, 21 | cannot reach or read the ЭПС | retry later |
| 30 | IKPU (MXIK) error | check `SPIC` and `PackageCode` with `scripts/mxik.py` and Tasnif |
| 100 | receipt more than 24 h older than server time | set the current `Time`, sign again, resend |
| 101 | receipt type not accepted | check `ReceiptType` |

Keep a queue per ВФМ: assign `ReceiptSeq` once, persist it before sending, and resend that
same number on codes 1, 4, 11, 20 and 21. A gap or a reused number on a ВФМ breaks the
sequence the ОФД expects. Send receipts right after payment; code 100 rejects anything
older than 24 hours (`fiscal.ofd-receipt-24h`).

## Registration API (txkm)

Base: `https://txkm.soliq.uz/api/txkm-api` (Swagger linked above). Log in at `/auth/login`
with the ОФД-issued login and password and send `Authorization: Bearer <TOKEN>`. Only
whitelisted IPs are accepted.

| Method | Purpose |
|---|---|
| `/emr-api/application/add/test` | apply for a **test** certificate |
| `/emr-api/application/add` | apply for a production certificate |
| `/emr-api/application/update` | change the legal address (same fields as `add`) |
| `/emr-api/application/download` | download the certificate: `Id`, `isTest` `true` / `false` |
| `/emr-api/application/logout` | deregister a ВФМ: `terminalId`, `phone`; reply `data`, `reason`, `success` |
| `/emr-api/application/region` | region and district codes |
| `/emr-api/application/activity-type` | activity categories and subcategories |
| `/emr-api/application/mp-app-category-list` | marketplace category IDs (not used for test) |
| `/emr-api/catalog/info/vfm/{terminalId}`, `.../vfm/test/{terminalId}` | ВФМ status, production / test |
| `/emr-api/catalog/info/vfm` | your certificates: `pageNo`, `pageSize` |
| `/emr-api/catalog/info/active-nkm` | active certificate count: `page`, `size`, `Tin` or `pinfl` |
| `/emr-api/catalog/check/lgota-by-mxik` | benefits by MXIK: `checkDate`, `lang`, `tasnifCodes` |
| `/emr-api/catalog/check/lgota-by-tin` | benefits by TIN |
| `/emr-api/catalog/check/is-vat/{tin_or_pinfl}` | VAT-payer status, `data` `true` / `false` |
| `/emr-api/mxik/list` | frequently used MXIK: `tin`, `date` (epoch millis) |
| `GET /emr-api/catalog/commission/list/{companyTin}` | registered commission agents |
| `/emr-api/catalog/commitent/list/{companyTin}` | registered principals |

Application fields (`add`, `add/test`): `phone`, `sale_point_address`, `csr_file`,
`cadastre_rent_file`, `application_file`, `sale_point_region`, `sale_point_district`,
`activity_type_category`, `activity_type_subcategory`, `version`, `mp_app_category_id`.
The ОФД and a tax inspector review the application before the certificate can be
downloaded.

## Commission sales

- A commission agent puts the **principal's** TIN or PINFL in `CommissionInfo`; a
  sub-agent puts the main principal's.
- The principal must register its agents in my.soliq.uz (or my3.soliq.uz); otherwise the
  turnover is reported as the agent's.
- A non-resident principal gets a system ID through the "Формирование комитента" service
  and it is used instead of a TIN.

## Classifier API (cl-api)

Base: `https://tasnif.soliq.uz/api/cl-api`. Details and saved replies are in the
[tasnif skill](../../../tasnif/SKILL.md).

| Method | Purpose |
|---|---|
| `/integration-mxik/get/information` | search: `page`, `size`, `mxikCode`, `classCode`, `lang`, `search_text`, `shtrixCode` |
| `/integration-mxik/get/history/{mxikCode}` | codes that replaced an old code (the instruction misspells the path as `integratiom`) |
| `/integration-mxik/check/hazelcast` | check codes: query `tin`, body `mxikCode` |

## Not documented in the instruction

- The production host of the receipt, payment and report endpoints.
- The sum and discount formula (an image; only the 100 сум tolerance is in the text).
- The `OwnerType` reference values.
- How long the ОФД keeps a `RequestId` or a rejected `ReceiptSeq`, and whether a rejected
  number may be reused.
