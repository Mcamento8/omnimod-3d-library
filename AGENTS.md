# AGENTS.md — how an AI agent uses this library

This repository is a **machine-readable catalogue of CC0 3D models** for building
Minecraft-like maps and mods (OmniMod / any engine that eats Wavefront OBJ).

**The design rule: an agent must be able to CHOOSE a model without downloading it.**
All decision data lives in one small file. The models themselves are only fetched
after the choice is made.

---

## 1. The one file you need

```
catalog/index.min.json
```

Fetch it once (a few hundred KB) and you can answer every selection question.
If you are working remotely without a clone:

```
https://raw.githubusercontent.com/Mcamento8/omnimod-3d-library/main/catalog/index.min.json
```

Shape:

```jsonc
{
  "count": 5952,
  "models": [
    {
      "id":       "kenney/furniture-kit/chair",
      "name":     "chair",
      "source":   "kenney",
      "pack":     "furniture-kit",
      "category": "furniture",
      "tags":     ["furniture"],
      "tri":      128,            // triangles after the ENGINE parsed it
      "grp":      1,              // display groups (independently animatable parts)
      "anim":     "whole-model",  // whole-model | two-part | per-part
      "uv":       true,           // texture coordinates present
      "tex":      true,           // a PNG texture is referenced by the MTL
      "size":     [0.5, 0.9, 0.5],// REAL size in blocks (1 OBJ unit == 1 block)
      "file":     "models/kenney/furniture-kit/chair.obj",
      "bytes":    4210
    }
  ]
}
```

Everything above was produced by **parsing the file with the engine's own OBJ
loader**, not by a third-party tool — so `tri`, `grp`, `uv`, `size` are what the
game will actually see.

---

## 2. Selection rules that matter

| Question | Field to read | Rule of thumb |
|---|---|---|
| Will it render at all? | `tri` | only entries with `tri > 0` are listed — everything unparsable was already rejected |
| Will it look right? | `uv`, `tex` | `tex:true` + `uv:true` = fully textured; `tex:false` = flat material colour |
| Can I animate parts of it? | `anim`, `grp` | `per-part` (3+ named groups) lets you move a door, a wheel, a limb. `whole-model` can only be moved/rotated as a whole |
| How big is it in the world? | `size` | already in **blocks**. A `size` of `[1,1,1]` is a single block; `[40,12,30]` is a large building |
| Will it hurt performance? | `tri` | budget: **≤ 30 000 triangles per model**, ≤ 150 000 per scene |
| What is it? | `tags`, `category`, `pack` | `tags` is a general keyword classification; `category` is the pack's dominant theme |

### Choosing by intent

- **"a chair"** → `category=furniture`, `tags` contains `furniture`
- **"a large building"** → `category=buildings` and sort by `size`
- **"a creature I can animate"** → `tags` contains `creature` or `character`, prefer `anim=per-part`
- **"something cheap for a village"** → sort ascending by `tri`, filter `max_size` small

---

## 3. Fetch only what you picked

Local clone:

```bash
python tools/omni3d_fetch.py --id kenney/furniture-kit/chair --dest ./out
```

No clone (downloads straight from the repo over HTTPS):

```bash
python tools/omni3d_fetch.py \
  --remote https://raw.githubusercontent.com/Mcamento8/omnimod-3d-library/main \
  --id kenney/furniture-kit/chair \
  --dest ./out
```

Both produce:

```
out/kenney__furniture-kit__chair/
  chair.obj
  chair.mtl
  Textures/colormap.png
  chair.obj.model3d.json      <- ready for POST /omni/model3d/upload
```

The `.model3d.json` is the **OmniMod OMNI3D profile**: `scale:1.0`,
`collision:"auto"`, `axisFix:"flip_xz"`, plus a `_source` block recording where
the model came from.

---

## 4. Search from the command line

```bash
python tools/omni3d_search.py --query "wooden chair"
python tools/omni3d_search.py --tag furniture --max-tri 800 --textured
python tools/omni3d_search.py --category buildings --anim per-part --limit 20
python tools/omni3d_search.py --id kenney/furniture-kit/chair
python tools/omni3d_search.py --tags        # the whole tag vocabulary
python tools/omni3d_search.py --stats       # measured totals
```

`--json` gives machine output. Exit code 1 means "no match".

---

## 5. Preview images — see the shape before you commit

```
thumbs/<source>__<pack>__<name>.png
```

A 160×160 z-buffered 3/4-view render produced by the engine's own parser:
same axis fix, same group/material split, textures sampled from the real MTL.
`thumbs/_coverage.tsv` gives `id<TAB>visiblePixelFraction`, a cheap signal for
"does this shape actually fill its frame" (useful to spot flat decals vs volumes).

Vision-capable agents can read the PNG directly to confirm a shape matches the
request before downloading the mesh.

---

## 6. What is in here, and what is not

**In:** OBJ + MTL + the PNG textures the MTL references. Nothing else.

**Deliberately excluded:** FBX / GLB / BLEND duplicates of the same models.
They triple the size and this library's consumer is an OBJ-only pipeline.

**Excluded on purpose (quality gate):** any model the engine's parser could not
turn into at least one triangle. Those are listed in `catalog/rejected.jsonl`
with the reason, so nothing is silently dropped.

---

## 7. Licence — why you can use all of it

Every model is **CC0 1.0 Universal (Public Domain Dedication)**:
commercial use allowed, **no attribution required**, no share-alike, no
non-commercial clause. `catalog/CREDITS.md` records the authors anyway, because
good practice costs nothing and protects you if an upstream licence ever changes.

Per-pack notices live next to the models: `models/<source>/<pack>/LICENSE.txt`.

---

## 8. Recommended agent workflow

1. `GET catalog/index.min.json` — one small request.
2. Filter in memory: `category`, `tags`, `tri`, `size`, `anim`, `tex`.
3. Optionally read `thumbs/<id>.png` to confirm the shape.
4. `omni3d_fetch.py --id <id>` for the chosen models only.
5. Feed the produced `*.obj.model3d.json` to `POST /omni/model3d/upload`
   (OmniMod) or load the OBJ with any standard importer.
