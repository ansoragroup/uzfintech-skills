# Checklist: BTS transport, auth and statuses

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each
item pass / fail / n.a. and cite the file and line that proves it.

## Transport

- [ ] The base URL comes from configuration, not code (`bts.host-from-config`)
- [ ] Every request sends `Accept: application/json` and a `language` header
- [ ] TLS verification is on
- [ ] Logs redact `Authorization`, `password`, `refresh_token` and `itx-apiKey`

## Auth

- [ ] The access token is cached and renewed before about 24 h (`bts.token-lifetime`)
- [ ] Only one login runs at a time, and concurrent callers wait for it
- [ ] A `401` triggers one new login and one repeat of the call, never a loop
- [ ] `login`, `password` and `webhook_token` live in a secret store

## Statuses and errors

- [ ] Statuses are read from `status.code`, never from `status.id` (`bts.status-code-not-id`)
- [ ] Unknown codes map to in-transit and are logged (`bts.undocumented-codes`)
- [ ] Both the envelope shape and the framework error shape are parsed
- [ ] 5xx, 429 and 425 are retried with backoff for reads; 4xx are not retried
