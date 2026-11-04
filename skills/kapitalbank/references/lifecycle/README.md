# Kapitalbank: payment order lifecycle, deadlines and open questions

Read this when building or reviewing a Kapital API integration or any UZS payment order,
and raise these traps before they cost money: old purpose codes that are refused, an
unpublished host, internet-banking credentials in every request, payment orders that need
an electronic signature, no webhooks, no recall method, and a `uniq` that is the only way
to find an order again.

- Source: https://b2b-api-docs.kapitalbank.uz/authorization/user-authorization,
  https://b2b-api-docs.kapitalbank.uz/payment-orders/create-payment-order,
  https://b2b-api-docs.kapitalbank.uz/payment-orders/payment-status,
  https://b2b-api-docs.kapitalbank.uz/statements-and-accounts/document-list,
  https://b2b-api-docs.kapitalbank.uz/clients-and-accounts/oper-day-information,
  https://b2b-api-docs.kapitalbank.uz/invoices/create-invoice,
  https://b2b-api-docs.kapitalbank.uz/invoices/invoice-status (Russian pages); purpose codes
  and dates: the sources in [purpose-codes](../purpose-codes/README.md)
- Fetched: 2026-11-04

## Warn without being asked

1. **`kapitalbank.old-purpose-codes-rejected`**: when building or migrating UZS payment
   orders in any Uzbek bank → use only the new codes (in force from 06.05.2026); old codes
   are refused from 26.05.2026, and the order is rejected or delayed. Check stored templates
   and hard-coded values with `scripts/purpose_codes.py check CODE`; the vendor sample's
   `00699` is old (now `00031`). [purpose-codes](../purpose-codes/README.md#dates)
2. **`kapitalbank.one-old-code-many-new`**: when mapping old codes to new ones → nine old
   codes split into several new codes (`00545` sanitary ware → `00039` / `00068` / `00069` /
   `00076` by material). Do not map them automatically; pick per goods with
   `scripts/purpose_codes.py old CODE`.
   [purpose-codes](../purpose-codes/README.md#the-table)
3. **`kapitalbank.payment-details-content`**: when filling "Детали платежа" (`purpose`) →
   include the code, the contract number and date when there is a contract, the goods,
   works or services, and the payment type. Assemble and check it with
   `scripts/purpose_codes.py details`; the bank may clean and complete the text, so read
   back what was stored.
   [purpose-codes](../purpose-codes/README.md#what-детали-платежа-must-contain)
4. **`kapitalbank.host-and-sandbox-not-published`**: when configuring the client → the docs
   print paths only; no production host, test host or sandbox is published. Take the host
   from the bank's connection instruction, keep it in configuration, and never guess one.
   [kapital-api](../kapital-api/README.md#host-and-paths), [sandbox](../sandbox/README.md)
5. **`kapitalbank.ib-credentials-basic-auth`**: when authenticating → `APILogin` takes the
   company's internet-banking login and password as `Authorization: Basic` with the login
   prefixed `IB#`. Keep them in a secret store, call from the server only, and never log the
   header, the password or `sid`. [kapital-api](../kapital-api/README.md#authorization)
6. **`kapitalbank.sms-or-ip-restriction`**: when the login runs unattended → the bank may ask
   for an SMS code, which a server cannot answer; the documented alternative is IP
   restriction, where every request carries Basic auth from an allowed IP. A call from
   another IP fails with `61002`. Agree the mode and the egress IPs with the bank before go-live.
   [kapital-api](../kapital-api/README.md#authorization)
7. **`kapitalbank.payment-needs-signature`**: when sending `SendPaymentIBK` → `signs[]` (the
   ЭЦП: `method`, `sert_num`, `signature`) is required, and the signing method and the signed
   content are not published. Get them from the bank's connection instruction before you
   build the order. [kapital-api](../kapital-api/README.md#payment-order-fields-sendpaymentibk)
8. **`kapitalbank.unique-doc-number`**: when creating an order → generate `uniq` (and `num`)
   per order, store it **before** the call, and never reuse it. `uniq` is optional on the page,
   but CheckPayments2 finds orders by it, and a deleted draft loses it.
   [kapital-api](../kapital-api/README.md#payment-order-fields-sendpaymentibk)
9. **`kapitalbank.poll-status-not-resend`**: when the answer is lost, times out or is unclear →
   there are no webhooks and no recall method, and sending again creates a **second real
   order**. Ask `CheckPayments2` by `uniq` first, and resend only when the order is not found.
   Poll statuses and statements instead of waiting for a push.
   [kapital-api](../kapital-api/README.md#statuses)
10. **`kapitalbank.oper-day-dating`**: when choosing the route and `ddate` → `anor: 0` goes
    through СЭП, 9:00–17:00 on days with an open balance; `anor: 1` goes through Anor, 24/7.
    Check `GetOperDays` for the branch, and treat a `fin: 0` statement as incomplete.
    [kapital-api](../kapital-api/README.md#payment-order-fields-sendpaymentibk)
11. **`kapitalbank.check-budget-account-first`**: when paying the budget or the treasury →
    check the payee with `GetBudjetAcc` (`ls`, `inn`) or take the treasury requisites from
    `GetNalogAcc` first. Budget payments use their own treasury codes, which are not in the
    commercial purpose-code table. [kapital-api](../kapital-api/README.md#gotchas)
12. **`kapitalbank.amount-units-unstated`**: when setting `amount` → the type is decimal but the
    unit (sum or tiyin) is not stated anywhere. Confirm it with the bank in writing and test
    with a small amount; never assume the unit of another provider. Invoice `amount` must be
    greater than `5000000` in the same unknown unit.
    [kapital-api](../kapital-api/README.md#payment-order-fields-sendpaymentibk)
13. **`kapitalbank.error-in-http-200`**: when handling answers → errors come back with HTTP `200`
    and a filled `error` object, and several success samples print `{"code": 0}` instead of
    `null`. Treat `error == null` or `error.code == 0` as success, and check every answer.
    [kapital-api](../kapital-api/README.md#errors)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| New purpose codes | in force from 06.05.2026 | n/a | [purpose-codes](../purpose-codes/README.md#dates) |
| Old purpose codes | refused from 26.05.2026 | the order is refused or delayed | [purpose-codes](../purpose-codes/README.md#dates) |
| Order through СЭП (`anor: 0`) | 9:00–17:00 on days with an open balance | not documented (derived: waits for the next open day) | https://b2b-api-docs.kapitalbank.uz/statements-and-accounts/document-list |
| Order through Anor (`anor: 1`) | 24/7 | n/a | https://b2b-api-docs.kapitalbank.uz/statements-and-accounts/document-list |
| Statement of the day (`GetDoc1C`) | final only when `fin` is `1` (day closed) | more entries may arrive | https://b2b-api-docs.kapitalbank.uz/statements-and-accounts/document-list |
| `CheckPayments2` | at most 100 `uniqs` or `general_ids` per call | not documented | https://b2b-api-docs.kapitalbank.uz/payment-orders/payment-status |
| `api/invoices/check-statuses` | at most 100 `invoiceId` per call | validation error in HTTP `200` | https://b2b-api-docs.kapitalbank.uz/invoices/invoice-status |
| Invoice `dueDate` | later than the current date | validation error in HTTP `200` | https://b2b-api-docs.kapitalbank.uz/invoices/create-invoice |
| `sid` lifetime | not documented | not documented | https://b2b-api-docs.kapitalbank.uz/authorization/user-authorization |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Recall a sent payment order | you | **none published**; ask the bank (internet banking or branch) | n/a | n/a | n/a | https://b2b-api-docs.kapitalbank.uz/api-reference |
| Draft deleted or cancelled | you or the bank, outside the API | none in the API; `CheckPayments2` shows `53` and the KapitalAPI draft loses its `uniq` | n/a | n/a | n/a | https://b2b-api-docs.kapitalbank.uz/payment-orders/payment-status |
| Money paid to the wrong payee | you | none in the API; ask the bank | n/a | n/a | n/a | not documented |
| Cancel an invoice | you | **none published** | n/a | n/a | n/a | https://b2b-api-docs.kapitalbank.uz/invoices/create-invoice |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Webhooks | none published | n/a | n/a | poll instead | https://b2b-api-docs.kapitalbank.uz/api-reference |
| `SendPaymentIBK` (you call) | n/a | n/a | your `uniq` (derived: the only lookup key) | not documented; after a lost reply ask `CheckPayments2` by `uniq` and resend only when it is not found | https://b2b-api-docs.kapitalbank.uz/payment-orders/create-payment-order |
| `CheckPayments2` (you call) | n/a | n/a | read-only | safe to repeat (derived) | https://b2b-api-docs.kapitalbank.uz/payment-orders/payment-status |
| `GetDoc1C` / `GetMT940` (you call) | n/a | n/a | read-only | de-duplicate entries by document id and number (derived) | https://b2b-api-docs.kapitalbank.uz/statements-and-accounts/document-list |
| `APILogin` (you call) | n/a | n/a | n/a | reuse `sid` until it fails; lifetime not documented (derived) | https://b2b-api-docs.kapitalbank.uz/authorization/user-authorization |
| `api/invoices` (you call) | n/a | n/a | none published | not documented; a resend may create a second invoice (derived) | https://b2b-api-docs.kapitalbank.uz/invoices/create-invoice |

## Fiscal receipts

- Not applicable: payment orders and invoices between legal entities are bank transfers,
  and the Kapital API pages say nothing about fiscal receipts.
- If the goods or services were sold to a consumer, the seller fiscalizes the sale itself,
  outside this API (derived).

## Not documented — ask the bank

- The production host, any test host or sandbox, and test credentials.
- The `amount` unit (sum or tiyin) for payment orders and invoices.
- The SMS step of `APILogin`: when it is triggered and how the code is sent back.
- The `sid` lifetime and the error returned when it expires.
- The ЭЦП in `signs[]`: what is signed, the format of `signature`, the values of `method`.
- The format and uniqueness scope of `uniq` and `num`, and what a repeated `uniq` returns.
- `result` of `SendPaymentIBK` (`1` in the sample, "document id and code 55" in the text),
  and whether an order at `55` (draft) still needs confirmation in internet banking.
- The meaning and finality of `CheckPayments2` states `53`, `54`, `56`.
- The full list of error codes.
- `dtype` values; `val` `"000"` and account `state` `2` in the `GetAccounts` sample.
- The path `/Mobile/svc/GetAccounts` versus `Mobile.svc`.
- The `date` format of `GetDoc1C` (`"2026-03-04"` in the sample, `dd.MM.yyyy` elsewhere).
- Whether `purpose` must repeat the code already sent in `purp_code`.
- How to recall a sent order, and whether an invoice can be cancelled.
- Invoices: the `status` values, the `Authorization` header scheme, the `purposeCode`
  directory (labelled "credit purpose"), and which side pays whom.
- GetOperDays `state` values other than `OPEN`.
