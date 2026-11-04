# Atmos Payments (Uzcard / Humo: SMS code or card token, multi-payments, refunds, widget, payment page)

Hand-written notes. Transport, auth, error codes, the Callback API and `ofd_items`:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/) (shared
`store_transaction` object: [`../common/schemas/store-transaction.json`](../common/schemas/store-transaction.json)).
Examples: [`examples/`](examples/).

- Source: https://docs.atmos.uz/en/#payments, https://docs.atmos.uz/en/#transaction-creating,
  https://docs.atmos.uz/en/#transaction-pre-confirmation,
  https://docs.atmos.uz/en/#transaction-verification,
  https://docs.atmos.uz/en/#multitransaction-creating,
  https://docs.atmos.uz/en/#repeated-confirmation-code-request,
  https://docs.atmos.uz/en/#transaction-cancellation,
  https://docs.atmos.uz/en/#retrieving-transaction-information,
  https://docs.atmos.uz/en/#creating-a-partial-reversal,
  https://docs.atmos.uz/en/#html-widget, https://docs.atmos.uz/en/#payment-page
- Fetched: 2026-11-04
- Needs: a Bearer token ([auth](../common/README.md#auth)), your `store_id`, a billing URL
  agreed with Atmos ([Callback API](../common/README.md#callback-api-your-billing-url)), and
  for token payments a card bound with [`../cards/`](../cards/README.md).

## Flow (one payment)

```
POST /merchant/pay/create {amount, account, store_id, terminal_id?, ofd_items?}
   └─> transaction_id                    (draft; nothing debited)
POST /merchant/pay/pre-apply, one of:
   a) {card_number, expiry, store_id, transaction_id}  -> SMS code sent to the payer
   b) {card_token, store_id, transaction_id}           -> no SMS
POST /merchant/pay/apply {transaction_id, otp, store_id}
   a) otp = the SMS code;  b) otp = 111111 (fixed value for token payments)
   └─> Atmos calls your billing URL; you answer 200 {"status":1}
   └─> store_transaction.success_trans_id, ofd_url        (money moved)
answer lost (timeout, 5xx, network)?  POST /merchant/pay/get  -- never apply again
```

Refunds use `success_trans_id`, not the `transaction_id` of the draft:

```
full:    POST /merchant/pay/reverse {transaction_id: <success_trans_id>, reason?}
partial: POST /merchant/pay/create-reverse-partial {transaction_id, store_id, amount}
           └─> transaction_partial_reverse_id
         POST /merchant/pay/confirm-reverse-partial {transaction_id,
              transaction_partial_reverse_id, store_id, ofd_items}   -- money moves here
         POST /merchant/pay/get-reverse-partial  -> reverted and left amounts
```

## Methods

| Method | Endpoint | Params (`*` required) | Result |
|---|---|---|---|
| pay-create | `POST /merchant/pay/create` | `amount*`, `account*`, `store_id*`, `terminal_id`, `lang`, `ofd_items` | `transaction_id`, `store_transaction` (not confirmed) |
| pay-pre-apply | `POST /merchant/pay/pre-apply` | `store_id*`, `transaction_id*`, and either `card_token` or `card_number` + `expiry` | `transaction_id`, `result` |
| pay-apply | `POST /merchant/pay/apply` | `transaction_id*`, `otp*`, `store_id*` | `store_transaction` with `success_trans_id`, `ofd_url`, `ofd_url_commission` |
| pay-otp-resend | `POST /merchant/pay/otp-resend` | `transaction_id*`, `store_id*` | `transaction_id` |
| pay-get | `POST /merchant/pay/get` | `transaction_id*`, `store_id*` | `store_transaction` |
| pay-reverse | `POST /merchant/pay/reverse` | `transaction_id*` (= `success_trans_id`), `reason`, `hold_amount` | `transaction_id` |
| create-reverse-partial | `POST /merchant/pay/create-reverse-partial` | `transaction_id*`, `store_id*`, `amount*`, `reason`, `request_id`, `lang` | `transaction_partial_reverse_id` |
| confirm-reverse-partial | `POST /merchant/pay/confirm-reverse-partial` | `transaction_id*`, `transaction_partial_reverse_id*`, `store_id*`, `ofd_items*`, `request_id`, `lang` | `transaction_reverted_amount`, `transaction_left_amount` |
| get-reverse-partial | `POST /merchant/pay/get-reverse-partial` | `transaction_id*`, `transaction_partial_reverse_id*`, `store_id*`, `lang` | as confirm |
| bulk-pay-create | `POST /merchant/bulk/pay/create` | `store_id*`, `params*[] {account*, amount*, terminal_id, details}` (the table and the sample disagree; this follows the sample) | `transaction_id`, `store_transactions[]` |
| bulk-pay-pre-apply | `POST /merchant/bulk/pay/pre-apply` | as pay-pre-apply | `result` only |
| bulk-pay-apply | `POST /merchant/bulk/pay/apply` | `transaction_id*`, `otp*`, `store_id*` | `store_transaction[]` |

A multi-payment (`bulk`) debits the card once and splits it across several accounts or
terminals of your store. `terminal_id` may be left out only when the merchant has a single
registered terminal.

## Hosted options (no card data on your side)

- **Payment page.** Call `pay/create`, then send the payer to
  `https://checkout.pays.uz/invoice/get?storeId=<store_id>&transactionId=<transaction_id>&redirectLink=<url>`
  (test: `http://test-checkout.pays.uz/invoice/get`). `redirectLink` is optional. Your
  billing URL still gets the callback; confirm the result with `pay/get` before you
  fulfil (derived).
- **HTML widget.** Load `https://cdn.pays.uz/checkout/js/v1.0.1/checkout.js` (test:
  `http://cdn.pays.uz/checkout/js/v1.0.1/test-checkout.js`) and pass `parent_id*`,
  `store_id*`, `account*`, `success_redirect*`, `fail_redirect*`, `amount*` (tiyin),
  `key*`, plus optional `terminal_id`, `version`, `details`, `lang` (`en`, `ru`, `uz`),
  `theme`. The docs call `key` an "authorization key" without saying which one; it ends up
  in the browser, so never put the consumer secret or the callback `api_key` there, and ask
  Atmos which key the widget expects.

## Errors

| Case | Answer |
|---|---|
| bad or missing fields | `STPIMS-ERR-006`, `-007`, `-009`: fix the request |
| card not found, wrong expiry | `STPIMS-ERR-004`, `-030`, `-043`, `-090` |
| wrong SMS code on apply | `STPIMS-ERR-098`: let the payer retry or resend with `pay/otp-resend` |
| your billing answer was not a success | `STPIMS-ERR-093` (derived); no money is taken |
| outcome unknown / in progress | `STPIMS-ERR-118`, `STPIMS-ERR-065`, `INFO-202`: poll `pay/get` |
| `pay/get` on a paid transaction | the vendor sample answers `STPIMS-ERR-092` (closed) **with** a confirmed `store_transaction` |
| refund refused | `STPIMS-ERR-101`: read the transaction, retry later |

Full table: [`../common/README.md`](../common/README.md#error-codes-resultcode).

## Gotchas

- `pay/create` and `pay/pre-apply` move no money. Only `pay/apply` does, and only after your
  billing URL answers `200 {"status": 1}`.
- `pay/reverse` takes the **`success_trans_id`** from the `apply` (or `get`) answer in its
  `transaction_id` field. The draft's `transaction_id` is a different number.
- Lost `apply` answer: call `pay/get`. Paid means `store_transaction.confirmed == true` and a
  non-null `success_trans_id`; do not decide on `result.code` alone (it can be
  `STPIMS-ERR-092` for a paid transaction).
- Never send `card_token` together with `card_number` + `expiry` in `pre-apply`.
- For token payments `otp` is the fixed `111111`; that value is not a test code there.
  `pay/otp-resend` works only for the SMS flow.
- The SMS flow sends a full PAN and expiry from your server: PCI DSS scope. Use a bound
  token, the payment page or the widget if you do not hold PCI DSS.
- `expiry` is written `YYmm` in the table (for example `2812` for 12/2028); test cards are
  printed `MM/YY`. Convert.
- `account` is described as a numeric order identifier used in reconciliation; the widget
  table calls it an arbitrary string. Keep it numeric and unique per order (derived).
- `ofd_url_comission` (table) vs `ofd_url_commission` (sample): read both.
- The resend path is `/merchant/pay/otp-resend` in the HTTP line and `/merchant/pay/retry-otp`
  in the sample. Use the HTTP line, test it, and ask Atmos if it fails.
- A partial reversal needs **two** calls; nothing is refunded until
  `confirm-reverse-partial` with `ofd_items` for the refunded part. The docs do not say
  whether `transaction_id` there is the draft id or `success_trans_id`; ask Atmos.
- Partial-reversal samples send `lang: "RU"` in upper case; other calls use `ru`.
- The test widget and test payment page are on `http://`, not `https://`.

## Examples

[`examples/`](examples/): pay-create, pay-pre-apply (token), pay-apply, pay-otp-resend,
pay-get (paid, `STPIMS-ERR-092`), pay-reverse, create / confirm / get-reverse-partial,
bulk-pay-create, bulk-pay-pre-apply, bulk-pay-apply (request and response each).
