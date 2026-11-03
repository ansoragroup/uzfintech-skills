# Alif: money lifecycle, deadlines and reversals

Read this when you build or review an Alif (alifpay) charge, hold, invoice or refund. It lists
the deadlines, refund limits, retry rules and fiscal duties to raise before the user hits them.

- Source: [common](../common/README.md), [checkout](../checkout/README.md),
  [payments](../payments/README.md), [hold](../hold/README.md), [cards](../cards/README.md),
  [legacy-v1](../legacy-v1/README.md); vendor docs https://docs.alifpay.uz/,
  https://docs.alifpay.uz/checkout/, https://docs.alifpay.uz/payments/,
  https://docs.alifpay.uz/hold/, https://docs.alifpay.uz/cards/,
  https://docs.alifpay.uz/changelog/
- Fetched: 2026-11-03

## Warn without being asked

1. **`alif.webhook-1h-auto-refund`** When you write a webhook handler, or plan downtime or a
   deploy: Alif retries delivery for about an hour until it gets HTTP 200. If no 200 ever
   arrives, the payment is **cancelled and the money returned**. Verify `Signature`, answer
   200 at once, process later. [common](../common/README.md#webhooks)
2. **`alif.persist-id-first`** When code calls `pay`, `hold` or `refundPaymentPartial`: you
   generate the `id`, so store it before the call. After a timeout or `1003`, read back
   (`getPayment`, `getHold`, `getRefund`) before any retry. Retry `1108` only with a **new**
   `id`. [common](../common/README.md#identifiers)
3. **`alif.error-is-http-200`** When code checks only the HTTP status: errors also come back as
   HTTP 200 with `{error:{code, message}}`. Only `SUCCEEDED` means paid, and `UNKNOWN_ERROR`
   needs a read back. [common](../common/README.md#response-and-error-envelope)
4. **`alif.hold-expiry-10-30-days`** When you hold funds (`hold`): capture before the scheme
   releases the hold, after 10 days on Humo or 30 days on Uzcard. `dismissed: true` does not
   say whether the hold was charged, released or expired, so track that yourself.
   [hold](../hold/README.md#flow)
5. **`alif.refund-full-only`** When the user wants a partial refund: `refundPayment` and
   `refundInvoice` refund the whole amount. Partial refunds exist only for instalment payments
   (`refundPaymentPartial`, `amount` > 50,000 tiyin). They go through review and return money
   to the instalment limit. [payments](../payments/README.md#partial-refunds-instalment-only)
6. **`alif.refund-receipt-needs-sale-receipt`** When you rely on Alif for the refund receipt:
   `refundPayment` / `refundInvoice` register one only if a sale receipt exists. A payment sent
   without `receipt` (or an invoice without `receipt: true`) gets no refund receipt either.
   [payments](../payments/README.md#methods)
7. **`alif.skip-payouts-refund-lock`** When you use `skip_payouts: true`: until `applyPayouts`,
   only a full `refundPayment` is possible. `applyPayouts` returns `1005` after a refund or on
   a non-`SUCCEEDED` payment. [payments](../payments/README.md#payment-struct)
8. **`alif.amount-equals-items`** When you send `receipt.items` or invoice `items`: the total
   must equal `sum(price x amount - discount)` in tiyin, within 50,000..20,000,000,000.
   `price` is per unit and `discount` covers the whole line; otherwise `1005`.
   [checkout](../checkout/README.md#post-invoice-parameters)
9. **`alif.otp-restart`** When you build the OTP step (`confirmPayment`, `confirmCardToken`): on
   `1100` (wrong code), ask again. On `1101` (expired) or `1106` (attempts used up), start a
   new `pay` with a new `id`. The OTP lifetime is not published.
   [cards](../cards/README.md#errors-you-will-see-here)
10. **`alif.invoice-timeout`** When you create invoices for stock or a time-limited price: set
    `timeout` (seconds until the invoice can no longer be paid) yourself. The default is not
    documented. [checkout](../checkout/README.md#post-invoice-parameters)
11. **`alif.invoice-hold-beta`** When you use invoice `hold.enabled`: it works for instalments
    only (beta) and is captured with `chargeInvoiceHold {id, items}`. Its expiry is not
    documented, so capture promptly. [checkout](../checkout/README.md#methods)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Webhook delivery (invoice, payment, partial refund) | retried for about an hour until HTTP 200 | payment cancelled, money returned to the customer | [common](../common/README.md#webhooks), https://docs.alifpay.uz/ |
| Card hold (`hold`) | auto-release after 10 days (Humo) or 30 days (Uzcard) | funds released; `dismissed: true` | [hold](../hold/README.md#flow), https://docs.alifpay.uz/hold/ |
| Invoice payment | `timeout` seconds you set; default not documented | invoice can no longer be paid | [checkout](../checkout/README.md#post-invoice-parameters) |
| Invoice hold (`hold.enabled`, beta) | not documented | not documented | [checkout](../checkout/README.md#methods) |
| Payment / card OTP | not documented | `1101` / `EXPIRED_OTP`; `1106` attempts exhausted | [common](../common/README.md#response-and-error-envelope) |
| alif mobi QR (`MOBI_SHOW_QR`) | not documented | final status `QR_EXPIRED` | [payments](../payments/README.md#method-request-by-type) |
| Invoice SMS (`sendInvoice`) | send limit per phone, number not published | `1109` | [checkout](../checkout/README.md#flow) |
| Charge or invoice amount | 50,000..20,000,000,000 tiyin (500..200,000,000 UZS) | `1005` | [checkout](../checkout/README.md#post-invoice-parameters) |
| Partial refund amount | `amount` > 50,000 tiyin, instalment payments only | rejected (code not stated) | [payments](../payments/README.md#methods) |
| Partial refund review | not documented | stays `PENDING`; `FAILED` gives no reason | [payments](../payments/README.md#partial-refunds-instalment-only) |
| Full refund (`refundPayment`, `refundInvoice`) | window not documented | not documented | https://docs.alifpay.uz/payments/ |
| Sandbox single charge or hold | 5,000,000,000 tiyin | insufficient-funds behaviour | [common](../common/README.md#sandbox) |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Paid payment (card, token, hold, QR) | you | `refundPayment {id}` -> `PENDING_REVERSAL` -> `REVERTED` | no | once | refund receipt registered if a sale receipt exists | [payments](../payments/README.md#methods) |
| Paid invoice | you | `refundInvoice {id}` -> `payment.status` `REVERTED` | no | once | same; links in top-level `receipts[{url, refund}]` | [checkout](../checkout/README.md#methods) |
| Instalment payment, part of it | you | `refundPaymentPartial {id, payment_id, amount, webhook_url}` | yes (> 50,000 tiyin) | not documented | not documented | [payments](../payments/README.md#partial-refunds-instalment-only) |
| `skip_payouts` payment before `applyPayouts` | you | `refundPayment {id}` only | no | once | as for `refundPayment` | [payments](../payments/README.md#payment-struct) |
| Webhook never answered with 200 | Alif | automatic cancel after about an hour of retries | no | once | not documented | [common](../common/README.md#webhooks) |
| Release a card hold | you, or the scheme on expiry | `dismissHold {id}` | no | once | none (nothing charged) | [hold](../hold/README.md#methods) |
| Capture a card hold | you | `pay {id: <new id>, method: {type: HOLD, id: <hold id>}}` | capture below the hold amount not documented | not documented | the `receipt` you send with `pay` | [hold](../hold/README.md#flow) |
| Capture an invoice hold (beta) | you | `chargeInvoiceHold {id, items}` | not documented | not documented | not documented | [checkout](../checkout/README.md#methods) |
| Legacy API refund | you | `refundPurchase {ref}` (now `refundPayment`) | no | once | refund receipt if a sale receipt existed | [legacy-v1](../legacy-v1/README.md#other-legacy-methods) |
| Cards, Monitoring, Summary, Sandbox | - | no money moves (tokens, history, scoring, test hosts) | - | - | - | [cards](../cards/README.md) |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Invoice webhook (`webhook_url`) | about an hour, until HTTP 200 | before the retries end; per-request timeout not published | invoice `id` | verify `Signature`, then `getInvoice`; fulfil once | [checkout](../checkout/README.md#gotchas) |
| Payment webhook (`pay`) | same | same | payment `id` | `body.get("payload", body)`, then `getPayment`; fulfil once | [payments](../payments/README.md#webhook) |
| Partial refund webhook | same | same | refund `id` | confirm with `getRefund` | [common](../common/README.md#webhooks) |
| `pay`, `hold`, `refundPaymentPartial` (you call) | you retry | - | your client `id` (UUID) | `1105` duplicate; read back first; `1108` needs a new `id` | [common](../common/README.md#identifiers) |
| `confirmPayment` | you retry | - | payment `id` | `1100` ask again; read `getPayment` after a timeout | [payments](../payments/README.md#statuses) |
| `refundPayment`, `refundInvoice` | you retry | - | payment or invoice `id` | repeat result not documented; check `REVERTED` first | [payments](../payments/README.md#statuses) |
| `applyPayouts` | you retry | - | payment `id` | idempotent per vendor | [payments](../payments/README.md#methods) |
| `invoice` | you retry | - | none: Alif issues the `id` | a blind retry creates a second invoice (derived) | [common](../common/README.md#identifiers) |

## Fiscal receipts

- **Alif registers the receipt when you ask it to.** For an invoice, send `receipt: true`
  with `spic` on every item (and `phone` for the receipt). For `pay`, send `receipt{type,
  phone, items[]}`, where `type` is `0` purchase, `1` advance or `2` credit. Items need
  `name`, `amount` (quantity), `price` (unit, tiyin) and `spic`. Add `marking_code` for some
  IKPU codes, and `tin` or `pin` for an agent's principal. The links appear in
  `payment.receipt.results[{merchant_id, url, refund}]`.
- **Sum rule:** the payment `amount` excludes discounts and equals
  `sum(price x amount - discount)`. `discount` is the line total, and VAT is computed after
  the discount. A mismatch gives `1005`.
- **Own cash register:** register the sale with the Soliq PaymentId from `receipt.payment_id`,
  then link it. For payments use `registerReceipt {id, fiscal_data{qr_code_url, is_refund,
  phone_number}, ...}`. For paid invoices use `addInvoiceReceiptURL {invoice_id, url}`, with
  an absolute `ofd.soliq.uz` URL.
- **Refund receipt:** a full `refundPayment` / `refundInvoice` registers it only when a sale
  receipt exists. Whether a sale linked through `registerReceipt` counts is not stated. With
  your own register, `registerReceipt` has `fiscal_data.is_refund` for a refund receipt. The
  receipt for `refundPaymentPartial` is not documented.
- **Timing:** no deadline for `registerReceipt` or `addInvoiceReceiptURL` is published.
- `registerReceipt` swaps the descriptions of `latitude` and `longitude`. Use the field
  names. [payments](../payments/README.md#gotchas)

## Not documented — ask the provider

- The OTP lifetime and SMS resend limit for `confirmPayment` and `confirmCardToken`; the
  alif mobi QR lifetime.
- The default invoice `timeout`, and the expiry of an invoice hold (`hold.enabled`).
- How long after payment `refundPayment` / `refundInvoice` still work.
- Whether a card hold can be captured for less than the held amount, or more than once.
- How many `refundPaymentPartial` requests one payment allows, how long review takes, and
  whether a refund receipt is registered.
- What a repeated `refundPayment` / `refundInvoice` returns.
- The URL the `/pay` webhook goes to (no `webhook_url` field exists on `pay`).
- Deadlines for `registerReceipt` and `addInvoiceReceiptURL`; whether a sale linked with
  `registerReceipt` gets an automatic refund receipt; how to link an own-register refund
  receipt to an invoice.
