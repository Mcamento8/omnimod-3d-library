# OmniMod 3D Asset Library

**5952 CC0 3D models in Wavefront OBJ — free for commercial use, no attribution required.**

A machine-readable model library built for **map and mod development**: props, furniture, buildings, characters, creatures, vehicles, nature and terrain parts. Every model ships as OBJ + MTL + the PNG textures its material references.

> **For AI agents: read [`AGENTS.md`](AGENTS.md) first.** You can choose a model from `catalog/index.min.json` alone — no download needed — then fetch just the one you picked.

---

## Measured contents

| metric | value |
|---|---|
| models | **5952** |
| total triangles | 3,042,518 |
| median triangles / model | 236 |
| largest model | 21,760 triangles |
| models within the 30 000-triangle engine budget | 5952 of 5952 |
| fully textured (UV + PNG) | 4924 |
| with texture coordinates | 5952 |
| multi-part (part-animatable) | 216 |
| OBJ payload | 152.2 MB |
| packs | 57 |
| unusable models rejected by the engine parser | 3 |

### By source

| source | models | author | licence |
|---|---|---|---|
| `kenney` | 4701 | Kenney — kenney.nl | CC0 1.0 |
| `kaykit` | 1251 | Kay Lousberg — kaylousberg.com | CC0 1.0 |

### By category

| category | models |
|---|---|
| `props-environments` | 2441 |
| `buildings` | 1554 |
| `vehicles-games` | 1133 |
| `nature-creatures` | 461 |
| `furniture` | 214 |
| `characters` | 149 |

### Animation capability (measured from the parsed `o`/`g` groups)

| mode | models | meaning |
|---|---|---|
| `per-part` | 216 | 3+ named parts — animate a door, a wheel, a limb independently |
| `two-part` | 232 | 2 named parts — e.g. a hinged lid |
| `whole-model` | 5504 | no named parts — move/rotate/scale the whole model only |

---

## Layout

```
catalog/
  index.min.json      <- the ONE file an agent needs to search everything
  models.jsonl        <- full per-model record (engine-parsed geometry + materials)
  models.csv          <- spreadsheet view
  tags.json           <- inverted tag -> model-id index
  STATS.md            <- measured statistics
  CREDITS.md          <- authors (not required by CC0, recorded anyway)
  rejected.jsonl      <- models dropped by the quality gate, with the reason
  by-category/*.md    <- human-browsable listings
  by-pack/*.md
models/<source>/<pack>/
  <name>.obj  <name>.mtl  Textures/*.png  LICENSE.txt
thumbs/
  <source>__<pack>__<name>.png   <- 160x160 render from the engine's own parser
  _coverage.tsv                  <- shape-fills-frame signal per model
tools/
  omni3d_search.py    <- query the catalogue from the command line
  omni3d_fetch.py     <- download only the models you chose (clone or HTTPS)
  omni3d_upload.py    <- push chosen models into a RUNNING OmniMod game
```

## Quick start

```bash
# what is in here?
python tools/omni3d_search.py --stats

# find a small, textured, part-animatable piece of furniture
python tools/omni3d_search.py --tag furniture --max-tri 500 --textured --limit 10

# take exactly one model, ready to use
python tools/omni3d_fetch.py --id kenney/furniture-kit/chair --dest ./out
```

## Why OBJ only

The target engine (OmniMod OMNI3D) consumes **Wavefront OBJ + MTL + PNG**. Kenney and KayKit both publish FBX and GLB copies of the same meshes; shipping them would triple the repository and add nothing. One format, one truth.

## Licence

CC0 1.0 Universal — public domain. Commercial use allowed, **no attribution required**, no share-alike, no non-commercial clause. See [`LICENSE.md`](LICENSE.md) and the per-pack `LICENSE.txt` files.

## Provenance

Every model is downloaded from the author's own distribution and reduced to its OBJ deliverable. Geometry, materials, groups, UVs and real-world size were then measured by running the **target engine's own OBJ parser** over each file, so the catalogue describes what the engine will actually load — not what a generic third-party tool reports.

*Rejected on purpose:* models the parser could not turn into at least one triangle are excluded from the catalogue and listed in `catalog/rejected.jsonl` with their reason. Nothing is silently dropped.
