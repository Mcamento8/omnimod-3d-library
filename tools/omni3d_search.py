#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
omni3d_search.py — query the OmniMod 3D asset library WITHOUT downloading it.

The whole catalogue lives in one small file (catalog/index.min.json). An agent
fetches that single file and can then answer "which model do I want?" from the
metadata alone — triangles, real world size in blocks, how many independently
animatable parts, whether it is textured, licence, and the exact path.

Usage
  python omni3d_search.py --query "wooden chair"
  python omni3d_search.py --tag furniture --max-tri 800 --textured
  python omni3d_search.py --category buildings --anim per-part --limit 20
  python omni3d_search.py --id kenney/furniture-kit/chair
  python omni3d_search.py --tags                 # list the tag vocabulary
  python omni3d_search.py --stats

Options
  --catalog PATH   catalogue file (default: <repo>/catalog/index.min.json)
  --json           emit raw JSON instead of a table
  --limit N        max rows (default 25)

Exit code 1 when nothing matched — convenient in scripts.
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CATALOG = os.path.join(os.path.dirname(HERE), "catalog", "index.min.json")


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def score(m, terms):
    """Relevance: id/name hits rank above tag/category hits."""
    if not terms:
        return 0
    ident = (m["id"] + " " + m["name"]).lower()
    tags = " ".join(m.get("tags", [])).lower()
    s = 0
    for t in terms:
        if t in ident:
            s += 10
            if re.search(r"\b" + re.escape(t), ident):
                s += 5
        if t in tags:
            s += 3
        if t in m.get("category", "").lower():
            s += 2
        if t in m.get("pack", "").lower():
            s += 2
    return s


def fmt(m):
    return ("%-52s tri=%-6d size=%.1fx%.1fx%.1f anim=%-11s %s%s" % (
        m["id"], m["tri"], m["size"][0], m["size"][1], m["size"][2],
        m["anim"], "tex " if m.get("tex") else "    ",
        " ".join(m.get("tags", [])[:5])))


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--catalog", default=DEFAULT_CATALOG)
    ap.add_argument("--query", "-q", default="")
    ap.add_argument("--id", default="")
    ap.add_argument("--tag", action="append", default=[])
    ap.add_argument("--category", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--pack", default="")
    ap.add_argument("--anim", default="", help="whole-model | two-part | per-part")
    ap.add_argument("--max-tri", type=int, default=0)
    ap.add_argument("--min-tri", type=int, default=0)
    ap.add_argument("--max-size", type=float, default=0.0,
                    help="max horizontal footprint in blocks")
    ap.add_argument("--textured", action="store_true")
    ap.add_argument("--no-uv", action="store_true")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--tags", action="store_true")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    data = load(args.catalog)
    models = data["models"]

    if args.stats:
        from collections import Counter
        c = Counter(m["category"] for m in models)
        s = Counter(m["source"] for m in models)
        a = Counter(m["anim"] for m in models)
        print("total models : %d" % len(models))
        print("by source    : %s" % dict(s))
        print("by category  : %s" % dict(c))
        print("by animation : %s" % dict(a))
        print("triangles    : median=%d max=%d" % (
            sorted(m["tri"] for m in models)[len(models) // 2],
            max(m["tri"] for m in models)))
        return 0

    if args.tags:
        from collections import Counter
        c = Counter(t for m in models for t in m.get("tags", []))
        for t, n in c.most_common():
            print("%-16s %d" % (t, n))
        return 0

    if args.id:
        hit = [m for m in models if m["id"] == args.id or m["id"].endswith("/" + args.id)]
        if not hit:
            print("no model with id %r" % args.id, file=sys.stderr)
            return 1
        print(json.dumps(hit[0], indent=2, ensure_ascii=False) if args.json else fmt(hit[0]))
        return 0

    out = []
    for m in models:
        if args.tag and not all(t in m.get("tags", []) for t in args.tag):
            continue
        if args.category and m["category"] != args.category:
            continue
        if args.source and m["source"] != args.source:
            continue
        if args.pack and args.pack not in m["pack"]:
            continue
        if args.anim and m["anim"] != args.anim:
            continue
        if args.max_tri and m["tri"] > args.max_tri:
            continue
        if args.min_tri and m["tri"] < args.min_tri:
            continue
        if args.textured and not m.get("tex"):
            continue
        if args.no_uv and m.get("uv"):
            continue
        if args.max_size and max(m["size"][0], m["size"][2]) > args.max_size:
            continue
        out.append(m)

    terms = [t for t in re.split(r"[\s,]+", args.query.lower()) if t]
    if terms:
        scored = [(score(m, terms), m) for m in out]
        scored = [(s, m) for s, m in scored if s > 0]
        scored.sort(key=lambda x: (-x[0], x[1]["tri"]))
        out = [m for _, m in scored]
    else:
        out.sort(key=lambda m: (m["category"], m["tri"], m["id"]))

    if args.json:
        print(json.dumps(out[:args.limit], indent=2, ensure_ascii=False))
    else:
        for m in out[:args.limit]:
            print(fmt(m))
        print("-- %d match(es), showing %d" % (len(out), min(len(out), args.limit)),
              file=sys.stderr)
    return 0 if out else 1


if __name__ == "__main__":
    sys.exit(main())
