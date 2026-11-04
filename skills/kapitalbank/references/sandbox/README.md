# Kapital API test data and sample values

Hand-written notes with exactly what Kapitalbank publishes for testing the Kapital API.
The answer is short: **no sandbox, no test host and no test credentials are published**.
The pages print paths without a host, and access is granted per company after the
connection application. Transport, auth and errors:
[`../kapital-api/README.md`](../kapital-api/README.md).

- Sources: https://b2b-api-docs.kapitalbank.uz/kapital-api-connect (connection) and the
  method pages named in "Vendor sample values" (Russian pages)
- Fetched: 2026-11-04

## Environments

| What | Test | Production |
|---|---|---|
| API host | not published | not published; from the bank's connection instruction |
| Credentials | not published | the company's internet-banking login (`IB#` prefix) and password |
| Payment orders | no test mode or flag in any method | real orders, signed with the company's ЭЦП |
| Exchange rates (`GetCoursesB2`) | no authorization needed, but the host is still unpublished | same |

- Every `SendPaymentIBK` that the bank accepts is a **real** payment order. There is no
  `test` field. Warning
  [`kapitalbank.host-and-sandbox-not-published`](../lifecycle/README.md).
- Ask the bank whether a test contour exists for your company; until it confirms one in
  writing, test against a local mock built from the samples below (derived).

## Test credentials (how to get them)

1. Download the connection application from the connect page, fill it in and hand it in at
   a Kapitalbank branch (connect page).
2. After access is granted, follow the bank's connection instruction
   (`api-documentation.pdf`, linked from the connect page). It is not part of this skill.
3. Agree the login mode with the bank: an SMS code, or IP restriction with your server's
   egress IPs (warning [`kapitalbank.sms-or-ip-restriction`](../lifecycle/README.md)).
4. Ask for the ЭЦП signing method for `signs[]`, the `amount` unit, and whether a test
   contour exists.

## Not published

- No test or sandbox host, no test login, no test `sid`, no test certificate or signature.
- No test accounts, MFOs or INNs with expected outcomes, and no way to simulate a rejected
  order or a closed operating day.
- No Postman collection and no error-code list.
- The purpose-code tool works offline and needs none of this:
  `scripts/purpose_codes.py --selftest`.

## Test scenarios against a mock (derived)

The docs list no scenarios. Replay these shapes in a mock of your own:

| Goal | Mock answer | Your code should |
|---|---|---|
| login from a wrong IP | the `61002` sample below | stop, alert, not retry in a loop |
| success envelope | `error: null` and also `error: {"code": 0, "message": "string"}` | treat both as success |
| lost `SendPaymentIBK` reply | drop the connection after the call | call `CheckPayments2` by `uniq` and not resend while the order exists (`kapitalbank.poll-status-not-resend`) |
| old purpose code | your own pre-send check with `purpose_codes.py check` | block `00699`, `00545` and other old codes before the call |
| unfinished day | `GetDoc1C` with `fin: 0` | treat the statement as incomplete and fetch again later |
| MT940 text | the sample string with `\\n` | parse both escaped and real line breaks |

## Vendor sample values

Copied exactly from the request and response samples on the method pages, except the IP
in the login error, which is replaced with `<CLIENT_IP>`. Full samples for every method
are in [`../kapital-api/examples/`](../kapital-api/examples/). These values are format
samples: none is documented as a working account, credential or test object. Never send
them to the bank.

Login refused by IP restriction (`Mobile.svc/APILogin`, authorization/user-authorization):

```json
{
  "error": {
    "code": 61002,
    "message": " IP : <CLIENT_IP>"
  },
  "id": 108377027,
  "result": null
}
```

Payment order (`/Mobile.svc/SendPaymentIBK`, payment-orders/create-payment-order):

```json
{
  "client_id": 123123,
  "sid": "example-session-id",
  "payment": {
    "document": {
      "num": "157",
      "branch": null,
      "general_id": null,
      "uniq": "20200504111647102176",
      "ddate": "20.05.2020",
      "mfo_dt": "00974",
      "acc_dt": "2020800002345678001",
      "name_dt": "OOO \\\"TRUE CLIENT OF BANK\\\"",
      "inn_dt": "777777777",
      "mfo_ct": "00974",
      "acc_ct": "20208000012345678001",
      "name_ct": "test",
      "inn_ct": "",
      "purpose": "test",
      "purp_code": "00699",
      "amount": 100,
      "dtype": "35",
      "state": 1,
      "dir": 1,
      "err": "",
      "err_msg": "",
      "anor": 1
    },
    "signs": [
      {
        "method": 1,
        "sert_num": "string",
        "signature": "string"
      }
    ]
  }
}
```

```json
{
  "result": 1,
  "error": {
    "code": 0,
    "message": "string"
  }
}
```

Status check (`/Mobile.svc/CheckPayments2`, payment-orders/payment-status):

```json
{
  "sid": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "client_id": 100001,
  "uniqs": [
    "UNIQ001",
    "UNIQ002",
    "UNIQ003"
  ]
}
```

Sample-specific caveats:

- `purp_code` `"00699"` is an **old** code, refused since 26.05.2026; the new code is `00031`
  (`purpose_codes.py check 00699`). `purpose` `"test"` has none of the required parts of
  "Детали платежа" (warning `kapitalbank.payment-details-content`). A correct order with
  placeholders is
  [`send-payment-ibk-new-code.request.json`](../kapital-api/examples/send-payment-ibk-new-code.request.json).
- `acc_dt` has 19 digits; accounts are 20 digits elsewhere in the docs.
- `name_dt` shows escaped quotes inside the JSON string; send ordinary JSON escaping.
- `signs[]` holds `"string"` placeholders; the real signature format is not published.
- `amount` `100` says nothing about the unit (warning `kapitalbank.amount-units-unstated`).
- The `CheckPayments2` reply sample shows `state` `1`, `2`, `3`; the mapping on the same page
  returns `53`, `54`, `55` or `56`.
- The `sid` values (`"example-session-id"`, `"DemoDemoDemoDemo"`, the 32-character one above)
  are placeholders, not test sessions.
