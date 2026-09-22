#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
omni3d_fetch.py — pull ONLY the model files you chose, from a git clone or
straight from the public repository over HTTPS (no clone required).

Two modes:

  1) local clone
       python omni3d_fetch.py --id kenney/furniture-kit/chair --dest ./out

  2) remote (no clone) — reads the catalogue over HTTPS and downloads just the
     OBJ + its MTL + the textures the MTL references
       python omni3d_fetch.py --id kenney/furniture-kit/chair --dest ./out \
              --remote https://raw.githubusercontent.com/<owner>/<repo>/main

It writes a ready-to-use folder plus a `model3d.json` profile that the OmniMod
OMNI3D uploader accepts, so the result can be fed straight to
`POST /omni/model3d/upload`.

Exit code 1 if any requested id was not found.
"""
import argparse
import io
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_CATALOG = os.path.join(REPO, "catalog", "index.min.json")
UA = {"User-Agent": "omni3d-fetch/1.0"}


def load_catalog(path=None, remote=None):
    if remote:
        url = remote.rstrip("/") + "/catalog/index.min.json"
        req = urllib.request.Request(url, headers=UA)
        return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
    with io.open(path or DEFAULT_CATALOG, encoding="utf-8") as f:
        return json.load(f)


def read_bytes(rel, remote=None):
    """`rel` is relative to the models/ root (that is how the catalogue stores it)."""
    rel = rel.replace("\\", "/").lstrip("/")
    if remote:
        url = remote.rstrip("/") + "/models/" + rel
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=120).read()
    with open(os.path.join(REPO, "models", rel.replace("/", os.sep)), "rb") as f:
        return f.read()


def mtl_texture_refs(mtl_text):
    """Relative texture paths the MTL actually references."""
    refs = []
    for line in mtl_text.splitlines():
        s = line.strip()
        for key in ("map_Kd", "map_Ka", "map_bump", "bump", "map_d", "disp", "map_Ks"):
            if s.startswith(key + " ") or s.startswith(key + "\t"):
                parts = s.split()
                if len(parts) > 1:
                    refs.append(parts[-1].replace("\\", "/"))
                break
    return refs


def fetch_one(m, dest_root, remote=None, profile=True):
    mid = m["id"]
    outdir = os.path.join(dest_root, mid.replace("/", "__"))
    os.makedirs(outdir, exist_ok=True)

    obj_rel = m["file"]
    name = m["name"]
    obj_bytes = read_bytes(obj_rel, remote)
    with open(os.path.join(outdir, name + ".obj"), "wb") as f:
        f.write(obj_bytes)

    written = [name + ".obj"]
    mtl_rel = re.sub(r"\.obj$", ".mtl", obj_rel)
    mtl_text = None
    try:
        mtl_bytes = read_bytes(mtl_rel, remote)
        mtl_text = mtl_bytes.decode("utf-8", "replace")
        with open(os.path.join(outdir, name + ".mtl"), "wb") as f:
            f.write(mtl_bytes)
        written.append(name + ".mtl")
    except Exception:
        pass

    if mtl_text:
        for ref in mtl_texture_refs(mtl_text):
            leaf = ref.split("/")[-1]
            for cand in (ref, "Textures/" + leaf,
                         os.path.dirname(obj_rel) + "/Textures/" + leaf):
                try:
                    data = read_bytes(cand, remote)
                except Exception:
                    continue
                os.makedirs(os.path.join(outdir, "Textures"), exist_ok=True)
                with open(os.path.join(outdir, "Textures", leaf), "wb") as f:
                    f.write(data)
                written.append("Textures/" + leaf)
                break

    if profile:
        prof = {
            "id": "omni3d:" + name,
            "displayName": name,
            "scale": 1.0,
            "collision": "auto",
            "axisFix": "flip_xz",
            "_source": {
                "library": "omnimod-3d-library",
                "modelId": mid,
                "license": "CC0-1.0",
                "triangles": m["tri"],
                "sizeBlocks": m["size"],
                "animatableParts": m["grp"],
            },
        }
        with open(os.path.join(outdir, name + ".obj.model3d.json"), "w",
                  encoding="utf-8") as f:
            json.dump(prof, f, indent=2, ensure_ascii=False)
        written.append(name + ".obj.model3d.json")

    return outdir, written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", action="append", default=[], required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--catalog", default=None)
    ap.add_argument("--remote", default=None,
                    help="raw base URL, e.g. https://raw.githubusercontent.com/u/r/main")
    ap.add_argument("--no-profile", action="store_true")
    args = ap.parse_args()

    data = load_catalog(args.catalog, args.remote)
    index = {m["id"]: m for m in data["models"]}
    missing = [i for i in args.id if i not in index]
    if missing:
        print("not found: %s" % ", ".join(missing), file=sys.stderr)
    ok = 0
    for mid in args.id:
        m = index.get(mid)
        if not m:
            continue
        outdir, written = fetch_one(m, args.dest, args.remote,
                                    profile=not args.no_profile)
        print("%s -> %s (%s)" % (mid, outdir, ", ".join(written)))
        ok += 1
    return 0 if ok and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
