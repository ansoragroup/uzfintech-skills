# Oson payment notification (incoming POST to your notify URL)

Hand-written notes. Statuses and auth: [`../common/README.md`](../common/README.md). The
invoice it belongs to: [`../invoice/README.md`](../invoice/README.md). Schema:
[`schemas/notify.json`](schemas/notify.json). Example:
[`examples/notify.request.json`](examples/notify.request.json) (signed with the test vector
of `scripts/sign.py`, secret `oson_test`).

- Source: https://github.com/Osonuz/Woocommerce-gateway-oson/blob/43ff85efb26c2284bfca7b186026ee0f3d011613/plugin.php
  (lines 180-225), https://github.com/Osonuz/OpenCart-Plugin/blob/b68320637c9dbd61f47359487921c036a466719d/upload/catalog/controller/extension/payment/osongw.php
  (lines 150-195), https://github.com/Osonuz/Webasyst-Shop-Script-Plugin/blob/ea43f49aa0a9ff801d4e3a5d5a74f386b7e35ae3/oson/lib/osonPayment.class.php
  (lines 120-160), https://github.com/Osonuz/OSON-modul-for-1C-Bitriks/blob/04c8fc3cc8fd2f920913b1b8a989d9f18711e137/oson.payment/lib/api.php
  (lines 130-170)
- Fetched: 2026-11-04
- Spec: none; reconstructed from plugin code. Warning
  [`oson.unverified-contract`](../lifecycle/README.md).

## Request

`POST <notify URL>` with a JSON body (the plugins read the raw body, not form fields):

| Field | Meaning |
|---|---|
| `transaction_id` | your id from `invoice/create` |
| `bill_id` | Oson's invoice id |
| `status` | one of the statuses in [`../common/README.md`](../common/README.md#statuses) |
| `signature` | lower-case hex SHA-256, below |

There is no amount, currency, payer or time in the body. Take the amount from your own
order, and confirm it with `invoice/status` before you ship if the reply ever carries one
(not documented).

The notify URL is the `notify_url` you send in `invoice/create` (OpenCart) or the one set
in the cabinet (the Bitrix settings default to `https://<shop>/oson/payment/notify.php`;
WooCommerce matches any path with `/webhook` in it).

## Signature

```
inner     = sha256_hex(token + ":" + merchant_id)
signature = sha256_hex(inner + ":" + transaction_id + ":" + bill_id + ":" + status)
```

- `token` is the same secret you send in the `token` header; `merchant_id` is your shop id.
  Both hashes are lower-case hex strings; the outer hash runs over the inner **hex
  string**, not its raw bytes.
- Build the string from the values exactly as received (no trimming, no number
  formatting of `bill_id`).
- Compare in constant time. Reject a missing or wrong signature with no state change.
- Check it: `python3 ${CLAUDE_SKILL_DIR}/scripts/sign.py oson.notify -f merchant_id=1001
  -f transaction_id=100001 -f bill_id=200001 -f status=PAID` with `OSON_TOKEN` set.
- Two vendor plugins are unsafe: the Bitrix module never checks the signature, and the
  Webasyst plugin skips it whenever the body contains `pay_url`, so a forged `PAID` body
  passes. Never copy either. Warning
  [`oson.verify-notify-signature`](../lifecycle/README.md).

## Handling

1. Read the raw body as JSON; reject anything else with HTTP 400.
2. Verify the signature. Wrong → HTTP 403 (derived; no plugin sends a status code), no
   change.
3. Find the invoice by `transaction_id` (WooCommerce, Bitrix, Webasyst) and check that
   `bill_id` matches the one you stored at create time (OpenCart looks up by `bill_id`).
   Unknown → log and answer 200 with no change (derived).
4. `PAID` → mark paid once; a repeat `PAID` for an already-paid invoice is a no-op.
   `DECLINED`, `PAY_ERROR`, `EXPIRED` → mark failed unless already paid. `REGISTRED`,
   `ON_PROGRESS` → record only. Warning [`oson.on-progress-not-paid`](../lifecycle/README.md).
5. Answer quickly with HTTP 200. Webasyst prints `OK`; the others print nothing useful. What
   Oson expects back and whether it retries is not documented.

## Not documented

- The expected answer body and status code, retries and their schedule.
- Whether a notification is sent for every status or only for final ones.
- Source IPs to allow-list.
