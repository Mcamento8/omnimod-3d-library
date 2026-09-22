#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
omni3d_upload.py — push chosen library models into the RUNNING game through the
OmniMod agent bridge (POST /omni/model3d/upload), so they become placeable with
`/omni3d place`.

This closes the loop: search -> fetch -> upload -> place.

Requires the in-game agent link to be running (default http://127.0.0.1:26911)
and its bearer token. Get the token from the project's omnimod_agent_token.txt
(OMNI_TOKEN=...) or pass --token.

Usage
  python omni3d_upload.py --id kenney/furniture-kit/chair --world test
  python omni3d_upload.py --id kenney/furniture-kit/chair --name my_chair --dry-run
  python omni3d_upload.py --tag furniture --max-tri 500 --limit 5 --world test

Notes
  - The bridge gates state-changing calls behind a context ack. This tool sends
    the ack automatically when the bridge answers 428.
  - The engine caps an uploaded OBJ at 8 MB of text; oversized models are
    reported and skipped rather than silently truncated.
"""
import argparse
import base64
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_CATALOG = os.path.join(REPO, "catalog", "index.min.json")
DEFAULT_TOKEN_FILE = os.path.join(os.path.dirname(REPO), "omnimod_agent_token.txt")
MAX_OBJ_BYTES = 8 * 1024 * 1024


def read_token(path):
    try:
        with io.open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("OMNI_TOKEN="):
                    return line.strip().split("=", 1)[1]
    except Exception:
        pass
    return None


class Bridge(object):
    def __init__(self, base, token, world=None):
        self.base = base.rstrip("/")
        self.token = token
        self.world = world
        self.acked = False

    def _req(self, path, body=None, method=None):
        url = self.base + path
        data = None
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if self.world:
            headers["X-Omni-Map"] = self.world
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers,
                                     method=method or ("POST" if data else "GET"))
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                return e.code, json.loads(raw)
            except Exception:
                return e.code, {"raw": raw[:400]}

    def ack_context(self):
        """Satisfy the context-first gate: read the pack, quote its fingerprint."""
        st, ctx = self._req("/omni/context?mode=link")
        if st != 200:
            return False, "context read failed: %s" % st
        fp = ctx.get("fingerprint") or ctx.get("packFingerprint")
        if not fp:
            return False, "no fingerprint in context"
        st2, res = self._req("/omni/context/ack", {"fingerprint": fp})
        self.acked = (st2 == 200)
        return self.acked, "ack %s" % st2

    def upload(self, name, obj_text, mtl_text, profile=None):
        body = {"name": name, "obj": obj_text}
        if mtl_text:
            body["mtl"] = mtl_text
        if profile:
            body["profile"] = profile
        st, res = self._req("/omni/model3d/upload", body)
        if st == 428 and not self.acked:
            ok, msg = self.ack_context()
            if ok:
                st, res = self._req("/omni/model3d/upload", body)
        return st, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:26911")
    ap.add_argument("--token", default=None)
    ap.add_argument("--token-file", default=DEFAULT_TOKEN_FILE)
    ap.add_argument("--world", default=None)
    ap.add_argument("--catalog", default=DEFAULT_CATALOG)
    ap.add_argument("--id", action="append", default=[])
    ap.add_argument("--tag", default="")
    ap.add_argument("--category", default="")
    ap.add_argument("--max-tri", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--name", default=None, help="override the model name (single id only)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = args.token or read_token(args.token_file)
    if not token and not args.dry_run:
        print("no token: pass --token or --token-file", file=sys.stderr)
        return 2

    with io.open(args.catalog, encoding="utf-8") as f:
        models = json.load(f)["models"]
    index = {m["id"]: m for m in models}

    chosen = list(args.id)
    if args.tag or args.category or args.max_tri:
        for m in models:
            if args.tag and args.tag not in m.get("tags", []):
                continue
            if args.category and m["category"] != args.category:
                continue
            if args.max_tri and m["tri"] > args.max_tri:
                continue
            chosen.append(m["id"])
        if args.limit:
            chosen = chosen[:args.limit]
    if not chosen:
        print("nothing selected", file=sys.stderr)
        return 2

    br = Bridge(args.base, token, args.world)
    if not args.dry_run:
        ok, msg = br.ack_context()
        print("[context] %s" % msg)

    done = 0
    for mid in chosen:
        m = index.get(mid)
        if not m:
            print("SKIP %s (not in catalogue)" % mid)
            continue
        obj_path = os.path.join(REPO, m["file"].replace("/", os.sep))
        with io.open(obj_path, encoding="utf-8", errors="replace") as f:
            obj_text = f.read()
        if len(obj_text.encode("utf-8")) > MAX_OBJ_BYTES:
            print("SKIP %s (OBJ exceeds the engine's 8 MB cap)" % mid)
            continue
        mtl_path = re.sub(r"\.obj$", ".mtl", obj_path)
        mtl_text = None
        if os.path.isfile(mtl_path):
            with io.open(mtl_path, encoding="utf-8", errors="replace") as f:
                mtl_text = f.read()
        name = args.name if (args.name and len(chosen) == 1) else m["name"]
        profile = {"displayName": m["name"], "scale": 1.0, "collision": "auto",
                   "axisFix": "flip_xz"}
        if args.dry_run:
            print("DRY  %-52s name=%-28s obj=%dB mtl=%s" % (
                mid, name, len(obj_text.encode("utf-8")),
                len(mtl_text.encode("utf-8")) if mtl_text else "none"))
            done += 1
            continue
        st, res = br.upload(name, obj_text, mtl_text, profile)
        okflag = isinstance(res, dict) and res.get("ok")
        print("%-4s %-52s %s" % ("OK" if okflag else "FAIL", mid,
                                 res.get("model") or res.get("error") or st))
        if okflag:
            done += 1
    print("\nuploaded/verified: %d/%d" % (done, len(chosen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
