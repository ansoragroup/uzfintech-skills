# Uzum sandbox: test hosts, test cards, test scenarios, vendor samples

Hand-written notes. Exact values published by Uzum for the **test environments only**. They move
no real money and do not work in production. Keep them in tests, fixtures and local configs, never
in production code paths. Test logins, passwords and API keys are always issued by your Uzum
manager; none are published.

- Sources: the Testing / "Тестирование" tag of each spec under
  https://developer.uzumbank.uz/redocusaurus/ (`ru_*.yaml`, `en_*.yaml`), the CrossBorder test
  PDFs and Postman collection, the Remit Core Postman collection, and
  https://developer.uzumbank.uz/paymenthub/testing/
- Fetched: 2026-11-03
- The vendor Postman collections ship pre-filled test login, password and API-key variables. They
  are deliberately **not** copied here; take them from the collection or your manager.

## Test hosts

| Product | Test host | Production host | Test credentials |
|---|---|---|---|
| Checkout | `https://test-chk-api.uzumcheckout.uz` | issued at go-live | test terminal (`X-Terminal-Id`) + `X-API-Key` from the manager |
| Fiscalization | `https://test-ofd.ipt-merch.com` | `https://ofd-key.inplat-tech.com` | test `X-API-Key` from the manager; production key on request in the Telegram chat |
| CrossBorder | `crossborder-transfer.ub.ufintech.uz` (scheme not stated) | `https://crossborder.transfer.uz` (IPSec) | Basic login / password from the manager |
| Remit Core | `https://remit-core.ipt-merch.com` | over IPSec (form `/remitcore/Sunnybox-IPsec.docx`) | `X-Api-Key` from the account manager |
| PaymentHub | `https://topup.ub.ufintech.uz` | issued at onboarding | Basic login / password and a test account from the manager |
| Merchant API, FastPay, Dynamic QR, Nasiya, Ratekeeper | no test data published | see the product README | ask the manager |

## Checkout

Source: tag "Тестирование" / "Testing" in `ru_checkout.yaml` / `en_checkout.yaml`.

| Scheme | PAN | Expiry | 3-DS code |
|---|---|---|---|
| HUMO | `9860 0901 0121 9724` | `10/26` | `777777` |
| UzCard | `8600 3129 2957 7175` | `09/26` | `777777` |

- Both printed expiry dates have passed as of 2026-11-03. If the test form rejects them, ask Uzum
  for current test cards.
- Sample redirect URLs used in the spec: `https://successUrl.sandbox.com`,
  `https://failureUrl.sandbox.com`, `https://returnUrl.sandbox.com`. Use your own test URLs in
  real runs.
- Order of onboarding: test terminal and key, test integration, then the production terminal.

Minimum test plan (Checkout):

| # | Scenario | Expect |
|---|---|---|
| 1 | `register` ONE_STEP, pay on the form with HUMO, 3-DS `777777` | callback, then `getOrderStatus` shows `COMPLETED` |
| 2 | same with UzCard | same |
| 3 | TWO_STEP: `register`, pay, `complete` | `AUTHORIZED` then `COMPLETED` |
| 4 | TWO_STEP: `register`, pay, `reverse` | `REVERSED` |
| 5 | ONE_STEP `refund`, full and partial | refund operations in `getOrderStatus` |
| 6 | `reverse` on ONE_STEP | `3036` (refund instead) |
| 7 | reuse an `orderNumber` | `3027` |
| 8 | card binding (`BINDING`), then `merchantPay` with the bound card | payment without the form |
| 9 | wrong 3-DS code / abandoned form | failed or expired order, nothing fulfilled |
| 10 | auto-fiscalization with a cart total that differs from `amount` | `3059` |

## Fiscalization

Source: tag "Testing" in `en_fiscalization.yaml` (same text in `ru_fiscalization.yaml`).

Receipts Uzum expects to see on the test host:

| Call | Variants to send |
|---|---|
| `POST /v2/receipt` (sale) | several items in `items`; if you use them: a discount (`items.discount > 0`) and a marketplace discount (`items.voucher > 0`, not subtracted from the total) |
| `POST /v2/refund_receipt` (refund) | the same three variants |
| receipt link | the Testing text says `/v2/receipt_url/{operation_id}`; the spec path is `/v2/receipt/{operation_id}/receipt_url` (see [`../fiscalization/README.md`](../fiscalization/README.md)) |
| `POST /v2/qr_payment` | only after prior approval from Uzum's development team |

Then post the links to the generated receipts in the Uzum Telegram chat for confirmation, and
request the production key there. Test SPIC values come from the manager.

## CrossBorder (transfers to Uzbekistan)

Sources (all on https://developer.uzumbank.uz):
`/crossborder/en_cbt_test_cases_partners.pdf`, Postman
`/crossborder/ru_cbt_test_cases_partners_postman_collection.json` (collection "TestCases with Test
Data", variables `baseUrl`, `login`, `password`). Paths are `{{baseUrl}}/cbt/v1/transfer/<method>`.
`senderAmount` is in minor units (`100700` = 1007 RUB).

### Case 1: happy path (steps 1-7, any valid data)

| Step | Call | Test data | Expect |
|---|---|---|---|
| 1 | `/convert` | `{"amount": "5000", "currencyFrom": "USD", "currencyTo": "UZS", "direction": "TO_UZ"}` | rate and converted amount |
| 2 | `/check_credit` | CARD `1234123412345678` or PHONE `998910707000`, rate and amounts from step 1 | `APPROVED` |
| 3 | `/confirm_credit` | ids from step 2 | `SUCCESS` |
| 4 | `/status` | id from step 3 | `SUCCESS` |
| 5 | `/check_credit` (new transfer) | CARD `4063571584532499` or PHONE `998910707000` | `APPROVED` |
| 6 | `/confirm_credit` | ids from step 5 | `SUCCESS` |
| 7 | `/transfer_list` | period covering steps 2-6, `status` `SUCCESS` | 2 transactions |

### Cases 2-5: errors

| Case | Call | Test data | Expect |
|---|---|---|---|
| 2.1 | `/check_credit` | wrong or empty password; CARD `4404489510015976` | HTTP 401 |
| 2.2 | `/check_credit` | `sender.personFullName` `"ANDREY VASILEV"`; CARD `4404489510015976` | sender check failed, `10201` |
| 2.3 | `/check_credit` | `sender.personFullName` `"PETR PETROV"`; CARD `4404489510015976` | check service error, `10101` |
| 2.4 | `/check_credit` | PHONE `998910102030` (PDF) / `998910102035` (Postman), or CARD `5614682209243632` | no cards, `10203` |
| 2.5 | `/check_credit` | PHONE `998910102040` or CARD `5674682209248632` | cards service error, `10101` |
| 3.1 | `/confirm_credit` | unknown operation | operation not found, `10212` |
| 3.2 | `/check_credit` with `"senderAmount": 100700`, then `/confirm_credit` | 1007 RUB | HTTP 200, `"status": "FAILED"` |
| 4.1 | `/status` | send the `externalTransferId` to Uzum QA and wait | `10101` service error, by arrangement |
| 5.1 | `/transfer_list` | a period with no transfers | HTTP 200, empty list |

Vendor discrepancy in case 2.4: the PDF gives PHONE `998910102030`, the Postman collection
`998910102035`. Try the PDF value first and fall back to the Postman one.

Vendor sample (`/check_credit`, Postman 1.2 CARD), copied exactly:

```json
{
  "clientId": "59e8c447-b0d2-4738-a40a-191b39470a65",
  "externalTransferId": "qwaesrdtfsdgsGy",
  "identificationType": "CARD",
  "identificationValue": "1234123412345678",
  "senderAmount": 40000,
  "senderCurrencyCode": "RUB",
  "receiverCurrencyCode": "UZS",
  "sender": {
    "personFullName": "RAUL JIMENEZ",
    "birthday": "1991-05-05",
    "birthPlace": "Tepeji del Rio de Ocampo",
    "nationality": "860",
    "address": "San Jerónimo 23,CDMX, Mexico",
    "passport": "12 34567890"
  },
  "senderCountry": "MX",
  "senderAccount": "453936******8500",
  "bankLabel": "KPT",
  "receiverAmount": 16999999,
  "exchangeRate": "140.00",
  "receiver": {
    "personFullName": "Guillermo Ochoa",
    "birthday": "1985-07-13",
    "birthPlace": "Guadalajara",
    "nationality": "860",
    "address": "C. Manuel Acuña 653 D,Guadalajar, Mexico",
    "passport": "12 34567890"
  }
}
```

Send a fresh `externalTransferId` on every run; the sample ids are already used.

## CrossBorder (transfers from Uzbekistan, DEBIT)

Source: `/crossborder/ru-cbt-test-cases-from-uz.pdf` (Russian only). The payer gets an SMS OTP
after `/check_debit`; the scenario inputs below force each outcome.

Case 1, happy path (steps 1-9, any valid data):

| Step | Call | Expect |
|---|---|---|
| 1 | `/convert` | rate and converted amount |
| 2 | `/check_debit` with the rate and amounts from step 1 | `APPROVED`, SMS with OTP |
| 3 | `/confirm_debit` with the id and OTP from step 2 | `SUCCESS` (printed "SUCCES") |
| 4 | `/status` for that transfer | `SUCCESS` |
| 5 | `/check_debit` (new transfer) | `APPROVED`, SMS with OTP |
| 6 | `/confirm_debit` with the id and OTP from step 5 | `SUCCESS` |
| 7 | `/cancel_debit` for the transfer from step 6 | `FAILED` |
| 8 | `/transfer_list` with `"status": "SUCCESS"` | one transfer, `SUCCESS` |
| 9 | `/transfer_list` with `"status": "FAILED"` | one transfer, `FAILED` |

Error cases:

| Case | Call | Test data | Expect |
|---|---|---|---|
| 2.1 | `/check_debit` | wrong login or password | HTTP 401 |
| 2.2 | `/check_debit` | `sender.personFullName` `"ANDREY VASILEV"` | `10201` sender check failed |
| 2.3 | `/check_debit` | `receiver.personFullName` `"Vasiliy Nesterov"` | `10202` receiver check failed |
| 2.4 | `/check_debit` | `sender.personFullName` `"PETR PETROV"` | `10101` service error |
| 2.5 | `/check_debit` | `"senderAmount": 20009` | `10101` service error |
| 2.6 | `/check_debit` | repeat with the same `externalTransferId` | `10211` transfer already exists |
| 2.7 | `/check_debit` | `"senderAmount": 20005` | `10301` card not found |
| 2.8 | `/check_debit` | `"senderAmount": 20001` | `10302` processing temporarily unavailable |
| 2.9 | `/check_debit` | `"senderAmount": 20007` | `10303` sender bank not found |
| 3.1 | `/resend_otp` | unknown transfer id | `10212` |
| 3.2 | `/resend_otp` | already confirmed transfer | `10220` transfer not approved to confirm |
| 4.1 | `/confirm_debit` | send the `externalTransferId` to Uzum QA and wait | `10208` exchange rate changed |
| 4.2 | `/confirm_debit` | `"code": "76511"` | `10312` OTP attempts exceeded, transfer failed |
| 4.3 | `/confirm_debit` | `"code": "76493"` | `10310` OTP expired |
| 4.4 | `/confirm_debit` | `"code": "76673"` | `10316` error during debit |
| 4.5 | `/confirm_debit` | the transfer from happy-path step 3 | transfer info, `SUCCESS` |
| 4.6 | `/confirm_debit` | the transfer from happy-path step 7 | transfer info, `FAILED` |
| 4.7 | `/confirm_debit` | a transfer without `/check_debit` | `10212` |
| 5.1 | `/cancel_debit` | send the `externalTransferId` to Uzum QA and wait | `10101` |
| 5.2 | `/cancel_debit` | a transfer in `APPROVED` | `10227` status must be SUCCESS to reverse |
| 5.3 | `/cancel_debit` | unknown transfer | `10212` |
| 6.1 | `/status` | send the `externalTransferId` to Uzum QA and wait | `10101` |
| 7.1 | `/transfer_list` | a period with no transfers | HTTP 200, empty list |

## CrossBorder (payments for services in Uzbekistan)

Sources: `/crossborder/en_cbt_payment_test_cases_integration.pdf` (real suppliers) and
`/crossborder/en_cbt_payment_test_cases_mocks.pdf` (mocks). **Contact your Uzum manager before
running the mock cases.**

Integration with suppliers:

| Case | Call | Test data | Expect |
|---|---|---|---|
| 1 | `/check_service` -> `/check_payment` -> `/confirm_payment` -> `/status` | an available service (`serviceId` 389 or 529; 498624986 for `check_payment`) | service info, `APPROVED`, `SUCCESS`, `SUCCESS` |
| 2.1 | `/check_service` | `serviceId` 1 | `20101` supplier service not found |
| 2.2 | `/check_service` | `serviceId` 381 | `20104` service not available now |
| 3.1 | `/check_payment` | `serviceId` 1 | `20101` |
| 3.2 | `/check_payment` | `serviceId` 381 | `"status": "FAILED"` |
| 3.3 | `/check_payment` | `payerInfo.persona` name `"K G V"` | `20211` payer check failed |

Mocks:

| `serviceId` | `/check_service` error | `serviceId` | `/check_payment` result |
|---|---|---|---|
| 1001 | `20202` transfer not found | 1009 | `FAILED`, `20202` |
| 1002 | `20103` service not active | 1010 | `FAILED`, `20104` |
| 1003 | `20104` service not available now | 1011 | `FAILED`, `20103` |
| 1004 | `20105` invalid service parameters | 1012 | `FAILED`, `20105` |
| 1005 | `20206` invalid payment amount | 1013 | `FAILED`, `20206` |
| 1006 | `20207` client number not found | 1014 | `FAILED`, `20207` |
| 1007 | `20208` number does not exist | 1015 | `FAILED`, `20208` |
| 1008 | `20209` invalid phone number | 1016 | `FAILED`, `20209` |
| | | 1017 | `FAILED`, `20210` declined by antifraud |

Mock case 3.1 (async antifraud decline): `/check_payment` with phone `998910142976` returns
`APPROVED`, `/confirm_payment` returns `PENDING`, `/status` returns `FAILED` with `20210`.

## Remit Core (CREDIT transfers)

Source: Postman `/remitcore/remitcore_postman_collection_credit.json` (collection "Remit-Core
CREDIT", variables `remitBaseUrl`, `remitApiKey`).

Success flow:

| Step | Call | Body (vendor test data) |
|---|---|---|
| 1 (optional) | `POST /v1/convert` | `{"senderCurrencyCode": "RUB", "senderCountry": "RUS", "receiverCurrencyCode": "UZS", "receiverCountry": "UZB", "senderAmount": 10000}` |
| 2 (optional, PHONE target) | `POST /info/v1/get_banks` | `{"phoneNumber": "+998901234567", "receiverCountry": "UZB"}` |
| 3 | `POST /v1/register` | see below; target CARD_PAN `9876543210987654` or PHONE `+998901234567` with `bankLabel` `UZB` |
| 4 | `POST /v1/get_status` | `{"transferId": ...}` or `{"externalTransferId": ...}` |
| 5 | `POST /v1/process` | `{"transferId": ...}` |
| 6 | `POST /v1/get_status` | `{"transferId": ...}` |

Minimal `/v1/register` (sender amount, CARD_PAN), copied exactly:

```json
{
  "transferType": "CREDIT",
  "externalTransferId": "{{$randomUUID}}",
  "transferData": {"senderCurrencyCode": "RUB", "senderCountry": "RUS", "receiverCountry": "UZB",
                   "senderAmount": 10000, "receiverCurrencyCode": "UZS"},
  "target": {"paymentInstrumentType": "CARD_PAN", "cardPan": "9876543210987654"},
  "sender": {"firstName": "IVAN", "lastName": "PETROV"}
}
```

The collection also has a receiver-amount variant (`receiverAmount` 12332233, `clientId`
`test_client_id`, `reason` `"Business payment"`, optional `source` ACCOUNT
`40817810099910004312`) and a PHONE-target variant.

Error cases:

| Case | Change to the request | Expect |
|---|---|---|
| wrong route | `receiverCountry` `AUT`, `receiverCurrencyCode` `USD` | route error |
| limit | `senderAmount` `9000000000000` | limit error |
| wrong key | wrong `X-Api-Key` | auth error |
| validation | `transferType` `"CREDI"` | validation error |
| validation | `sender.firstName` missing | validation error |
| not found | `/v1/process` with `transferId` `01990610-f6fb-72fd-84c1-ff8cf5840599` | `3054` |

## PaymentHub (account to card)

Source: https://developer.uzumbank.uz/paymenthub/testing/account-to-card/ and
`/paymenthub/testing/getting-started/`. Use test data only on the test host.

Test account `ACCOUNT_VALID`: number from the manager, MFO `01190`.

Receiver test cards:

| Key | PAN | Result |
|---|---|---|
| `SUCCESS` | `8600533000000000` | `state` 4 |
| `CANCELED` | `8600533000000001` | `state` 50 |
| `PENDING` | `8600533000000002` | `state` 57 |
| `CARD_NOT_FOUND` | `8600533000000006` | `-31620` `card_not_found` |
| `CARD_NOT_ACTIVE` | `8600533000000009` | `-31608` `card.not.active` |

Scenarios (the page prints amount `2000`; the sample body uses `2900000`; amounts are tiyin):

| Id | Receiver | Expect |
|---|---|---|
| ACC2CARD-01 | `SUCCESS` | create `state` 0, confirm `state` 4 |
| ACC2CARD-02 | `PENDING` | confirm `state` 57; poll `receipt.check.id` |
| ACC2CARD-03 | `CANCELED` | confirm `state` 50, reason in `result.error` (e.g. `card.blocked`) |
| ACC2CARD-04 | `SUCCESS`, amount above the account balance (check with `account.transfer.balance`) | `state` 51 |
| ACC2CARD-05 | `CARD_NOT_ACTIVE` | create fails with `-31608`; do not call confirm |
| ACC2CARD-06 | `CARD_NOT_FOUND` | create fails with `-31620`; do not call confirm |

Order per scenario: new unique `ext_id`, create, compare, save `result.id` when `state` is 0,
confirm, compare. Pass when the code or state matches, `result.id` is non-empty on `state` 0, a
successful confirm has `state` 4 with an empty `error`, and confirm is never called without
`state` 0.

Vendor samples, copied exactly:

```json
{"jsonrpc": "2.0", "id": "5a11a6a4-f6f4-443d-9fa9-fbc8019bf4b0",
 "method": "receipt.account.create.transfer",
 "params": {"amount": 2900000, "ext_id": "30f581c4-cd6e-449e-bfdb-049536d03f86",
            "account": {"number": "29896000909991110000", "mfo": "01190"},
            "sender": {"id": "test:acc2card-user-001", "name": "Test User"},
            "receiver": {"number": "8600533000000000"},
            "description": "Acc2Card test transfer"}}
```

```json
{"jsonrpc": "2.0", "id": "5a11a6a4-f6f4-443d-9fa9-fbc8019bf4b0", "error": null,
 "result": {"id": "4d4deb9ed934433abc80f6c9499ade01", "state": 0}}
```

```json
{"jsonrpc": "2.0", "id": "f31d224b-04f4-42d1-9d92-65161a15aa7c",
 "method": "receipt.account.confirm.transfer",
 "params": {"id": "4d4deb9ed934433abc80f6c9499ade01"}}
```

A successful confirm returns `result` `{id, state: 4, error: ""}`. The sample account number is
illustrative; use the one your manager issues.
