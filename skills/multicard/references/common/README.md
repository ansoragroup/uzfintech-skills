# Multicard API: transport, auth, errors, callbacks, fiscal items, sandbox

Hand-written notes. Applies to every Multicard product in this skill. Schemas:
[`schemas/`](schemas/) (shared models). Examples: [`examples/`](examples/).

- Source: https://docs.multicard.uz/llms.txt (index), https://docs.multicard.uz/4736405f0
  (intro), https://docs.multicard.uz/4488543f0 and https://docs.multicard.uz/19729295e0
  (auth), https://docs.multicard.uz/19729300e0 (success callback),
  https://docs.multicard.uz/19729301e0 (webhooks), model pages
  https://docs.multicard.uz/9357883d0 (payment), https://docs.multicard.uz/9355028d0 (ofd),
  https://docs.multicard.uz/9355022d0 (split), https://docs.multicard.uz/9655483d0 (store),
  https://docs.multicard.uz/9655813d0 (tax receipt) (Russian pages; each page also has a
  `.md` twin that `scripts/sync` tracks)
- Fetched: 2026-11-03
- Spec: each `.md` page embeds a one-path OpenAPI 3.0.1 fragment; there is no combined
  OpenAPI file and no `llms-full.txt`.

## Transport

| Item | Value |
|---|---|
| Base URL | production `https://mesh.multicard.uz/`, sandbox `https://dev-mesh.multicard.uz/` |
| Format | JSON request and response bodies |
| Auth | `Authorization: Bearer <JWT>` on every call except `POST /auth` |
| Amounts | integer **tiyin** (1 UZS = 100 tiyin) |
| Times | `Y-m-d H:i:s` strings in **GMT+5** (Tashkent), no zone suffix |
| Ids | Multicard objects use a 36-char `uuid`; `store_id` is your cashbox id (an integer; some endpoints also take the cashbox uuid) |
| Your order id | `invoice_id`, string up to 255 chars; it comes back as `store_invoice_id` |

## Auth

`POST /auth {application_id*, secret*}` returns `{token, role, expiry}` (schema:
[`schemas/auth.json`](schemas/auth.json)).

- The token lives **24 hours**; `expiry` is the expiry time (GMT+5). After it, every call
  answers HTTP `401`.
- Cache the token for its lifetime. The vendor asks you not to request a token per call.
  Refresh shortly before `expiry`, and once more on a `401` (derived).
- This response is **not** wrapped in `{success, data}`. A `400` from `/auth` uses another
  shape: `{"errors": [{"message": [{"message", "field"}]}]}`.
- `application_id` and `secret` are issued by Multicard. Keep `secret` on the server; it
  also signs callbacks.

## Envelope

Every endpoint except `/auth` answers:

- success: `{"success": true, "data": <payload>}`;
- error: `{"success": false, "error": {"code": "<ERROR_CODE>", "details": "<text>"}}`
  ([`schemas/error.json`](schemas/error.json)).

In this skill, each schema's `result` is the content of `data`. Path parameters are under
`path`, query parameters under `query`. The intro page's error example is not valid JSON;
the shape above is the one the endpoint pages use.

## Error codes

The docs have no central list. These codes appear in the endpoint pages:

| Code | HTTP | Meaning | Action (derived) |
|---|---|---|---|
| `ERROR_FIELDS` | 400 | validation failed; also "already confirmed" and "identification required" (payouts) | fix the request; do not retry as is |
| `ERROR_CARD_NOT_FOUND` | 400 | wrong card number or expiry | ask the payer to re-enter |
| `ERROR_WRONG_OTP` | 400 | wrong SMS code | let the payer retry |
| (OTP expired) | 423 | SMS code expired | restart the step that sent the SMS |
| (SMS already sent) | 429 | a code was sent recently | wait, then resend |
| `ERROR_DEBIT_UNKNOWN` | 400 | debit outcome unknown | **poll** `GET /payment/{uuid}` until final |
| `ERROR_CALLBACK_TIMEOUT` | 400 | your billing callback timed out | **poll** until final |
| `ERROR_UNKNOWN` | 400 | payouts: outcome unknown | **poll** `GET /payment/credit/{uuid}` |
| `ERROR_TRANS_NOT_READY` | 400 | invoice expired | create a new invoice |
| `ERROR_NOT_FOUND` | 404 | object not found; the refund page also uses it for a payment that can no longer be cancelled | read the object, then decide |
| `ERROR_PAYMENT_APPLIED` | 403 | hold no longer active (cancel hold) | read the hold state |
| `ERROR_ACCESS_DENIED` | 403 | registry for another store | check `store_id` |
| (no code) | 401 | token missing or expired | get a new token, retry once |

Several pages describe `423`, `429` and `403` cases in the text as "400"; branch on the
HTTP status and on `error.code` together. On a timeout or HTTP 5xx from a money-moving call
(confirm, scanpay, charge hold, payout), poll the object; never resend the request blindly.

## Payment statuses

| Status | Meaning | Final |
|---|---|---|
| `draft` | created, not confirmed | no |
| `progress` | confirmed, executing | no |
| `billing` | authorized; Multicard is calling your billing | no |
| `hold` | funds blocked on the card | no |
| `success` | paid | yes |
| `error` | debit failed, or your billing refused | yes |
| `revert` | refunded to the card | yes |

The full payment object is [`schemas/payment.json`](schemas/payment.json). `otp_hash` not
`null` means the payment still needs an OTP (or the hosted `checkout_url`).
`commission_type`: `up` = commission added on top and paid by the payer, `down` = paid by
the merchant; `total_amount` is what the card is charged.

## Success callback (your `callback_url`)

After a successful debit Multicard `POST`s to the `callback_url` from the invoice or payment
request. Schema: [`../invoice/schemas/callback-success.json`](../invoice/schemas/callback-success.json).

- Verify `sign` = md5 hex of the string `{store_id}{invoice_id}{amount}{secret}` (no
  separators), or accept the callback only from the single source IP listed on
  https://docs.multicard.uz/19729300e0. Checking the sign is the safer choice (derived).
- Check that `invoice_id` and `amount` match your order before you accept.
- Answer **HTTP 200** with `{"success": true}`. Any other status, or `success` not `true`,
  **cancels the payment and refunds the payer**. `{"success": false, "message": "..."}`
  shows `message` on the payer's receipt page.
- On a timeout or HTTP 500 the funds stay blocked and the callback may be repeated. A repeat
  for the same `uuid` must get the same success answer (idempotency).

## Status webhooks (optional)

Multicard can configure your merchant to `POST` on every status change (`draft`, `progress`,
`success`, `error`, `revert`; the schema also lists `hold`). Schema:
[`../invoice/schemas/webhook-status.json`](../invoice/schemas/webhook-status.json).

- Answer any `2xx`; otherwise the request is repeated 5 times.
- The sign rule conflicts on the same page: the text says md5 of `{uuid}{amount}{secret}`,
  the field schema says SHA1 of `{uuid}{invoice_id}{amount}{secret}`. Accept a webhook only
  if one known rule matches, log which one, and confirm with Multicard; or re-read the
  payment with `GET /payment/{uuid}` before acting.

```python
import hashlib, hmac

def _hex(algo, s):
    return hashlib.new(algo, s.encode()).hexdigest()

def callback_ok(b, secret):
    want = _hex("md5", f"{b['store_id']}{b['invoice_id']}{b['amount']}{secret}")
    return hmac.compare_digest(want, str(b.get("sign", "")).lower())

def webhook_ok(b, secret):
    got = str(b.get("sign", "")).lower()
    for algo, s in (("md5", f"{b['uuid']}{b['amount']}{secret}"),
                    ("sha1", f"{b['uuid']}{b['invoice_id']}{b['amount']}{secret}")):
        if hmac.compare_digest(_hex(algo, s), got):
            return True
    return False
```

The card-bind callback is **not signed**; see [`../cards/`](../cards/README.md).

## Fiscal items (`ofd`)

`ofd` is required when you create an invoice and accepted on payments and refunds. Schema:
[`schemas/ofd.json`](schemas/ofd.json).

| Field (`*` required) | Meaning |
|---|---|
| `qty*` | integer quantity |
| `price*` | **unit** price, tiyin |
| `total*` | `qty x price` before discounts, tiyin |
| `mxik*` | IKPU code from tasnif.soliq.uz |
| `package_code*` | package code for that IKPU |
| `name*` | item name |
| `vat` | VAT percent, integer |
| `tin` | company TIN |
| `mark` | array of marking codes, one per unit; required for marked goods |

- Fiscalization mode is a cashbox setting, `tax_registration` on the store
  ([`../reports/`](../reports/README.md)): `0` off, `1` on, `2` only the on-top commission,
  `3` only the merchant-paid commission. The store may carry a default `tax_mxik` and
  `tax_package_code`.
- When Multicard fiscalizes, the receipt is in `tax` (refund: `refund_tax`) with `qr_url`.
- When **you** fiscalize, send the receipt link with `PATCH /payment/{uuid}/fiscal`
  ([`../payments/`](../payments/README.md)).
- The vendor `ofd` examples have `total` values that are not `qty x price`; follow the field
  definition.

## Split (`split`)

Array of `{type*, amount*, details*, recipient}` ([`schemas/split.json`](schemas/split.json)):
`account` = a bank account by requisites uuid (`recipient`; default: your own), `wallet` =
your partner wallet, `card` = a card. The sum of `amount` must not exceed the payment
amount minus the commission. Read requisites with `GET /payment/merchant-account/{recipient}`.

## Sandbox

- Host `https://dev-mesh.multicard.uz/`. Credentials come from Multicard.
- The test card, the sandbox OTP `111111`, credential steps and test runs are in
  [`../sandbox/README.md`](../sandbox/README.md). Keep them out of production code paths.
- `short_link` on invoices is production only.
