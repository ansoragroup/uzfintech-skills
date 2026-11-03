# Payme: money lifecycle, deadlines and reversals

Read this when building or reviewing a Payme integration, and raise these traps before
they cost money: timeouts, what can be undone and by whom, retries, OTP and token
validity, and who issues the fiscal receipt.

- Source: https://developer.help.paycom.uz/protokol-merchant-api/skhema-vzaimodeystviya/,
  https://developer.help.paycom.uz/metody-merchant-api/canceltransaction/,
  https://developer.help.paycom.uz/metody-merchant-api/setfiscaldata/,
  https://developer.help.paycom.uz/metody-subscribe-api/cards.get_verify_code/,
  https://developer.help.paycom.uz/metody-subscribe-api/receipts.cancel/,
  https://developer.help.paycom.uz/metody-subscribe-api/kholdirovanie/,
  https://developer.help.paycom.uz/telegram-bot/ (Russian pages), plus the references
  linked in each row
- Fetched: 2026-11-03

## Warn without being asked

1. **`payme.idempotent-replays`**: when code handles `CreateTransaction`,
   `PerformTransaction` or `CancelTransaction` → Payme repeats Create and Perform with the
   same params when a response is lost, and the sandbox sends all three twice and wants
   identical answers. Key on the Payme `id`, return the stored values, and never fulfil
   twice. [merchant](../merchant/README.md#idempotency-rules-derived)
2. **`payme.create-timeout-12h`**: when code reserves an order or handles Create/Perform →
   a state `1` transaction is cancelled **43 200 000 ms (12 h)** after the Payme `time`
   (state `-1`, reason `4`). Answer `-31008` to a Create or Perform after that and release
   the order. [merchant](../merchant/README.md#flow-and-state-machine)
3. **`payme.http-200-always`**: when the endpoint sits behind a framework error handler,
   auth middleware or a proxy → every answer, including business errors, must be HTTP 200;
   any other status is read as `-32400`. [common](../common/README.md#transport)
4. **`payme.cancel-is-the-refund`**: when the task mentions refunds → a Merchant API
   refund is `CancelTransaction` on a performed transaction (state `-2`, reason `5`).
   Cabinet refunds work only if it is implemented. It has no amount param, so it is always
   full. Answer `-31007` to refuse when the goods were fully delivered.
   [merchant](../merchant/README.md#error-codes)
5. **`payme.no-second-receipt`**: when code issues fiscal receipts → if Payme fiscalizes
   from `detail`, never register your own receipt for the same payment. Store a
   `SetFiscalData` `CANCEL` as a separate receipt; do not overwrite `PERFORM`.
   [fiscalization](../fiscalization/README.md#setfiscaldata-payme-calls-you-optional)
6. **`payme.check-before-debit`**: when writing `CheckPerformTransaction` → probe the
   database, billing and stock that Create/Perform need and answer `-32400` if one is down,
   so the payer is not debited for an order you cannot complete.
   [merchant](../merchant/README.md#gotchas)
7. **`payme.return-url-not-proof`**: when checkout redirects back to `callback` / `c` →
   the return is not a payment confirmation. Mark paid only on `PerformTransaction`
   (state `2`) or a Subscribe receipt in state `4`. [checkout](../checkout/README.md#flow)
8. **`payme.hold-30-days`**: when code uses `hold: true` → it is needed in both
   `receipts.create` and `receipts.pay`. Uzcard releases the hold automatically after 30
   days; Humo allows confirm or cancel within 30 days, after that only confirm.
   `receipts.confirm_hold` captures the whole amount. Holds need Payme staff to enable them
   and can be tested only in production. [subscribe](../subscribe/README.md#hold)
9. **`payme.one-time-account-lock`**: when a one-time order gets a second payment attempt
   → a new `id` while the account already has a state `1` transaction must get `-31008`.
   [merchant](../merchant/README.md#idempotency-rules-derived)
10. **`payme.otp-wait-is-validity`**: when building card binding → `cards.get_verify_code`
    returns `wait` in ms; the vendor defines it as how long the code stays valid (sample
    `60000`). Use a token only after `cards.verify` returns `verify: true`.
    https://developer.help.paycom.uz/metody-subscribe-api/cards.get_verify_code/
11. **`payme.one-time-token`**: when saving cards → `save: false` gives a token Payme
    deletes after one payment; recurring charges need `save: true`. Vendor advice: delete
    the token after 3 wrong PINs. [subscribe](../subscribe/README.md#methods)
12. **`payme.subscribe-runs-merchant-api`**: when a cashbox has both protocols → paying a
    Subscribe receipt runs the Merchant API calls against your endpoint (derived), so the
    12 h and replay rules apply there too. [subscribe](../subscribe/README.md#flow)
13. **`payme.detail-unit-price`**: when building `detail` → `price` is the **unit** price in
    tiyin and `discount` is the line total; `code` is the 17-digit IKPU and `package_code`
    is mandatory. [fiscalization](../fiscalization/README.md#detail-object)
14. **`payme.get-statement-mandatory`**: when the Merchant API is "done" → `GetStatement`
    is mandatory; filter on the Payme `time` (inclusive), ascending, and leave out failed
    creates. [merchant](../merchant/README.md#flow-and-state-machine)
15. **`payme.telegram-10s`**: when a Telegram bot takes Payme payments → answer
    `answerPreCheckoutQuery` within 10 s. https://developer.help.paycom.uz/telegram-bot/

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Merchant API transaction in state `1` | 43 200 000 ms (12 h) from the Payme `time` | cancelled: state `-1`, reason `4`; Create / Perform answer `-31008` | [merchant](../merchant/README.md#flow-and-state-machine) |
| Your answer to Create / Perform | no number published | Payme repeats the call; long silence pauses the payment for manual handling by Payme staff | [common](../common/README.md#delivery-and-retries-merchant-api) |
| Refund (`CancelTransaction` on state `2`) | not documented | see "Not documented" | https://developer.help.paycom.uz/metody-merchant-api/canceltransaction/ |
| Hold on an Uzcard card | 30 days | released automatically | [subscribe](../subscribe/README.md#hold) |
| Hold on a Humo card | 30 days to confirm or cancel | after that only `receipts.confirm_hold` | [subscribe](../subscribe/README.md#hold) |
| SMS code from `cards.get_verify_code` | `wait` ms from the response (vendor sample `60000`) | code no longer valid; request a new one | https://developer.help.paycom.uz/metody-subscribe-api/cards.get_verify_code/ |
| One-time token (`save: false`) | one payment | deleted by Payme | [subscribe](../subscribe/README.md#methods) |
| Card PIN (vendor recommendation) | 3 wrong attempts | delete the token | [subscribe](../subscribe/README.md#card-form-and-security-rules) |
| Checkout `callback_timeout` / `ct` | ms after a successful payment before the redirect; form comment says `15`, so set it | redirect timing only, not a payment state | [checkout](../checkout/README.md#gotchas) |
| Telegram `answerPreCheckoutQuery` | 10 s | the Payme page states only the deadline | https://developer.help.paycom.uz/telegram-bot/ |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Created, not performed; debit failed | Payme | `CancelTransaction {id, reason}` to your endpoint → state `-1` | n/a, nothing debited | once; repeats get the stored answer | none (no sale receipt yet; derived) | [merchant](../merchant/README.md#flow-and-state-machine) |
| Created, 12 h passed | you, on the next call | set `-1`, reason `4`; answer `-31008` | n/a | once | none (derived) | [merchant](../merchant/README.md#idempotency-rules-derived) |
| Performed; refund to the payer | merchant in the Payme cabinet; Payme then calls you | `CancelTransaction` → state `-2`, reason `5` | no, no amount param | once per transaction | Payme's cancel receipt, reported by `SetFiscalData` `type: CANCEL`; store it separately | https://developer.help.paycom.uz/metody-merchant-api/canceltransaction/, https://developer.help.paycom.uz/metody-merchant-api/setfiscaldata/ |
| Performed; goods fully delivered, you refuse | you | answer `-31007` to `CancelTransaction` | n/a | n/a | none | [merchant](../merchant/README.md#error-codes) |
| Subscribe receipt unpaid (state `0`) | you | `receipts.cancel {id}` → `21` → `50` | n/a | once | none (derived) | [subscribe](../subscribe/README.md#receipt-states) |
| Subscribe receipt paid (state `4`) | you | `receipts.cancel {id}` → `21` → `50` | no amount param; not documented | not documented | Payme `CANCEL` via `SetFiscalData`; own module: no refund method documented | https://developer.help.paycom.uz/metody-subscribe-api/receipts.cancel/ |
| Hold (state `5`) released | you; Uzcard automatically after 30 days | `receipts.cancel {id}` | n/a | once | not documented | [subscribe](../subscribe/README.md#hold) |
| Hold captured | you | `receipts.confirm_hold {id}` → state `4` | no, whole held amount | once | Payme `PERFORM` from `detail` | https://developer.help.paycom.uz/metody-subscribe-api/kholdirovanie/ |
| Telegram payment refund | not documented | not documented | | | not documented | https://developer.help.paycom.uz/telegram-bot/ |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| `CreateTransaction` | yes, same params when the response is lost; sandbox sends it twice | not published | Payme `id` | state `1` in time: stored `create_time`, `transaction`, `state`; timed out: cancel (`-1`, `4`) and `-31008`; other state: `-31008` | [merchant](../merchant/README.md#idempotency-rules-derived) |
| `PerformTransaction` | yes; sandbox twice | not published | Payme `id` | state `2`: stored `perform_time`, `state: 2`; cancelled or timed out: `-31008` | [merchant](../merchant/README.md#idempotency-rules-derived) |
| `CancelTransaction` | sandbox twice; live retry not stated | not published | Payme `id` | `-1` / `-2`: stored `cancel_time`, `state`; `2` that cannot be reversed: `-31007` | [merchant](../merchant/README.md#idempotency-rules-derived) |
| `CheckTransaction` | status probe | not published | Payme `id` | must show a perform or cancel that committed even if its response was lost | [merchant](../merchant/README.md#idempotency-rules-derived) |
| `CheckPerformTransaction` | not stated | not published | none, creates nothing | stateless; same answer each time | [merchant](../merchant/README.md#flow-and-state-machine) |
| `SetFiscalData` | not documented | not documented | `id` + `type` (derived) | keep `PERFORM` and `CANCEL` as separate records | [fiscalization](../fiscalization/README.md#setfiscaldata-payme-calls-you-optional) |
| `receipts.pay` (you call Payme) | n/a | n/a | none documented | on a timeout read `receipts.check` / `receipts.get` before paying again (derived) | [subscribe](../subscribe/README.md#methods) |

## Fiscal receipts

- **Who**: Payme fiscalizes from the `detail` you pass in `CheckPerformTransaction`
  `result.detail`, `receipts.create` `params.detail`, or the checkout POST form (base64 of
  the JSON). The GET link has no `detail`. [fiscalization](../fiscalization/README.md#flow)
- **Sale and refund**: Payme sends `SetFiscalData {id, type: PERFORM|CANCEL,
  fiscal_data}` after the receipt succeeds, whichever protocol created it. The tax
  authority makes separate payment and cancel receipts, so store `CANCEL` as its own
  record. Answer `{"result": {"success": true}}`; errors `-32001`, `-32700`, `-32602`.
- **Never twice**: when Payme fiscalizes, do not also register the payment through your own
  fiscal module or another OFD.
- **Own fiscal module** (Subscribe API): report the receipt with `receipts.set_fiscal_data
  {id, fiscal_data{receipt_id (integer), qr_code_url, ...}}` (back-end `X-Auth`). No
  refund-receipt counterpart is documented.
- **Fields**: `receipt_type` `0`; `items[]` with `title`, `price` (unit, tiyin), `count`,
  `code` (IKPU), `package_code`, `vat_percent`; optional `discount` (line total, tiyin),
  `units`; optional `shipping {title, price}` in tiyin.
- **Sum (derived)**: `sum(price x count - discount) + shipping.price` should equal the
  transaction `amount` in tiyin. A refund is always the full amount, so the cancel receipt
  cannot exceed the sale.
- **Timing**: Payme reports after the receipt succeeds; no deadline is published for a
  receipt from your own module.

## Not documented — ask the provider

- How long after perform a `CancelTransaction` refund or a `receipts.cancel` of a paid
  receipt is still allowed.
- Partial refunds: neither `CancelTransaction` nor `receipts.cancel` takes an amount.
- Live retry count and interval for Create / Perform, the response timeout on your
  endpoint, how long "silent for long" is, and whether Cancel and `SetFiscalData` retry.
- Whether a `CANCEL` fiscal receipt is always registered automatically on a refund.
- How a merchant with its own fiscal module reports a refund receipt
  (`receipts.set_fiscal_data` has no type field).
- Subscribe API error codes, the lifetime of a `save: true` token, and the resend limit
  for `cards.get_verify_code`.
- What a never-confirmed Humo hold does after 30 days, and how an Uzcard auto-release shows
  in the receipt state.
- An idempotency key for retrying `receipts.pay`.
- Refunds and fiscal receipts for Telegram bot payments.
