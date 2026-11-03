#!/usr/bin/env python3
"""Compute or verify the signatures and auth headers of Uzbek payment providers.

Deterministic, python3 standard library only. The same file is copied into every
skills/<provider>/scripts/ by `scripts/lint --fix`; edit scripts/shared/sign.py. A copy
inside a skill lists only that provider's schemes.

  sign.py --list                          schemes, the fields they need, the secret variable
  sign.py SCHEME [PAYLOAD] [-f k=v ...]   compute; verifies too when PAYLOAD carries the sign
  sign.py SCHEME ... --expect VALUE       verify a received signature or header
  sign.py --selftest                      check the implementation against fixed vectors

PAYLOAD is a file or '-' (stdin): JSON or form-urlencoded, except alif.webhook, which signs
the raw body bytes. `-f key=value` adds or overrides a field. The secret is read from the
environment variable the scheme names (override with --secret-env), never from argv, so it
stays out of shell history. Output masks the secret; Basic headers print only with --reveal.
Exit status: 0 computed or matched, 1 mismatch, 2 usage error.
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.parse

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASK = "<SECRET>"


def hexdigest(algo, text):
    return hashlib.new(algo, text.encode("utf-8")).hexdigest()


def concat(f, keys, secret_at):
    """Concatenate raw field values, the secret inserted before keys[secret_at]."""
    parts = [str(f[k]) for k in keys]
    return parts[:secret_at], parts[secret_at:]


def click_shop(f, secret, complete):
    keys = ["click_trans_id", "service_id", "merchant_trans_id"]
    keys += ["merchant_prepare_id"] if complete else []
    keys += ["amount", "action", "sign_time"]
    head, tail = concat(f, keys, 2)
    return "".join(head + [secret] + tail), "md5", "sign_string", head, tail


def click_advanced(f, secret):
    params = f.get("params") or {}
    if not isinstance(params, dict):
        raise ValueError("params must be the JSON object from the request body")
    head = [str(f["click_paydoc_id"]), str(f["attempt_trans_id"]), str(f["service_id"])]
    tail = [raw(v) for v in params.values()] + [str(f["action"]), str(f["sign_time"])]
    return "".join(head + [secret] + tail), "md5", "sign_string", head, tail


def raw(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def ts_header(f, secret, user_key, millis):
    ts = str(f.get("timestamp") or int(time.time() * (1000 if millis else 1)))
    digits = len(ts)
    if millis and digits != 13 or not millis and digits != 10:
        print("warning: timestamp %s has %d digits; this scheme wants %s" %
              (ts, digits, "milliseconds (13)" if millis else "seconds (10)"), file=sys.stderr)
    digest = hexdigest("sha1", ts + secret)
    return "%s:%s:%s" % (f[user_key], digest, ts), ts + MASK


def basic(user, secret):
    return "Basic " + base64.b64encode(("%s:%s" % (user, secret)).encode()).decode()


# scheme -> provider, summary, fields, default secret variable
SCHEMES = {
    "alif.webhook": ("alif", "Signature header = base64(HMAC-SHA256(secret, raw body))",
                     "PAYLOAD = raw body bytes", "ALIF_WEBHOOK_SECRET"),
    "click.prepare": ("click", "SHOP API Prepare sign_string = md5(...)",
                      "click_trans_id service_id merchant_trans_id amount action sign_time",
                      "CLICK_SECRET_KEY"),
    "click.complete": ("click", "SHOP API Complete sign_string = md5(...)",
                       "click_trans_id service_id merchant_trans_id merchant_prepare_id amount "
                       "action sign_time", "CLICK_SECRET_KEY"),
    "click.advanced": ("click", "Advanced / Split Shop sign_string = md5(..., params values in "
                       "body order, ...)", "click_paydoc_id attempt_trans_id service_id params "
                       "action sign_time", "CLICK_SECRET_KEY"),
    "click.auth": ("click", "Merchant API Auth: merchant_user_id:sha1(ts+secret):ts, ts in seconds",
                   "merchant_user_id [timestamp]", "CLICK_SECRET_KEY"),
    "multicard.callback": ("multicard", "success callback sign = md5(store_id invoice_id amount secret)",
                           "store_id invoice_id amount", "MULTICARD_SECRET"),
    "multicard.webhook": ("multicard", "status webhook sign: md5(uuid amount secret) or "
                          "sha1(uuid invoice_id amount secret); reports which one matched",
                          "uuid amount [invoice_id]", "MULTICARD_SECRET"),
    "uzum.fastpay": ("uzum", "FastPay / Dynamic QR Authorization: user:sha1(ts+secret):ts, ts in ms",
                     "merchant_service_user_id [timestamp]", "UZUM_SECRET_KEY"),
    "uzum.basic": ("uzum", "Merchant API webhooks, CrossBorder, PaymentHub: Basic login:password",
                   "login", "UZUM_PASSWORD"),
    "payme.basic": ("payme", "Merchant API: Authorization: Basic base64(login:CASHBOX_KEY)",
                    "login", "PAYME_KEY"),
    "payme.xauth": ("payme", "Subscribe API X-Auth: CASHBOX_ID (front end) or CASHBOX_ID:KEY "
                    "(back end, add --backend)", "cashbox_id", "PAYME_KEY"),
    "payme.checkout": ("payme", "checkout GET URL = host/ + base64(m=..;ac.<field>=..;a=..;l=..)",
                       "m a ac.<field>... [l] [c] [host]", None),
    "paynet.basic": ("paynet", "Authorization: Basic base64(service_id:secret_key)",
                     "service_id", "PAYNET_SECRET_KEY"),
}


def compute(scheme, f, secret, body, backend=False):
    """Return (value, masked canonical string, field that carries the sign or None)."""
    if scheme == "alif.webhook":
        sig = base64.b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).decode()
        return sig, "HMAC-SHA256 over %d raw body bytes" % len(body), None
    if scheme in ("click.prepare", "click.complete", "click.advanced"):
        if scheme == "click.advanced":
            text, algo, field, head, tail = click_advanced(f, secret)
        else:
            text, algo, field, head, tail = click_shop(f, secret, scheme == "click.complete")
        return hexdigest(algo, text), "".join(head + [MASK] + tail), field
    if scheme == "click.auth":
        value, shown = ts_header(f, secret, "merchant_user_id", millis=False)
        return value, "sha1(%s)" % shown, None
    if scheme == "uzum.fastpay":
        value, shown = ts_header(f, secret, "merchant_service_user_id", millis=True)
        return value, "sha1(%s)" % shown, None
    if scheme == "multicard.callback":
        head = "%s%s%s" % (f["store_id"], f["invoice_id"], f["amount"])
        return hexdigest("md5", head + secret), "md5(%s%s)" % (head, MASK), "sign"
    if scheme in ("uzum.basic", "payme.basic", "paynet.basic"):
        user = f["service_id" if scheme == "paynet.basic" else "login"]
        return basic(user, secret), "base64(%s:%s)" % (user, MASK), None
    if scheme == "payme.xauth":
        value = "%s:%s" % (f["cashbox_id"], secret) if backend else str(f["cashbox_id"])
        return value, value.replace(secret, MASK) if backend else value, None
    if scheme == "payme.checkout":
        host = f.pop("host", "https://checkout.paycom.uz").rstrip("/")
        order = ["m"] + sorted(k for k in f if k.startswith("ac.")) + ["a", "l", "c", "ct", "cr"]
        pairs = ";".join("%s=%s" % (k, f[k]) for k in order if k in f)
        return host + "/" + base64.b64encode(pairs.encode()).decode(), pairs, None
    raise KeyError(scheme)


def multicard_webhook(f, secret, got):
    """The status webhook rule conflicts in the docs; try both and say which matched."""
    variants = [("md5", "%s%s" % (f["uuid"], f["amount"]))]
    if "invoice_id" in f:
        variants.append(("sha1", "%s%s%s" % (f["uuid"], f["invoice_id"], f["amount"])))
    rows = []
    for algo, head in variants:
        value = hexdigest(algo, head + secret)
        rows.append((value, "%s(%s%s)" % (algo, head, MASK), bool(got) and hmac.compare_digest(value, got)))
    return rows


def load_fields(payload, scheme):
    if payload is None:
        return {}, b""
    body = sys.stdin.buffer.read() if payload == "-" else open(payload, "rb").read()
    if scheme == "alif.webhook":
        return {}, body
    text = body.decode("utf-8").strip()
    if text.startswith("{"):
        # keep numbers as their original text: signatures hash the raw values
        return json.loads(text, parse_int=str, parse_float=str), body
    return dict(urllib.parse.parse_qsl(text, keep_blank_values=True)), body


def provider():
    name = os.path.basename(SKILL_DIR)
    return name if any(p == name for p, _, _, _ in SCHEMES.values()) else None


def run(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scheme", nargs="?")
    ap.add_argument("payload", nargs="?")
    ap.add_argument("-f", "--field", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--expect", help="received signature or header value to verify")
    ap.add_argument("--secret-env", help="environment variable that holds the secret")
    ap.add_argument("--backend", action="store_true", help="payme.xauth: CASHBOX_ID:KEY form")
    ap.add_argument("--reveal", action="store_true", help="print Basic / X-Auth values unmasked")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    mine = provider()
    names = [s for s, row in SCHEMES.items() if mine in (None, row[0])]
    if a.selftest:
        return selftest(names)
    if a.list or not a.scheme:
        for s in names:
            _, summary, fields, env = SCHEMES[s]
            print("%-19s %s\n%19s fields: %s; secret: %s" % (s, summary, "", fields, env or "none"))
        return 0 if a.list else 2
    if a.scheme not in SCHEMES:
        print("sign.py: unknown scheme %r; run --list" % a.scheme, file=sys.stderr)
        return 2
    env = a.secret_env or SCHEMES[a.scheme][3]
    secret = os.environ.get(env, "") if env else ""
    if env and not secret and not (a.scheme == "payme.xauth" and not a.backend):
        print("sign.py: set %s (export it, or use a .env loader); the secret is never "
              "taken from argv" % env, file=sys.stderr)
        return 2
    try:
        f, body = load_fields(a.payload, a.scheme)
    except (OSError, ValueError) as e:
        print("sign.py: cannot read %s: %s" % (a.payload, e), file=sys.stderr)
        return 2
    for kv in a.field:
        k, _, v = kv.partition("=")
        f[k] = v
    try:
        if a.scheme == "multicard.webhook":
            got = (a.expect or str(f.get("sign", ""))).lower()
            rows = multicard_webhook(f, secret, got)
            for value, shown, ok in rows:
                print("%s  %s%s" % (value, shown, "  MATCH" if ok else ""))
            if got:
                print("MATCH" if any(r[2] for r in rows) else "MISMATCH against %s" % got)
                return 0 if any(r[2] for r in rows) else 1
            return 0
        value, shown, sign_field = compute(a.scheme, f, secret, body, a.backend)
    except KeyError as e:
        print("sign.py: missing field %s for %s; fields: %s" % (e, a.scheme, SCHEMES[a.scheme][2]),
              file=sys.stderr)
        return 2
    except ValueError as e:
        print("sign.py: %s" % e, file=sys.stderr)
        return 2
    hide = secret and secret in value or a.scheme.endswith(".basic")
    print("input   %s" % shown)
    print("value   %s" % ("<hidden: contains the secret, add --reveal>" if hide and not a.reveal
                          else value))
    got = a.expect if a.expect is not None else f.get(sign_field) if sign_field else None
    if got is None:
        return 0
    if a.scheme.endswith(".basic") and got.lower().startswith("authorization:"):
        got = got.split(":", 1)[1].strip()
    ok = hmac.compare_digest(value.lower(), str(got).strip().lower()) if a.scheme != "alif.webhook" \
        else hmac.compare_digest(value, str(got).strip())
    print("MATCH" if ok else "MISMATCH, received %s" % ("<hidden>" if hide and not a.reveal else got))
    return 0 if ok else 1


# Fixed regression vectors; each expected value was computed independently with
# `printf %s ... | openssl dgst -md5|-sha1` or `openssl dgst -sha256 -hmac ... -binary | base64`.
VECTORS = [
    ("alif.webhook", {}, b'{"id":"inv-1","status":"paid"}', "whsec_test",
     "bYZrEbZNMdfrQ9KbCwBXR4TfGQiRn4/zT2v/jV9QsJk="),
    ("click.prepare", {"click_trans_id": "2032049", "service_id": "100", "merchant_trans_id": "A-1",
                       "amount": "1000.00", "action": "0", "sign_time": "2026-11-03 10:00:00"},
     b"", "click_test", "9ea42e2cf92f86eb543affb2831ab65a"),
    ("click.complete", {"click_trans_id": "2032049", "service_id": "100", "merchant_trans_id": "A-1",
                        "merchant_prepare_id": "7", "amount": "1000.00", "action": "1",
                        "sign_time": "2026-11-03 10:00:05"},
     b"", "click_test", "85c3d2f31dcf6256a6f119b2ec3cce3c"),
    ("click.advanced", {"click_paydoc_id": "5200001", "attempt_trans_id": "6300001",
                        "service_id": "100", "params": {"amount": "25000", "account": "77"},
                        "action": "1", "sign_time": "2026-11-03 10:00:00"},
     b"", "click_test", "966663a8c6c06913d196fdc056049f0b"),
    ("click.auth", {"merchant_user_id": "12345", "timestamp": "1762146000"}, b"", "click_test",
     "12345:33c6f9de029dd6018c0763d27de4d0de95b17239:1762146000"),
    ("multicard.callback", {"store_id": "6", "invoice_id": "A-1", "amount": "500000"}, b"",
     "mc_test", "240f92395c47226ae7ad17770e2e61bd"),
    ("uzum.fastpay", {"merchant_service_user_id": "u-1", "timestamp": "1762146000000"}, b"",
     "uz_test", "u-1:598249f27311ea11eeacd69ba5698e4f2cfe1ab3:1762146000000"),
    ("payme.basic", {"login": "Paycom"}, b"", "payme_test", "Basic UGF5Y29tOnBheW1lX3Rlc3Q="),
    ("paynet.basic", {"service_id": "101"}, b"", "paynet_test", "Basic MTAxOnBheW5ldF90ZXN0"),
    ("uzum.basic", {"login": "merchant"}, b"", "uz_pass", "Basic bWVyY2hhbnQ6dXpfcGFzcw=="),
    ("payme.xauth", {"cashbox_id": "5e730e8e0b852a417aa49ceb"}, b"", "", "5e730e8e0b852a417aa49ceb"),
    ("payme.checkout", {"m": "5e730e8e0b852a417aa49ceb", "ac.order_id": "100001", "a": "500000",
                        "l": "ru"}, b"", "",
     "https://checkout.paycom.uz/bT01ZTczMGU4ZTBiODUyYTQxN2FhNDljZWI7YWMub3JkZXJfaWQ9MTAwMDAxO2E9NTAwMDAwO2w9cnU="),
]


def selftest(names):
    failed = 0
    for scheme, fields, body, secret, want in VECTORS:
        if scheme not in names:
            continue
        got, _, _ = compute(scheme, dict(fields), secret, body)
        ok = got == want
        failed += not ok
        print("%s %s" % ("ok  " if ok else "FAIL", scheme) + ("" if ok else "\n  want %s\n  got  %s" % (want, got)))
    if "multicard.webhook" in names:
        f = {"uuid": "u-1", "invoice_id": "A-1", "amount": "500000"}
        rows = multicard_webhook(f, "mc_test", hexdigest("sha1", "u-1A-1500000mc_test"))
        ok = [r[2] for r in rows] == [False, True]
        failed += not ok
        print("%s multicard.webhook" % ("ok  " if ok else "FAIL"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
