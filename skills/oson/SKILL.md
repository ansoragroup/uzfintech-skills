---
name: oson
description: API contracts for the Oson payment service (Uzbekistan, api.oson.uz) reconstructed from Oson's own open-source shop plugins (WooCommerce, OpenCart, 1C-Bitrix, Webasyst), because Oson publishes no API reference - invoice/create with a pay_url redirect, invoice/status, the payment notification signed with sha256(sha256(token:merchant_id):transaction_id:bill_id:status), statuses (REGISTRED, ON_PROGRESS, PAID, DECLINED, PAY_ERROR, EXPIRED), the token header plus merchant_id in the body, amounts in soum, and the gaps (no sandbox, no test flag, no refund method, unknown lifetime unit). Use when building, reviewing, debugging or testing an Oson integration or a notify handler, or when validating an implementation against the reconstructed contract.
---

# Oson integrations

This file is a router. Answer contract questions from the files referenced below, not from
memory.

Oson publishes no API reference: `oson.uz/docs` answers 404. Every contract here is
**rebuilt from Oson's own shop plugins** on GitHub, pinned to the commits in
[references/common/README.md](references/common/README.md). Field names and the signature
are exact; required fields, types, limits and error codes are what the plugins send and
read. Say so when you answer (`oson.unverified-contract`).

Each product folder has:
- `README.md`: hand-written notes;
- `schemas/<method>.json`: JSON Schemas with `params` (body) and `result` (reply),
  carrying the source URL and fetched date;
- `examples/`: placeholder bodies built from the plugin code.

The host, the auth pair, statuses and error fields are in
[references/common/README.md](references/common/README.md); read it first. What exists for
testing (nothing official) is in [references/sandbox/](references/sandbox/README.md).

## Products

| Product | Methods | Reference |
|---|---|---|
| Common (all products) | hosts, `token` header + `merchant_id`, amounts, statuses, error fields | [references/common/](references/common/README.md) |
| Invoice (payment page by link) | create (`invoice/create` -> `pay_url`), status (`invoice/status`) | [references/invoice/](references/invoice/README.md) |
| Notification (incoming) | notify: `transaction_id`, `bill_id`, `status`, `signature` | [references/notify/](references/notify/README.md) |
| Sandbox and test data | none published; offline signature and handler tests; placeholders | [references/sandbox/](references/sandbox/README.md) |
| Lifecycle (all products) | lifetime, no cancel or refund method, retries, fiscal receipts, open questions | [references/lifecycle/](references/lifecycle/README.md) |

Calls are `POST` JSON to `https://api.oson.uz/api/invoice/...` with a `token` header and
`merchant_id` in the body. The older Bitrix module uses `https://core.oson.uz:8443/api/`.

## Which product?

| The user wants to... | Use |
|---|---|
| send the payer to an Oson payment page | Invoice: create -> redirect to `pay_url` |
| learn whether an invoice is paid | Invoice: status with the same `transaction_id` |
| receive the payment result on the server | Notification: verify `signature`, then update the order |
| cancel an unpaid invoice | no method; let `lifetime` run out (`EXPIRED`) |
| refund a paid invoice | no API method; the Oson cabinet or support (`oson.no-refund-api`) |
| issue a tax receipt | not covered by Oson's plugins; see [lifecycle](references/lifecycle/README.md#fiscal-receipts) |
| test | [sandbox](references/sandbox/README.md): no test mode exists |

## Rules that apply everywhere

- Amounts are **major units** (soum for `UZS`), not tiyin.
- `token` and `merchant_id` stay on the server. The token is also the notification signing
  secret.
- Success of create is `status: "REGISTRED"` (Oson's spelling) with a `pay_url`; anything
  else is an error with `error_code` and `message`.
- Fulfil only on `PAID`, from a notification whose signature you verified or from
  `invoice/status`. `return_url` proves nothing.
- `transaction_id` is yours and unique per attempt; store `bill_id` with it.
- Keep TLS verification on and the host in configuration.

## Warn without being asked

Raise each item the task touches, even if nobody asked: give its ID, the consequence and
the fix. Every window, cancel path and source is in
[references/lifecycle/](references/lifecycle/README.md).

- `oson.unverified-contract`: no public API reference; the contract comes from plugin code.
  Confirm fields and error codes with Oson before go-live.
- `oson.host-from-config`: two hosts are in use (`api.oson.uz`, `core.oson.uz:8443`); keep
  the base URL in configuration.
- `oson.verify-notify-signature`: verify the sha256 signature in constant time; the Bitrix
  module never checks it and Webasyst skips it when `pay_url` is present.
- `oson.status-before-shipping`: read `invoice/status` before you ship; the return URL is
  not proof.
- `oson.on-progress-not-paid`: only `PAID` is paid; OpenCart wrongly treats `ON_PROGRESS`
  as paid.
- `oson.registred-spelling`: compare with `REGISTRED`; a corrected spelling never matches.
- `oson.tls-verify`: two plugins disable TLS verification; never copy that.
- `oson.amount-major-units`: soum, not tiyin; WooCommerce rounds up, Bitrix sends two
  decimals.
- `oson.unique-transaction-id`: a fresh `transaction_id` per attempt; Bitrix reuses the
  order id.
- `oson.lifetime-unit`: the `lifetime` unit is not documented (plugins send 30 or 14400).
- `oson.no-test-mode`: no sandbox and no test flag; every invoice is real.
- `oson.no-refund-api`: no cancel or refund method; plan refunds through Oson.

## Top gotchas

1. `REGISTRED` is spelled without the second E in every plugin.
2. The outer signature hash runs over the inner **hex string** joined with `:`; hashing raw
   bytes or skipping the colon gives a different value.
3. The notification carries no amount; match the order by `transaction_id` and check
   `bill_id`.
4. Only OpenCart sends `notify_url`; set the notify URL in the cabinet as well.
5. Webasyst also sends `token` in the body; the header is what every plugin sends.
6. The Bitrix module passes `amount` as a two-decimal string and `lifetime` 14400; the
   others send numbers and 30.
7. OpenCart reads errors from `errno` / `errstr`, the others from `error_code` / `message`.

## Validate an implementation

Run [checklists/common.md](checklists/common.md) first, then
[checklists/invoice.md](checklists/invoice.md) and
[checklists/notify.md](checklists/notify.md); before launch,
[checklists/go-live.md](checklists/go-live.md).

Mark each item pass, fail or n.a. with a file:line citation. Then compare the payloads with
`schemas/` and `examples/`.

## Tools: run them, do not compute by hand

`scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/` in Claude Code) holds two
python3 scripts, standard library only. Secrets come from environment variables, never from
arguments, and print as `<SECRET>`.

```sh
python3 scripts/sign.py --list     # oson.notify
python3 scripts/sign.py oson.notify -f merchant_id=<MERCHANT_ID> notify.json   # OSON_TOKEN
python3 scripts/validate.py --list [text]
python3 scripts/validate.py create body.json [--part result]
```

`sign.py` prints the exact string it signed and, given a received value, `MATCH` or
`MISMATCH`. `validate.py` prints `OK` or `INVALID` with JSON paths. Both exit 1 on a
mismatch. Run them before you call a signature or payload correct, and quote their output.

## Answering rules

- Reply in the user's language, but never translate method names, fields, codes or enum
  values.
- Fit the answer to where it goes. In chat, give the conclusion first, in about 100 words
  unless code is asked for. In a PR or review, write Problem, Change, Validation. Code uses
  placeholders and runs as written.
- With several providers in one task, work each one from its own SKILL.md, then compare.
  Never carry a rule (units, auth, retries) over from another provider.
- Lifecycle: before you finish an answer that creates, checks, cancels or refunds a
  payment, check "Warn without being asked" and
  [references/lifecycle/](references/lifecycle/README.md). For an item under "Not
  documented", say so and send the user to Oson.
- Quote endpoints, fields and statuses exactly as they appear in the references, and say
  they come from plugin code. If a fact is not there, say Oson does not publish it.
- For tests use the notes in [references/sandbox/](references/sandbox/README.md). Never use
  real merchant credentials, tokens or real people's data; use placeholders such as
  `<OSON_TOKEN>` and `<MERCHANT_ID>`.
- Commission rates, payout percentages, settlement terms and fees differ per merchant
  contract. Do not quote or estimate them; say they come from the merchant's agreement.
- Freshness: each README carries `Fetched:`. Run `scripts/sync --check` to compare against
  upstream.
