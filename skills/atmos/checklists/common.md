# Checklist: Atmos transport, auth, errors and the Callback API (applies to every product)

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] The base URL `https://apigw.atmos.uz` and the test setup Atmos gave you come from configuration, per environment.
- [ ] Requests are JSON (`Content-Type: application/json`), except the form bodies of `/token` and `/revoke`.
- [ ] Amounts are integer tiyin everywhere (no floats, no UZS mix-up).
- [ ] Nothing is called on `partner.atmos.uz` without Atmos confirming it; card linking uses `https://apigw.atmos.uz/partner/...`.

## Auth
- [ ] `consumer_key` and `consumer_secret` come from secrets and never reach a front end or a log.
- [ ] `POST /token` sends `grant_type=client_credentials` in the form body with `Authorization: Basic base64(consumer_key:consumer_secret)`.
- [ ] The token is cached and renewed before `expires_in` runs out (3600 s by the text), not requested per call.
- [ ] A `401` triggers one token renewal and one retry, not a loop.
- [ ] The header reads `Authorization: Bearer <token>` with the word `Bearer` once.

## Errors
- [ ] Code branches on the HTTP status first, then on the module's code: `result.code` (`OK` / `STPIMS-ERR-*`), PINFL `code`, or MPS `status.code`; never on `description` text.
- [ ] `STPIMS-ERR-118`, `STPIMS-ERR-065`, `INFO-202`, a timeout or a 5xx lead to a read (`pay/get` and the like), never to a repeated money call.
- [ ] `STPIMS-ERR-006` / `-007` / `-009` are treated as request bugs and not retried as they are.
- [ ] `STPIMS-ERR-031` and HTTP `429` back off.

## Callback API (your billing URL)
- [ ] The handler recomputes `sign` from `store_id`, `transaction_id`, `invoice`, `amount` and the `api_key` (no separators) and compares in constant time; `sign.py atmos.callback` was run against a real test callback to learn the hash.
- [ ] `invoice` (your `account`) and `amount` (tiyin) are matched to an open order before accepting.
- [ ] Accept answers HTTP 200 `{"status": 1, "message": "Successfully"}`; refuse answers `{"status": 0, "message": "<reason>"}`.
- [ ] A repeated callback for the same `transaction_id` gets the same answer and fulfils the order once (derived).
- [ ] The handler answers quickly; slow work runs after the answer (derived).
- [ ] Requests are accepted only from the Atmos address published on the vendor page, taken from there and kept in configuration.
- [ ] The `api_key` comes from secrets and is never logged.

## Fiscal items (`ofd_items`)
- [ ] Each line has `ofd_code` (IKPU), `name`, `amount` (tiyin) and `details` with `quantity`, `package_code` and, for marked goods, `mark_code`.
- [ ] The line amounts add up to the payment amount (derived).

## Sandbox and logging
- [ ] Tests use the test cards and OTP from [`../references/sandbox/README.md`](../references/sandbox/README.md); none of them appear in production code paths.
- [ ] Logs never contain `consumer_secret`, tokens, `api_key`, full PANs, expiry, CVC, OTPs, card balances or PINFL / passport data.
