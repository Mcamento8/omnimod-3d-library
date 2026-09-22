#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_kenney.py — download every Kenney 3D kit (CC0) and keep ONLY the OBJ
deliverable (OBJ + MTL + the textures that the MTL references).

Why OBJ-only: the OmniMod OMNI3D engine consumes Wavefront OBJ + MTL + PNG.
FBX/GLB/BLEND duplicates would triple the repository size for zero value.

Output layout (repo-ready):
  <OUT>/<kit-slug>/<model>.obj
  <OUT>/<kit-slug>/<model>.mtl
  <OUT>/<kit-slug>/Textures/*.png
  <OUT>/<kit-slug>/LICENSE.txt        (CC0 notice, copied from the pack)
"""
import io
import json
import os
import re
import sys
import time
import urllib.request
import zipfile

UA = {"User-Agent": "Mozilla/5.0 (compatible; OmniModAssetHarvester/1.0)"}
ROOT = os.path.dirname(os.path.abspath(__file__))
# The library is its OWN git repository (nested inside the project so it never
# pollutes the game repo). Scripts + raw zips live in the (gitignored) build dir.
LIB = os.path.join(os.path.dirname(ROOT), "omnimod-3d-library")
OUT = os.path.join(LIB, "models", "kenney")
RAW = os.path.join(ROOT, "_raw")


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def get_text(url, timeout=60):
    return get(url, timeout).decode("utf-8", "replace")


def kit_zip_url(slug):
    """Scrape a kit page for its direct .zip download link."""
    html = get_text("https://kenney.nl/assets/" + slug)
    urls = re.findall(r"https://kenney\.nl/media/pages/assets/" + re.escape(slug) +
                      r"/[0-9a-f]+-\d+/[^'\" <>]+\.zip", html)
    if not urls:
        return None
    # prefer the highest version suffix (…_2.0.zip beats …_1.0.zip)
    def ver(u):
        m = re.search(r"_(\d+)\.(\d+)\.zip$", u)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    urls = sorted(set(urls), key=ver)
    return urls[-1]


def keep_member(name):
    """Only OBJ / MTL / texture images that the OBJ deliverable needs."""
    low = name.lower()
    if "/obj format/" not in low and not low.endswith((".obj", ".mtl")):
        return False
    return low.endswith((".obj", ".mtl", ".png", ".jpg", ".jpeg", ".tga", ".bmp"))


def flatten_target(name):
    """Models/OBJ format/sub/x.obj -> x.obj ; Textures/y.png -> Textures/y.png"""
    n = name.replace("\\", "/")
    parts = [p for p in n.split("/") if p and p != "."]
    low = [p.lower() for p in parts]
    if "obj format" in low:
        i = low.index("obj format")
        rest = parts[i + 1:]
    else:
        rest = parts[-1:]
    if not rest:
        return None
    # collapse any nested folders: keep only the leaf for models, keep
    # a Textures/ prefix for images so MTL relative refs still resolve
    leaf = rest[-1]
    if leaf.lower().endswith((".png", ".jpg", ".jpeg", ".tga", ".bmp")):
        return "Textures/" + leaf
    return leaf


def harvest_kit(slug, results):
    outdir = os.path.join(OUT, slug)
    if os.path.isdir(outdir) and os.path.isfile(os.path.join(outdir, ".done")):
        results[slug] = {"status": "cached"}
        return results[slug]
    try:
        zurl = kit_zip_url(slug)
    except Exception as e:
        results[slug] = {"status": "page_error", "error": str(e)}
        return results[slug]
    if not zurl:
        results[slug] = {"status": "no_zip"}
        return results[slug]

    os.makedirs(RAW, exist_ok=True)
    zpath = os.path.join(RAW, slug + ".zip")
    if not os.path.isfile(zpath) or os.path.getsize(zpath) < 1024:
        try:
            data = get(zurl, timeout=180)
            with open(zpath, "wb") as f:
                f.write(data)
        except Exception as e:
            results[slug] = {"status": "download_error", "error": str(e), "zip": zurl}
            return results[slug]

    n_obj = n_mtl = n_tex = 0
    try:
        zf = zipfile.ZipFile(zpath)
    except Exception as e:
        results[slug] = {"status": "bad_zip", "error": str(e)}
        return results[slug]

    os.makedirs(outdir, exist_ok=True)
    seen = set()
    for info in zf.infolist():
        if info.is_dir():
            continue
        name = info.filename
        if not keep_member(name):
            continue
        tgt = flatten_target(name)
        if not tgt or tgt in seen:
            continue
        seen.add(tgt)
        dest = os.path.join(outdir, tgt.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            with zf.open(info) as src, open(dest, "wb") as dst:
                dst.write(src.read())
        except Exception:
            continue
        low = tgt.lower()
        if low.endswith(".obj"):
            n_obj += 1
        elif low.endswith(".mtl"):
            n_mtl += 1
        else:
            n_tex += 1

    # CC0 licence notice — copied from the pack if present, else generated
    lic = None
    for info in zf.infolist():
        base = info.filename.replace("\\", "/").split("/")[-1].lower()
        if base in ("license.txt", "license", "licence.txt") or base.endswith("_license.txt"):
            try:
                lic = zf.read(info).decode("utf-8", "replace")
                break
            except Exception:
                pass
    if lic is None:
        lic = ("This asset pack is licensed CC0 1.0 Universal (Public Domain Dedication).\n"
               "Source: https://kenney.nl/assets/%s\n"
               "You may use it for any purpose, including commercial, with no attribution required.\n"
               "License: https://creativecommons.org/publicdomain/zero/1.0/\n" % slug)
    with open(os.path.join(outdir, "LICENSE.txt"), "w", encoding="utf-8") as f:
        f.write(lic)
    with open(os.path.join(outdir, ".done"), "w") as f:
        f.write("ok\n")

    results[slug] = {"status": "ok", "obj": n_obj, "mtl": n_mtl, "tex": n_tex,
                     "zip": zurl, "zipBytes": os.path.getsize(zpath)}
    return results[slug]


def main():
    with open(os.path.join(ROOT, "kenney_kits.json"), encoding="utf-8") as f:
        kits = json.load(f)
    results = {}
    for i, slug in enumerate(kits, 1):
        t0 = time.time()
        r = harvest_kit(slug, results)
        print("[%2d/%d] %-34s %s (%.1fs)" % (i, len(kits), slug, r.get("status"),
                                             time.time() - t0), flush=True)
    with open(os.path.join(ROOT, "kenney_harvest_report.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, ensure_ascii=False)
    ok = [k for k, v in results.items() if v.get("status") in ("ok", "cached")]
    print("\nDONE kits=%d ok=%d" % (len(results), len(ok)))


if __name__ == "__main__":
    main()
