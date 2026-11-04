#!/usr/bin/env python3
"""Build and summarize Tasnif (MXIK / IKPU) catalogue requests; optionally send one GET.

Standard library only (python3.9+). Nothing touches the network unless --online is given.

  tasnif.py search TEXT [--via elasticsearch|by-params|subposition] [--size N] [--page N]
  tasnif.py gtin BARCODE               barcode (GTIN) to code, mxik/search/by-params?gtin=
  tasnif.py code MXIK                  the card with package codes, mxik/get/by-mxik
  tasnif.py history MXIK               names, isActive, dates, package names
  tasnif.py info MXIK [--tin <TIN>] [--terminal-id <ID>]   cl-api point-of-sale reply
  tasnif.py classes GROUP              classes of a 3-digit group, class/short-info
  tasnif.py pictures MXIK              picture file names and their file URLs
  tasnif.py vat <TIN>                  txkm VAT-payer check
  tasnif.py COMMAND --file reply.json  summarize a saved reply (offline; any command)
  tasnif.py --selftest

Add --online to send the one GET. Exit codes: 0 found, 1 not found or invalid input,
2 usage error, network error or an unexpected reply (treat as unknown, retry later).

The endpoints are the ones the public site tasnif.soliq.uz and point-of-sale software call.
They are not a documented integration API and may change; confirm codes on the site.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

CLS = "https://tasnif.soliq.uz/api/cls-api"
CL = "https://tasnif.soliq.uz/api/cl-api"
TXKM = "https://txkm.soliq.uz/api/txkm-api"
SITE = "https://tasnif.soliq.uz/"
SANDBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "sandbox")


def text(v):
    return "n/a" if v is None else str(v)


def check_mxik(code):
    """Return an error line for a malformed 17-digit code, or None."""
    if not code.isdigit():
        return "INVALID: an MXIK has digits only"
    if len(code) != 17:
        return ("INVALID: %d digits; an MXIK has exactly 17 (run the fiscal skill's "
                "scripts/mxik.py check for hints)" % len(code))
    return None


def check_gtin(code):
    """Return an error line for a malformed barcode (GS1 check digit), or None."""
    if not code.isdigit() or len(code) not in (8, 12, 13, 14):
        return "INVALID: a GTIN has 8, 12, 13 or 14 digits"
    digits = [int(c) for c in code]
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits[:-1])))
    if (10 - total % 10) % 10 != digits[-1]:
        return "INVALID: the check digit of %s is wrong; re-scan the barcode" % code
    return None


def check_input(cmd, value):
    if cmd in ("code", "history", "info", "pictures"):
        return check_mxik(value)
    if cmd == "gtin":
        return check_gtin(value)
    if cmd == "classes" and not (value.isdigit() and len(value) == 3):
        return "INVALID: a group code has 3 digits, for example 040"
    if cmd == "vat" and not (value.isdigit() and len(value) == 9):
        return "INVALID: a TIN has 9 digits"
    if cmd == "search" and not value.strip():
        return "INVALID: empty search text"
    return None


def q(params):
    return urllib.parse.urlencode([(k, v) for k, v in params if v is not None])


def url_for(cmd, value, lang="ru", size=10, page=0, via="elasticsearch", tin=None, terminal_id=None):
    if cmd == "search":
        if via == "by-params":
            return "%s/mxik/search/by-params?%s" % (CLS, q([("text", value), ("size", size), ("page", page), ("lang", lang)]))
        if via == "subposition":
            return "%s/mxik/search-subposition?%s" % (CLS, q([("search_text", value), ("page", page), ("size", size), ("lang", lang)]))
        return "%s/elasticsearch/search?%s" % (CLS, q([("search", value), ("size", size), ("page", page), ("lang", lang)]))
    if cmd == "gtin":
        return "%s/mxik/search/by-params?%s" % (CLS, q([("gtin", value), ("lang", lang)]))
    if cmd == "code":
        return "%s/mxik/get/by-mxik?%s" % (CLS, q([("mxikCode", value), ("lang", lang)]))
    if cmd == "history":
        return "%s/integration-mxik/get/history/%s" % (CLS, value)
    if cmd == "info":
        return "%s/integration-mxik/get/information?%s" % (CL, q([("mxikCode", value), ("lang", lang), ("tin", tin), ("terminalId", terminal_id)]))
    if cmd == "classes":
        return "%s/class/short-info?%s" % (CLS, q([("groupCode", value), ("lang", lang)]))
    if cmd == "pictures":
        return "%s/integration-mxik/references/get/mxik/picture-names?%s" % (CLS, q([("mxik_code", value)]))
    if cmd == "vat":
        return "%s/ccm-api/info/check/is-vat/%s" % (TXKM, value)
    raise ValueError(cmd)


def picture_url(name):
    return "%s/integration-mxik/references/get/file/%s" % (CLS, urllib.parse.quote(name))


def epoch_ms(v):
    try:
        return datetime.datetime.fromtimestamp(int(v) / 1000, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError, OverflowError, OSError):
        return text(v)


def packages_lines(packages, name_key):
    lines = []
    for p in packages or []:
        lines.append("  package %s  %s" % (text(p.get("code")), text(p.get(name_key))))
    if any(isinstance(p.get("code"), (int, float)) for p in packages or []):
        lines.append("  note: package codes arrive as JSON numbers; store them as strings")
    return lines


def summarize(reply):
    """Return (status, lines) for any reply this tool knows. 0 found, 1 not found, 2 unknown."""
    if isinstance(reply, list):
        if not all(isinstance(n, str) for n in reply):
            return 2, ["unknown: a list that is not picture file names"]
        if not reply:
            return 1, ["pictures: none"]
        return 0, ["pictures: %d" % len(reply)] + ["  %s" % picture_url(n) for n in reply]
    if not isinstance(reply, dict):
        return 2, ["unknown: not a JSON object or array; treat as unknown and retry later"]
    if "status" in reply and "path" in reply and "error" in reply:
        return 2, ["endpoint error: HTTP %s %s on %s (Spring error page; this path does not work)"
                   % (text(reply.get("status")), text(reply.get("error")), text(reply.get("path")))]
    if "percent" in reply or isinstance(reply.get("data"), bool):
        if not reply.get("success"):
            return 1, ["vat: no answer (%s)" % text(reply.get("reason"))]
        return 0, ["vat payer: %s" % ("yes" if reply.get("data") else "no"),
                   "  percent=%s cashSaleAllowed=%s fractionalSale=%s baseCalculationAmount=%s"
                   % (text(reply.get("percent")), text(reply.get("cashSaleAllowed")),
                      text(reply.get("fractionalSale")), text(reply.get("baseCalculationAmount"))),
                   "  data from the service, not tax advice; the accountant sets VAT"]
    if "mxikCode" in reply and "packages" in reply:
        code = text(reply.get("mxikCode"))
        lines = ["%s  %s" % (code, text(reply.get("mxikName"))),
                 "  label=%s useCard=%s lgota=%s unit=%s" % (text(reply.get("label")), text(reply.get("useCard")),
                                                            text(reply.get("lgotaName")), text(reply.get("unitName")))]
        pk = reply.get("packages") or []
        for p in pk:
            lines.append("  package %s  %s  unit=%s parent=%s x %s unitPackage=%s" % (
                text(p.get("code")), text(p.get("name")), text(p.get("unitName")), text(p.get("parentCode")),
                text(p.get("parentValue")), text(p.get("isUnitPackage"))))
        if not pk:
            lines.append("  packages: none on the card")
        elif any(isinstance(p.get("code"), (int, float)) for p in pk):
            lines.append("  note: package codes arrive as JSON numbers; store them as strings")
        lines.append("  createdBy is not shown: it can hold a person's name")
        return 0, lines
    if "success" not in reply:
        return 2, ["unknown: no success field; treat as unknown and retry later"]
    data = reply.get("data")
    if "permitted" in reply:
        if not reply.get("success"):
            return 1, ["info: success false (%s)" % text(reply.get("reason"))]
        if not data:
            return 1, ["info: no record (data is empty, recordTotal %s); unknown code" % text(reply.get("recordTotal"))]
        lines = ["info: %d record(s), permitted=%s" % (len(data), text(reply.get("permitted")))]
        for it in data:
            lines.append("%s  %s" % (text(it.get("mxik")), text(it.get("name"))))
            lines.append("  label=%s usePackage=%s cashSale=%s created=%s updated=%s" % (
                text(it.get("label")), text(it.get("usePackage")), text(it.get("cashSale")),
                epoch_ms(it.get("createdAt")), epoch_ms(it.get("updateAt"))))
            lines += packages_lines(it.get("packages"), "nameRu")
        lines.append("  permitted is not documented; show it, do not block sales on it")
        return 0, lines
    if not reply.get("success"):
        return 1, ["not found: success false, code %s, reason %s" % (text(reply.get("code")), text(reply.get("reason")))]
    if isinstance(data, dict) and "content" in data:
        items = data.get("content") or []
        lines = ["page: %d shown of %s (page %s, last %s)" % (len(items), text(data.get("totalElements")),
                                                             text(data.get("number")), text(data.get("last")))]
        for it in items:
            lines.append("  %s  %s  barcode=%s" % (text(it.get("mxikCode")), text(it.get("mxikName")),
                                                   text(it.get("internationalCode"))))
        lines.append("next: load the card (code MXIK) for package codes; a person confirms the choice")
        return (0 if items else 1), lines
    if isinstance(data, dict) and "packageNames" in data:
        name = data.get("attributeNameRu") or data.get("subPositionNameRu") or data.get("attributeNameUz")
        lines = ["%s  %s" % (text(data.get("mxikCode")), text(name)),
                 "  isActive=%s status=%s created=%s updated=%s" % (
                     text(data.get("isActive")), text(data.get("status")), text(data.get("createdAt")),
                     text(data.get("updatedAt"))),
                 "  class: %s / sub-position: %s" % (text(data.get("classNameRu")), text(data.get("subPositionNameRu")))]
        lines += packages_lines(data.get("packageNames"), "nameRu")
        lines.append("  id is not shown: it changes on every call; key by mxikCode")
        return 0, lines
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "count" in data[0]:
            lines = ["classes: %d" % len(data)]
            lines += ["  %s  %s  (%s)" % (text(it.get("code")), text(it.get("name")), text(it.get("count"))) for it in data]
            return 0, lines
        lines = ["search: %d shown of %s" % (len(data), text(reply.get("recordTotal")))]
        for it in data:
            lines.append("  %s  %s  usePackage=%s lgota=%s" % (text(it.get("mxikCode")), text(it.get("name")),
                                                             text(it.get("usePackage")), text(it.get("lgotaName"))))
        if data:
            lines.append("next: load the card (code MXIK) for package codes")
        return (0 if data else 1), lines
    return 2, ["unknown: success true but no data this tool knows; treat as unknown"]


def fetch(url):
    """Return (http status, body text). Never raises on HTTP errors."""
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "uzfintech-skills-tasnif/1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def interpret(cmd, status, body):
    """Return (status, lines) for a live reply, including the non-JSON ones."""
    try:
        reply = json.loads(body)
    except ValueError:
        if cmd == "code" and status == 403 and "topilmadi" in body:
            return 1, ["not found: HTTP 403 %s" % body.strip()[:80]]
        return 2, ["unknown: HTTP %d, not JSON: %s; retry later" % (status, body.strip()[:80])]
    return summarize(reply)


def selftest():
    fails = []

    def expect(cond, what):
        if not cond:
            fails.append(what)

    def sample(name):
        with open(os.path.join(SANDBOX, name), encoding="utf-8") as f:
            return summarize(json.load(f))

    expect(check_mxik("04016001002000000") is None, "valid mxik")
    expect(check_mxik("4016001002000000") is not None, "16 digits rejected")
    expect(check_gtin("4607001771555") is None, "valid gtin")
    expect(check_gtin("4607001771556") is not None, "bad check digit rejected")
    expect(check_gtin("12345") is not None, "short gtin rejected")
    expect(check_input("classes", "40") is not None, "2-digit group rejected")
    expect(check_input("vat", "12345678") is not None, "8-digit TIN rejected")
    expect(url_for("gtin", "4607001771555") == CLS + "/mxik/search/by-params?gtin=4607001771555&lang=ru", "gtin url")
    expect(url_for("search", "коврик", size=2) == CLS + "/elasticsearch/search?search=%D0%BA%D0%BE%D0%B2%D1%80%D0%B8"
           "%D0%BA&size=2&page=0&lang=ru", "search url")
    expect(url_for("search", "x", via="subposition").startswith(CLS + "/mxik/search-subposition?search_text=x"), "subposition url")
    expect(url_for("history", "04016001002000000") == CLS + "/integration-mxik/get/history/04016001002000000", "history url")
    expect(url_for("info", "04016001002000000") == CL + "/integration-mxik/get/information?mxikCode=04016001002000000&lang=ru",
           "info url without tin")
    expect(url_for("info", "04016001002000000", tin="<TIN>", terminal_id="T1").endswith("&tin=%3CTIN%3E&terminalId=T1"),
           "info url with tin")
    expect(url_for("vat", "<TIN>") == TXKM + "/ccm-api/info/check/is-vat/<TIN>", "vat url")
    expect(url_for("pictures", "04016001002000000") == CLS + "/integration-mxik/references/get/mxik/picture-names"
           "?mxik_code=04016001002000000", "pictures url")

    st, out = sample("by-params-gtin.ru.json")
    expect(st == 0 and any("00901001004004005" in ln and "4607001771555" in ln for ln in out), "gtin hit")
    st, out = sample("by-params-gtin-not-found.ru.json")
    expect(st == 1 and "code -1" in out[0], "gtin miss")
    st, out = sample("by-params-text.ru.json")
    expect(st == 0 and out[0].startswith("page: 2 shown"), "by-params text page")
    st, out = sample("search-subposition.ru.json")
    expect(st == 0 and out[0].startswith("page: 2 shown"), "subposition page")
    st, out = sample("elasticsearch-search.ru.json")
    expect(st == 0 and out[0].startswith("search: 1 shown"), "elasticsearch search")
    st, out = sample("by-mxik-gtin.ru.json")
    expect(st == 0 and any("package 1391155" in ln for ln in out), "card package")
    expect(not any("USER" in ln for ln in out), "createdBy not printed")
    st, out = sample("history.json")
    expect(st == 0 and any("isActive=1" in ln for ln in out), "history active")
    expect(any("package 1342705" in ln for ln in out) and any("package 1659249" in ln for ln in out), "history packages")
    st, out = sample("history-not-found.json")
    expect(st == 1 and "Mxik code not found!" in out[0], "history miss")
    st, out = sample("information.ru.json")
    expect(st == 0 and "permitted=False" in out[0], "info permitted")
    expect(sum(1 for ln in out if ln.startswith("  package ")) == 1, "info has one package")
    expect(any("2022-04-29" in ln for ln in out), "info epoch dates")
    st, out = sample("information-two-packages.ru.json")
    expect(st == 0 and sum(1 for ln in out if ln.startswith("  package ")) == 2, "info two packages")
    st, out = sample("information-not-found.ru.json")
    expect(st == 1 and "no record" in out[0], "info miss with success true")
    st, out = sample("class-short-info.ru.json")
    expect(st == 0 and out[0] == "classes: 17", "classes ru")
    st, out = sample("class-short-info.json")
    expect(st == 0 and out[0] == "classes: 17", "classes default lang")
    st, out = sample("picture-names.json")
    expect(st == 0 and out[0] == "pictures: 3" and "/references/get/file/04016001002000000_1.png" in out[1], "pictures")
    st, out = sample("is-vat.json")
    expect(st == 0 and out[0] == "vat payer: yes", "vat")
    st, out = sample("cl-api-class-search.json")
    expect(st == 2 and "HTTP 404" in out[0], "spring 404 is unknown")
    st, out = sample("dv-cert-number-empty.ru.json")
    expect(st == 1 and "empty cert number" in out[0], "dv-cert-number empty")
    st, out = interpret("code", 403, "MXIK ma'lumotlari topilmadi")
    expect(st == 1, "by-mxik 403 text is not found")
    st, out = interpret("search", 403, "Синф коди хато жўнатилган")
    expect(st == 2, "other 403 text is unknown")
    st, out = interpret("code", 502, "<html>Bad Gateway</html>")
    expect(st == 2, "proxy html is unknown")
    expect(summarize({"success": True, "code": 200, "data": None})[0] == 2, "success without data is unknown")
    for f in fails:
        print("FAIL: " + f)
    print("selftest: %s (%d checks failed)" % ("ok" if not fails else "FAILED", len(fails)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    helps = {"search": "text search", "gtin": "barcode to code", "code": "card with package codes",
             "history": "names, status, dates, package names", "info": "cl-api point-of-sale reply",
             "classes": "classes of a 3-digit group", "pictures": "picture file names",
             "vat": "txkm VAT-payer check by TIN"}
    for name, h in helps.items():
        p = sub.add_parser(name, help=h)
        p.add_argument("value", nargs="?")
        p.add_argument("--online", action="store_true", help="send the one GET")
        p.add_argument("--file", help="summarize a saved reply instead")
        p.add_argument("--lang", default="ru", help="lang parameter (ru and uz seen in clients)")
        if name == "search":
            p.add_argument("--via", choices=["elasticsearch", "by-params", "subposition"], default="elasticsearch")
            p.add_argument("--size", type=int, default=10)
            p.add_argument("--page", type=int, default=0)
        if name == "info":
            p.add_argument("--tin", help="your own merchant's TIN; never another person's")
            p.add_argument("--terminal-id")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.cmd:
        ap.print_help()
        return 2
    if a.file:
        try:
            with open(a.file, encoding="utf-8") as f:
                body = f.read()
        except OSError as e:
            print("cannot read %s: %s" % (a.file, e))
            return 2
        st, out = interpret(a.cmd, 200, body)
        print("\n".join(out))
        return st
    if not a.value:
        print("usage: %s needs a value or --file" % a.cmd)
        return 2
    value = a.value.strip()
    bad = check_input(a.cmd, value)
    if bad:
        print(bad)
        return 1
    if a.cmd == "info" and a.tin and check_input("vat", a.tin):
        print(check_input("vat", a.tin))
        return 1
    url = url_for(a.cmd, value, a.lang, getattr(a, "size", 10), getattr(a, "page", 0),
                  getattr(a, "via", "elasticsearch"), getattr(a, "tin", None), getattr(a, "terminal_id", None))
    if not a.online:
        print("offline: not called. GET %s" % url)
        print("add --online to send it (a public endpoint, not a documented API), or save the reply and use --file")
        return 0
    try:
        status, body = fetch(url)
    except (urllib.error.URLError, OSError) as e:
        print("network error: %s" % e)
        return 2
    st, out = interpret(a.cmd, status, body)
    print("HTTP %d" % status)
    print("\n".join(out))
    if st == 0 and a.cmd in ("search", "gtin", "code"):
        print("confirm on %s before you store a code" % SITE)
    return st


if __name__ == "__main__":
    sys.exit(main())
