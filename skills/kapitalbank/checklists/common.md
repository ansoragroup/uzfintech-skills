# Checklist: Kapital API transport, auth, errors and logging (applies to every method)

Contract: [`../references/kapital-api/README.md`](../references/kapital-api/README.md). Mark
each item pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] The host comes from configuration, taken from the bank's connection instruction; no host is hard-coded or guessed (`kapitalbank.host-and-sandbox-not-published`).
- [ ] Every call is `POST` with a JSON body, from the server only; no browser or app calls the API.
- [ ] Paths are taken from the methods table; the `/Mobile/svc/GetAccounts` spelling has been confirmed with the bank before it is used.

## Auth
- [ ] `APILogin` sends `Authorization: Basic base64("IB#" + login + ":" + password)` with the company's internet-banking credentials from a secret store (`kapitalbank.ib-credentials-basic-auth`).
- [ ] The login mode is settled with the bank: SMS code (a person answers it) or IP restriction with the server's egress IPs on the bank's list (`kapitalbank.sms-or-ip-restriction`).
- [ ] With IP restriction, every request carries `Authorization: Basic`; `X-Original-Forwarded-For` is set only to the real client IP.
- [ ] `sid` is sent in the body of `CheckPayments2`, `GetDoc1C` and `GetAcc1C`, where the pages mark it required.
- [ ] `client_id` is `Client.id` from the login answer, converted from string to integer.
- [ ] An expired or refused `sid` leads to one fresh login, not a login loop (lifetime not documented).

## Envelope and errors
- [ ] Success is `error == null` **or** `error.code == 0`; any other `error` is a failure even with HTTP `200` (`kapitalbank.error-in-http-200`).
- [ ] `61002` (IP not allowed) stops the job and alerts; it is not retried in a loop.
- [ ] Unknown error codes are logged with `error.message` and surfaced; the full list is not published.

## Logging and secrets
- [ ] Logs never contain the `Authorization` header, the password, `sid`, or the ЭЦП `signature`.
- [ ] Account numbers and INNs in logs are masked where the logs leave the finance system.
- [ ] Tests run against a mock built from [`../references/sandbox/README.md`](../references/sandbox/README.md); vendor sample values never reach the bank.
