---
name: kapitalbank
description: Exact API contracts for the Kapital API (KapitalAPI), the corporate Open API of Kapitalbank (Uzbekistan) to internet banking (ДБО) for legal entities - APILogin with the internet-banking login (IB# prefix, Basic auth, SMS code or IP restriction), payment orders through SendPaymentIBK with ЭЦП signs over СЭП or Anor 24/7, CheckPayments2 status polling by uniq, GetDoc1C and GetMT940 statements, account, operating-day, budget and treasury payee checks, exchange rates and invoices - plus the CBU payment purpose codes (directory 60, new codes from 06.05.2026, old codes refused from 26.05.2026) and the "Детали платежа" content rules, which apply to UZS payment orders in every Uzbek bank, with an offline lookup and check tool. Use when building, reviewing, debugging or testing a Kapitalbank corporate API integration, or when choosing, migrating or validating the purpose code and payment details of any UZS payment order.
---

# Kapitalbank integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json` (Kapital API): trimmed JSON Schemas with `requestBody` and
  `responses."200"`, carrying the source URL and fetched date;
- `examples/`: anonymized bodies, copied from the vendor samples where they exist.

Transport, the unpublished host, authorization, statuses and errors are in
[references/kapital-api/README.md](references/kapital-api/README.md); read it first. The
purpose codes and the "Детали платежа" rules are a CBU rule for **every Uzbek bank**, in
[references/purpose-codes/](references/purpose-codes/README.md).

## Products

| Product | Methods | Reference |
|---|---|---|
| Kapital API | APILogin, SendPaymentIBK, CheckPayments2, GetDoc1C, GetMT940, GetAcc1C, GetAccounts, GetOperDays, GetBudjetAcc, GetNalogAcc, GetCoursesB2, api/invoices, api/invoices/check-statuses | [references/kapital-api/](references/kapital-api/README.md) |
| Purpose codes (every Uzbek bank) | CBU directory 60: 115 new codes, 69 old codes and their mapping, "Детали платежа" content, dates, errata, offline tool | [references/purpose-codes/](references/purpose-codes/README.md) |
| Sandbox and test data | what is and is not published, how to get access, mock scenarios, vendor sample values | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | warnings, СЭП / Anor windows, `fin`, recall, retries, idempotency, open questions | [references/lifecycle/](references/lifecycle/README.md) |

The pages print paths without a host (`Mobile.svc/APILogin`, `/Mobile.svc/SendPaymentIBK`,
`api/invoices`). Every call is `POST` JSON from your server; the host comes from the bank's
connection instruction and lives in configuration.

## Which product?

| The user wants to... | Use |
|---|---|
| log in and get `sid` | APILogin with `Authorization: Basic base64("IB#<LOGIN>:<PASSWORD>")` |
| run unattended, without an SMS code | IP restriction agreed with the bank; Basic auth on every request |
| send a UZS payment order | GetOperDays -> (budget payee: GetBudjetAcc / GetNalogAcc) -> SendPaymentIBK with `uniq`, `purp_code`, `purpose`, `signs[]` |
| pay outside banking hours | SendPaymentIBK with `anor: 1` (Anor, 24/7); `anor: 0` is СЭП, 9:00–17:00 |
| learn the outcome of an order | CheckPayments2 by `uniqs[]` or `general_ids[]` (100 at most) |
| get a day's statement | GetDoc1C (JSON with `fin`) or GetMT940 (MT940 text) |
| read balances and account details | GetAcc1C (with `sid`) or GetAccounts |
| check a budget or treasury payee | GetBudjetAcc (`ls`, `inn`) or GetNalogAcc (`ls`) |
| show exchange rates | GetCoursesB2 (no authorization) |
| issue an invoice to another company | api/invoices, then api/invoices/check-statuses |
| pick or migrate a purpose code, write "Детали платежа" (any bank) | Purpose codes: `scripts/purpose_codes.py` |
| test | [sandbox](references/sandbox/README.md): no sandbox is published; mock from the samples |

## Rules that apply everywhere

- Success is `error == null` or `error.code == 0`; errors arrive with HTTP `200`. Check
  `error` in every answer.
- The internet-banking login and password are company secrets: server side only, from a
  secret store, never logged. The same goes for `sid` and the ЭЦП `signature`.
- The `amount` unit is not stated; confirm sum or tiyin with the bank in writing.
- Store `uniq` before SendPaymentIBK. After a lost reply ask CheckPayments2 by `uniq`
  before you send again: a second call is a second real order.
- No webhooks are published: poll CheckPayments2 and the statements.
- Every UZS payment order, in any Uzbek bank, carries a **new** purpose code and a
  "Детали платежа" text with the code, the contract number and date, the goods, works or
  services, and the payment type. Old codes are refused from 26.05.2026.
- The host, a sandbox, test credentials and the ЭЦП format are not published. Never invent
  them; send the user to the bank.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the deadline or
consequence, and the fix. Every window, recall path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `kapitalbank.old-purpose-codes-rejected`: old purpose codes are refused from 26.05.2026
  in every Uzbek bank; check templates and stored codes with `purpose_codes.py check`.
- `kapitalbank.one-old-code-many-new`: nine old codes split into several new ones (`00545`
  -> `00039` / `00068` / `00069` / `00076` by material); map them per goods, not by script.
- `kapitalbank.payment-details-content`: "Детали платежа" needs the code, the contract
  number and date (when there is a contract), the goods or services and the payment type.
- `kapitalbank.host-and-sandbox-not-published`: no host, test host or sandbox is printed;
  take the host from the bank's connection instruction and keep it in configuration.
- `kapitalbank.ib-credentials-basic-auth`: APILogin takes the company's internet-banking
  login (`IB#` prefix) and password as Basic auth; secret store, server only, no logs.
- `kapitalbank.sms-or-ip-restriction`: an SMS code may be asked, which a server cannot
  answer; agree IP restriction and the egress IPs, or expect `61002`.
- `kapitalbank.payment-needs-signature`: SendPaymentIBK needs `signs[]` (ЭЦП); the signing
  method is not published, so get it from the bank before building the order.
- `kapitalbank.unique-doc-number`: generate `uniq` per order, store it before the call and
  never reuse it; it is the only lookup key.
- `kapitalbank.poll-status-not-resend`: no webhooks and no recall method; after a lost
  reply ask CheckPayments2 by `uniq`, and resend only when the order is not found.
- `kapitalbank.oper-day-dating`: `anor: 0` (СЭП) runs 9:00–17:00 on open days, `anor: 1`
  (Anor) 24/7; a `fin: 0` statement is not final.
- `kapitalbank.check-budget-account-first`: check budget payees with GetBudjetAcc or take
  treasury requisites from GetNalogAcc; budget codes are not in the commercial table.
- `kapitalbank.amount-units-unstated`: `amount` is decimal with no stated unit; confirm it
  with the bank and test with a small amount.
- `kapitalbank.error-in-http-200`: errors come with HTTP `200`; success samples print
  `{"code": 0}` as well as `null`.

## Top gotchas

1. The vendor SendPaymentIBK sample uses `purp_code` `"00699"`, an old code (now `00031`),
   `purpose` `"test"` and a 19-digit `acc_dt`. Copy its shape, not its values.
2. SendPaymentIBK's text says success returns the document id and code `55`, but the sample
   prints `"result": 1`. Read the outcome from CheckPayments2, not from `result`.
3. CheckPayments2 maps internal statuses to `55` (draft), `53`, `54`, `56`; the reply
   sample shows `1`, `2`, `3`. A deleted draft loses its `uniq`.
4. The account-by-number path is printed `/Mobile/svc/GetAccounts`; all others use
   `Mobile.svc`. Confirm with the bank.
5. `Client.id` is a string in the login answer; `client_id` in requests is an integer.
6. GetDoc1C's sample sends `date` `"2026-03-04"`; every other date is `dd.MM.yyyy`.
7. GetMT940's sample writes line breaks as `\\n`, and `platPurposeCode` is an integer
   (`76` for `00076`); accept both line breaks and left-pad codes to 5 digits.
8. Invoices: `amount` greater than `5000000`, `dueDate` later than now, `purposeText` of
   20–450 characters labelled "credit purpose", errors in HTTP `200`.
9. The CBU sheets contain Latin look-alike letters in some Cyrillic names and one shifted
   Uzbek row; `codes.json` keeps them as published. Type the goods name yourself.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then the product checklist:

- [checklists/payment-orders.md](checklists/payment-orders.md) (SendPaymentIBK, CheckPayments2)
- [checklists/purpose-codes.md](checklists/purpose-codes.md) (codes and "Детали платежа", any bank)
- [checklists/statements.md](checklists/statements.md) (GetDoc1C, GetMT940, accounts)
- [checklists/go-live.md](checklists/go-live.md) (access, ЭЦП, written answers from the bank)

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file holds python3 scripts, standard library only, all offline.

```sh
python3 scripts/purpose_codes.py check 00545 [--date YYYY-MM-DD]
python3 scripts/purpose_codes.py old 00545
python3 scripts/purpose_codes.py search алюмин
python3 scripts/purpose_codes.py details --code 00076 --goods "алюминиевые смесители" \
    --contract-no 100001 --contract-date 03.11.2026 --payment-type оплата
python3 scripts/purpose_codes.py account 20208000012345678001 --mfo 01042
python3 scripts/validate.py --list [text]
python3 scripts/validate.py send-payment-ibk body.json [--part response]
```

`purpose_codes.py` prints `OK`, `NO ...` or `INVALID` with the reason, and exits `1` on a
rejected, unknown or invalid input. `validate.py` prints `OK` or `INVALID` with JSON paths.
`sign.py` has no Kapital recipe: the ЭЦП for `signs[]` is not published. Run the tools
before you call a code, a text or a payload correct, and quote their output.

## Answering rules

- Reply in the user's language, but never translate method names, fields, codes, enum
  values or the Russian and Uzbek code names.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation. Code takes
  the host and credentials from configuration and runs as written.
- With several providers in one task, work each one from its own SKILL.md, then compare.
  Never carry a rule (units, auth, retries) over from another provider. The purpose-code
  rules are the exception: they hold for UZS payment orders in every Uzbek bank.
- Lifecycle: before you finish an answer that creates, signs, retries or reconciles a
  payment order, check "Warn without being asked" and
  [references/lifecycle/](references/lifecycle/README.md). State the deadline, whether the
  step can be undone, and the warning ID, even if nobody asked. For an item under "Not
  documented", say so and send the user to the bank.
- Quote paths, fields, types and codes exactly as they appear in the references. If a fact
  is not there, say the docs do not specify it and link the `Source:` page.
- For tests use a mock built from [references/sandbox/](references/sandbox/README.md).
  Kapitalbank publishes no test host or credentials; never send the vendor sample values.
  Never use real credentials or real company data; use placeholders such as `<LOGIN>`,
  `<PASSWORD>`, `<SID>`, Merchant Example and `merchant.example.com`.
- Bank tariffs and fees for payment orders differ per client contract. Do not quote or
  estimate them; say they come from the client's agreement with the bank.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
