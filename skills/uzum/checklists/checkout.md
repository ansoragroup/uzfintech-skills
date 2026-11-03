# Checklist: Uzum Checkout (hosted card payments)

Contract: [`../references/checkout/README.md`](../references/checkout/README.md).

## Requests
- [ ] Base URL from config (test and production differ; production is not in the spec).
- [ ] Tests cover the sandbox cards (HUMO, UzCard, 3-DS `777777`) and the test plan in [`references/sandbox/`](../references/sandbox/README.md#checkout); test cards stay in tests and fixtures.
- [ ] `X-Terminal-Id` and `X-API-Key` on every call, from secrets.
- [ ] Fresh UUID `X-Operation-Id` per `merchantPay` / `complete` / `refund` / `reverse` / `purchaseReceipt`; reused only to retry the same request; persisted.
- [ ] `register`: `amount` in tiyin, `currency` `860` (number), `orderNumber` unique per attempt (`3027` handled), `sessionTimeoutSecs` 600..1800.
- [ ] `payType` chosen deliberately (`ONE_STEP` vs `TWO_STEP`) and supported by the terminal (`3004` / `3034`).
- [ ] With auto-fiscalization: `merchantParams.cart.total` == sum of item `total` == `amount` (`3059`); every item has `receiptParams.spic`, `packageCode`, `vatPercent`.
- [ ] Refunds under auto-fiscalization send the cart of returned items (`3045`).

## Responses
- [ ] Every response is checked for `errorCode != 0` before reading `result` (HTTP is 200 on errors).
- [ ] `unBindCard` tolerates `errorCode` as a string.
- [ ] Error codes map to user-facing outcomes (decline vs retry vs bug).

## Callbacks and confirmation
- [ ] Callback endpoints answer HTTP 200 quickly and are idempotent (up to 5 retries).
- [ ] Callbacks are not trusted alone: `getOrderStatus` confirms `status` and amounts before fulfilment.
- [ ] iframe / WebView: the `postMessage` handler checks the origin, closes the frame, then calls `getOrderStatus`.

## State handling
- [ ] Only `COMPLETED` is treated as paid; `AUTHORIZED` (TWO_STEP) means funds are held, not captured.
- [ ] TWO_STEP authorizations are always completed or reversed; a job handles stale `AUTHORIZED`.
- [ ] ONE_STEP payments are refunded, never reversed (`3036`).
- [ ] Partial refunds track `refundedAmount`; totals never exceed `completedAmount`.
- [ ] `cardType 3` stores `ofdPan` if you fiscalize yourself.

## Security
- [ ] No PAN / CVV touches your servers unless PCI DSS scope and `getMerchantCertificate` encryption are in place.
- [ ] API key, terminal id and binding ids are not logged in full.
