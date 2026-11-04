# Checklist: Oson payment notification handler

Contract: [`../references/notify/README.md`](../references/notify/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Input
- [ ] The handler reads the raw body as JSON and rejects anything else without a state change.
- [ ] `transaction_id`, `bill_id`, `status` and `signature` are all required.

## Signature
- [ ] The handler computes `sha256_hex(sha256_hex(token + ":" + merchant_id) + ":" + transaction_id + ":" + bill_id + ":" + status)` from the values as received (`oson.verify-notify-signature`).
- [ ] The comparison is constant time (`hmac.compare_digest`, `hash_equals`, `crypto.timingSafeEqual`).
- [ ] No branch skips the check (not for `pay_url`, not for a missing signature, not in "debug" mode).
- [ ] A test proves a wrong or missing signature changes nothing; `scripts/sign.py oson.notify` reproduces the expected value.

## Effects
- [ ] The invoice is found by `transaction_id` and its stored `bill_id` must match.
- [ ] Only `PAID` marks the order paid, once; a repeated `PAID` is a no-op (`oson.on-progress-not-paid`).
- [ ] `DECLINED`, `PAY_ERROR` and `EXPIRED` mark the order failed unless it is already paid.
- [ ] The amount is taken from your order, never from the notification.
- [ ] The handler answers quickly with HTTP 200 for a processed or unknown invoice and does slow work after the answer.
