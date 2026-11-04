# Checklist: Oson transport, auth, statuses and errors (applies to every product)

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] The base URL comes from configuration (`https://api.oson.uz/api/` or the older `https://core.oson.uz:8443/api/`); no host is hard-coded (`oson.host-from-config`).
- [ ] Requests are `POST` JSON with `Content-Type: application/json`.
- [ ] TLS certificate and host verification stay on; no `CURLOPT_SSL_VERIFYPEER => 0` or `verify=False` (`oson.tls-verify`).
- [ ] Connect and read timeouts are set, and a timeout leads to `invoice/status`, not to a new invoice.

## Auth
- [ ] `token` and `merchant_id` come from secrets, are sent only from the server (`token` header, `merchant_id` in the body) and never reach a browser or app.
- [ ] The token is never logged; request logs mask the `token` header (and the `token` body field if you copy Webasyst).

## Statuses and errors
- [ ] Statuses are compared exactly as Oson spells them, including `REGISTRED` (`oson.registred-spelling`).
- [ ] Only `PAID` marks an order paid; `ON_PROGRESS` and `REGISTRED` are pending (`oson.on-progress-not-paid`).
- [ ] `DECLINED`, `PAY_ERROR` and `EXPIRED` are all handled as failures.
- [ ] Errors are read from `error_code` and `message`, logged as received, and the payer sees a neutral message.
- [ ] The body is parsed whatever the HTTP status, and a body that is not JSON is treated as a failure followed by `invoice/status`.
