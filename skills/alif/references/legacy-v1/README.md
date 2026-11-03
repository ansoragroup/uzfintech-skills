# Alif legacy API (original version, "v1" docs)

Hand-written notes. Use them to **maintain or migrate** an integration built on the original
API. Do not start new work here: build new integrations on the current methods (`pay`,
`invoice` with `payment`, `getSummary`, `matchCardPIN`).

- Sources (Russian pages): https://docs.alifpay.uz/v1/ with `checkout/`, `purchases/`,
  `cards/`, `scoring/`, `hold/`, `monitoring/`
- Fetched: 2026-11-03
- Status: the changelog says the original version is still supported but no longer extended.

Transport is the same as the current API. Every call is `POST https://api.alifpay.uz/v2/<method>`
with a JSON body and the `Token` header. Errors use HTTP 200 with `{"error": {"code", "message"}}`
and the same 1001-1110 codes, and webhooks carry the same `Signature` HMAC. See
[`../common/README.md`](../common/README.md). Only the method names and payload shapes below
differ.

## Migration map

| Legacy | Current | What changes |
|---|---|---|
| `purchase` | `pay` | `ref` -> `id`; add `amount` (total tiyin); the three method fields -> one `method{type, ...}`; `receipt` bool + top-level `items`/`phone` -> `receipt{type, phone, items}`; items optional |
| `confirmChargeOTP {ref, otp}` | `confirmPayment {id, otp}` | confirm by the payment `id`, not `charge.ref` |
| `getPurchase {ref}` | `getPayment {id}` | `tax_receipts` -> `receipt.results` |
| `refundPurchase {ref}` | `refundPayment {id}` | partial refunds exist only in the current API (`refundPaymentPartial`, instalments) |
| purchase webhook `{type: "purchase", payload: purchase}` | payment webhook | body is the payment struct (accept a `payload` wrapper too, see common) |
| `invoice` ... `charge{ref, ...}` | `invoice` ... `payment{id, ...}` | `charge` renamed; `payouts` added |
| invoice webhook `{type: "invoice", payload: invoice}` | invoice webhook | body is the bare invoice struct |
| `sendInvoice -> {id, sms_id, phone, price, link, content}` | `sendInvoice -> {id}` | do not depend on `link` / `content` from the response |
| `pinfl {token, pinfl}` | `matchCardPIN {token, pin}` | param renamed; result still `{ok}` |
| `scoring {ref, token, from_date, to_date}` | `getSummary {id, token, from, to}` | `YYYY-MM-DD` -> `YYYY-MM`; `to` must be before the current month |
| `history {ref, ...}` | `history {id, ...}` | request id renamed |
| `hold`, `dismissHold`, `getHold` | same | unchanged |
| `getCardToken`, `confirmCardToken`, `getCardType` | same | unchanged |

Only the current API has `payouts` / `skip_payouts` / `applyPayouts`, `registerReceipt`,
`addInvoiceReceiptURL`, `chargeInvoiceHold`, `MOBI_SHOW_QR` and branch `Store-Token` auth.

## `POST /purchase` (legacy)

Charges a payment method, registers fiscal receipts (when asked) and routes funds to sellers.
Aggregators set a per-item `merchant_id`.

| Param | Type | Rule |
|---|---|---|
| `ref*` | string | purchase id, unique per API client (client-generated) |
| `items*` | array | item list; one item for the full sum is enough when no receipt is needed |
| `phone` | string | buyer phone `998NNNNNNNNN`; used for the receipt |
| `receipt` | bool | `true` = register fiscal receipts |
| `card` | object | `{pan, exp (MMYY)}`; one-off payment, SMS OTP, then `confirmChargeOTP` |
| `bound_card` | object | `{token}`; confirmed card token, no OTP |
| `hold` | object | `{id}`; charge an existing hold |

Set **exactly one** of `card`, `bound_card`, `hold`. The request fails if more than one is set.

Item: `name*`, `amount*` (quantity, natural number), `price*` (unit price, tiyin), `spic`
(ИКПУ, required when `receipt: true`), `marking_code`, `discount` (line total, tiyin, at most
`price x amount`), `merchant_id` (seller the item is paid to). The same limit applies:
`sum(price x amount - discount)` must be 50,000..20,000,000,000 tiyin per charge.

### Purchase struct (response of `purchase` / `getPurchase`, webhook payload)

`ref`, `merchant_id`, `phone`, `receipt`, `items[]`, `charge`, `tax_receipts[]`
(`{merchant_id, url, refund}`; `getPurchase` only, once registered).

`charge` holds the payment: `ref` (the id that `confirmChargeOTP` takes), `amount` (tiyin),
`status`, `method{type, payload{pan (masked)}}`, and `user_action{phone (masked)}` while an OTP
is pending.

### Statuses (legacy list)

`PENDING`, `SUCCEEDED`, `INSUFFICIENT_FUNDS`, `INVALID_CARD`, `PENDING_REVERSAL`, `REVERTED`,
`OTP_REQUIRED`, `UNKNOWN_ERROR`, `BLOCKED_CARD`, `EXPIRED_CARD`, `SMS_NOTIFICATION_IS_OFF`,
`INCORRECT_OTP`, `EXPIRED_OTP`.

The current list adds `HELD`, `DECLINED`, `PIN_TRIES_EXCEEDED`, `QR_EXPIRED` and
`CREDIT_RESTRICTED_BY_CLIENT` (see [payments](../payments/README.md#statuses)). A migrated
integration must treat unknown statuses as not paid.

## Other legacy methods

| Method | Params | Result |
|---|---|---|
| `confirmChargeOTP` | `ref*` (= `charge.ref`), `otp*` | payment struct (`ref`, `amount`, `status`, `method`) |
| `getPurchase` | `ref*` | purchase struct with `tax_receipts` |
| `refundPurchase` | `ref*` | `{ref}`; refund receipt registered if a sale receipt existed |
| `pinfl` | `token*` (confirmed), `pinfl*` (14 digits) | `{ok: bool}`; Humo may say `false` when the scheme has no PINFL |
| `scoring` | `ref*`, `token*`, `from_date*`, `to_date*` (`YYYY-MM-DD`; at most one year; Uzcard `from_date` at least two months back) | `{"YYYY-MM": [{type, amount, count}], ...}`; months with no transactions are omitted |
| `history` | `ref*`, `token*`, `from_date*`, `to_date*` | `{txns: [...]}`, same transaction shape as [monitoring](../monitoring/README.md) |

Legacy checkout (`invoice`, `getInvoice`, `refundInvoice`, `sendInvoice`) takes the request
fields of the current [checkout](../checkout/README.md) with these exceptions:

- It has no `payouts`, `hold.enabled` or item `vat_percent`.
- It has no `addInvoiceReceiptURL` or `chargeInvoiceHold`.
- The invoice carries `charge` instead of `payment`. Only card payments (`payload.pan`) are
  documented; there are no `MOBI` / instalment payload fields.
- The webhook wraps the invoice as `{type: "invoice", payload: invoice}`, and the payload also
  has a `purchase_id`.

## Migration checklist

- [ ] No calls remain to `purchase`, `confirmChargeOTP`, `getPurchase`, `refundPurchase`, `pinfl`
  or `scoring`.
- [ ] Request ids are sent as `id`, not `ref`, including `history` and `getSummary`.
- [ ] Invoice code reads `payment` (not `charge`). Webhook parsing accepts the bare struct and a
  `payload` wrapper.
- [ ] `/pay` sends `amount` equal to `sum(price x amount - discount)` and puts items under
  `receipt.items`.
- [ ] Stored legacy `charge.ref` values are mapped before `getPayment` lookups. Confirm with Alif
  that legacy purchases can be read by the current methods; the docs do not say.
- [ ] Status handling covers the extra current statuses (`HELD`, `DECLINED`, ...).
