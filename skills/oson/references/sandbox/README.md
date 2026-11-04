# Oson test mode and sample data

Hand-written notes. Oson publishes **no sandbox host, no test flag and no test cards**,
and none of its plugins has a test setting. Transport, auth and errors:
[`../common/README.md`](../common/README.md).

- Source: the four Oson plugins listed in [`../common/README.md`](../common/README.md);
  WooCommerce `README.md` for the cabinet
- Fetched: 2026-11-04

## Environments

| What | Test | Production |
|---|---|---|
| API base URL | none published | `https://api.oson.uz/api/` (older Bitrix module: `https://core.oson.uz:8443/api/`) |
| Switch | none | n/a |
| Credentials | ask Oson for a test merchant | `merchant_id` and `token` from `https://business.oson.uz/` |

- Every invoice is real. Warning [`oson.no-test-mode`](../lifecycle/README.md).
- Test offline first: the notification signature with
  `python3 ${CLAUDE_SKILL_DIR}/scripts/sign.py oson.notify` and your handler with the
  example bodies in [`../notify/examples/`](../notify/examples/).

## Sample values used in this skill

These are placeholders, not vendor values.

| Value | Where |
|---|---|
| `merchant_id` `1001`, `token` `oson_test` | the `oson.notify` test vector in `scripts/sign.py` |
| `transaction_id` `100001`, `bill_id` `200001` | invoice and notify examples |
| phone `998901234567` | invoice example |
| `https://merchant.example.com/...` | return and notify URLs |
| `https://pay.example.com/oson/200001` | stand-in for `pay_url`; use the URL Oson returns |
