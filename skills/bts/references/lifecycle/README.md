# BTS lifecycle: traps, windows, cancel, retries

Where BTS integrations break in practice, and what the docs leave out. Every ID below is
the one used in [`../../SKILL.md`](../../SKILL.md) and in the checklists.

- Source: https://docs.bts.uz/page/order-add, https://docs.bts.uz/page/order-cancel,
  https://docs.bts.uz/page/webhook, https://docs.bts.uz/page/status,
  https://docs.bts.uz/page/auth-login
- Fetched: 2026-11-06

## Warn without being asked

1. **`bts.no-blind-retry-create`**: when `order/add` times out or answers 5xx → do not
   send it again. It has no idempotency key, so a resend can create a second shipment.
   Mark the order for review and reconcile it ([order](../order/README.md#rules)).
2. **`bts.status-code-not-id`**: when you read a status → use `status.code` (100-1400).
   `status.id` is an internal number, and `id * 100` gives the wrong status
   ([webhook](../webhook/README.md#handling)).
3. **`bts.cancel-only-new`**: when you cancel → it works only at code 100. Treat `400
   error.already_cancelled` as success. Later codes need BTS support
   ([order](../order/README.md#rules)).
4. **`bts.token-lifetime`**: when you call any endpoint → cache the access token (it lives
   about 24 h) and renew it early. Let only one login run at a time. On a `401`, log in
   once and retry the call once ([common](../common/README.md#auth)).
5. **`bts.webhook-token-check`**: when a webhook arrives → check `itx-apiKey` (header,
   Bearer or form field) in constant time before changing anything. On a mismatch, answer
   `401` ([webhook](../webhook/README.md#handling)).
6. **`bts.webhook-form-json`**: when you parse the webhook → the body is form-data and one
   field holds a JSON string. Strings carry stray spaces, so trim them
   ([webhook](../webhook/README.md#incoming-notify)).
7. **`bts.host-from-config`**: when you set the host → read it from configuration. The test
   host uses port 28345, and BTS issues the production host with the contract
   ([common](../common/README.md#transport)).
8. **`bts.weight-in-kg`**: when you send a weight → use kilograms, rounded to one decimal,
   at least 0.1. Shops usually store grams ([quote](../quote/README.md#rules)).
9. **`bts.phone-format`**: when you send a phone number → send `+998` and nine digits. Add
   `998` to a bare nine-digit number ([order](../order/README.md#create-fields)).
10. **`bts.sticker-after-create`**: when you need a label → fetch the sticker after
    `order/add` succeeds, as its own step that can be retried. A failed sticker must not
    fail the order ([order](../order/README.md#rules)).
11. **`bts.undocumented-codes`**: when a code is not in `status/index` (900, 1000 or a new
    one) → map it to in-transit and log it. Do not reject the webhook
    ([common](../common/README.md#statuses)).
12. **`bts.mxik-per-item`**: when you build `cargo.options[].goods` → send one line per item
    with its MXIK code, amount and price ([order](../order/README.md#create-fields)).
13. **`bts.test-env-webhook`**: when you test on `apitest` → register the webhook with
    `environment: "test"`, or the simulator never calls you
    ([sandbox](../sandbox/README.md#status-simulator)).

## Deadlines and windows

| Operation | Window or limit | When it is missed | Source |
|---|---|---|---|
| Access token | about 24 h | `401`; log in again | auth-login |
| Refresh token | about 30 days | `422`; log in with login and password | auth-login-refresh |
| Cancel | while the code is 100 | refused; ask BTS support | order-cancel |
| Pickup point storage | not documented | code 1400 (Срок истек) | status |
| Webhook answer | not documented | not documented | webhook |

## Cancel, reverse and refund

| Situation | Who starts it | Method / endpoint | Partial? | How many times | Fiscal receipt | Source |
|---|---|---|---|---|---|---|
| Cancel before pickup | merchant | `GET /v1/order-cancel/index?orderId=` | no | once; a repeat answers `already_cancelled` | not documented | order-cancel |
| Cancel after pickup | merchant via BTS support | none in the API | no | — | not documented | order-cancel |
| Recipient refuses or storage runs out | BTS | none; ends at code 1400 | no | — | not documented | status |
| Cash on delivery refund | merchant | outside the BTS API | — | — | the merchant's own receipt | not documented |

## Retries and idempotency

| Call or webhook | Provider retries | Your answer deadline | Idempotency key | Duplicate handling | Source |
|---|---|---|---|---|---|
| `auth/login` | — | — | none | safe to repeat | auth-login |
| `order-calculate/index`, `order/track`, `order/sticker`, directory | — | — | none | reads; safe to repeat | order-calculator, tracking |
| `order/add` | — | — | none | never resend blindly (`bts.no-blind-retry-create`) | order-add |
| `order-cancel/index` | — | — | `orderId` | `already_cancelled` counts as success | order-cancel |
| Incoming webhook | not documented | not documented | `orderId:code:date` | answer `200` and change nothing | webhook |

## Fiscal receipts

`order/add` takes MXIK codes, amounts and prices per item in `cargo.options[].goods`. The
docs do not say whether BTS registers a fiscal receipt for cash on delivery. Until BTS
confirms in writing, the merchant registers its own receipt.

## Not documented — ask the provider

- The production base URL and whether it also uses a non-standard port.
- Webhook retry policy, timeout, and whether delivery order is guaranteed.
- The HTTP verb of `webhook-config` (the page says GET but shows a body).
- The meaning of codes 900 and 1000, and whether 1300 and 1400 are final.
- How long a pickup point keeps a parcel before code 1400.
- Who issues the fiscal receipt for cash on delivery.
- Whether `order/add` can be looked up by `clientId` after a timeout.
