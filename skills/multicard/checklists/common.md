# Checklist: Multicard transport, auth, errors and callbacks (applies to every product)

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] The base URL comes from configuration: `https://mesh.multicard.uz/` in production, `https://dev-mesh.multicard.uz/` in tests.
- [ ] Requests and responses are JSON; amounts are integer tiyin (no floats, no UZS mix-up).
- [ ] Date strings are sent and parsed as `Y-m-d H:i:s` in GMT+5, not UTC or server-local time.
- [ ] `invoice_id` is your own order id (up to 255 chars) and is matched back from `invoice_id` / `store_invoice_id`.

## Auth
- [ ] `application_id` and `secret` come from secrets, separately for sandbox and production, and never reach a front end.
- [ ] The JWT from `POST /auth` is cached until `expiry` (24 h), not requested per call.
- [ ] A `401` triggers one token refresh and one retry, not a loop.
- [ ] The `/auth` answer is parsed without the `{success, data}` envelope, and its `400` shape (`errors[].message[]`) is handled.

## Errors
- [ ] Every other answer is read as `{success, data}` or `{success: false, error{code, details}}`; code branches on the HTTP status and `error.code`, never on `details` text.
- [ ] `423` (OTP expired), `429` (SMS already sent), `403` and `404` are handled even where the page text calls them "400".
- [ ] On a timeout, a 5xx, `ERROR_DEBIT_UNKNOWN`, `ERROR_CALLBACK_TIMEOUT` or `ERROR_UNKNOWN`, the object is polled until `success`, `error` or `revert`; the money-moving call is never resent.
- [ ] Only `success`, `error` and `revert` are treated as final payment statuses; `draft`, `progress`, `billing` and `hold` are not.

## Success callback
- [ ] `sign` is checked as md5 hex of `{store_id}{invoice_id}{amount}{secret}` with a constant-time compare before anything else.
- [ ] `invoice_id` and `amount` are matched to the order before accepting.
- [ ] The handler answers HTTP 200 `{"success": true}` on accept; `{"success": false, "message"}` is sent only when the order really cannot be fulfilled (it refunds the payer).
- [ ] A repeated callback for the same payment `uuid` gets the same success answer and fulfils the order once.
- [ ] The handler answers quickly; slow work runs after the answer (derived).

## Status webhooks (if enabled)
- [ ] The webhook `sign` is checked against a known rule (md5 `{uuid}{amount}{secret}` or SHA1 `{uuid}{invoice_id}{amount}{secret}`), or the payment is re-read with `GET /payment/{uuid}` before acting.
- [ ] The handler answers 2xx and tolerates up to 5 repeats.

## Fiscal items (`ofd`)
- [ ] Each item has `qty`, unit `price` (tiyin), `total` = `qty x price`, `mxik` (IKPU), `package_code` and `name`; `vat` and `mark` are sent where they apply.
- [ ] Whether you or Multicard fiscalizes follows the store `tax_registration` value.

## Sandbox and logging
- [ ] Tests use the sandbox host, the test card and OTP `111111` from [`../references/sandbox/README.md`](../references/sandbox/README.md); none of them appear in production code paths.
- [ ] Logs never contain `secret`, JWTs, full PANs, expiry, CVC, OTPs or `kyc_data`.
