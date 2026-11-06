# BTS test host and sample data

Hand-written notes. Transport, auth and errors: [`../common/README.md`](../common/README.md).

- Source: https://docs.bts.uz/page/test-update-status, https://docs.bts.uz/page/auth-login,
  https://docs.bts.uz/page/webhook
- Fetched: 2026-11-06

## Environments

| What | Test | Production |
|---|---|---|
| API base URL | `https://apitest.bts.uz:28345` | issued by BTS with the contract |
| Credentials | test `login` / `password` from BTS | production `login` / `password` from BTS |
| Webhook | register with `environment: "test"` | register with `environment: "production"` |
| Status changes | `POST /v1/order/test-update-status` | real couriers only |

## Status simulator

```
POST /v1/order/test-update-status {"orderId": 1234567, "statusCode": "200"}
  └─> data {success, orderId, oldStatus, newStatus}; then BTS calls your test webhook
```

- `statusCode` is a string.
- Follow `next_possible_statuses` from `status/index`. An illegal step answers `422`
  "Неверный переход статуса".
- To test the full path:
  1. Walk the order through 100 → 200 → 300 → ... → 1200.
  2. Check that each webhook arrives exactly once.
  3. Try to cancel one order at status 100 and another at status 200.
- Schema: [`../order/schemas/test-update-status.json`](../order/schemas/test-update-status.json).

## Sample values used in this skill

These are placeholders, not vendor values.

| Item | Value |
|---|---|
| Login / password | `<BTS_LOGIN>` / `<BTS_PASSWORD>` |
| Tokens | `<ACCESS_TOKEN>`, `<REFRESH_TOKEN>`, `<WEBHOOK_TOKEN>` |
| Phone | `+998901234567` |
| Your order id (`clientId`) | `"100001"` |
| BTS order id / barcode | `1234567` / `"0101 1234567"` |
| City codes | `"1001"` (sender), `"7001"` (receiver) |
| Region / branch | `"70"` / `"7017"` |
| Sender | `Merchant Example` |
| Webhook URL | `https://merchant.example.com/bts/webhook` |
| MXIK code | `<MXIK_CODE>` |
