#!/usr/bin/env python3
"""Check MXIK (IKPU / SPIC) product codes offline; optionally look them up on Tasnif.

Standard library only (python3.9+). Nothing touches the network unless --online is given.

  mxik.py check CODE [CODE ...]       17 digits, split into levels, hints for common mistakes
  mxik.py lookup CODE                 print the Tasnif by-mxik URL (offline)
  mxik.py lookup CODE --online        GET it and summarize name, flags and package codes
  mxik.py lookup "text" --online      full-text search (Tasnif search endpoint)
  mxik.py lookup --file reply.json    summarize a saved Tasnif reply (offline)
  mxik.py --selftest

Exit codes: 0 ok, 1 invalid code or no record, 2 usage or network error.

The Tasnif endpoints are the ones the public site tasnif.soliq.uz calls. They are not a
documented integration API and may change; confirm every code on the site itself.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://tasnif.soliq.uz/api/cls-api"
SITE = "https://tasnif.soliq.uz/"
# (level, length of the prefix) as the classifier's own reply names them:
# groupCode 3, classCode 5, positionCode 8, subPositionCode 11, brandCode 14, mxikCode 17.
LEVELS = [("group", 3), ("class", 5), ("position", 8), ("sub-position", 11), ("brand", 14), ("full", 17)]
REPLY_KEYS = [("groupCode", 3), ("classCode", 5), ("positionCode", 8), ("subPositionCode", 11),
              ("brandCode", 14)]


def split(code):
    return [(name, code[:n]) for name, n in LEVELS]


def check(raw):
    """Return (ok, lines) for one code. Pure function; no network."""
    lines = []
    code = "".join(ch for ch in raw.strip() if ch not in " -. ")
    if code != raw.strip():
        lines.append("note: separators removed; send the provider %s (digits only, as a string)" % code)
    if not code:
        return False, ["INVALID: empty code"]
    if not code.isdigit():
        bad = sorted(set(ch for ch in code if not ch.isdigit()))
        lines.append("INVALID: an MXIK has digits only; found %s" % " ".join(repr(c) for c in bad))
        if len(code) >= 20:
            lines.append("hint: long mixed strings are usually marking codes (Data Matrix); they go "
                         "in the provider's marking field, not in the MXIK field")
        return False, lines
    n = len(code)
    if n == 17:
        lines.append("OK: 17 digits")
        for name, part in split(code):
            lines.append("  %-13s %s" % (name, part))
        if code.endswith("000000"):
            lines.append("  kind          base code (brand and attribute digits are zero; derived)")
        else:
            lines.append("  kind          identification code (brand or attribute digits set; derived)")
        if code[:3] == "000":
            lines.append("warning: group 000 is unusual; look the code up before you use it (heuristic)")
        lines.append("confirm on %s and take the package code from the code's card" % SITE)
        return True, lines
    lines.append("INVALID: %d digits; an MXIK has exactly 17" % n)
    if n in (15, 16):
        fixed = "0" * (17 - n) + code
        lines.append("hint: leading zeros look lost (code stored as a number?). Candidate %s; "
                     "store MXIK as a string and confirm the candidate on %s" % (fixed, SITE))
    level = [name for name, k in LEVELS[:-1] if k == n]
    if level:
        lines.append("hint: %d digits is the %s level only; use the full 17-digit code from the card"
                     % (n, level[0]))
    if n == 13:
        lines.append("hint: 13 digits is the length of an EAN-13 barcode, which is not an MXIK")
    if n > 17:
        lines.append("hint: too long; a barcode, a marking code or two codes glued together?")
    return False, lines


def url_for(query, lang="ru", size=10):
    q = query.strip()
    if q.isdigit():
        return "%s/mxik/get/by-mxik?%s" % (BASE, urllib.parse.urlencode({"mxikCode": q, "lang": lang}))
    return "%s/elasticsearch/search?%s" % (BASE, urllib.parse.urlencode({"search": q, "size": size, "lang": lang}))


def flag(v):
    return "n/a" if v is None else str(v)


def summarize(reply):
    """Return (ok, lines) for a Tasnif by-mxik or search reply."""
    lines = []
    if isinstance(reply, dict) and isinstance(reply.get("data"), list):
        items = reply["data"]
        lines.append("search: %d shown of %s" % (len(items), flag(reply.get("recordTotal"))))
        for it in items:
            lines.append("  %s  %s  unit=%s label=%s useCard=%s usePackage=%s lgota=%s" % (
                it.get("mxikCode"), it.get("name"), flag(it.get("unitsName")), flag(it.get("label")),
                flag(it.get("useCard")), flag(it.get("usePackage")), flag(it.get("lgotaName"))))
        lines.append("next: look up one code (by-mxik) to get its package codes")
        return bool(items), lines
    if not isinstance(reply, dict) or not reply.get("mxikCode"):
        return False, ["no record: the reply has no mxikCode (unknown code, or the endpoint changed)"]
    code = str(reply["mxikCode"])
    ok, check_lines = check(code)
    lines.append("%s  %s" % (code, flag(reply.get("mxikName"))))
    lines += ["  " + ln for ln in check_lines if not ln.startswith("confirm")]
    for key, n in REPLY_KEYS:
        got = reply.get(key)
        if got is not None and str(got) != code[:n]:
            ok = False
            lines.append("MISMATCH: %s %s is not the first %d digits of %s" % (key, got, n, code))
    lines.append("  group: %s / class: %s" % (flag(reply.get("groupName")), flag(reply.get("className"))))
    lines.append("  label=%s useCard=%s lgota=%s unit=%s" % (
        flag(reply.get("label")), flag(reply.get("useCard")), flag(reply.get("lgotaName")),
        flag(reply.get("unitName"))))
    packages = reply.get("packages") or []
    if not packages:
        lines.append("  packages: none in the reply; ask the provider or Tasnif which package code to send")
    for p in packages:
        lines.append("  package %s  %s  container=%s unitPackage=%s parent=%s" % (
            p.get("code"), flag(p.get("name")), flag(p.get("containerName")),
            flag(p.get("isUnitPackage")), flag(p.get("parentCode"))))
    if packages:
        lines.append("  send the package code as a string in the provider's package field")
    return ok, lines


def fetch(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "uzfintech-skills-mxik/1"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def selftest():
    fails = []

    def expect(cond, what):
        if not cond:
            fails.append(what)

    ok, out = check("04016001002000000")
    expect(ok, "valid code accepted")
    expect("  group         040" in out and "  brand         04016001002000" in out, "split levels")
    expect(any("base code" in ln for ln in out), "base code detected")
    ok, out = check("04016001002000123")
    expect(ok and any("identification code" in ln for ln in out), "identification code detected")
    ok, out = check("4016001002000000")
    expect(not ok and any("04016001002000000" in ln for ln in out), "16 digits -> leading zero hint")
    ok, out = check("305001001000000")
    expect(not ok and any("00305001001000000" in ln for ln in out), "15 digits -> two zeros hint")
    ok, out = check("04016001002")
    expect(not ok and any("sub-position level" in ln for ln in out), "11 digits -> level hint")
    ok, out = check("4600000000008")
    expect(not ok and any("EAN-13" in ln for ln in out), "13 digits -> barcode hint")
    ok, out = check("0401600100200000A")
    expect(not ok and any("digits only" in ln for ln in out), "non-digit rejected")
    ok, out = check("040 16001 002000000")
    expect(ok and any("separators removed" in ln for ln in out), "separators normalized")
    ok, out = check("")
    expect(not ok, "empty rejected")
    expect(url_for("04016001002000000") ==
           BASE + "/mxik/get/by-mxik?mxikCode=04016001002000000&lang=ru", "by-mxik url")
    expect(url_for("коврик", size=2) == BASE + "/elasticsearch/search?search=%D0%BA%D0%BE%D0%B2%D1%80%D0%B8"
           "%D0%BA&size=2&lang=ru", "search url")
    by_code = {"mxikCode": "04016001002000000", "mxikName": "Коврик для мыши", "groupCode": "040",
               "classCode": "04016", "positionCode": "04016001", "subPositionCode": "04016001002",
               "brandCode": "04016001002000", "label": 0, "useCard": 0, "lgotaName": None,
               "packages": [{"code": 1342705, "parentCode": None, "name": "шт.", "isUnitPackage": "1"}]}
    ok, out = summarize(by_code)
    expect(ok and any("package 1342705" in ln for ln in out), "by-mxik summary")
    bad = dict(by_code, classCode="04017")
    ok, out = summarize(bad)
    expect(not ok and any("MISMATCH: classCode" in ln for ln in out), "prefix mismatch caught")
    ok, out = summarize({"success": True, "data": [{"mxikCode": "04016001002000000", "name": "Коврик для мыши",
                                                    "label": "0", "useCard": "0", "usePackage": "1"}],
                         "recordTotal": 118})
    expect(ok and "search: 1 shown of 118" in out[0], "search summary")
    ok, out = summarize({"success": True, "data": []})
    expect(not ok, "empty search is not ok")
    ok, out = summarize({})
    expect(not ok and "no record" in out[0], "empty reply")
    for f in fails:
        print("FAIL: " + f)
    print("selftest: %s (%d checks failed)" % ("ok" if not fails else "FAILED", len(fails)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="offline structure check")
    c.add_argument("codes", nargs="+")
    lk = sub.add_parser("lookup", help="Tasnif lookup (network only with --online)")
    lk.add_argument("query", nargs="?", help="17-digit code or search text")
    lk.add_argument("--online", action="store_true", help="actually call tasnif.soliq.uz")
    lk.add_argument("--file", help="summarize a saved Tasnif reply instead")
    lk.add_argument("--lang", default="ru", help="lang parameter (ru is the value verified here)")
    lk.add_argument("--size", type=int, default=10, help="search result count")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "check":
        status = 0
        for i, code in enumerate(a.codes):
            ok, out = check(code)
            if i:
                print()
            print(code.strip())
            print("\n".join("  " + ln for ln in out))
            status = status or (0 if ok else 1)
        return status
    if a.cmd == "lookup":
        if a.file:
            try:
                reply = json.load(open(a.file, encoding="utf-8"))
            except (OSError, ValueError) as e:
                print("cannot read %s: %s" % (a.file, e))
                return 2
            ok, out = summarize(reply)
            print("\n".join(out))
            return 0 if ok else 1
        if not a.query:
            ap.error("lookup needs a code, search text or --file")
        if a.query.strip().isdigit() and len(a.query.strip()) != 17:
            ok, out = check(a.query)
            print("\n".join(out))
            return 1
        url = url_for(a.query, a.lang, a.size)
        if not a.online:
            print("offline: not called. GET %s" % url)
            print("add --online to call the public Tasnif endpoint (not a documented API), "
                  "or save the reply and use --file")
            return 0
        try:
            reply = fetch(url)
        except (urllib.error.URLError, OSError, ValueError) as e:
            print("network or parse error for %s: %s" % (url, e))
            return 2
        ok, out = summarize(reply)
        print("source: %s" % url)
        print("\n".join(out))
        print("confirm on %s before you store the code" % SITE)
        return 0 if ok else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
