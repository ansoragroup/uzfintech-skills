# Checklist: Uzum Nasiya (installments)

Contract: [`../references/nasiya/README.md`](../references/nasiya/README.md).

- [ ] `Authorization: Bearer <token>` from secrets; HTTP 401 handled.
- [ ] `buyers/check-status` sends `phone` as an **integer**; SMS endpoints send it as a **string**.
- [ ] Buyer `status` branches: `4` -> proceed; `0,1,2,5,10,11,12` -> open `webview`; `8,9,13,14,403` -> refuse.
- [ ] `orders/calculate` result shown to the buyer; `period` in `orders` is the exact `tariff` string.
- [ ] Price unit (UZS vs tiyin) confirmed with the manager and documented in code.
- [ ] `contract_id` read from `data.paymart_client.contract_id` and persisted with the order.
- [ ] `ext_order_id` set to your order id for reconciliation.
- [ ] Signing completed (WebView or SMS code) before `contracts/confirm`; `4010` treated as already active.
- [ ] Contract status polled (no webhooks documented); cancelled orders call `contracts/cancel`.
- [ ] Envelope `status` / `response_code` checked; retry only on `1000` and HTTP 5xx with backoff.
