# Uzum Checkout (hosted card payment gateway)

Hand-written notes. Generated field tables: [`endpoints.md`](endpoints.md); per-operation
JSON Schemas: [`schemas/ops/`](schemas/ops/).

- Source: https://developer.uzumbank.uz/redocusaurus/ru_checkout.yaml (en labels: `en_checkout.yaml`)
- Fetched: 2026-11-03
- Direction: **you call Uzum**; Uzum calls your callback URLs.

## Hosts and auth

| Env | Base URL |
|---|---|
| Test | `https://test-chk-api.uzumcheckout.uz` |
| Production | not published; issued at go-live |

Headers on every call:

| Header | Value |
|---|---|
| `X-Terminal-Id` | terminal UUID issued by Uzum |
| `X-API-Key` | API key issued by Uzum |
| `Content-Language` | `ru-RU`, `uz-UZ` or `en-EN` (payment form language; register only) |
| `X-Operation-Id` | **your** fresh UUID per money-moving call: `merchantPay`, `complete`, `refund`, `reverse`, `purchaseReceipt`. Idempotency key. |

Test cards are listed on the vendor "Testing" tag. Do not hard-code them.

## Operations

| Group | Path (`POST`) | Purpose |
|---|---|---|
| Payment | `/api/v1/payment/register` | create order, get `orderId` + `paymentRedirectUrl` |
| Payment | `/api/v1/payment/merchantPay` | pay a registered order without the form (bound card, or encrypted PAN with PCI DSS) |
| Payment | `/api/v1/payment/getOrderStatus` | order status + operations list |
| Payment | `/api/v1/payment/getOperationState` | one operation by `operationId` |
| Payment | `/api/v1/payment/getReceipts` | fiscal receipt URLs |
| Acquiring | `/api/v1/acquiring/complete` | capture a TWO_STEP authorization |
| Acquiring | `/api/v1/acquiring/reverse` | void an authorization (TWO_STEP) |
| Acquiring | `/api/v1/acquiring/refund` | full or partial refund after `COMPLETED` |
| Acquiring | `/api/v1/acquiring/purchaseReceipt` | purchase receipt after a `PREPAID` receipt |
| Acquiring | `/api/v1/acquiring/getMerchantCertificate` | certificate + fingerprint for PAN encryption |
| Acquiring | `/api/v1/acquiring/getBindings` | saved cards of a `clientId` |
| Acquiring | `/api/v1/acquiring/unBindCard` | delete a binding |

Callbacks (Uzum POSTs to URLs agreed at onboarding):

| Callback | Body (required fields) |
|---|---|
| acquiring | `orderId`, `orderNumber`, `operationType` (`AUTHORIZE`/`COMPLETE`/`REFUND`/`REVERSE`/`TOP_UP_COMPLETED`), `operationState` (`SUCCESS`/`FAIL`); optional `rrn`, `bindingId`, `cardType`, `merchantOperationId` |
| event | `orderId`, `orderNumber`, `eventType` (`FORM_CLOSED`), `actionCode`, `actionCodeDescription` |
| receipt | `orderId`, `receiptType` (`PURCHASE`/`PREPAID`/`REFUND`), `receiptUrl` |

Answer callbacks with HTTP 200. Without a 200 Uzum retries, at most 5 times.
Callbacks are not signed: verify by calling `getOrderStatus` before fulfilment.

## Response envelope

All responses: HTTP 200 with `{"errorCode": <int>, "message": <string|null>, "result": {...}}`.
`errorCode: 0` is success; anything else is an error and `result` may be absent.
Exception: `unBindCard` declares `errorCode` as a string.

## register

| Field | Rule |
|---|---|
| `viewType` | `WEB_VIEW`, `IFRAME`, `REDIRECT` |
| `clientId` | your stable customer id (bindings hang off it) |
| `currency` | `860` (UZS, ISO 4217 numeric) |
| `orderNumber` | your order id, 1-36 chars; must be unique (`3027` on reuse) |
| `sessionTimeoutSecs` | 600-1800 |
| `amount` | tiyin |
| `successUrl`, `failureUrl` | where the form returns the payer |
| `paymentParams.operationType` | `PAYMENT` or `BINDING` (BINDING: no amount/cart) |
| `paymentParams.payType` | `ONE_STEP` (charge now) or `TWO_STEP` (authorize, then `complete`) |
| `paymentParams.phoneNumber`, `force3ds` | optional |
| `merchantParams.cart` | required when auto-fiscalization is on: `cartId`, `receiptType` (`PURCHASE`/`PREPAID`), `items[]`, `total` |
| `items[]` | `title`, `productId`, `quantity`, `unitPrice`, `total` (tiyin), `receiptParams{spic, packageCode, vatPercent, TIN or PINFL, discount, voucher, labels[]}` |

Result: `{orderId (uuid), paymentRedirectUrl}`.

## Status model

`AcquiringStatus` on `getOrderStatus.result.status`:

```
REGISTERED ──ONE_STEP──> COMPLETED ──refund──> REFUNDED
     │                        
     ├──TWO_STEP──> AUTHORIZED ──complete──> COMPLETED
     │                   └──reverse──> REVERSED
     └──────────> DECLINED
TOP_UP_COMPLETED: top-up (credit to card) finished
```

Operation-level: `operationType` `AUTHORIZE`/`COMPLETE`/`REFUND`/`REVERSE`/`TOP_UP_COMPLETED`,
`state` `IN_PROGRESS`/`SUCCESS`/`FAIL`.

`getOrderStatus.result` also carries `amount`, `totalAmount`, `completedAmount`,
`refundedAmount`, `reversedAmount`, `merchantOrderId` (your `orderNumber`),
`cardType` (`1` corporate, `2` private, `3` social), `ofdPan` (only for `cardType` 3;
pass it as `card_number` to Fiscalization), `bindingId`, `operations[]`.

## Iframe / WebView postMessage

The form posts `{"status": "SUCCESS"|"CANCEL"|"ERROR", "action": "close", "errorCode": <int>, "payment_id"?: <string>}`
to the parent. Close the frame on receipt, then confirm with `getOrderStatus`.

## Error codes (`errorCode`)

| Code | Meaning |
|---|---|
| 0 | Success |
| 1001 | Invalid UzumId token |
| 1006 | Insufficient rights for the operation |
| 2000 | Request validation error |
| 3000 | Operation not allowed in the current payment status |
| 3001 | Terminal not found |
| 3002 | Invalid amount, currency or fee |
| 3003 | Invalid cart parameters |
| 3004 | Terminal does not support this payType |
| 3005 | Payment not found |
| 3006 | Binding not found |
| 3007 | Invalid card details / MCC |
| 3008 | Insufficient funds |
| 3009 | Antifraud decline |
| 3010 | Card blocked by sanctions or restrictions |
| 3011 | Issuer decline |
| 3012 | Transaction limit exceeded |
| 3013 | Amount above configured limit |
| 3014 | MCC not allowed |
| 3015 | Payment system not allowed |
| 3016 | Decryption error (certificate or AES token) |
| 3019 / 3020 | Bad amount / timeout for cancellation |
| 3021 / 3022 | Bad amount / timeout for refund |
| 3023 | Partner not found |
| 3024 | BIN not found |
| 3025 | Encryption not allowed |
| 3026 | Payment form validation error |
| 3027 | `orderNumber` already used |
| 3028 | Operation already exists (reused `X-Operation-Id`) |
| 3029 | Payment data expired |
| 3030 | `complete` not allowed for ONE_STEP |
| 3034 | ONE_STEP not allowed on terminal |
| 3035 | Operation not found |
| 3036 | ONE_STEP payment cannot be reversed (use refund) |
| 3037 | Terminal misconfigured |
| 3038 / 3039 | `complete` / `reverse` not allowed for BINDING |
| 3040 | 3DS not supported |
| 3041 | Session timed out |
| 3042 | Payer closed the form |
| 3043 | Processing-side problem |
| 3045 | Refund cart missing (auto-fiscalization on) |
| 3046 | Refund cart item invalid |
| 3047 | Unknown payment type |
| 3048 | Partner inactive |
| 3049 | Processing not responding |
| 3050 / 3052 | Unknown card scheme configuration |
| 3051 / 3057 | 3DS error (internal / external MPI) |
| 3053 | Marked items count does not match marking codes |
| 3054 | Duplicate marking codes |
| 3055 | Wrong VAT rate, SPIC, package or marking code |
| 3056 | Partner not set up |
| 3058 | Cart not required (auto-fiscalization off) |
| 3059 | Cart total mismatch |
| 3060 | Partner blocked |
| 3401 | Mobile payment allowed only via binding |
| 3404 | Mobile payment temporarily blocked |
| 3405 | SMS-notification phone mismatch or SMS service off |
| 5000 | Internal error |

The response enum also lists `1000-1009` and `3200-3212` without published meanings.

## Gotchas

- Amounts are tiyin everywhere; `currency` is numeric `860`, not `"UZS"`.
- `cart.total` must equal the sum of item `total`s and `amount` (`3059` otherwise).
- ONE_STEP cannot be reversed; refund it. TWO_STEP authorizations must be completed
  or reversed; `complete.amount` may be lower than the authorized amount.
- A fresh `X-Operation-Id` per attempt; reuse it only to retry the *same* request.
- Refund with auto-fiscalization requires the `cart` of returned items (`3045`).
- Auto-fiscalization is off by default and enabled by your Uzum manager. When it is
  off, fiscalize yourself via [Fiscalization](../fiscalization/README.md).
- Production host is not in the spec; keep it in config.

## Examples

[`examples/`](examples/): register (one-step with cart), register response,
getOrderStatus response, acquiring callback, refund request, postMessage, error.
