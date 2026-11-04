#!/usr/bin/env python3
"""Look up and check CBU payment purpose codes offline (UZS payment orders, every Uzbek bank).

Python 3 standard library only. Reads ../references/purpose-codes/codes.json, the CBU
comparison table of old and new commercial codes (new codes in force 2026-05-06, old codes
refused from 2026-05-26).

  purpose_codes.py search TEXT...            find new codes (and old ones) by name, RU or UZ
  purpose_codes.py list [--legacy]           print every new code (or every old code)
  purpose_codes.py old CODE                  old code -> new code(s), with the table's notes
  purpose_codes.py check CODE [--date D]     is CODE accepted on date D (default: today)?
  purpose_codes.py details --code C --goods G --payment-type T
                           [--contract-no N --contract-date DD.MM.YYYY] [--extra X] [--date D]
                                             assemble and check a "Детали платежа" text
  purpose_codes.py account ACC [--mfo MFO]   format check of a 20-digit account / 5-digit MFO
  purpose_codes.py --selftest                check the data file and this tool

Exit status: 0 accepted / found, 1 rejected / not found / invalid, 2 usage error.
Codes outside the published table (budget and treasury payments, salary, loans) are not
in the data: the tool answers "not in the published table - ask your bank".
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "references", "purpose-codes", "codes.json")

# Latin letters that the published sheets use inside Cyrillic words (e.g. "ПРОФEССИОНАЛЬНЫЕ",
# "AТРОФ"), mapped to the Cyrillic letter they imitate. Applied before casefold().
HOMOGLYPHS = str.maketrans("AEOPCXYKMTHBaeopcxy", "АЕОРСХУКМТНВаеорсху")
# Loose folding for search only: the old-code names drop the Uzbek letters (Гушт / Гўшт).
LOOSE = str.maketrans({"ё": "е", "ў": "у", "қ": "к", "ғ": "г", "ҳ": "х",
                       "ъ": None, "ʼ": None, "ʻ": None, "'": None, "’": None})
CYRILLIC = re.compile(r"[Ѐ-ӿ]")
CODE_RE = re.compile(r"\d{5}")
DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
NOT_IN_TABLE = ("not in the published table - budget and treasury payments, salary and loan "
                "codes are not part of it; ask your bank which code applies")


def load(path=DATA):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    d["by_code"] = {c["code"]: c for c in d["codes"]}
    d["by_old"] = {c["code"]: c for c in d["legacy"]}
    d["in_force_date"] = iso(d["in_force"])
    d["rejected_date"] = iso(d["old_codes_rejected_from"])
    return d


def iso(text):
    return datetime.datetime.strptime(text, "%Y-%m-%d").date()


def norm(text):
    """casefold, Latin look-alikes -> Cyrillic when the text has Cyrillic, loose letters."""
    t = text.translate(HOMOGLYPHS) if CYRILLIC.search(text) else text
    return re.sub(r"\s+", " ", t.casefold().translate(LOOSE)).strip()


def targets(d, old):
    out = []
    for m in old["maps_to"]:
        new = d["by_code"][m["code"]]
        note = m.get("note_ru") or ""
        if m.get("note_uz_cyrl"):
            note = "%s / %s" % (note, m["note_uz_cyrl"]) if note else m["note_uz_cyrl"]
        out.append((new, note))
    return out


def fmt_new(c):
    return "%s  %s | %s" % (c["code"], c["name_ru"], c["name_uz_cyrl"])


def fmt_old(d, old):
    lines = ["old %s  %s | %s" % (old["code"], old["name_ru"], old["name_uz_cyrl"])]
    for new, note in targets(d, old):
        lines.append("  -> " + fmt_new(new) + ("   [note: %s]" % note if note else ""))
    if len(old["maps_to"]) > 1:
        lines.append("  several new codes: pick the one whose note or name fits the goods")
    return "\n".join(lines)


def search(d, words):
    q = [norm(w) for w in words if norm(w)]
    if not q:
        return [], []

    def hit(*texts):
        hay = " ".join(norm(t) for t in texts if t)
        return all(w in hay for w in q)

    new = [c for c in d["codes"] if hit(c["name_ru"], c["name_uz_cyrl"])]
    old = [o for o in d["legacy"]
           if hit(o["name_ru"], o["name_uz_cyrl"],
                  *[m.get(k, "") for m in o["maps_to"] for k in ("note_ru", "note_uz_cyrl")])]
    return new, old


def check(d, code, on):
    """-> (accepted: bool, status: str, message: str)"""
    code = code.strip()
    if not CODE_RE.fullmatch(code):
        return False, "invalid", "%r is not a 5-digit code" % code
    if code in d["by_code"]:
        c = d["by_code"][code]
        if on < d["in_force_date"]:
            return True, "new-not-yet", "%s (new code; in force from %s)" % (
                fmt_new(c), d["in_force"])
        return True, "new", fmt_new(c)
    if code in d["by_old"]:
        old = d["by_old"][code]
        if on >= d["rejected_date"]:
            return False, "old-rejected", "REJECTED on %s: old codes are refused from %s\n%s" % (
                on.isoformat(), d["old_codes_rejected_from"], fmt_old(d, old))
        if on >= d["in_force_date"]:
            return True, "old-transition", "accepted only until %s (transition period)\n%s" % (
                (d["rejected_date"] - datetime.timedelta(days=1)).isoformat(), fmt_old(d, old))
        return True, "old", "old code, refused from %s\n%s" % (
            d["old_codes_rejected_from"], fmt_old(d, old))
    return False, "unknown", "%s is %s" % (code, NOT_IN_TABLE)


def details(d, code, goods, payment_type, contract_no=None, contract_date=None, extra=None,
            on=None):
    """-> (text, problems). Problems empty = every required part is present."""
    problems = []
    ok, status, msg = check(d, code or "", on or datetime.date.today())
    if not ok:
        problems.append("code: " + msg.splitlines()[0])
    elif status in ("old", "old-transition"):
        problems.append("code: %s is an old code; use the new one (refused from %s)" % (
            code, d["old_codes_rejected_from"]))
    if not (goods or "").strip():
        problems.append("goods: name the goods, works or services")
    if not (payment_type or "").strip():
        problems.append("payment type: say what the payment is (prepayment, payment, ...)")
    if bool(contract_no) != bool(contract_date):
        problems.append("contract: give both the number and the date, or neither")
    if contract_date:
        m = DATE_RE.fullmatch(contract_date.strip())
        try:
            if not m:
                raise ValueError
            datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            problems.append("contract date: %r is not DD.MM.YYYY" % contract_date)
    parts = [(code or "").strip(), (goods or "").strip()]
    if contract_no and contract_date:
        parts.append("по договору № %s от %s" % (contract_no.strip(), contract_date.strip()))
    parts.append((payment_type or "").strip())
    if extra:
        parts.append(extra.strip())
    text = ", ".join(p for p in parts[1:] if p)
    text = ("%s %s" % (parts[0], text)).strip()
    return text, problems


def account(acc, mfo=None):
    problems = []
    if not re.fullmatch(r"\d{20}", acc or ""):
        problems.append("account %r: expected exactly 20 digits (got %d characters)" % (
            acc, len(acc or "")))
    if mfo is not None and not re.fullmatch(r"\d{5}", mfo):
        problems.append("MFO %r: expected exactly 5 digits" % mfo)
    return problems


def selftest():
    d = load()
    codes = [c["code"] for c in d["codes"]]
    assert len(codes) == 115 and len(set(codes)) == 115, len(codes)
    assert all(CODE_RE.fullmatch(c) for c in codes)
    span = {"%05d" % i for i in range(1, 118)}
    assert span - set(codes) == {"00077", "00115"}, sorted(span - set(codes))
    assert set(codes) <= span
    olds = [o["code"] for o in d["legacy"]]
    assert len(olds) == 69 and len(set(olds)) == 69, len(olds)
    assert not set(olds) & set(codes)
    for o in d["legacy"]:
        assert o["maps_to"], o["code"]
        for m in o["maps_to"]:
            assert m["code"] in d["by_code"], (o["code"], m["code"])
    multi = sorted(o["code"] for o in d["legacy"] if len(o["maps_to"]) > 1)
    assert multi == ["00512", "00513", "00518", "00525", "00532", "00535", "00545",
                     "00668", "00693"], multi
    t = dict((n["code"], note) for n, note in targets(d, d["by_old"]["00545"]))
    assert sorted(t) == ["00039", "00068", "00069", "00076"], t
    assert "аллюмин" in t["00076"] and "пластмасс" in t["00039"]
    assert [n["code"] for n, _ in targets(d, d["by_old"]["00699"])] == ["00031"]
    assert [n["code"] for n, _ in targets(d, d["by_old"]["00652"])] == ["00099"]
    # homoglyphs and case: the sheets carry Latin E / A inside Cyrillic words
    assert "00106" in [c["code"] for c in search(d, ["профессиональные"])[0]]
    assert "00106" in [c["code"] for c in search(d, ["ПРОФЕССИОНАЛ", "хизматлар"])[0]]
    assert "00116" in [c["code"] for c in search(d, ["атроф"])[0]]
    assert "00069" in [c["code"] for c in search(d, ["керамик", "маҳсулот"])[0]]
    assert "00545" in [o["code"] for o in search(d, ["сантехн"])[1]]
    assert "00545" in [o["code"] for o in search(d, ["алюмендан"])[1]]
    assert "00513" in [o["code"] for o in search(d, ["гўшт"])[1]]  # old name says "Гушт"
    assert search(d, ["qwertyzzz"]) == ([], [])
    day = iso
    assert check(d, "00076", day("2026-06-01"))[:2] == (True, "new")
    assert check(d, "00076", day("2026-05-01"))[:2] == (True, "new-not-yet")
    assert check(d, "00545", day("2026-05-01"))[:2] == (True, "old")
    assert check(d, "00545", day("2026-05-25"))[:2] == (True, "old-transition")
    assert check(d, "00545", day("2026-05-26"))[:2] == (False, "old-rejected")
    assert check(d, "00699", day("2026-11-04"))[:2] == (False, "old-rejected")
    assert check(d, "00077", day("2026-11-04"))[:2] == (False, "unknown")
    assert check(d, "00999", day("2026-11-04"))[:2] == (False, "unknown")
    for bad in ("123", "0007a", "000760", ""):
        assert check(d, bad, day("2026-11-04"))[:2] == (False, "invalid"), bad
    text, probs = details(d, "00076", "алюминиевые смесители", "оплата", "100001",
                          "03.11.2026", on=day("2026-11-04"))
    assert probs == [], probs
    assert text == "00076 алюминиевые смесители, по договору № 100001 от 03.11.2026, оплата"
    assert details(d, "00076", "товар", "предоплата", on=day("2026-11-04"))[1] == []
    assert len(details(d, "00545", "товар", "оплата", on=day("2026-11-04"))[1]) == 1
    assert len(details(d, "00545", "товар", "оплата", on=day("2026-05-20"))[1]) == 1
    assert len(details(d, "00076", "", "", "1", None, on=day("2026-11-04"))[1]) == 3
    assert len(details(d, "00076", "x", "y", "1", "31.02.2026", on=day("2026-11-04"))[1]) == 1
    assert account("20208000900000000001", "01001") == []
    assert len(account("2020800090000000001")) == 1  # 19 digits, like one vendor sample
    assert len(account("20208000900000000001", "0100")) == 1
    print("selftest OK: %d new codes, %d old codes, %d old codes with several new ones"
          % (len(codes), len(olds), len(multi)))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("search")
    p.add_argument("text", nargs="+")
    p = sub.add_parser("list")
    p.add_argument("--legacy", action="store_true")
    p = sub.add_parser("old")
    p.add_argument("code")
    p = sub.add_parser("check")
    p.add_argument("code")
    p.add_argument("--date", help="YYYY-MM-DD, default today")
    p = sub.add_parser("details")
    p.add_argument("--code", required=True)
    p.add_argument("--goods", required=True)
    p.add_argument("--payment-type", required=True)
    p.add_argument("--contract-no")
    p.add_argument("--contract-date", help="DD.MM.YYYY")
    p.add_argument("--extra")
    p.add_argument("--date", help="YYYY-MM-DD the order is sent, default today")
    p = sub.add_parser("account")
    p.add_argument("account")
    p.add_argument("--mfo")
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_usage(sys.stderr)
        return 2
    d = load()
    try:
        on = iso(a.date) if getattr(a, "date", None) else datetime.date.today()
    except ValueError:
        print("purpose_codes.py: --date must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if a.cmd == "search":
        new, old = search(d, a.text)
        for c in new:
            print(fmt_new(c))
        for o in old:
            print(fmt_old(d, o))
        if not new and not old:
            hint = "" if CYRILLIC.search(" ".join(a.text)) else \
                " (names are published in Cyrillic, RU and UZ; search in Cyrillic)"
            print("no match%s; the table holds commercial codes only: %s" % (hint, NOT_IN_TABLE))
            return 1
        return 0
    if a.cmd == "list":
        for row in (d["legacy"] if a.legacy else d["codes"]):
            print(fmt_old(d, row) if a.legacy else fmt_new(row))
        return 0
    if a.cmd == "old":
        code = a.code.strip()
        if code in d["by_old"]:
            print(fmt_old(d, d["by_old"][code]))
            return 0
        if code in d["by_code"]:
            print("%s is already a new code: %s" % (code, fmt_new(d["by_code"][code])))
            return 0
        print("%s is %s" % (code, NOT_IN_TABLE if CODE_RE.fullmatch(code) else
                            "not a 5-digit code"))
        return 1
    if a.cmd == "check":
        ok, status, msg = check(d, a.code, on)
        print(("OK " if ok else "NO ") + status + ": " + msg)
        return 0 if ok else 1
    if a.cmd == "details":
        text, problems = details(d, a.code, a.goods, a.payment_type, a.contract_no,
                                 a.contract_date, a.extra, on)
        print("purp_code: %s" % a.code.strip())
        print("text:      %s" % text)
        for pr in problems:
            print("PROBLEM   " + pr)
        print("OK" if not problems else "INVALID")
        return 0 if not problems else 1
    if a.cmd == "account":
        problems = account(a.account, a.mfo)
        for pr in problems:
            print("PROBLEM   " + pr)
        print("OK (format only; the check key is not public)" if not problems else "INVALID")
        return 0 if not problems else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
