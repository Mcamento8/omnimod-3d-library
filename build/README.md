# build/ — how this library was produced

Everything here is reproducible. The pipeline is:

```
fetch_kenney.py  +  fetch_kaykit.py     download, reduce to the OBJ deliverable
        |
AnalyzeModels.java                      parse EVERY model with the engine's own OBJ loader
        |
build_catalog.py                        classify, tag, index, per-pack listings
        |
RenderThumbs.java                       z-buffered preview PNG per model
        |
make_readme.py                          README from the measured catalogue
```

`run_pipeline.py` runs steps 2-5 in order.

## Requirements

* Python 3.8+ (standard library only — no pip installs)
* A JDK (17 used here) for `AnalyzeModels` and `RenderThumbs`
* `ObjModelLoader.java` + `ObjModelData.java` from the target engine, so the
  analysis and the renders describe what the engine will actually load

## Running it

```bash
python build/fetch_kenney.py      # 50 kits -> models/kenney/
python build/fetch_kaykit.py      # CC0 mirror -> models/kaykit/
python build/run_pipeline.py      # analyze -> catalog -> thumbs -> readme
```

`run_pipeline.py` expects the engine sources next to the library. Adjust the
`JAVA_HOME`, `CLS` and `OMNI3D` constants at the top of that file for your
checkout; the other scripts are path-independent (they derive everything from
their own location).

## Notes on the sources

* **Kenney** — the 50 slugs in `kenney_kits.json` are scraped from
  `kenney.nl/assets/category:3D`; each kit page is then scraped for its direct
  `.zip`. Only the `Models/OBJ format/**` tree is extracted.
* **KayKit** — pulled as a tarball from the public CC0 mirror
  `GeorgeQLe/assets-kaykit-3d-props` (upstream: kaylousberg.com). Only
  `Assets/obj/**` plus its `Textures/` are extracted.
* **Quaternius** — not included. Their packs are distributed through Google Drive
  folders and itch.io with no scriptable direct download.
* **Poly Haven** — not included. Verified via their API that model downloads are
  offered as `blend / fbx / gltf / usd` only; there is no OBJ, and the meshes are
  high-poly (well beyond the engine's per-model triangle budget).

## The quality gate

A model is kept only if the engine's parser turns it into **at least one
triangle**. Everything else is written to `catalog/rejected.jsonl` with its
reason — nothing is dropped silently. In this build, 3 of 5,955 upstream files
were rejected: they are empty 70-byte OBJ placeholders (zero vertices, zero
faces) shipped by the upstream author.
