# Tools

**English** · [Русский](Tools.ru.md) · [Oʻzbekcha](Tools.uz.md) · [简体中文](Tools.zh-CN.md)

Every skill ships two scripts in `skills/<provider>/scripts/`. They need `python3` 3.9+ and
nothing else. A model that computes an MD5 or a base64 header in its head gets it wrong often
enough to matter; these scripts get it right every time, and they show their work.

| Script | Answers | Output |
|---|---|---|
| `sign.py` | "Is this signature or auth header right? What should it be?" | the exact signed string with the secret masked, the value, `MATCH` / `MISMATCH` |
| `validate.py` | "Does this body match the contract?" | `OK` or `INVALID` with JSON paths |

Both exit `0` on success, `1` on a mismatch or an invalid body, and `2` on a usage error.

## sign.py

```
sign.py --list                          schemes, the fields they need, the secret variable
sign.py SCHEME [PAYLOAD] [-f k=v ...]   compute; verifies too when PAYLOAD carries the sign
sign.py SCHEME ... --expect VALUE       verify a received signature or header
sign.py --selftest                      check the implementation against fixed vectors
```

`PAYLOAD` is a file or `-` for stdin, JSON or form-urlencoded. `alif.webhook` signs the raw
body bytes instead. `-f key=value` adds or overrides a field. The copy inside a skill lists
only that provider's schemes.

### Schemes

| Scheme | What it computes | Secret variable |
|---|---|---|
| `alif.webhook` | `Signature` header = base64(HMAC-SHA256(secret, raw body)) | `ALIF_WEBHOOK_SECRET` |
| `click.prepare` | SHOP API Prepare `sign_string` (MD5) | `CLICK_SECRET_KEY` |
| `click.complete` | SHOP API Complete `sign_string` (MD5) | `CLICK_SECRET_KEY` |
| `click.advanced` | Advanced / Split Shop `sign_string`, `params` values in body order | `CLICK_SECRET_KEY` |
| `click.auth` | Merchant API `Auth` header: `merchant_user_id:sha1(ts+secret):ts`, seconds | `CLICK_SECRET_KEY` |
| `multicard.callback` | success callback `sign` = md5(store_id invoice_id amount secret) | `MULTICARD_SECRET` |
| `multicard.webhook` | status webhook `sign`; tries the MD5 and SHA1 forms and says which matched | `MULTICARD_SECRET` |
| `payme.basic` | Merchant API `Authorization: Basic base64(login:KEY)` | `PAYME_KEY` |
| `payme.xauth` | Subscribe API `X-Auth`: `CASHBOX_ID`, or `CASHBOX_ID:KEY` with `--backend` | `PAYME_KEY` |
| `payme.checkout` | checkout GET URL = host + base64(`m=..;ac.<field>=..;a=..;l=..`) | none |
| `paynet.basic` | `Authorization: Basic base64(service_id:secret_key)` | `PAYNET_SECRET_KEY` |
| `uzum.fastpay` | FastPay / Dynamic QR `Authorization`: `user:sha1(ts+secret):ts`, milliseconds | `UZUM_SECRET_KEY` |
| `uzum.basic` | Merchant API webhooks, CrossBorder, PaymentHub: Basic `login:password` | `UZUM_PASSWORD` |

### Secrets

The secret comes only from the environment variable in the table (or the one you name with
`--secret-env`), never from an argument, so it stays out of shell history and agent logs.
Output prints it as `<SECRET>`. Values that contain the secret in clear text, such as a Basic
header, print only with `--reveal`.

### Examples

Find why Click rejects a Prepare request:

```console
$ CLICK_SECRET_KEY=test-secret python3 skills/click/scripts/sign.py click.prepare body.txt \
    --expect d7696dbc2b950daf03e1191fbea5fbb3
input   12345100<SECRET>100011000.002026-11-03 10:00:00
value   24d6c366acd79c05457ddf0547d6d65c
MISMATCH, received d7696dbc2b950daf03e1191fbea5fbb3
```

Click signed `amount=1000.00` as sent. The handler rebuilt it as `1000.0`. Sign the raw
values as received.

Build a Payme checkout link:

```console
$ python3 skills/payme/scripts/sign.py payme.checkout \
    -f m=5e730e8e0b852a417aa49ceb -f ac.order_id=10001 -f a=500000 -f l=uz
input   m=5e730e8e0b852a417aa49ceb;ac.order_id=10001;a=500000;l=uz
value   https://checkout.paycom.uz/bT01ZTczMGU4ZTBiODUyYTQxN2FhNDljZWI7YWMub3JkZXJfaWQ9MTAwMDE7YT01MDAwMDA7bD11eg==
```

`a` is in tiyin: `500000` is 5 000 sum.

Build the Click Merchant API `Auth` header:

```console
$ CLICK_SECRET_KEY=... python3 skills/click/scripts/sign.py click.auth \
    -f merchant_user_id=1 -f timestamp=1762160400
input   sha1(1762160400<SECRET>)
value   1:0df3d3bac209c59a2feefb9ad688c7e003f411c3:1762160400
```

Leave out `timestamp` to use the current time.

Check a Multicard status webhook when you are not sure which formula the store uses:

```console
$ MULTICARD_SECRET=... python3 skills/multicard/scripts/sign.py multicard.webhook \
    -f uuid=u-1 -f amount=500000 -f invoice_id=10001
30501c3fbfec8d8fa0a9451049a92fda  md5(u-1500000<SECRET>)
33faffb79880f2af5ca164b7ce5e890aa87a29a2  sha1(u-110001500000<SECRET>)
```

## validate.py

```
validate.py --list [TEXT]                 list schemas: name, method, endpoint
validate.py SCHEMA PAYLOAD [--part PART]  validate PAYLOAD (file, '-' = stdin)
```

`SCHEMA` is a schema name (`CreateTransaction`), `product/name` when a name exists in two
products (`merchant/CreateTransaction`), or a file path.

| Option | Use |
|---|---|
| `--part params` / `result` | JSON-RPC methods: the request params (default) or your result |
| `--part body` / `query` / `path` | hand-written REST schemas |
| `--part request` / `response` with `--status 400` | schemas generated from OpenAPI (`schemas/ops/*.json`) |

What it handles for you:

- A JSON-RPC envelope, with or without `"jsonrpc"`, and a `{success, data}` envelope are
  unwrapped. An error envelope passed as a result is reported as an error, not as valid.
- A form-urlencoded body (`a=1&b=2`) is accepted, and numeric strings are read as numbers
  where the schema says so, because every form value arrives as a string.
- Placeholders such as `"<CARD_TOKEN>"` match anything and are counted in the output.

```console
$ python3 skills/payme/scripts/validate.py CreateTransaction body.json
INVALID references/merchant/schemas/CreateTransaction.json (params): 1 problem(s)
  $.amount: expected integer, got string

$ python3 skills/uzum/scripts/validate.py --list crossborder/confirm
crossborder/confirmcredit                    POST /cbt/v1/transfer/confirm_credit Confirm Transfer to Uzbekistan
crossborder/confirmdebit                     POST /cbt/v1/transfer/confirm_debit Confirm Transfer from Uzbekistan
crossborder/confirmpayment                   POST /cbt/v1/payment/confirm_payment Confirm a Cross-border Payment
```

## In your CI

The scripts are deterministic, so you can run them on the fixtures in your own repository:

```sh
for f in tests/fixtures/payme/create-*.json; do
  python3 vendor/uzfintech-skills/skills/payme/scripts/validate.py CreateTransaction "$f" || exit 1
done
```

## For maintainers

The source of both scripts is `scripts/shared/`. `scripts/lint --fix` copies it into every
skill, and `scripts/lint --only tools` fails when a copy drifts, when `sign.py --selftest`
fails, or when `validate.py` crashes on any schema. Add a test vector to `sign.py` together
with every new scheme.
