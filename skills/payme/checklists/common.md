# Checklist: Payme transport, auth and errors (applies to every product)

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport
- [ ] Merchant API: one HTTPS Endpoint URL accepts JSON-RPC 2.0 `POST`; non-`POST` requests answer `-32300`.
- [ ] Merchant API: every outcome, including errors, is sent with **HTTP 200** and `Content-Type: text/json; charset=UTF-8`.
- [ ] Subscribe API: calls go to `https://checkout.paycom.uz/api` (test: `https://checkout.test.paycom.uz/api`), chosen by configuration, never hard-coded per environment.
- [ ] Amounts are integer tiyin everywhere (no floats, no UZS mix-up); times are epoch milliseconds.

## Auth
- [ ] Merchant API checks `Authorization: Basic base64(<login>:<key>)` on every call and answers `-32504` on a mismatch.
- [ ] The production key and `TEST_KEY` come from secrets and are kept apart.
- [ ] Optional defence in depth: the source IP is checked against the list on the vendor page (`/protokol-merchant-api/skhema-vzaimodeystviya/`), loaded from configuration.
- [ ] Subscribe API: `X-Auth: <CASHBOX_ID>:<CASHBOX_KEY>` is sent only from the back end; front ends send only `X-Auth: <CASHBOX_ID>`.

## Errors
- [ ] Every response echoes the request `id`; success uses `result`, failure uses `error {code, message, data}`.
- [ ] Malformed JSON answers `-32700`; missing or mistyped RPC fields answer `-32600`; unknown methods answer `-32601` with the method name in `data`.
- [ ] Internal failures (database, file system) answer `-32400`, not an HTTP 5xx.
- [ ] Merchant API business errors carry a localized `message` object with `ru`, `uz` and `en`.
- [ ] Subscribe API callers branch on `error.code`, log `error.message`, and never parse message text.

## Sandbox and logging
- [ ] Both sandbox scenarios at https://test.paycom.uz pass before go-live (scenario 1 first; steps in [`../references/sandbox/README.md`](../references/sandbox/README.md)).
- [ ] Subscribe tests cover the error cards (expired, blocked, system error, 10 s delay), not only the happy-path card.
- [ ] Test cards, the SMS code and test-cabinet credentials are not hard-coded in production paths.
- [ ] Logs never contain the cashbox key, `TEST_KEY`, the Basic auth header, card numbers, expiry or SMS codes.
