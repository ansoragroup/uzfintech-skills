---
name: bts
description: API contracts for the BTS Express courier service (Uzbekistan, docs.bts.uz) - login and refresh tokens (Bearer, 24 h access, 30 d refresh), the regions -> cities -> branches directory, the price quote (order-calculate, courier/branch pairs, weight in kg), order/add with sender, receiver, cargo and MXIK goods, cancel (only at status 100), tracking, PDF stickers, the webhook config and the incoming status webhook (form-data JSON, itx-apiKey token), the status codes 100-1400, the test host apitest.bts.uz:28345 and the test-update-status tool. Use when building, reviewing, debugging or testing a BTS delivery integration or its webhook handler, or when validating an implementation against the documented contract.
---

# BTS integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

BTS Express is a courier and parcel network in Uzbekistan. Its API reference lives at
`https://docs.bts.uz/page/<slug>`; every contract here was rebuilt from those pages and
checked against a production client. Where a page contradicts itself, the reference says
so.

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json`: JSON Schemas with `params` (query or body) and `result`
  (reply), carrying the source URL and fetched date;
- `examples/`: placeholder bodies shaped like the documented samples.

Hosts, headers, login and refresh, the reply envelope, statuses, errors, retries and the
configuration a client needs are in [references/common/README.md](references/common/README.md);
read it first. The test host and the status simulator are in
[references/sandbox/](references/sandbox/README.md).

## Products

| Product | Methods | Reference |
|---|---|---|
| Common (all products) | hosts, headers, `auth/login`, `auth/refresh`, envelope, statuses, errors, config | [references/common/](references/common/README.md) |
| Directory | `directory/regions`, `directory/cities`, `directory/branches`, `status/index` | [references/directory/](references/directory/README.md) |
| Quote | `order-calculate/index` (price for each pickup/drop-off pair) | [references/quote/](references/quote/README.md) |
| Order | `order/add`, `order-cancel/index`, `order/track`, `order/sticker`, `order/test-update-status` | [references/order/](references/order/README.md) |
| Webhook | `webhook/webhook-config` (you call), notify (BTS calls you) | [references/webhook/](references/webhook/README.md) |
| Sandbox and test data | test host, status simulator, placeholders | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | token lifetimes, cancel window, retries, fiscal data, open questions | [references/lifecycle/](references/lifecycle/README.md) |

Calls are JSON over HTTPS with `Authorization: Bearer <ACCESS_TOKEN>`, `Accept:
application/json` and a `language` header (`ru`, `uz` or `en`).

## Which product?

| The user wants to... | Use |
|---|---|
| show the shopper a delivery price | Directory for city codes, then Quote |
| let the shopper pick a pickup point | Directory: `directory/branches` |
| book a shipment | Order: `order/add`, store `orderId` and `barcode` |
| print the label | Order: `order/sticker` after create |
| follow a parcel | Webhook first; `order/track` to poll or reconcile |
| cancel a shipment | Order: `order-cancel/index`, only while status is 100 |
| move a test order through statuses | Order: `order/test-update-status` on the test host |
| deliver through Fargo | no public API; see [common](references/common/README.md#fargo) |

## Rules that apply everywhere

- Weight is **kilograms** (float), dimensions are centimetres. Convert from grams before
  you send.
- City and branch codes are strings such as `"7001"` and `"7017"`; take them from the
  directory, never from names.
- Login, password and the webhook token stay on the server. Cache the access token; do not
  log in per request.
- Act on `status.code`, never on `status.id` or the localized `name`.
- Keep the base URL in configuration; the test host carries a port.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the consequence and
the fix. Every window, cancel path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `bts.no-blind-retry-create`: `order/add` has no idempotency key; a retry after a lost
  reply books a second shipment.
- `bts.status-code-not-id`: map `status.code`; `id` is an internal number, not `code/100`.
- `bts.cancel-only-new`: cancel works only at code 100; after pickup it fails.
- `bts.token-lifetime`: access token 24 h, refresh 30 d; refresh early and retry once on 401.
- `bts.webhook-token-check`: compare the `itx-apiKey` in constant time before any change.
- `bts.webhook-form-json`: the webhook is form-data with one JSON string field; trim values.
- `bts.host-from-config`: test and production hosts differ; keep the URL in configuration.
- `bts.weight-in-kg`: send kilograms with one decimal, at least 0.1.
- `bts.phone-format`: send `+998` and nine digits; add the prefix to local numbers.
- `bts.sticker-after-create`: fetch the sticker after `order/add`, not in the same step.
- `bts.undocumented-codes`: codes 900 and 1000 occur but are not in the status list.
- `bts.mxik-per-item`: goods carry their MXIK code, amount and price per line.
- `bts.test-env-webhook`: the simulator fires the webhook only when it is registered with
  `environment: "test"`.

## Top gotchas

1. The quote takes `senderCityCode` / `receiverCityCode` in camelCase; `order/add` takes
   `city_code` inside `sender` / `receiver` in snake_case.
2. `door` and `pvz` are not BTS words: door is `courier`, pickup point is `branch`.
3. Cancel is a `GET` with `orderId` in the query; an already cancelled order answers 400
   `error.already_cancelled`, which you should treat as done.
4. Webhook strings carry stray spaces (`" Доставлен "`, `"0101 1234567 "`).
5. The tracking page sample pairs code 400 with the name of 800; trust the code.
6. The webhook-config page says `GET` but documents a body.
7. Directory replies wrap items in `data.items`; be ready for a bare array as well.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then
[checklists/order.md](checklists/order.md) and
[checklists/webhook.md](checklists/webhook.md); before launch,
[checklists/go-live.md](checklists/go-live.md).

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only.

```sh
python3 scripts/validate.py --list [text]
python3 scripts/validate.py add body.json [--part result]
python3 scripts/validate.py notify webhook.json
```

`validate.py` prints `OK` or `INVALID` with JSON paths and exits 1 on a mismatch. Run it
before you call a payload correct, and quote its output. `sign.py` has no BTS method: the
webhook carries a shared token, not a signature.

## Answering rules

- Reply in the user's language, but never translate method names, fields, codes or enum
  values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation. Code uses
  placeholders and runs as written.
- With several providers in one task, work each one from its own SKILL.md, then compare.
  Never carry a rule (units, auth, retries) over from another provider.
- Lifecycle: before you finish an answer that creates, cancels or tracks a shipment, check
  "Warn without being asked" and [references/lifecycle/](references/lifecycle/README.md).
  For an item under "Not documented", say so and send the user to BTS.
- Quote endpoints, fields and status codes exactly as they appear in the references. If a
  fact is not there, say BTS does not publish it.
- For tests use the values in [references/sandbox/](references/sandbox/README.md). Never
  use real credentials, tokens or real people's data; use placeholders such as
  `<BTS_LOGIN>`, `<BTS_PASSWORD>` and `<ACCESS_TOKEN>`.
- Delivery tariffs, discounts, commissions and settlement terms differ per contract. Do not
  quote or estimate them; read prices from the quote call and say terms come from the
  merchant's agreement.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
