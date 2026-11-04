# Atmos Withdrawal by PINFL (debit a person's cards found by PINFL under your contract)

Hand-written notes. Transport and auth: [`../common/README.md`](../common/README.md).
Schemas: [`schemas/`](schemas/). Examples: [`examples/`](examples/).

- Source: https://docs.atmos.uz/en/#withdrawal-by-tin-pinfl,
  https://docs.atmos.uz/en/#transaction-creation-pinfl,
  https://docs.atmos.uz/en/#transaction-confirmation-pinfl,
  https://docs.atmos.uz/en/#transaction-data-request,
  https://docs.atmos.uz/en/#transaction-cancellation-pinfl,
  https://docs.atmos.uz/en/#updating-cards-by-pinfl,
  https://docs.atmos.uz/en/#checking-card-update-status, https://docs.atmos.uz/en/#status-guide
- Fetched: 2026-11-04
- Needs: a Bearer token ([auth](../common/README.md#auth)); the service enabled for you by
  Atmos; the person's PINFL, passport series and number, full name and your contract
  number with them; an ePOS `branch_id` and `terminal_group_id` if Atmos gave you one.

No card number, token or SMS code from the payer is used. Atmos finds the cards linked to the
PINFL and debits them. That makes it a product for collecting under a signed contract
(derived from the `contract_number` field); keep proof of the person's consent.

## Flow

```
POST /ppa/transaction/create {ext_id, first_name, last_name, middle_name, pinfl,
     passport_series, passport_number, contract_number, amount, partial_debit?, ofd_items?, epos?}
   └─> payload {transaction_id, transaction_status: CREATED, available_balance}
POST /ppa/transaction/confirm {ext_id, transaction_id}
   └─> payload {transaction_status: SUCCESS, details[] {pan, amount, status}}, ofd_url?
or, before confirm:  POST /ppa/transaction/cancel {ext_id, transaction_id}  -> CANCELED
any time:            POST /ppa/transaction/check {ext_id, pinfl, passport_series, passport_number}
-109 "cards not found"?  POST /ppa/cards/update-cards-list {pinfl, ext_id, epos}
                         POST /ppa/cards/check/{ext_id}  -> payload.status SUCCESSFUL
                         then create a new transaction with a new ext_id
```

Base URL: `https://apigw.atmos.uz/ppa`.

## Methods

| Method | Endpoint | Params (`*` required) | Result (`payload`) |
|---|---|---|---|
| pinfl-create | `POST /ppa/transaction/create` | `ext_id*`, `first_name*`, `last_name*`, `middle_name*`, `pinfl*`, `passport_series*`, `passport_number*`, `contract_number*`, `amount*`, `partial_debit`, `ofd_items`, `epos {branch_id, terminal_group_id}` | `transaction_id`, `transaction_status`, `available_balance` |
| pinfl-confirm | `POST /ppa/transaction/confirm` | `ext_id*`, `transaction_id*` | `transaction_status`, `details[]`; `ofd_url` only if fiscal data was sent on create |
| pinfl-check | `POST /ppa/transaction/check` | `ext_id*`, `pinfl*`, `passport_series*`, `passport_number*` | as confirm |
| pinfl-cancel | `POST /ppa/transaction/cancel` | `ext_id*`, `transaction_id*` | `transaction_status: CANCELED` |
| pinfl-update-cards | `POST /ppa/cards/update-cards-list` | `pinfl*`, `ext_id`, `epos.branch_id*`, `epos.terminal_group_id*` | not documented (HTTP `200` on success) |
| pinfl-cards-check | `POST /ppa/cards/check/{ext_id}` | path `ext_id*` | `ext_id`, `masked_pinfl`, `status` (`SUCCESSFUL` when done), `request_date` |

`ofd_items` and `epos` are optional, but once you send one of them every field inside it is
required. The PINFL `ofd_items` shape is `{ofd_code, package_code, tin}`, not the payments
shape.

## Errors

Success is `code` `"200"` (a string in most samples, a number in `cards/check`). The table
header says the code is `ok`, `progress` or `error`; the samples never show those words.
Errors come as `{code: <negative>, message, payload: null}`:

| Code | Meaning | What to do |
|---|---|---|
| `-100`, `-200` | unexpected error | retry later; then `check` before a new create |
| `-101`, `-102` | contract or client registration failed | ask Atmos |
| `-103` | client with this PINFL not available | do not retry |
| `-105`, `-106`, `-107`, `-108` | no card with balance, not enough balance, full amount not possible, balance unavailable | retry later, or allow `partial_debit` if your contract permits it |
| `-109` | no cards for this PINFL | run `update-cards-list`, wait for `SUCCESSFUL`, try again |
| `-202` | the transaction failed (only from `check`) | final |
| `-301` | client, contract or ePOS not found: the check data does not match the create data | send the same identity fields as on create |
| `-302` | `ext_id` already used | never reuse an `ext_id`; use `check` to read the earlier one |
| `-303` | a field is invalid (the message names it) | fix the field |
| `-306` | amount below the minimum | the minimum is not published; ask Atmos |
| `-307` | ePOS not found or not sent | fix `epos` |
| `-308` | no request with this `ext_id` | wrong id, or the create never arrived |

## Gotchas

- Money moves on `confirm`, not on `create`. `cancel` works only **before** `confirm`; no
  refund call is documented for a confirmed PINFL debit. Ask Atmos how to return money.
- `ext_id` is your idempotency key and must be unique for ever (`-302`). On a timeout call
  `check` with the same `ext_id`; do not create again with a new one until you know the
  first failed.
- `partial_debit` defaults to `false`. With `true` Atmos may debit less than `amount` from
  one or more cards; sum `details[].amount` for what was really taken (derived).
- `details[]` lists each card that was debited with a masked `pan`. Do not show the full
  list to anyone but the cardholder.
- `available_balance` in the create answer is the person's card balance: do not log or
  store it (derived).
- PINFL is 14 digits; some vendor samples show an 18-digit value. Validate 14 digits.
- `transaction_id` is a string in some samples and a number in others; store it as a
  string.
- `update-cards-list` may be billed and its use should be agreed with Atmos first; its
  response body is not documented. Read the result with `cards/check/{ext_id}`.
- The `check` sample sends `contract_number` and `amount`, which the table does not list.
  Sending them is harmless; the table fields are the required ones.

## Examples

[`examples/`](examples/): pinfl-create, pinfl-confirm, pinfl-check, pinfl-cancel (request and
response each), pinfl-update-cards (request), pinfl-cards-check (response).
