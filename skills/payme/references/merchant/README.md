# Payme Merchant API (JSON-RPC methods you implement)

Hand-written notes. Transport, auth, the error envelope and the sandbox:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://developer.help.paycom.uz/protokol-merchant-api/ and
  https://developer.help.paycom.uz/metody-merchant-api/ (Russian pages)
- Fetched: 2026-11-03
- Direction: **Payme calls you.** You expose one HTTPS Endpoint URL (set in the cashbox
  settings); Payme sends every method to it as JSON-RPC 2.0 over `POST`.

## Units and types

| Type | Shape | Rule |
|---|---|---|
| `ID` | string, 24 chars | Payme transaction id (`params.id`); your idempotency key |
| `Timestamp` | integer, 13 digits | Unix epoch **milliseconds** (UTC) |
| `Amount` | integer > 0 | **tiyin** (1 UZS = 100 tiyin) |
| `Account` | object | fields you define in the cashbox, e.g. `{"order_id": "100001"}` |
| `Receiver` | `{id, amount}` | `id` = receiver cashbox id, `amount` in tiyin; split ("chain") payments only |
| `transaction` | string | **your** transaction id in your billing; format is yours |
| `State` | integer | `1`, `2`, `-1`, `-2` (below) |
| `Reason` | integer or `null` | `1`, `2`, `3`, `4`, `5`, `10` (below) |

## Flow and state machine

```
CheckPerformTransaction (no state)
        │
CreateTransaction ──> 1 (created) ──PerformTransaction──> 2 (performed)
                         │                                   │
                CancelTransaction                    CancelTransaction
                         ▼                                   ▼
                  -1 (cancelled)                 -2 (cancelled after perform)
```

| State | Meaning |
|---|---|
| `1` | created, waiting for perform |
| `2` | performed (paid); fulfil the order |
| `-1` | cancelled before perform |
| `-2` | cancelled after perform (refund) |

| Reason | Meaning |
|---|---|
| `1` | one or more receivers not found or inactive |
| `2` | debit error at the processing centre |
| `3` | transaction execution error |
| `4` | timeout (12 h after creation) |
| `5` | refund |
| `10` | unknown error |

1. `CheckPerformTransaction {amount, account}`: can this account be paid with this amount?
   Create nothing. Return `allow: true`, optionally `detail` (fiscal items, see
   [`../fiscalization/`](../fiscalization/README.md)) and `additional` (tell Payme staff if
   you use it).
2. `CreateTransaction {id, time, amount, account}`: validate account and amount again,
   persist the transaction keyed by `id`, reserve the order ("waiting for payment"), block
   order edits. Return `create_time` (your time), `transaction`, `state: 1`, and
   `receivers` only for split payments (omit or `null` otherwise).
3. `PerformTransaction {id}`: Payme debited the payer. Mark paid, fulfil. Return
   `transaction`, `perform_time`, `state: 2`.
4. `CancelTransaction {id, reason}`: cancel a created (`-1`) or performed (`-2`)
   transaction. Return `transaction`, `cancel_time`, `state`. Refunds from the merchant
   cabinet work only when this method is implemented.
5. `CheckTransaction {id}`: return the stored `create_time`, `perform_time`,
   `cancel_time` (0 when not happened), `transaction`, `state`, `reason` (`null` unless
   cancelled).
6. `GetStatement {from, to}` (**mandatory**): reconciliation. Return every successfully
   created transaction with `from <= time <= to` (Payme `time`, inclusive), sorted
   ascending by `time`; `[]` when none. Never include transactions whose create failed.
7. `SetFiscalData` (optional): Payme reports the fiscal receipt it registered. See
   [`../fiscalization/`](../fiscalization/README.md).

Timing rules from the contract:

- A transaction in state `1` is cancelled by timeout **43 200 000 ms (12 h)** after its
  Payme `time`: state `-1`, reason `4`.
- If a `CreateTransaction` or `PerformTransaction` response is lost, Payme repeats the call
  with the same params. If your server stays silent for long, the payment is paused and a
  Payme employee handles it manually.
- A debit failure makes Payme call `CancelTransaction` itself.

## Methods

| Method | Params (`*` required) | Result | Method errors |
|---|---|---|---|
| `CheckPerformTransaction` | `amount*`, `account*` | `allow*`, `additional`, `detail` | `-31001`, `-31050..-31099` |
| `CreateTransaction` | `id*`, `time*`, `amount*`, `account*` | `create_time*`, `transaction*`, `state*` (1), `receivers` | `-31001`, `-31008`, `-31050..-31099` |
| `PerformTransaction` | `id*` | `transaction*`, `perform_time*`, `state*` (2) | `-31003`, `-31008`, `-31050..-31099` |
| `CancelTransaction` | `id*`, `reason*` | `transaction*`, `cancel_time*`, `state*` | `-31003`, `-31007` |
| `CheckTransaction` | `id*` | `create_time*`, `perform_time*`, `cancel_time*`, `transaction*`, `state*`, `reason*` | `-31003` |
| `GetStatement` | `from*`, `to*` | `transactions*` (Transaction[]) | (common only) |
| `SetFiscalData` | `id*`, `type*`, `fiscal_data*` | `success*` | `-32001`, `-32700`, `-32602` |
| `ChangePassword` | not documented on the doc site | not documented | see Gotchas |

`GetStatement` Transaction fields: `id`, `time`, `amount`, `account`, `create_time`,
`perform_time`, `cancel_time`, `transaction`, `state`, `reason`, `receivers` (optional).

## Responses

- Success: `{"result": {...}, "id": <request id>}`.
- Error: `{"error": {"code": <int>, "message": {"ru", "uz", "en"}, "data": ...}, "id": <request id>}`.
  `message` is shown to the payer, so localize all three languages.
- Always echo the request `id` (an integer).
- Send `HTTP 200` with `Content-Type: text/json; charset=UTF-8` for both success and
  business errors. Details: [`../common/README.md`](../common/README.md).

## Error codes

Common (JSON-RPC level) codes are in [`../common/README.md`](../common/README.md):
`-32300`, `-32700`, `-32600`, `-32601`, `-32504`, `-32400`.

| Code | Meaning | Typical method |
|---|---|---|
| `-31001` | wrong amount: does not match the order (one-time accounts) | CheckPerform, Create |
| `-31003` | transaction not found | Perform, Cancel, Check |
| `-31007` | cannot cancel: the goods or service were fully delivered | Cancel |
| `-31008` | operation not allowed in the current transaction state | Create, Perform |
| `-31050..-31099` | wrong account input (order not found, login not found, ...). Localized `message` is **mandatory**; `data` = the name of the `account` sub-field | CheckPerform, Create, Perform |

## Idempotency rules (derived)

The sandbox sends `CreateTransaction`, `PerformTransaction` and `CancelTransaction` twice
and requires the repeat to return the **same** response as the first call.

- `CreateTransaction` with a known `id`: if state is `1` and not timed out, return the
  stored `create_time`, `transaction`, `state` unchanged. If it timed out, cancel it
  (`-1`, reason `4`) and answer `-31008`. If state is not `1`, answer `-31008`.
- `CreateTransaction` with a new `id` while a one-time account already has a transaction in
  state `1`: `-31008` (sandbox scenario "new transaction, account waiting for payment").
  Accumulative accounts (e.g. a wallet top-up) may accept many transactions.
- `PerformTransaction` on state `2`: return the stored `perform_time` and `state: 2`. On a
  cancelled transaction, or a timed-out one: `-31008`.
- `CancelTransaction` on `-1` / `-2`: return the stored `cancel_time` and `state`. On `2`
  when the order can no longer be reversed: `-31007`.
- `CheckTransaction` must reflect a perform or cancel that committed even if the HTTP
  response was lost.

## Gotchas

- The doc site swaps two pages: `/metody-merchant-api/checkperformtransaction/` shows
  **CheckTransaction**, and `/metody-merchant-api/checktransaction/` shows
  **CheckPerformTransaction**. The schema files cite the page that holds the content.
- `ChangePassword` is not on the fetched doc site. Unknown methods must answer `-32601`
  with the method name in `data`; ask Payme support before relying on any other contract.
- `transaction` is a string even if your ids are numbers.
- Unset times are `0`, not `null`; `reason` is `null`, not `0`.
- Amounts are tiyin: 50 000 UZS is `5000000`.
- `GetStatement` filters on the **Payme** `time` from `CreateTransaction`, not on your
  `create_time`.
- `-31050..-31099` without a localized `message` and `data` fails the sandbox.
- Vendor recommendation: `CheckPerformTransaction` should probe every system that
  `CreateTransaction` and `PerformTransaction` depend on (database, billing, stock) and
  answer `-32400` if one is down, so the payer is not debited for an order you cannot
  complete.

## Examples

[`examples/`](examples/): request and response pairs for every method
(`check-perform-transaction`, `create-transaction`, `perform-transaction`,
`cancel-transaction`, `check-transaction`, `get-statement`, `set-fiscal-data`), plus
`error.response.json` (account error) and `error-transaction-not-found.response.json`.
