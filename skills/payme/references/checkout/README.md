# Payme Checkout (hosted payment page: GET link, POST form, button, QR)

Hand-written notes. Transport, auth, errors and the sandbox:
[`../common/README.md`](../common/README.md). Schemas: [`schemas/`](schemas/). Examples:
[`examples/`](examples/).

- Source: https://developer.help.paycom.uz/initsializatsiya-platezhey/ and its subpages
  `otpravka-cheka-po-metodu-get/`, `otpravka-cheka-po-metodu-post/`,
  `generatsiya-knopki-oplaty-i-qr-koda/`, `oshibki-otpravki-cheka/` (Russian pages)
- Fetched: 2026-11-03
- Direction: **you send the payer to Payme.** The payment itself then runs through the
  Merchant API methods you implement ([`../merchant/`](../merchant/README.md)).

## Flow

```
your site builds a "receipt" (GET URL or POST form)
   └─> payer opens checkout.paycom.uz ─> Payme calls your Endpoint URL:
          CheckPerformTransaction ─> CreateTransaction ─> PerformTransaction
   └─> payer is sent back to `callback` / `c` after `callback_timeout` / `ct`
```

The return to your site is **not** a payment confirmation. Mark an order paid only from
`PerformTransaction` (state `2`).

## Hosts

| Environment | Checkout host |
|---|---|
| Production | `https://checkout.paycom.uz` |
| Sandbox | `https://test.paycom.uz` (the sandbox page lists it as the receipt URL) |

## GET link

`<checkout host>/` + base64 of `key=value` pairs joined with `;`.

| Param | Meaning |
|---|---|
| `m` | cashbox (merchant) id or alias |
| `ac.<field>` | one per Account field, e.g. `ac.order_id=100001` |
| `a` | amount, tiyin |
| `l` | language: `ru`, `uz`, `en` |
| `c` | return URL after payment or cancel |
| `ct` | ms to wait after a successful payment before returning to `c` |
| `cr` | currency code, ISO format |

```python
import base64
params = "m=<CASHBOX_ID>;ac.order_id=100001;a=500000;l=ru"
url = "https://checkout.paycom.uz/" + base64.b64encode(params.encode()).decode()
```

The GET format has no `detail` parameter. Use the POST form, or return `detail` from
`CheckPerformTransaction`, when fiscal items are needed.

## POST form

`<form method="POST" action="https://checkout.paycom.uz">` (sandbox:
`https://test.paycom.uz`), all fields as hidden inputs.

| Field (`*` required) | Meaning |
|---|---|
| `merchant*` | cashbox id |
| `amount*` | amount, tiyin |
| `account[<field>]*` | one input per Account field |
| `lang` | `ru` (default), `uz`, `en`; other values are ignored |
| `callback` | return URL; defaults to the `Referer`. Placeholders: `:transaction` (Payme transaction id, or `null` if creation failed) and `:account.<field>` |
| `callback_timeout` | ms after a successful payment before redirecting to `callback` |
| `description` | text; or one `description[ru]`, `description[uz]`, `description[en]` per language |
| `detail` | **base64** of the detail JSON (items, shipping); see [`../fiscalization/`](../fiscalization/README.md) |

## Button and QR code

- Load `https://cdn.paycom.uz/integration/js/checkout.min.js` and build the same POST form.
- `Paycom.Button(form_selector, container_selector)` renders a pay button; add
  `<input type="hidden" name="button" data-type="svg|png" value="colored|white" data-width="200px">`.
- `Paycom.QR(form_selector, container_selector)` renders a QR code; add
  `<input type="hidden" name="qr" data-width="250">`.
- Selectors may be CSS selectors, jQuery objects or DOM nodes.

## Errors shown by checkout

| Code | Meaning |
|---|---|
| `-31601` | merchant not found or blocked |
| `-31610` | invalid field value |
| `-31611` | amount below the minimum |
| `-31612` | amount above the maximum |
| `-31622` | merchant service unavailable (typically: your Endpoint URL did not answer) |
| `-31623` | merchant service misbehaves (typically: invalid Merchant API responses) |
| `-31630` | card problem: insufficient funds, wrong number or expiry, expired or blocked card, or a corporate card |

## Gotchas

- `amount` / `a` are tiyin. A wrong unit shows as `-31611` / `-31612` or as `-31001` from
  your own `CheckPerformTransaction`.
- `account[...]` keys must match the Account fields configured in the cashbox, or your
  Merchant API sees an empty `account`.
- `detail` in the form is base64 of JSON, not raw JSON.
- The POST "data types" table marks `items` optional, but every item field except
  `discount` and `units` is required, and fiscalization needs items. Always send items.
- `callback_timeout` is in ms, yet the form comment says its default is `15`. Set it
  explicitly.
- `-31622` / `-31623` mean Payme could not use your Merchant API. Check the Endpoint URL,
  Basic auth and TLS first.

## Examples

[`examples/`](examples/): `checkout-post.form.json` (form fields as name/value pairs) and
`checkout-get.params.json` (decoded params string and the resulting URL shape).
