#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_kaykit.py — download the CC0 KayKit 3D asset collection and keep ONLY the
OBJ deliverable (OBJ + MTL + referenced PNG).

Source: the public CC0 mirror `GeorgeQLe/assets-kaykit-3d-props`
(upstream: https://kaylousberg.com/game-assets — "Free for personal and
commercial use, no attribution required. (CC0 Licensed)").

Layout produced:
  <LIB>/models/kaykit/<pack>/<model>.obj
  <LIB>/models/kaykit/<pack>/<model>.mtl
  <LIB>/models/kaykit/<pack>/Textures/*.png
  <LIB>/models/kaykit/<pack>/LICENSE.txt
"""
import io
import os
import re
import sys
import tarfile
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; OmniModAssetHarvester/1.0)"}
ROOT = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(ROOT), "omnimod-3d-library")
OUT = os.path.join(LIB, "models", "kaykit")
RAW = os.path.join(ROOT, "_raw")

REPO = "GeorgeQLe/assets-kaykit-3d-props"
BRANCHES = ["main", "master"]

KEEP = (".obj", ".mtl", ".png", ".jpg", ".jpeg", ".tga")


def fetch_tarball():
    os.makedirs(RAW, exist_ok=True)
    dest = os.path.join(RAW, "kaykit.tar.gz")
    if os.path.isfile(dest) and os.path.getsize(dest) > 1_000_000:
        print("using cached tarball")
        return dest
    last = None
    for br in BRANCHES:
        url = "https://codeload.github.com/%s/tar.gz/refs/heads/%s" % (REPO, br)
        try:
            req = urllib.request.Request(url, headers=UA)
            data = urllib.request.urlopen(req, timeout=300).read()
            with open(dest, "wb") as f:
                f.write(data)
            print("downloaded %s (%d bytes)" % (url, len(data)))
            return dest
        except Exception as e:
            last = e
            print("branch %s failed: %s" % (br, e))
    raise SystemExit("tarball download failed: %s" % last)


def pack_of(path):
    """…/assets/kaykit/<pack>/Assets/obj/x.obj -> <pack>

    The GitHub tarball prefixes every entry with a top-level directory
    (e.g. `assets-kaykit-3d-props-main/`), so locate the `kaykit` segment
    instead of assuming a fixed offset.
    """
    parts = [p for p in path.split("/") if p]
    low = [p.lower() for p in parts]
    if "kaykit" in low:
        i = low.index("kaykit")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "misc"


def main():
    tar_path = fetch_tarball()
    os.makedirs(OUT, exist_ok=True)
    # remove a stale mis-grouped run (pack detection was fixed to handle the
    # tarball's top-level directory prefix)
    stale = os.path.join(OUT, "misc")
    if os.path.isdir(stale):
        import shutil
        shutil.rmtree(stale, ignore_errors=True)
        print("removed stale misc/")

    counts = {}
    tf = tarfile.open(tar_path, "r:gz")

    # the upstream CC0 licence text, reused for every pack folder
    upstream_license = None
    for m in tf.getmembers():
        if m.isfile() and "licenses/" in m.name.lower() and m.name.lower().endswith(".txt"):
            try:
                upstream_license = tf.extractfile(m).read().decode("utf-8", "replace")
                print("upstream licence: %s" % m.name)
                break
            except Exception:
                pass

    members = [m for m in tf.getmembers() if m.isfile()]
    print("tarball members: %d" % len(members))
    for m in members:
        name = m.name
        low = name.lower()
        if not low.endswith(KEEP):
            continue
        # only the OBJ deliverable folder + its textures
        if "/obj/" not in low and "/textures/" not in low:
            continue
        if low.endswith(".png") and "/textures/" not in low:
            continue
        pack = pack_of(name)
        leaf = name.split("/")[-1]
        if low.endswith(".png"):
            rel = os.path.join(pack, "Textures", leaf)
        else:
            rel = os.path.join(pack, leaf)
        dest = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.isfile(dest) and os.path.getsize(dest) == m.size:
            continue
        try:
            src = tf.extractfile(m)
            if src is None:
                continue
            with open(dest, "wb") as f:
                f.write(src.read())
        except Exception:
            continue
        ext = leaf.rsplit(".", 1)[-1].lower()
        counts[ext] = counts.get(ext, 0) + 1
    tf.close()

    # one CC0 notice per pack
    for pack in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, pack)
        if not os.path.isdir(d):
            continue
        lic = os.path.join(d, "LICENSE.txt")
        if not os.path.isfile(lic):
            body = upstream_license
            if not body:
                body = ("KayKit — %s\n"
                        "Author: Kay Lousberg (https://kaylousberg.com/game-assets)\n"
                        "License: CC0 1.0 Universal (Public Domain Dedication)\n"
                        "\"Free for personal and commercial use, no attribution required.\"\n"
                        "https://creativecommons.org/publicdomain/zero/1.0/\n"
                        "Source mirror: https://github.com/%s\n" % (pack, REPO))
            with open(lic, "w", encoding="utf-8") as f:
                f.write(body)
    print("extracted:", counts)
    print("packs:", len([d for d in os.listdir(OUT) if os.path.isdir(os.path.join(OUT, d))]))


if __name__ == "__main__":
    main()
