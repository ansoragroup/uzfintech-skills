# BTS webhook (`webhook/webhook-config`, incoming notify)

Hand-written notes. Transport, auth, statuses and errors:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://docs.bts.uz/page/webhook
- Fetched: 2026-11-06

## Register

```
GET /v1/webhook/webhook-config
    {"webhook_url": "https://merchant.example.com/bts/webhook",
     "environment": "production" | "test", "has_token": true, "itx-apiKey": "<WEBHOOK_TOKEN>"}
  └─> data echoes the settings plus "method": "POST" and "date"; bad input answers 422
```

The page says `GET` yet documents a body; send JSON and confirm the verb with BTS.
`itx-apiKey` is at most 512 characters. Register the test host with `environment: "test"`
or the simulator will not call you (`bts.test-env-webhook`).

## Incoming notify

BTS sends `POST <webhook_url>` as form-data. One field holds a JSON string:

```json
{"clientId": null, "orderId": 1234567, "barcode": "0101 1234567 ",
 "status": {"id": 6, "code": 1200, "name": " Доставлен "}, "date": "2022-06-20 07:55:01"}
```

## Handling

1. Read the token, in this order: the `itx-apiKey` header, `Authorization: Bearer`, the
   form field `itx-apiKey`, the form field `token`. Compare it with your `webhook_token` in
   constant time; accept the previous token during rotation. On mismatch answer `401`
   `{"ok":false}` and change nothing (`bts.webhook-token-check`).
2. Find the field whose value parses as JSON (`bts.webhook-form-json`). Trim every string.
3. Use `status.code`. `status.id` is an internal number; never derive the code as
   `id * 100` (`bts.status-code-not-id`).
4. Match the order by `orderId` (and `clientId` when set). Deduplicate on
   `orderId:code:date`; a repeat is a no-op.
5. Answer `400` for unparseable input, `200` once stored. Retries and timeouts are not
   documented.
