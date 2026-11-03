# Checklist: Payme Checkout

Contract: [`../references/checkout/README.md`](../references/checkout/README.md). Also run
[`common.md`](common.md) and [`merchant.md`](merchant.md).

## Building the receipt
- [ ] GET: the path is base64 of `m=...;ac.<field>=...;a=...` with optional `l`, `c`, `ct`, `cr`, joined with `;`.
- [ ] Values containing `;` or `=` (for example a return URL with a query string) are avoided or tested: the docs define no escaping.
- [ ] POST: hidden fields `merchant`, `amount` (tiyin) and one `account[<field>]` per cashbox Account field; optional `lang`, `callback`, `callback_timeout`, `description`, `detail`.
- [ ] `account` field names match the cashbox settings exactly.
- [ ] `detail` (POST only) is base64 of the JSON string and its items add up to `amount`.
- [ ] `callback_timeout` is set explicitly, in ms.
- [ ] The host comes from configuration: `https://checkout.paycom.uz` in production, `https://test.paycom.uz` in tests.

## After the payer returns
- [ ] The `callback` / `c` return never marks an order paid; only `PerformTransaction` does.
- [ ] `:transaction` in the callback may be `null`; the page handles that case.

## Button and QR
- [ ] `checkout.min.js` is loaded from `https://cdn.paycom.uz/integration/js/` and `Paycom.Button` / `Paycom.QR` target the same POST form.

## Errors
- [ ] `-31622` / `-31623` reports trigger a check of the Endpoint URL, Basic auth and TLS.
