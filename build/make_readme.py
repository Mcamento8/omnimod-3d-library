#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_readme.py — generate the library README from the measured catalogue, so the
published numbers can never drift from the actual contents.
"""
import io
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(ROOT), "omnimod-3d-library")
CAT = os.path.join(LIB, "catalog")


def main():
    with io.open(os.path.join(CAT, "index.min.json"), encoding="utf-8") as f:
        data = json.load(f)
    models = data["models"]
    with io.open(os.path.join(CAT, "models.jsonl"), encoding="utf-8") as f:
        full = [json.loads(l) for l in f if l.strip()]
    usable = [r for r in full if r.get("usable")]
    rejected = [r for r in full if not r.get("usable")]

    src = Counter(m["source"] for m in models)
    cat = Counter(m["category"] for m in models)
    anim = Counter(m["anim"] for m in models)
    packs = Counter("%s/%s" % (m["source"], m["pack"]) for m in models)
    tris = sorted(m["tri"] for m in models)
    total_tris = sum(tris)
    textured = sum(1 for m in models if m.get("tex"))
    with_uv = sum(1 for m in models if m.get("uv"))
    per_part = sum(1 for m in models if m["anim"] == "per-part")
    obj_bytes = sum(m["bytes"] for m in models)
    over_budget = sum(1 for t in tris if t > 30000)

    def human(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024 or unit == "GB":
                return "%.1f %s" % (n, unit) if unit != "B" else "%d B" % n
            n /= 1024.0

    lines = []
    A = lines.append
    A("# OmniMod 3D Asset Library")
    A("")
    A("**%d CC0 3D models in Wavefront OBJ — free for commercial use, no attribution required.**" % len(models))
    A("")
    A("A machine-readable model library built for **map and mod development**: props, "
      "furniture, buildings, characters, creatures, vehicles, nature and terrain parts. "
      "Every model ships as OBJ + MTL + the PNG textures its material references.")
    A("")
    A("> **For AI agents: read [`AGENTS.md`](AGENTS.md) first.** You can choose a model "
      "from `catalog/index.min.json` alone — no download needed — then fetch just the one "
      "you picked.")
    A("")
    A("---")
    A("")
    A("## Measured contents")
    A("")
    A("| metric | value |")
    A("|---|---|")
    A("| models | **%d** |" % len(models))
    A("| total triangles | %s |" % "{:,}".format(total_tris))
    A("| median triangles / model | %d |" % tris[len(tris) // 2])
    A("| largest model | %s triangles |" % "{:,}".format(tris[-1]))
    A("| models within the 30 000-triangle engine budget | %d of %d |" % (len(models) - over_budget, len(models)))
    A("| fully textured (UV + PNG) | %d |" % sum(1 for m in models if m.get("tex") and m.get("uv")))
    A("| with texture coordinates | %d |" % with_uv)
    A("| multi-part (part-animatable) | %d |" % per_part)
    A("| OBJ payload | %s |" % human(obj_bytes))
    A("| packs | %d |" % len(packs))
    A("| unusable models rejected by the engine parser | %d |" % len(rejected))
    A("")
    A("### By source")
    A("")
    A("| source | models | author | licence |")
    A("|---|---|---|---|")
    A("| `kenney` | %d | Kenney — kenney.nl | CC0 1.0 |" % src.get("kenney", 0))
    A("| `kaykit` | %d | Kay Lousberg — kaylousberg.com | CC0 1.0 |" % src.get("kaykit", 0))
    A("")
    A("### By category")
    A("")
    A("| category | models |")
    A("|---|---|")
    for k, v in cat.most_common():
        A("| `%s` | %d |" % (k, v))
    A("")
    A("### Animation capability (measured from the parsed `o`/`g` groups)")
    A("")
    A("| mode | models | meaning |")
    A("|---|---|---|")
    mean = {"per-part": "3+ named parts — animate a door, a wheel, a limb independently",
            "two-part": "2 named parts — e.g. a hinged lid",
            "whole-model": "no named parts — move/rotate/scale the whole model only"}
    for k in ("per-part", "two-part", "whole-model"):
        if anim.get(k):
            A("| `%s` | %d | %s |" % (k, anim[k], mean[k]))
    A("")
    A("---")
    A("")
    A("## Layout")
    A("")
    A("```")
    A("catalog/")
    A("  index.min.json      <- the ONE file an agent needs to search everything")
    A("  models.jsonl        <- full per-model record (engine-parsed geometry + materials)")
    A("  models.csv          <- spreadsheet view")
    A("  tags.json           <- inverted tag -> model-id index")
    A("  STATS.md            <- measured statistics")
    A("  CREDITS.md          <- authors (not required by CC0, recorded anyway)")
    A("  rejected.jsonl      <- models dropped by the quality gate, with the reason")
    A("  by-category/*.md    <- human-browsable listings")
    A("  by-pack/*.md")
    A("models/<source>/<pack>/")
    A("  <name>.obj  <name>.mtl  Textures/*.png  LICENSE.txt")
    A("thumbs/")
    A("  <source>__<pack>__<name>.png   <- 160x160 render from the engine's own parser")
    A("  _coverage.tsv                  <- shape-fills-frame signal per model")
    A("tools/")
    A("  omni3d_search.py    <- query the catalogue from the command line")
    A("  omni3d_fetch.py     <- download only the models you chose (clone or HTTPS)")
    A("  omni3d_upload.py    <- push chosen models into a RUNNING OmniMod game")
    A("```")
    A("")
    A("## Quick start")
    A("")
    A("```bash")
    A("# what is in here?")
    A("python tools/omni3d_search.py --stats")
    A("")
    A("# find a small, textured, part-animatable piece of furniture")
    A("python tools/omni3d_search.py --tag furniture --max-tri 500 --textured --limit 10")
    A("")
    A("# take exactly one model, ready to use")
    A("python tools/omni3d_fetch.py --id kenney/furniture-kit/chair --dest ./out")
    A("```")
    A("")
    A("## Why OBJ only")
    A("")
    A("The target engine (OmniMod OMNI3D) consumes **Wavefront OBJ + MTL + PNG**. "
      "Kenney and KayKit both publish FBX and GLB copies of the same meshes; shipping "
      "them would triple the repository and add nothing. One format, one truth.")
    A("")
    A("## Licence")
    A("")
    A("CC0 1.0 Universal — public domain. Commercial use allowed, **no attribution "
      "required**, no share-alike, no non-commercial clause. See [`LICENSE.md`](LICENSE.md) "
      "and the per-pack `LICENSE.txt` files.")
    A("")
    A("## Provenance")
    A("")
    A("Every model is downloaded from the author's own distribution and reduced to its "
      "OBJ deliverable. Geometry, materials, groups, UVs and real-world size were then "
      "measured by running the **target engine's own OBJ parser** over each file, so the "
      "catalogue describes what the engine will actually load — not what a generic "
      "third-party tool reports.")
    A("")
    A("*Rejected on purpose:* models the parser could not turn into at least one "
      "triangle are excluded from the catalogue and listed in `catalog/rejected.jsonl` "
      "with their reason. Nothing is silently dropped.")

    with io.open(os.path.join(LIB, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("README.md written (%d models)" % len(models))


if __name__ == "__main__":
    main()
