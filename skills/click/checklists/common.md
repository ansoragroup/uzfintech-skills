# Checklist: Click credentials, auth, units and errors (applies to every product)

Contract: [`../references/common/README.md`](../references/common/README.md). Mark each item
pass / fail / n.a. and cite the file and line that proves it.

## Credentials
- [ ] `secret_key` comes from a secret store, never from code, client bundles or logs.
- [ ] `merchant_id`, `service_id` and `merchant_user_id` are configuration, kept apart per
  service when the merchant has several.
- [ ] Test and production values are separate, and switching between them is a config change.

## Units
- [ ] Money is stored as integer tiyin and converted to soums only at the Click edge.
- [ ] Soum amounts (SHOP API, Merchant API, CLICK Pass, payment link) are never compared as
  floats; they are parsed into tiyin first.
- [ ] Fiscalization amounts are sent as integer tiyin, not soums.

## Inbound signature (SHOP API, Advanced / Split Shop)
- [ ] `sign_string` is recomputed from the **raw** received values, in the documented order,
  with `SECRET_KEY` in its place.
- [ ] The comparison is constant-time.
- [ ] A mismatch returns `error: -1` and changes no state.

## Outbound auth (Merchant API family)
- [ ] `Auth` is `merchant_user_id:sha1(timestamp + secret_key):timestamp`, lowercase hex.
- [ ] `timestamp` is Unix **seconds** (10 digits), fresh per request; the server clock is synced.
- [ ] `Accept` and `Content-Type` are sent on every call, including `card_token/request`.

## Errors
- [ ] Merchant API calls check the HTTP status **and** `error_code`; only `0` counts as success.
- [ ] `error_note` is logged; code never branches on its text.
- [ ] Inbound handlers answer with `error` (not `error_code`) as a JSON number, HTTP 200.
- [ ] After a timeout on a money-moving call, the state is read back (`payment/status`) before
  any retry.
