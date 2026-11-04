# Kapital API (Kapitalbank corporate Open API, "KapitalAPI")

Hand-written notes. Schemas: [`schemas/`](schemas/) (one file per method: `requestBody` and
`responses."200"`, with the source URL and fetched date). Examples: [`examples/`](examples/).
Codes for `purp_code` and the text of `purpose`: [`../purpose-codes/`](../purpose-codes/README.md).
Testing: [`../sandbox/`](../sandbox/README.md). Deadlines, statuses and open questions:
[`../lifecycle/`](../lifecycle/README.md).

- Source: https://b2b-api-docs.kapitalbank.uz/api-reference and the method pages linked in
  the [Methods](#methods) table; connection: https://b2b-api-docs.kapitalbank.uz/kapital-api-connect
  (Russian pages, client-rendered site)
- Fetched: 2026-11-04
- Needs: a legal entity served by Kapitalbank with internet banking (ДБО); KapitalAPI access,
  granted after the connection application is handed in at a branch; an internet-banking
  login and password; the base host from the bank's connection instruction; an electronic
  signature (ЭЦП) for payment orders.

## What it is

Open API to the bank's remote banking (ДБО) for **legal entities only**. Your server calls
the bank; every method is `POST` with a JSON body and the answer is a JSON object. The
pages publish **no webhooks**, so outcomes are learned by polling.

To connect, download the application template from the connect page, fill it in and hand it
in at a Kapitalbank branch. After access is granted the bank's connection instruction
(`api-documentation.pdf`, linked from the connect page) describes the next steps.

## Host and paths

The public pages print **paths only** and no host: `Mobile.svc/APILogin`,
`/Mobile.svc/SendPaymentIBK`, `api/invoices` and so on (the leading slash is printed
inconsistently). No production or test host is published. Take the host from the connection
instruction, keep it in configuration, and never guess one. Warning
`kapitalbank.host-and-sandbox-not-published`.

## Authorization

1. `POST Mobile.svc/APILogin` with `Authorization: Basic base64(login:password)`, using the
   company's **internet-banking** credentials. The login gets the prefix `IB#`, so the
   encoded string is `IB#<LOGIN>:<PASSWORD>`. Optional `X-Original-Forwarded-For` carries
   the client IP.
2. The bank checks the pair and, when needed, an SMS code (the SMS step is not described).
   On success it returns `result.login`, `result.sid` and `result.clients[]` (organizations
   with their `accounts[]`).
3. Later methods take `sid` in the JSON body, **or** the login and password again in
   `Authorization: Basic`.
4. **IP restriction** (no SMS code): when the bank turns it on for the login, every request
   carries `Authorization: Basic` and the server checks the login together with the caller's
   IP. A request from another IP fails, for example `error.code` `61002` with
   `" IP : <CLIENT_IP>"` ([`examples/apilogin.response.json`](examples/apilogin.response.json)).
5. Invoices (`api/invoices*`) accept `sid` in the body or an `Authorization` header, and the
   header wins. The scheme of that header is not stated on the invoice pages.

`client_id` in payment calls is `Client.id` from the login answer. Warnings
`kapitalbank.ib-credentials-basic-auth`, `kapitalbank.sms-or-ip-restriction`.

## Flow

```
APILogin (Basic IB#login:password)            -> sid, clients[].id, clients[].accounts[]
GetOperDays {branch}                          -> is the branch day open? (state)
budget payee? GetBudjetAcc {ls, inn} / GetNalogAcc {ls} -> mfo, acc, name, inn of the payee
SendPaymentIBK {client_id, sid, payment{document{.. uniq, purp_code, purpose, anor ..}, signs[]}}
   -> result, error            (store your uniq BEFORE the call)
CheckPayments2 {sid, client_id, uniqs[]}      -> state 55 draft / 54 / 53 / 56, state_name, err
GetDoc1C {sid, branch, account, date}         -> documents, turnovers, balances, fin 0|1
GetMT940 {branch, account, date}              -> MT940 text for the same day
```

## Methods

All methods are `POST` JSON. Paths as published.

| Method | Path | Schema | Required body fields | Result |
|---|---|---|---|---|
| [Login](https://b2b-api-docs.kapitalbank.uz/authorization/user-authorization) | `Mobile.svc/APILogin` | [`apilogin`](schemas/apilogin.json) | none (header `Authorization: Basic`) | `login`, `sid`, `clients[]` |
| [Create payment order](https://b2b-api-docs.kapitalbank.uz/payment-orders/create-payment-order) | `/Mobile.svc/SendPaymentIBK` | [`send-payment-ibk`](schemas/send-payment-ibk.json) | `client_id`, `payment.document{ddate, mfo_dt, name_dt, mfo_ct, acc_ct, name_ct, purpose, purp_code, amount, anor}`, `payment.signs[]` | `result` (integer), `error` |
| [Payment status](https://b2b-api-docs.kapitalbank.uz/payment-orders/payment-status) | `/Mobile.svc/CheckPayments2` | [`check-payments2`](schemas/check-payments2.json) | `sid`, `client_id`, and `uniqs[]` or `general_ids[]` (100 values at most) | `result[]{branch, err, err_msg, general_id, state, state_name, uniq}` |
| [Statement (documents)](https://b2b-api-docs.kapitalbank.uz/statements-and-accounts/document-list) | `/Mobile.svc/GetDoc1C` | [`get-doc1c`](schemas/get-doc1c.json) | `sid`, `branch`, `account`; optional `date`, `from_time`, `to_time` | `result{content[], total_debit, total_credit, saldo_in, saldo_out, fin, oper_day}` |
| [Statement (MT940)](https://b2b-api-docs.kapitalbank.uz/statements-and-accounts/mt940-statement) | `/Mobile.svc/GetMT940` | [`get-mt940`](schemas/get-mt940.json) | `branch`, `account`, `date` (`dd.MM.yyyy`) | `result` (MT940 text) |
| [Account (user)](https://b2b-api-docs.kapitalbank.uz/clients-and-accounts/account-information) | `Mobile.svc/GetAcc1C` | [`get-acc1c`](schemas/get-acc1c.json) | `sid`, `branch` (5 characters), `account` (20 digits) | `result[]` of Account |
| [Account (by number)](https://b2b-api-docs.kapitalbank.uz/clients-and-accounts/client-account-information) | `/Mobile/svc/GetAccounts` | [`get-accounts`](schemas/get-accounts.json) | `branch` (5 characters), `account` (20 digits) | `result[]` with one Account |
| [Operating day](https://b2b-api-docs.kapitalbank.uz/clients-and-accounts/oper-day-information) | `/Mobile.svc/GetOperDays` | [`get-oper-days`](schemas/get-oper-days.json) | `branch` | `result[]{branch, name, date, state, desc}` |
| [Budget payee check](https://b2b-api-docs.kapitalbank.uz/directories/budget-recipient-account-check) | `/Mobile.svc/GetBudjetAcc` | [`get-budjet-acc`](schemas/get-budjet-acc.json) | `ls`; optional `inn` | `result{mfo, acc, name, inn, sid}` |
| [Treasury account](https://b2b-api-docs.kapitalbank.uz/directories/treasury-account-check) | `Mobile.svc/GetNalogAcc` | [`get-nalog-acc`](schemas/get-nalog-acc.json) | `ls` | `result{mfo, acc, name, inn, sid}` (fixed treasury requisites) |
| [Exchange rates](https://b2b-api-docs.kapitalbank.uz/directories/currency-rates) | `/Mobile.svc/GetCoursesB2` | [`get-courses-b2`](schemas/get-courses-b2.json) | none; optional `tobo`; **no authorization** | `result{filial, date, time, courses[]}` |
| [Create invoice](https://b2b-api-docs.kapitalbank.uz/invoices/create-invoice) | `api/invoices` | [`create-invoice`](schemas/create-invoice.json) | `code` (8), `branch` (5), `senderAccountNumber` (20), `amount`, `purposeCode`, `dueDate`; one of `receiverBusinessCode` / `receiverTinOrPinfl`; `sid` unless the header is sent | `result{invoice_id}` |
| [Invoice status](https://b2b-api-docs.kapitalbank.uz/invoices/invoice-status) | `api/invoices/check-statuses` | [`check-invoice-statuses`](schemas/check-invoice-statuses.json) | `code`, `branch`, `invoiceId[]` (100 at most); `sid` unless the header is sent | `result{invoiceId, status}` |

## Payment order fields (SendPaymentIBK)

- `ddate` document date (`dd.MM.yyyy` in the sample); `num` your document number; `uniq` your
  unique document code. Both are optional on the page, but `uniq` is what CheckPayments2
  looks up, so always send it. Warning `kapitalbank.unique-doc-number`.
- Payer `mfo_dt`, `acc_dt`, `name_dt`, `inn_dt`; payee `mfo_ct`, `acc_ct`, `name_ct`, `inn_ct`.
  An MFO is 5 characters and an account 20 digits elsewhere in the docs.
- `purp_code` is the CBU payment purpose code (5 digits) and `purpose` the "Детали платежа"
  text. Both are required. The bank "cleans and completes" `purpose` when needed, so read
  the stored text back from GetDoc1C (derived). Build both with
  `scripts/purpose_codes.py details`. Warnings `kapitalbank.old-purpose-codes-rejected`,
  `kapitalbank.payment-details-content`.
- `amount` is typed decimal; its unit is not stated. Warning `kapitalbank.amount-units-unstated`.
- `anor`: `0` sends through СЭП (the interbank clearing system), open 9:00–17:00 on days with
  an open balance; `1` sends through the Anor online system, 24/7 (wording from GetDoc1C).
  Warning `kapitalbank.oper-day-dating`.
- `signs[]` holds the ЭЦП: `method`, `sert_num` (certificate serial), `signature`. The array is
  required; the signing method, what is signed and the value format are not published.
  Warning `kapitalbank.payment-needs-signature`.
- `branch`, `general_id`, `dtype`, `state`, `dir`, `err`, `err_msg` are optional; the vendor
  sample sends them as `null`, `""` or fixed values.

## Statuses

CheckPayments2 maps internal statuses to its own codes:

| Where the document is | Internal status | `state` returned |
|---|---|---|
| Draft (Черновик) | any (`0`–`4`, other) | `55` |
| B2 (the bank's core system) | `-1` | `56` |
| B2 | `0` | `53` |
| B2 | `1`, `2`, `3`, other | `54` |
| Deleted or cancelled | n/a | `53` |

- When `state` is `54`, `branch` is the MFO where the document was created and `general_id`
  its unique number in that branch; otherwise `branch` is `""` and `general_id` `0`.
- A deleted draft created through KapitalAPI loses its `uniq`, so it can no longer be found
  by `uniq`.
- The page gives the mapping, not the meaning of `53`, `54` and `56`, nor which of them is
  final. Read `state_name`, `err` and `err_msg` and confirm the final states with the bank.

GetDoc1C documents carry a separate `state` ("0-9"): internal `1`→`1`, `3`→`2`, `2`→`3`,
`-1`→`16`, other→`0`. `dir` is `1` incoming, `2` outgoing. `fin` `0` means the operating day
is not closed and more entries may arrive; `1` means the statement is final.

## Errors

| Case | Answer |
|---|---|
| success | `error` is `null` (several samples print `{"code": 0, "message": "string"}` instead) |
| login from an IP that is not allowed | `error.code` `61002`, `message` `" IP : <CLIENT_IP>"`, `result` `null` |
| invoices: authorization, validation, or the upstream service answering 4xx/5xx | HTTP `200` with `error{code, message}` filled |
| unknown `purposeCode` (invoices) | an error; the code is not printed |
| no access to the account (statements, accounts) | an error; the code is not printed |

The full list of error codes is not published. Check `error` in every answer; an HTTP `200`
alone is not success. Warning `kapitalbank.error-in-http-200`.

## Gotchas

- The account-by-number path is printed `/Mobile/svc/GetAccounts`; every other method uses
  `Mobile.svc`. Ask the bank which one works before you hard-code it.
- SendPaymentIBK: the algorithm says success returns the new document id and code `55`,
  but `result` is described as "result code" and the sample prints `"result": 1`. Do not
  read meaning into `result`; follow up with CheckPayments2 by `uniq`.
- The vendor SendPaymentIBK sample uses `purp_code` `"00699"`, an **old** code refused since
  26.05.2026 (its new code is `00031`), and a 19-digit `acc_dt`. Copy its shape, not its
  values.
- The method pages mark `sid` required for CheckPayments2, GetDoc1C and GetAcc1C, while the
  login page says Basic auth may replace `sid` in every later method. Send `sid` there.
- `Client.id` is typed string in the login answer, while `client_id` in requests is an integer.
  Convert it.
- GetDoc1C does not state the format of `date`, and its sample sends `"2026-03-04"`, while
  every other date in the docs is `dd.MM.yyyy`. Without `date` the current day is used.
- GetMT940 types `result` as a string (the MT940 text) but its table also lists
  `paymentId` … `transactionType` sub-fields. The sample is a string whose JSON writes the
  line breaks as `\\n`, so the decoded text holds a backslash and `n`, not newlines. Accept
  both shapes and both kinds of line break. In those sub-fields `platPurposeCode` is typed
  integer, so `00076` can arrive as `76`; left-pad to 5 digits before you compare codes.
- GetDoc1C marks `purp_code` optional and its sample prints `null`; match incoming payments
  on `purpose` text and amounts, not on the code alone (derived).
- `val` (currency) is described as UZS, USD, EUR, but the GetAccounts sample prints `"000"`,
  and its `state` `2` is not explained (the table says `1` open, `0` closed, "and so on").
- CheckPayments2's sample shows `state` `1`, `2`, `3`, which are internal values, not the
  mapped `53`/`54`/`55`/`56`. Expect the mapped codes.
- Invoices: `purposeText` and `purposeCode` are labelled "credit purpose" (цели кредита)
  and checked against a directory that is not published. It is not stated that this is the
  CBU payment purpose table. `amount` must be greater than `5000000` (unit not stated) and
  `dueDate` later than now. If `purposeText` is omitted, the bank fills it from the directory.
- Invoice status: the request takes an array of ids but `result` is described as one object
  `{invoiceId, status}`; the `status` values are not published and there are no samples.
- GetNalogAcc returns **fixed** treasury requisites of the Ministry of Finance; GetBudjetAcc
  checks a budget payee account (and INN) against the CBU directories. Budget purpose codes
  are not in the commercial purpose-code table. Warning `kapitalbank.check-budget-account-first`.

## Examples

Copied exactly from the vendor pages, except where noted:

- [`apilogin.response.json`](examples/apilogin.response.json): the IP-restriction error; the IP
  in `message` is replaced with `<CLIENT_IP>`.
- `send-payment-ibk`, `check-payments2`, `get-doc1c`, `get-accounts`, `get-oper-days`,
  `get-budjet-acc`, `get-nalog-acc`, `get-courses-b2` (request and response),
  `get-acc1c.response.json`.
- [`get-mt940.response.json`](examples/get-mt940.response.json): the `:86:` line content is
  replaced with `<DETAILS>`.

Built by us from the field tables (no vendor sample, or the sample holds only `"string"`):

- [`get-mt940.request.json`](examples/get-mt940.request.json)
- [`apilogin-success.response.json`](examples/apilogin-success.response.json): a successful login
  with placeholders.
- [`send-payment-ibk-new-code.request.json`](examples/send-payment-ibk-new-code.request.json): a
  payment order with a **new** purpose code `00076` and a "Детали платежа" text from
  `scripts/purpose_codes.py details`.
- [`create-invoice.request.json`](examples/create-invoice.request.json),
  [`create-invoice.response.json`](examples/create-invoice.response.json),
  [`check-invoice-statuses.request.json`](examples/check-invoice-statuses.request.json),
  [`check-invoice-statuses.response.json`](examples/check-invoice-statuses.response.json).
