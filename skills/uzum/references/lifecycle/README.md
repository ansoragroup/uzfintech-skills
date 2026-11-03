# Uzum: money lifecycle, deadlines and reversals

Read this when you build or review any Uzum flow that moves money. It lists the deadlines,
reversal paths, retry rules and fiscal duties to raise before the user runs into them.

- Source: [merchant](../merchant/README.md), [checkout](../checkout/README.md),
  [fiscalization](../fiscalization/README.md), [fastpay](../fastpay/README.md),
  [dynamicqr](../dynamicqr/README.md), [crossborder](../crossborder/README.md),
  [remitcore](../remitcore/README.md), [ratekeeper](../ratekeeper/README.md),
  [nasiya](../nasiya/README.md), [paymenthub](../paymenthub/README.md); vendor specs
  https://developer.uzumbank.uz/redocusaurus/ (`en_<product>.yaml`, `ru_<product>.yaml`) and
  https://developer.uzumbank.uz/paymenthub/
- Fetched: 2026-11-03

## Warn without being asked

1. **`uzum.merchant-lost-confirm`** When you implement the Merchant API `/confirm` or `/status`:
   if `/confirm` answers 5xx or times out, Uzum polls `/status` (up to 10 times). `/status` must
   report `CONFIRMED` for a confirm that committed, even if its HTTP answer was lost. Treat
   `CREATED` older than 30 minutes as failed. [merchant](../merchant/README.md#flow-and-state-machine)
2. **`uzum.paymenthub-never-recreate`** When a PaymentHub receipt times out or returns `30`, `57`
   or `-31615`: poll `receipt.check.id` / `receipt.check.extId`. Never create a new receipt or
   re-confirm, because that can send the transfer twice. Only `state 4` means paid.
   [paymenthub](../paymenthub/README.md#gotchas)
3. **`uzum.fastpay-no-recharge`** When a FastPay `payment` times out or returns
   `operation.is.inProcess`: poll `status` and never re-charge with a new `order_id`.
   `DUPLICATED` points to the earlier sale. [fastpay](../fastpay/README.md#gotchas)
4. **`uzum.checkout-operation-id`** When code retries a Checkout `refund`, `complete`, `reverse`,
   `merchantPay` or `purchaseReceipt`: each operation needs its own `X-Operation-Id` UUID.
   `3028` means the operation already exists, so read it with `getOperationState`. Do not
   resend it under a fresh id, or you may refund twice. [checkout](../checkout/README.md#gotchas)
5. **`uzum.crossborder-no-refund`** When a CrossBorder transfer to Uzbekistan or a service payment
   succeeds: credited funds cannot be returned, and there is no cancel. `cancel_debit` only
   undoes a FROM_UZ `SUCCESS` debit whose onward credit failed (`10227`, `10229`).
   [crossborder](../crossborder/README.md#gotchas)
6. **`uzum.fiscal-receipt-24h`** When receipts go out from a queue, a batch job or a retry loop:
   `date_time` must fall within 24 hours after the confirmed payment and must not be in the
   future. A late receipt gets 422 "date_time should be within 24 hours". Send at payment time.
   [fiscalization](../fiscalization/README.md#gotchas)
7. **`uzum.fiscal-refund-needs-sale`** When you write a refund receipt: `/v2/refund_receipt`
   needs the sale's `payment_id` and a sale receipt that was already fiscalized. Each refund
   needs a new `operation_id`. `card_type` must be `1` or `2`. 400 `{message}` means refund
   expired; that period is not published. [fiscalization](../fiscalization/README.md#v2refund_receipt)
8. **`uzum.checkout-fiscal-owner`** When you use Checkout: auto-fiscalization is off by default
   (your Uzum manager turns it on, for one-step payments). While it is off, you send the sale
   and refund receipts yourself. While it is on, a refund needs `cart` (`3045`).
   [checkout](../checkout/README.md#gotchas)
9. **`uzum.merchant-no-refund-api`** When the user wants to refund a Merchant API payment from
   their side: there is no outbound refund call. Uzum calls your `/reverse` (no amount, so the
   whole transaction), and you answer `REVERSED`, `10017` or `10018`.
   [merchant](../merchant/README.md#error-codes-errorcode-string)
10. **`uzum.checkout-refund-cap`** When you add partial Checkout refunds: before each one, read
    `getOrderStatus`; a new refund must not exceed `completedAmount` minus `refundedAmount`.
    `3021` means a bad amount. `3022` means the refund timed out (no duration is published).
    [checkout](../checkout/README.md#status-model)
11. **`uzum.checkout-stale-authorized`** When you use TWO_STEP: every `AUTHORIZED` order needs
    `complete` (the amount may be lower) or `reverse`. Run a job for stale ones. ONE_STEP
    cannot be reversed (`3036`), so refund it. The hold expiry is not published (`3020`).
    [checkout](../checkout/README.md#status-model)
12. **`uzum.checkout-callback-unsigned`** When you write a Checkout callback handler: callbacks
    are unsigned, and Uzum resends them at most 5 times until it gets HTTP 200. Confirm with
    `getOrderStatus` and make fulfilment idempotent. [checkout](../checkout/README.md#operations)
13. **`uzum.remitcore-2000-async`** When Remit Core returns `2000` or `2002`: it is in progress,
    not failed. Wait for the callback or `get_status`, and never re-register. `/v1/cancel` is
    DEBIT only (`8003`) and only from `SUCCESS`. [remitcore](../remitcore/README.md#gotchas)
14. **`uzum.dynamicqr-cancel-abandoned`** When a Dynamic QR order is abandoned or times out on
    your side: call `cancel-order`, so a late scan cannot pay. `reversal` may return
    `REVERSE_PENDING`; poll until `REVERSED`. [dynamicqr](../dynamicqr/README.md#gotchas)
15. **`uzum.nasiya-cancel-full-only`** When the user asks to return part of a Nasiya purchase:
    `contracts/cancel` cancels the whole contract and needs the right status (`4009`). No
    partial or post-activation return is documented. [nasiya](../nasiya/README.md#enums)

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Merchant API `/create` to `/confirm` | 30 minutes | treat as failed; Uzum will not confirm it later | [merchant](../merchant/README.md#flow-and-state-machine) |
| Merchant API outcome after a lost `/confirm` | up to 10 `/status` polls | Uzum takes your `/status` answer as the truth | [merchant](../merchant/README.md#flow-and-state-machine) |
| Checkout payment session | `sessionTimeoutSecs` 600-1800 | `3041` session timed out; `3029` payment data expired | [checkout](../checkout/README.md#register) |
| Checkout TWO_STEP void | not published | `3020` timeout for cancellation | [checkout](../checkout/README.md#error-codes-errorcode) |
| Checkout refund | not published | `3022` timeout for refund | [checkout](../checkout/README.md#error-codes-errorcode) |
| Fiscalization sale `date_time` | within 24 h after the confirmed payment, not in the future (Tashkent time if no zone) | 422 `date_time should be within 24 hours` | [fiscalization](../fiscalization/README.md#v2receipt-request), https://developer.uzumbank.uz/redocusaurus/ru_fiscalization.yaml |
| Fiscalization refund receipt | `date_time` has the same 24 h rule; the refund expiry period is not published | 400 `{message}` refund unavailable due to expiration | https://developer.uzumbank.uz/redocusaurus/en_fiscalization.yaml |
| FastPay / Dynamic QR request signature | timestamp at most 50 s old | `error_code` 403 | [fastpay](../fastpay/README.md#errors) |
| FastPay payer QR (`otp_data`) | not published | `apelsin.pay.user.otp.data.expired` | [fastpay](../fastpay/README.md#errors) |
| CrossBorder confirm after check | 20 minutes | `10221` (transfers), `20204` (payments) | [crossborder](../crossborder/README.md#gotchas) |
| CrossBorder `PENDING` (manual review) | no deadline published; poll hourly | no callback arrives | [crossborder](../crossborder/README.md#transfer-state-machine) |
| CrossBorder debit OTP | not published | `10310` expired, `10312` no attempts left | [crossborder](../crossborder/README.md#error-codes-errorcode) |
| CrossBorder limits (UZ cards) | single 19,999,999 UZS; 9,999 USD per 30 days; 5 per day; 150 per month | `10209`, `10210`, `10230`, `10231` | [crossborder](../crossborder/README.md#limits-uz-issued-debit-cards) |
| Remit Core DEBIT confirm | not published | `3036` confirm window expired; `3040` OTP expired | [remitcore](../remitcore/README.md#codes) |
| Remit Core limits (UZ cards) | single 18,749,999 UZS; 9,999 USD per 30 days; 5 per day; 150 per month | `3003`, `3004`, `3012`, `3013`, `3014` | [remitcore](../remitcore/README.md#limits-uz-cards-and-bins) |
| PaymentHub `cards.add` OTP | 2 minutes | `-31617` expired, `-31618` wrong, `-31622` attempts exceeded | [paymenthub](../paymenthub/errors.md#domain-errors) |
| PaymentHub requisite transfer (`type 7`) | up to two business days in progress | keep polling; do not resend | [paymenthub](../paymenthub/README.md#receipt-state-machine-state) |
| Nasiya SMS code (4 digits) | not published | re-send with `send-code-sms` | [nasiya](../nasiya/README.md#flow) |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Merchant API, before `/confirm` | Uzum | your `/reverse` on `CREATED` -> `REVERSED` | no (no amount field) | once; `10018` on repeat | none (nothing sold) | [merchant](../merchant/README.md#flow-and-state-machine) |
| Merchant API, after `CONFIRMED` | Uzum | your `/reverse` -> `REVERSED`, or `10017` if you cannot cancel | no | once | you send `/v2/refund_receipt` if you fiscalized the sale | [merchant](../merchant/README.md#error-codes-errorcode-string) |
| Merchant API, merchant wants to refund | nobody (no API) | not documented | - | - | - | [merchant](../merchant/README.md#flow-and-state-machine) |
| Checkout TWO_STEP void | you | `/api/v1/acquiring/reverse` (`AUTHORIZED` only) | not documented (`reversedAmount` exists) | not documented | none if you fiscalize at capture | [checkout](../checkout/README.md#operations) |
| Checkout TWO_STEP capture of less | you | `/api/v1/acquiring/complete` with a lower `amount` | yes | once | sale receipt for the captured amount | [checkout](../checkout/README.md#gotchas) |
| Checkout refund after `COMPLETED` | you | `/api/v1/acquiring/refund` | yes, total <= `completedAmount` | several; limit not published | auto-fiscalization on: Uzum (`REFUND` receipt callback; `cart` required). Off: you | [checkout](../checkout/README.md#operations) |
| FastPay reversal | you | `PUT /api/apelsin-pay/merchant/v2/payment/reversal/{orderId}` | no, full only | once (-> `REVERSED`) | you (the merchant fiscalizes FastPay sales) | [fastpay](../fastpay/README.md#fiscal--status--reversal) |
| Dynamic QR, unpaid order | you | `cancel-order` -> `CANCELLED` | - | once | none | [dynamicqr](../dynamicqr/README.md#state-machine-payment_status) |
| Dynamic QR, paid order | you | `reversal` -> `REVERSE_PENDING` -> `REVERSED` | not documented (`PARTIAL_CANCELLED` exists) | not documented | you | [dynamicqr](../dynamicqr/README.md#state-machine-payment_status) |
| CrossBorder FROM_UZ debit, onward credit failed | you | `/cbt/v1/transfer/cancel_debit` (`SUCCESS` only) | no (only `externalTransferId`, `reason`) | once (-> `REVERSED`) | not documented | [crossborder](../crossborder/README.md#transfer-state-machine) |
| CrossBorder TO_UZ credit or service payment | - | none: cancellation is not supported | - | - | - | https://developer.uzumbank.uz/redocusaurus/en_crossborder.yaml |
| Remit Core DEBIT cancel | you | `/v1/cancel {transferId}`; `8003` for CREDIT; `3055` retry | no | until `CANCELLED` / `CANCELLING_FAILED` | not documented | [remitcore](../remitcore/README.md#operations-all-post) |
| Nasiya contract | you | `/api/v1/contracts/cancel` | no, full cancellation | once; `4009` wrong status | not documented | [nasiya](../nasiya/README.md#operations-all-post) |
| PaymentHub receipt | - | no public method (states `21`, `23`, `52` exist without a flow) | - | - | - | [paymenthub](../paymenthub/README.md#receipt-state-machine-state) |
| Ratekeeper | - | quotes only; no money moves | - | - | - | [ratekeeper](../ratekeeper/README.md) |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| Merchant API `/create`, `/confirm`, `/reverse` (Uzum calls you) | after a 5xx or timeout on `/confirm`: up to 10 `/status` calls | not published | `transId` | repeat `/create` -> `10010`; repeat `/confirm` -> `10016`; repeat `/reverse` -> `10018` (vendor) | [merchant](../merchant/README.md#idempotency-rules-derived), https://developer.uzumbank.uz/redocusaurus/en_merchant.yaml |
| Checkout acquiring / event / receipt callbacks | at most 5 until HTTP 200 | not published | `orderId` + `operationType` (derived) | unsigned: re-read `getOrderStatus`, then act once | [checkout](../checkout/README.md#operations) |
| Checkout money calls (you call Uzum) | you retry | - | `X-Operation-Id`, unique per operation | `3028` operation already exists: read `getOperationState` | [checkout](../checkout/README.md#error-codes-errorcode) |
| Fiscalization `/v2/receipt`, `/v2/refund_receipt` | Uzum retries the OFD itself on 202 (`code` 1, 2) | - | `operation_id` (same `payment_id` on retry) | 500: retry with the same `operation_id`; 400 `code` 2: same `payment_id` + `receipt_type` already sent | [fiscalization](../fiscalization/README.md#responses) |
| FastPay `payment` | none (no callbacks) | timestamp within 50 s | `order_id`, `transaction_id` | `DUPLICATED`, `order.id.duplicated`, `transaction.duplicated`, `qr.duplicated` | [fastpay](../fastpay/README.md#errors) |
| Dynamic QR `create`, `reversal` | none (no callbacks) | timestamp within 50 s | `order_id` | `order.id.duplicated`; poll `status-by-order` | [dynamicqr](../dynamicqr/README.md#errors) |
| CrossBorder check / confirm | none; `PENDING` has no callback | - | `externalTransferId`, `externalPaymentId` | `10211` / `20201` on reuse; read `status` | [crossborder](../crossborder/README.md#error-codes-errorcode) |
| Remit Core callback `TransferResultInfo` | after `2000`; retry count not published | any 2xx counts as delivered | `externalTransferId` | `3001` duplicate id; `2002` repeated request: poll `get_status` | [remitcore](../remitcore/README.md#callback) |
| Nasiya calls | none (no webhooks) | - | not documented | retry only on `1000` or HTTP 5xx; `4010` on a repeated `confirm` | [nasiya](../nasiya/README.md#enums) |
| PaymentHub receipts | none (no callbacks) | - | `ext_id` | `-31613 ext.id.exist`: look up with `receipt.check.extId` | [paymenthub](../paymenthub/README.md#gotchas) |

## Fiscal receipts

- **Merchant API, FastPay, Dynamic QR, own acquiring:** you fiscalize. Send sale receipts
  through [Fiscalization](../fiscalization/README.md) or your own cash register. FastPay and
  Dynamic QR then attach the receipt link with `fiscal` (`fiscal_url`). After a reverse or
  reversal, send `/v2/refund_receipt` yourself (derived: nothing else issues it).
- **Checkout:** auto-fiscalization is off by default; your manager enables it, for one-step
  payments. When it is on, Uzum issues `PURCHASE` / `PREPAID` / `REFUND` receipts and posts a
  receipt callback with `receiptUrl` (also `getReceipts`). Send `merchantParams.cart` (`3059`
  if `cart.total` mismatches) and a refund `cart` (`3045`). After `PREPAID`, issue the final
  sale with `purchaseReceipt`. When it is off, use Fiscalization, with `payment_id` set to
  the Checkout order id. For `cardType` 3, send `ofdPan` as `card_number`.
- **Fiscalization rules:** amounts are in tiyin. `cash_amount + card_amount` equals the total
  **before** discounts. A new `operation_id` per receipt; reuse it only to retry. One
  `receipt_type` 0 per `payment_id` (400 `code` 2). For cash sales `payment_id` is
  auto-assigned and returned in the 200; store it, because the refund needs it. `labels`
  are mandatory for marked goods. A 202 is not an error: poll
  `GET /v2/receipt/{operation_id}/receipt_url`.
- **Refund receipt:** sale `payment_id`, `card_type` `1` or `2`, a new `operation_id` per
  refund (several refunds per purchase are allowed), and the sale must already be
  fiscalized. The vendor does not say that refunds may not exceed the sale total.
- **`/v2/qr_payment`:** registers a QR receipt printed by your own cash register. It needs
  prior approval from Uzum.
- **CrossBorder, Remit Core, Nasiya:** who fiscalizes is not documented.
- **PaymentHub:** online card receipts (`type 1`) return `ofd{url, terminal_id,
  fiscal_sign}`. Who registers them is not stated. Ratekeeper moves no money.

## Not documented — ask the provider

- Merchant API: how a merchant requests a refund after `CONFIRMED`, and until when Uzum may
  still call `/reverse`.
- Checkout: the `3020` / `3022` timeouts, TWO_STEP authorization expiry, the maximum number
  of partial refunds, whether `reverse` can be partial, and the answer deadline for callbacks.
- Fiscalization: the refund expiry period behind "Refund is unavailable due to expiration".
  Whether the refund `date_time` 24 h counts from the refund or from the sale. Whether
  refunds are capped at the sale total. How to subscribe to result callbacks.
- FastPay and Dynamic QR: QR lifetime, reversal window, partial reversal.
- CrossBorder and Remit Core: OTP lifetime and resend limits; the Remit Core `3036` window,
  the cancel window and the callback retry count; who fiscalizes.
- Nasiya: SMS code validity, the unit of `price` (UZS or tiyin), partial or post-activation
  returns, fiscal ownership.
- PaymentHub: reversal / refund method and the flow behind states `21`, `23`, `52` and
  `init_amount`.
