# Checklist: Uzum Merchant API (you implement the webhooks)

Contract: [`../references/merchant/README.md`](../references/merchant/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Transport and auth
- [ ] Five `POST` endpoints exist: `/check`, `/create`, `/confirm`, `/reverse`, `/status`.
- [ ] Basic auth is checked on every call with a constant-time compare; failure -> HTTP 400 + `errorCode "10001"`.
- [ ] Invalid JSON -> `10002`; non-POST -> `10003`; missing required field -> `10005`.
- [ ] `serviceId` is validated against config (`10006`).
- [ ] Credentials and `serviceId` come from config / secrets, not source code.

## Types and units
- [ ] `amount` handled as integer tiyin end to end (no float, no UZS mix-up).
- [ ] `timestamp`, `transTime`, `confirmTime`, `reverseTime` in Unix **milliseconds**.
- [ ] `errorCode` serialized as a **string**.
- [ ] `data` values wrapped as `{"key": {"value": "..."}}`.
- [ ] Business errors use HTTP 400 with `status: "FAILED"`; success uses HTTP 200.

## State machine and idempotency
- [ ] `/check` creates nothing and returns `OK` or the right error (`10006`, `10007`, `10008`, `10009`).
- [ ] `/create` persists a row keyed by `transId` (unique constraint) and returns `CREATED` + `transTime`.
- [ ] Repeated `/create` with the same `transId` -> `10010`; amount outside limits -> `10012` / `10013`.
- [ ] Amount mismatch with the order -> `10011`.
- [ ] `/confirm` is atomic (row lock / transaction), marks paid once, returns `CONFIRMED` + `confirmTime`.
- [ ] Repeated `/confirm` -> `10016`; confirm after reverse -> `10015`; repeated `/reverse` -> `10018`.
- [ ] Unknown `transId` on confirm / reverse / status -> `10014`.
- [ ] `/reverse` handles `CREATED` and (policy) `CONFIRMED`; repeated reverse -> `10018`.
- [ ] `/status` returns the stored state with matching times, including a confirm whose HTTP response was lost.
- [ ] Transactions left `CREATED` for 30+ minutes are expired on your side.
- [ ] Confirm-only fields (`paymentSource`, `phone`, `tariff`, `processingReferenceNumber`, `cardType`) are stored.

## App deeplink (if checkout sends payers to the Uzum Bank app)
- [ ] Link built from config: `https://uzumbank.uz/open-service?serviceId=<id>&<param_key>=<order>&amount=<tiyin>`.
- [ ] `<param_key>` equals the `params` key `/check` reads; order number URL-encoded.
- [ ] `amount` in tiyin, equal to the amount `/check` and `/create` will accept.
- [ ] Live and test `serviceId` are separate config values; the link uses the same one the webhooks validate.

## Operations
- [ ] Every call is logged with `transId` and outcome, without secrets.
- [ ] A test covers each endpoint, each error code you emit, and the confirm-retry path.
