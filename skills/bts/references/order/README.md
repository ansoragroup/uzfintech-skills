# BTS order (`order/add`, `order-cancel/index`, `order/track`, `order/sticker`)

Hand-written notes. Transport, auth, statuses and errors:
[`../common/README.md`](../common/README.md). Status pushes:
[`../webhook/README.md`](../webhook/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://docs.bts.uz/page/order-add, https://docs.bts.uz/page/order-cancel,
  https://docs.bts.uz/page/tracking, https://docs.bts.uz/page/order-sticker,
  https://docs.bts.uz/page/test-update-status
- Fetched: 2026-11-06

## Flow

```
POST /v1/order/add {clientId, pickup_type, dropoff_type, sender{}, receiver{}, cargo{}, ...}
   └─> data {orderId, barcode, status, cost}; store orderId and barcode on your order
GET  /v1/order/sticker?orderId=...&decode=0|1   -> PDF label URLs (base64 with decode=1)
webhook pushes status codes  ─┐
GET  /v1/order/track?orderId=... ─┴─> data {orderId, status{code, name}}
GET  /v1/order-cancel/index?orderId=...  (only while code is 100)
   └─> data {orderId, status{id 0, code 1300, name "Cancelled Order"}}
```

## Create fields

| Field | Notes |
|---|---|
| `clientId` | your order id as a string; comes back in the webhook |
| `pickup_type` | `courier` (BTS collects) or `self` (you bring it to a branch) |
| `dropoff_type` | `courier` (to the door) or `branch` (pickup point) |
| `sender`, `receiver` | `name`, `phone` (`+998` and nine digits), `address`, `city_code`, `branch_code`; `receiver.phone1` optional |
| `is_sender_location`, `is_receiver_location`, `ready_to_take`, `wcs_code` | optional; see the page |
| `bringBackMoney`, `back_money` | cash on delivery flag and amount |
| `takePhoto`, `bringBackWaybill` | `0` or `1` |
| `cargo.weight` | kilograms (`bts.weight-in-kg`) |
| `cargo.volume`, `cargo.piece` | centimetres, piece count |
| `cargo.packageId`, `cargo.postTypeId`, `cargo.postTypes[]` | values BTS issues for your account |
| `cargo.options[]` | `{optionId: 2, goods: [{mxikGoodsId, amount, goodPrice}]}`, one line per item (`bts.mxik-per-item`) |

## Rules

- `order/add` has no idempotency key. On a timeout or 5xx, do not resend; look the order up
  (by `clientId` in BTS support or your next webhook) and mark it for review
  (`bts.no-blind-retry-create`).
- Fetch the sticker in a separate step after create succeeds; retry it freely
  (`bts.sticker-after-create`).
- Cancel only at code 100 (`bts.cancel-only-new`). `400 error.already_cancelled` means it
  is already cancelled: treat as success. Later codes need BTS support.
- Track: `404 Ресурс не найден.` for an unknown id. The page sample pairs code 400 with
  "В офисе доставки" (the name of 800); trust `code`.
- Sticker errors: `400` and `401` in the framework shape, `404 error.not_found`.
- `order/test-update-status` exists on the test host only; see
  [`../sandbox/README.md`](../sandbox/README.md).
