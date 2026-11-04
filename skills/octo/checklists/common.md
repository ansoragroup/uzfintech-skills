# Checklist: Octo transport, auth, errors and notifications (applies to every product)

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] The base URL `https://secure.octo.uz` comes from configuration; no code points at `dev-pay.octo.uz` or `pay-dev.octo.uz` as an API host.
- [ ] Requests are `POST` JSON (`verificationInfo` is `GET`); amounts are decimal **major units** of `currency`, not tiyin.
- [ ] `init_time` is sent as `yyyy-MM-dd HH:mm:ss`; `payed_time` and `refund_time` are parsed in that format, and the partner transaction times (`createTime`, `expireTime`, `peyedTime`) as epoch milliseconds.
- [ ] `shop_transaction_id` is your own id, unique per payment attempt, and is stored before the call.

## Auth and the test flag
- [ ] `octo_shop_id` and `octo_secret` come from secrets, go only in server-side request bodies, and never reach a browser or app.
- [ ] `test` is set explicitly from per-environment configuration on every `prepare_payment`; a missing setting stops the service instead of creating a real payment (`octo.test-flag-real-money`).
- [ ] `error: 2` (`fiscal-data`: `error: 1`) is treated as a configuration fault and is not retried.

## Envelope and errors
- [ ] Code checks `error == 0` first and reads `data.*`, never the top-level copies or the deprecated `errorMessage`.
- [ ] A body without `error` (`{title, status: 500, detail}`) is treated as a failure, followed by a status check.
- [ ] Processing codes are read together with the card network (`500` differs for Humo and Uzcard).
- [ ] Only `succeeded` and `canceled` are treated as final; `created`, `wait_user_action`, `waiting_for_capture`, `pending` and unknown values are re-checked.

## Notifications (`notify_url`)
- [ ] `signature` is checked as upper-case hex `sha1` over `unique_key`, `octo_payment_UUID`, `status` (as `scripts/sign.py octo.notify` computes it) with a constant-time compare; `unique_key` is a separate secret, not `octo_secret`.
- [ ] Before an order changes, the status is re-read with the three-field `prepare_payment` call (`octo.notify-verify-status`).
- [ ] `total_sum`, `currency` and `shop_transaction_id` are matched to the order.
- [ ] The handler is idempotent by `octo_payment_UUID` + `status`, answers HTTP `200` quickly and runs slow work afterwards (derived).
- [ ] `card_vendor` is parsed as a free string (the sample sends `Visa`, which the enum lacks).

## Fiscal items
- [ ] Every `basket` item matches an item registered with Octo (`spic`, `package_code`, `nds`, `inn` or `pinfl`); see [`fiscal.md`](fiscal.md).

## Sandbox and logging
- [ ] Tests use `test: true` and your own shop; the vendor sample cards from [`../references/sandbox/README.md`](../references/sandbox/README.md) appear only in offline fixtures, never in a live call.
- [ ] Logs never contain `octo_secret`, `unique_key`, full PANs, expiry, CVC2, OTPs or `card_token`.
