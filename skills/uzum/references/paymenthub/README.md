# Uzum PaymentHub (BaaS: JSON-RPC payments, transfers, card binding)

Hand-written notes from the HTML reference (no machine-readable spec is published).
Method details: [`methods.md`](methods.md). Errors: [`errors.md`](errors.md). Per-method
JSON Schemas: [`schemas/`](schemas/) (`params` and `result` for each method).

- Source: https://developer.uzumbank.uz/paymenthub/ (Russian pages)
- Fetched: 2026-11-03
- Direction: your backend calls Uzum. No callbacks are documented: poll receipt status.

## Transport and auth

| Item | Value |
|---|---|
| Protocol | JSON-RPC 2.0 over HTTPS (TLS 1.2), one `POST` per call |
| Test host | `https://topup.ub.ufintech.uz` (from "Getting started"; path not stated) |
| Production host | not published; issued at onboarding |
| Auth | `Authorization: Basic base64(<BASIC_USER>:<BASIC_PASSWORD>)` on every call |
| Headers | `Content-Type: application/json`; `Accept-Language: EN` (default) / `RU` / `UZ` |
| SMS language | `cards.add` also reads a `lang` header `RU` (default) / `EN` / `UZ` |

Envelope: request `{"jsonrpc": "2.0", "id": <string|number>, "method": "...", "params": {...}}`;
response has `result` on success or `error {code, message, data?}` on failure. The partner is
identified only by the Basic-auth login; there is no merchant id in the auth.

## Products and receipt types

| Scenario | Methods | Receipt `type` |
|---|---|---|
| Online payment by card token (utility / service providers) | `merchant.*` -> `receipt.create` -> `receipt.pay.by.card` | 1 |
| Online payment with hold | not documented as a public flow | 2 |
| Card to card | listed in models only | 5 |
| Account to card (payouts from your corporate account) | `account.attached.list {type: 6}` -> `receipt.account.create.transfer` -> `receipt.account.confirm.transfer` | 6 |
| Card to account by requisites | `receipt.create.requisite` -> `receipt.confirm.requisite` | 7 |
| Account to account by requisites | `account.balance`, `account.check` -> `receipt.pay.requisite` | 7 |
| Card binding (token for the flows above) | `cards.add` -> `cards.add.confirm` | - |
| Reconciliation and registry | `receipt.compare.payment` / `receipt.compare.check`, `receipt.registry` | - |

`account.attached.list` accepts operation type `1`, `5`, `6`, `7` and also `12` (online
payment from an account).

## Receipt state machine (`state`)

```
0 CREATED ──confirm/pay──> 4 SUCCESS
   │                ├────> 30 WAITING / 57 PENDING ──poll check.id──> 4 | 50 | 51
   │                ├────> 50 CANCELED (processing declined; reason in result.error)
   │                └────> 51 FAILED (e.g. insufficient funds)
   └─ other codes: 1 CHECK, 2 DEBIT, 3 CONFIRMATION, 5 HOLD, 6 WAITING_SMS_CONFIRMATION,
      20 STOPPED, 21 REVERSE, 22 INSUFFICIENT_FUNDS, 23 HOLD_CANCELED, 52 PARTIAL_CANCELED,
      53 CUSTOMER_NOT_VALID, 54 CURRENCY_RATE_CHANGED, 56 PROCESSING_NOT_AVAILABLE,
      58 VERIFICATION_FAILED, 59 LIMIT_PASSED
```

The documented confirm outcomes are `4` success, `50` canceled, `51` failed and `57` / `30`
in progress. The spec does not classify the other codes; treat only `4` as paid and keep
polling anything you do not recognise as final. Requisite transfers (`type 7`) can take up to
two business days.

## Units and formats

- Amounts: integer **tiyin** (1 UZS = 100). `currency` is ISO 4217 numeric (`860`).
- Times: Unix **milliseconds** (`create_date`, `pay_date`, filters). `pay_date = 0` until paid.
- Card expiry in `cards.add`: `MMYY` string. PAN: 16 digits.
- Bank accounts: 20 digits, or 25-27 digits for some receivers (`receipt.pay.requisite`);
  MFO is a string (keep leading zeros).
- `receipt.account.create.transfer`: `sender.id` is `"<your_login>:<sender_id>"`;
  `sender.document` (all five fields) is required above 50 BRV (base calculation units).

## Gotchas

- **Result wrapping is inconsistent.** Most methods wrap the result (`result.receipt`,
  `result.card`, `result.account`, `result.compare`, `result.registry`), but
  `receipt.account.*` and `receipt.create.requisite` / `receipt.confirm.requisite` return
  the receipt directly in `result`. See the table in [`methods.md`](methods.md).
- Two error channels: a JSON-RPC `error` means the call was rejected; a processing decline
  comes back as a normal `result` with `state` 50/51 and a free-text `error` string. Branch on
  `state`, use `error` only for diagnostics.
- On `57`, `30`, a timeout, a lost response or `-31615 operation.being.processing`: poll
  `receipt.check.id` (or `receipt.check.extId`). Never create a new receipt and never blindly
  re-confirm: that risks a double transfer.
- `ext_id` must be unique per receipt; a reuse returns `-31613 ext.id.exist`. Keep it so you
  can recover the receipt with `receipt.check.extId`.
- Per-method error tables on the vendor pages print codes without the minus sign (`31602`);
  the wire value is negative (`-31602`).
- OTP from `cards.add` lives 2 minutes. Resend by calling `cards.add` with `{id, sms.hash}`.
- `receipt.registry`: page size max 100; give `create_time` (then `states` is required) or
  `pay_time` (successful receipts only).

## Testing

Test credentials and the test account come from your Uzum manager. Receiver test PANs that
force each outcome (success, canceled, pending, not found, not active), the ACC2CARD
scenarios and vendor samples: [`../sandbox/README.md`](../sandbox/README.md#paymenthub-account-to-card).
Vendor page: https://developer.uzumbank.uz/paymenthub/testing/account-to-card/ . Do not send
real payment or personal data to the test host.

## Examples

[`examples/`](examples/): account-to-card create request/response, confirm (success,
pending, canceled), check by id, JSON-RPC error, online payment create/pay.
