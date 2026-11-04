#!/usr/bin/env python3
"""Validate a request or response body against this skill's trimmed schemas.

Deterministic check, python3 standard library only. The same file is copied into every
skills/<provider>/scripts/ by `scripts/lint --fix`; edit scripts/shared/validate.py.

  validate.py --list [TEXT]                 list schemas: name, method, endpoint
  validate.py SCHEMA PAYLOAD [--part PART]  validate PAYLOAD (file, '-' = stdin)

SCHEMA is a file path, a schema name (`getPayment`, `webhook-check`) or `product/name`.
PART: params (default), result, body, query, path for hand-written schemas; request
(default) or response for `schemas/ops/*.json` (`--status`, default 200).
A JSON-RPC envelope (with or without "jsonrpc") or a {success, data} envelope is unwrapped.
Placeholder strings such as "<CARD_TOKEN>" match any schema and are counted, not checked.
A form-urlencoded PAYLOAD
(`a=1&b=2`) is accepted; numeric strings are coerced for `x-in: form|query` schemas,
because every form value arrives as a string.
Exit status: 0 valid, 1 invalid, 2 usage error.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
}
PLACEHOLDER = re.compile(r"<[^<>]+>")
RPC_KEYS = {"jsonrpc", "id", "method", "params", "result", "error"}


def schema_files():
    root = os.path.join(SKILL_DIR, "references")
    for dirpath, _, names in os.walk(root):
        if os.path.basename(dirpath) not in ("schemas", "ops"):
            continue
        for n in sorted(names):
            if n.endswith(".json") and n != "openapi.min.json":
                yield os.path.join(dirpath, n)


def product_of(path):
    rel = os.path.relpath(path, os.path.join(SKILL_DIR, "references"))
    return rel.split(os.sep)[0]


def find_schema(name):
    if os.path.isfile(name):
        return name
    want = name[:-5] if name.endswith(".json") else name
    product, _, stem = want.rpartition("/")
    hits = [p for p in schema_files()
            if os.path.basename(p)[:-5] == stem and (not product or product_of(p) == product)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise LookupError("no schema named %r; run --list" % name)
    rels = ", ".join(product_of(p) + "/" + os.path.basename(p)[:-5] for p in hits)
    raise LookupError("%r is ambiguous, pick one: %s" % (name, rels))


def resolve(ref, root, base):
    """Return (schema, root, base) for a local `#/...` or a relative `file.json#/...` ref."""
    target, _, pointer = ref.partition("#")
    if target:
        base = os.path.normpath(os.path.join(os.path.dirname(base), target))
        with open(base, encoding="utf-8") as fh:
            root = json.load(fh)
    node = root
    for part in [p for p in pointer.split("/") if p]:
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node, root, base


def check(value, schema, root, base, path, errors, skipped=None):
    if not isinstance(schema, dict):
        return
    if isinstance(value, str) and PLACEHOLDER.fullmatch(value):
        if skipped is not None:
            skipped.append(path)
        return
    if "$ref" in schema:
        sub, sub_root, sub_base = resolve(schema["$ref"], root, base)
        check(value, sub, sub_root, sub_base, path, errors, skipped)
    for sub in schema.get("allOf", []):
        check(value, sub, root, base, path, errors, skipped)
    for key in ("anyOf", "oneOf"):
        if key in schema:
            ok = 0
            for sub in schema[key]:
                trial = []
                check(value, sub, root, base, path, trial)
                ok += not trial
            if ok == 0 or (key == "oneOf" and ok > 1):
                errors.append("%s: matches %d of the %s branches" % (path, ok, key))
    if value is None and schema.get("nullable"):
        return
    types = schema.get("type")
    if types is not None:
        types = types if isinstance(types, list) else [types]
        if not any(TYPES.get(t, lambda v: True)(value) for t in types):
            errors.append("%s: expected %s, got %s" % (path, "/".join(types), kind(value)))
            return
    if "const" in schema and value != schema["const"]:
        errors.append("%s: must be %s" % (path, json.dumps(schema["const"])))
    if "enum" in schema and value not in schema["enum"]:
        errors.append("%s: %s is not one of %s" % (path, json.dumps(value), json.dumps(schema["enum"])))
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append("%s: %r does not match %s" % (path, value, schema["pattern"]))
        if len(value) < schema.get("minLength", 0):
            errors.append("%s: shorter than %d" % (path, schema["minLength"]))
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append("%s: longer than %d" % (path, schema["maxLength"]))
    if TYPES["number"](value):
        for key, bad in (("minimum", lambda v, b: v < b), ("maximum", lambda v, b: v > b),
                         ("exclusiveMinimum", lambda v, b: v <= b),
                         ("exclusiveMaximum", lambda v, b: v >= b)):
            if isinstance(schema.get(key), (int, float)) and bad(value, schema[key]):
                errors.append("%s: %s violates %s %s" % (path, value, key, schema[key]))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append("%s: fewer than %d items" % (path, schema["minItems"]))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append("%s: more than %d items" % (path, schema["maxItems"]))
        for i, item in enumerate(value):
            check(item, schema.get("items", {}), root, base, "%s[%d]" % (path, i), errors, skipped)
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append("%s: missing required %r" % (path, key))
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            sub = "%s.%s" % (path, key)
            if key in props:
                check(item, props[key], root, base, sub, errors, skipped)
            elif extra is False:
                errors.append("%s: not allowed by the schema" % sub)
            elif isinstance(extra, dict):
                check(item, extra, root, base, sub, errors, skipped)


def kind(value):
    for name in ("boolean", "integer", "number", "string", "array", "object", "null"):
        if TYPES[name](value):
            return name
    return type(value).__name__


def coerce_form(value, schema):
    """Form values are strings; turn them into the numbers the schema names."""
    if not isinstance(value, dict):
        return value
    out = {}
    for key, item in value.items():
        t = schema.get("properties", {}).get(key, {}).get("type")
        if isinstance(item, str) and t in ("integer", "number"):
            try:
                item = int(item) if t == "integer" and re.fullmatch(r"-?\d+", item) else float(item)
                if t == "number" and item == int(item):
                    item = int(item)
            except ValueError:
                pass
        out[key] = item
    return out


def load_payload(arg):
    raw = sys.stdin.read() if arg == "-" else open(arg, encoding="utf-8").read()
    text = raw.strip()
    if text.startswith(("{", "[")):
        return json.loads(text), False
    pairs = urllib.parse.parse_qsl(text, keep_blank_values=True)
    if not pairs:
        raise ValueError("payload is neither JSON nor form-urlencoded")
    return dict(pairs), True


def pick(doc, part, status):
    if "requestBody" in doc or "responses" in doc:
        part = part or "request"
        if part == "request":
            return (doc.get("requestBody") or {}).get("schema"), "request"
        resp = doc.get("responses", {}).get(str(status)) or {}
        return resp.get("schema"), "response %s" % status
    part = part or ("params" if "params" in doc else "body")
    return doc.get(part), part


def list_schemas(text):
    for path in schema_files():
        doc = json.load(open(path, encoding="utf-8"))
        name = product_of(path) + "/" + os.path.basename(path)[:-5]
        what = " ".join(doc[k] for k in ("method", "path", "endpoint", "summary")
                        if isinstance(doc.get(k), str))
        line = "%-44s %s" % (name, re.sub(r"\s+", " ", what).strip()[:110])
        if not text or text.lower() in line.lower():
            print(line)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("schema", nargs="?")
    ap.add_argument("payload", nargs="?")
    ap.add_argument("--part", choices=["params", "result", "body", "query", "path",
                                       "request", "response"])
    ap.add_argument("--status", default="200")
    ap.add_argument("--list", action="store_true", help="list schemas, optionally filtered by SCHEMA as text")
    a = ap.parse_args(argv)
    if a.list:
        list_schemas(a.schema)
        return 0
    if not a.schema or not a.payload:
        ap.print_usage(sys.stderr)
        return 2
    try:
        path = find_schema(a.schema)
    except LookupError as e:
        print("validate.py: %s" % e, file=sys.stderr)
        return 2
    doc = json.load(open(path, encoding="utf-8"))
    schema, label = pick(doc, a.part, a.status)
    if not isinstance(schema, dict):
        print("validate.py: %s has no %s schema" % (os.path.basename(path), label), file=sys.stderr)
        return 2
    try:
        value, is_form = load_payload(a.payload)
    except (OSError, ValueError) as e:
        print("validate.py: cannot read %s: %s" % (a.payload, e), file=sys.stderr)
        return 2
    if isinstance(value, dict) and label in ("params", "result") and set(value) <= RPC_KEYS \
            and ("jsonrpc" in value or "method" in value or "error" in value or label in value):
        if label == "result" and "error" in value:
            print("JSON-RPC error response, not a result: %s" % json.dumps(value["error"])[:300])
            return 1
        value = value.get(label)  # unwrap the JSON-RPC envelope
    elif label == "result" and isinstance(value, dict) and "data" in value \
            and set(value) <= {"success", "data", "error"}:
        if value.get("success") is False:
            print("error response, not a result: %s" % json.dumps(value.get("error"))[:300])
            return 1
        value = value["data"]  # unwrap the {success, data} envelope
    if is_form or schema.get("x-in") in ("form", "query"):
        value = coerce_form(value, schema)
    errors, skipped = [], []
    check(value, schema, doc, path, "$", errors, skipped)
    rel = os.path.relpath(path, SKILL_DIR)
    if errors:
        print("INVALID %s (%s): %d problem(s)" % (rel, label, len(errors)))
        for e in errors:
            print("  " + e)
        return 1
    note = ", %d placeholder value(s) not checked" % len(skipped) if skipped else ""
    print("OK %s (%s%s)" % (rel, label, note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
