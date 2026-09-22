#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_catalog.py — turn the raw engine-analysis JSONL into an agent-consumable
catalogue for the OmniMod 3D asset library.

Inputs
  <LIB>/_analysis/models.jsonl     produced by AnalyzeModels.java (real engine parse)
  sources.json                     source/pack -> licence, category, homepage

Outputs (all under <LIB>/)
  catalog/models.jsonl             full enriched record per model
  catalog/index.min.json           compact array — what an agent loads to search
  catalog/models.csv               spreadsheet-friendly
  catalog/STATS.md                 measured totals
  catalog/by-category/<cat>.md     per-category listings
  catalog/by-pack/<pack>.md        per-pack listings
  catalog/tags.json                tag -> model ids (inverted index)
  README.md  AGENTS.md  CREDITS.md  LICENSE.md
"""
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(ROOT), "omnimod-3d-library")
CAT = os.path.join(LIB, "catalog")

BUDGET_TRIS = 30000

# ----------------------------------------------------------------------------
# Tag vocabulary — GENERAL keyword rules (no per-model hardcoding).
#
# IMPORTANT: each rule body is an alternation that gets wrapped as
#     \b(?:BODY)(?:s|es)?\b
# so every alternative must match a WHOLE word (optionally pluralised).
# Without that wrapper the leading \b would guard only the first alternative and
# substrings would leak — e.g. "crate" contains "rat" and "catapult" contains
# "cat", which silently mis-tagged dozens of props as `creature`.
# ----------------------------------------------------------------------------
TAG_RULES = [
    ("wall",          r"wall|fence|railing|balustrade|palisade|parapet|hedge|barrier"),
    ("door",          r"door|gate|gateway|portcullis|hatch|doorway"),
    ("window",        r"window|shutter|pane|skylight|glass"),
    ("roof",          r"roof|shingle|thatch|gable|eave|chimney|dormer|awning"),
    ("floor",         r"floor|ground|pavement|path|road|street|sidewalk|plank|platform|tile"),
    ("stairs",        r"stair|step|ramp|ladder|escalator"),
    ("pillar",        r"pillar|column|post|beam|arch|support|brace|strut"),
    ("building",      r"building|house|home|hut|cabin|tower|castle|church|shop|store|"
                      r"tavern|inn|temple|tomb|shrine|garage|warehouse|silo|barn|windmill|"
                      r"cottage|mansion|palace|barrack|fort|mill|bakery|bank|hotel|station"),
    ("furniture",     r"chair|table|desk|bed|sofa|couch|bench|stool|shelf|bookcase|cabinet|"
                      r"drawer|wardrobe|dresser|counter|stove|fridge|toilet|sink|bathtub|"
                      r"furniture|rug|carpet|curtain|lamp|chandelier|candle|mirror"),
    ("container",     r"crate|barrel|chest|box|basket|bin|bottle|jar|bucket|bag|"
                      r"coffin|sack|pot|vase|carton|package|can|keg|tank|ammo|magazine"),
    ("tree",          r"tree|pine|oak|birch|palm|bush|shrub|foliage|branch|log|stump|"
                      r"leaf|leaves|plant|flower|grass|fern|mushroom|cactus|vine|trunk|root"),
    ("rock",          r"rock|stone|boulder|cliff|pebble|gravel|mountain|cave|crystal|ore|"
                      r"gem|ruby|emerald|diamond|coal|iron|gold|quartz"),
    ("water",         r"water|river|lake|pond|sea|ocean|well|fountain|bridge|dock|pier|"
                      r"boat|ship|raft|canoe|submarine|buoy|anchor|harbor"),
    ("vehicle",       r"car|truck|van|bus|tractor|tank|bike|motorcycle|cart|wagon|"
                      r"train|trailer|vehicle|suv|kart|tram|lorry|bulldozer"),
    ("aircraft",      r"plane|aircraft|jet|helicopter|heli|rocket|shuttle|drone|balloon|"
                      r"airship|spaceship|ufo|satellite|fighter"),
    ("weapon",        r"sword|axe|bow|arrow|spear|dagger|knife|gun|pistol|rifle|blaster|"
                      r"cannon|bomb|grenade|shield|bullet|turret|club|hammer|mace|"
                      r"scythe|staff|wand|weapon|catapult|ballista|mine|missile"),
    ("tool",          r"tool|wrench|screwdriver|saw|shovel|pickaxe|hoe|rake|"
                      r"drill|pliers|mallet|crowbar|anvil|furnace|workbench|hammer"),
    ("food",          r"food|apple|banana|bread|meat|fruit|vegetable|carrot|potato|"
                      r"cake|pizza|burger|coffee|tea|beer|wine|plate|bowl|"
                      r"cup|mug|potion|cheese|egg|corn|pumpkin|berry|sushi|donut|"
                      r"sandwich|salad|soup|juice|drink|meal"),
    ("character",     r"character|human|man|woman|boy|girl|person|people|npc|"
                      r"hero|adventurer|knight|wizard|villager|worker|soldier|guard|"
                      r"pirate|ninja|robot|android|zombie|skeleton|ghost|goblin|orc|"
                      r"player|body|head|hand|arm|leg|torso|survivor|protagonist|"
                      r"skater|doctor|chef|farmer|miner|blacksmith"),
    ("creature",      r"monster|creature|beast|dragon|slime|spider|bat|wolf|bear|"
                      r"lion|tiger|snake|dinosaur|dino|animal|dog|cat|cow|pig|sheep|"
                      r"chicken|bird|shark|whale|frog|rat|mouse|horse|deer|"
                      r"fox|rabbit|elephant|penguin|crab|octopus|insect|bee|"
                      r"fish|eagle|owl|boar|goat|duck|camel|monkey"),
    ("interior",      r"interior|indoor|kitchen|bathroom|bedroom|livingroom|office|"
                      r"restaurant|cafe|classroom|laboratory|hospital"),
    ("city",          r"city|urban|apartment|skyscraper|downtown|"
                      r"commercial|industrial|suburban|neighborhood"),
    ("medieval",      r"medieval|castle|knight|village|tavern|blacksmith|market|"
                      r"kingdom|fortress|dungeon|fantasy|rpg|wizard|sword|shield|"
                      r"peasant|throne|joust|heraldry"),
    ("scifi",         r"scifi|space|alien|futuristic|cyber|neon|laser|plasma|"
                      r"mech|spaceship|reactor|hologram|robot|console|panel"),
    ("nature",        r"nature|forest|jungle|field|meadow|garden|desert|swamp|"
                      r"mountain|island|beach|terrain|hill|valley"),
    ("industrial",    r"industrial|factory|machine|pipe|conveyor|generator|"
                      r"scaffold|crane|refinery|turbine|silo|depot|hangar"),
    ("decor",         r"decor|ornament|banner|flag|sign|poster|painting|frame|"
                      r"statue|sculpture|monument|vase|carpet|rug|curtain|"
                      r"lantern|torch|brazier|trophy|medal|plaque|mural"),
    ("sports",        r"sport|ball|goal|hoop|racket|skate|golf|soccer|football|"
                      r"basketball|tennis|arena|stadium|trampoline|bowling"),
    ("toy",           r"toy|block|brick|puzzle|game|dice|card|chess|marble|"
                      r"coaster|arcade|pinball|minigolf|domino|spinner"),
    ("holiday",       r"holiday|christmas|halloween|easter|santa|snowman|"
                      r"gift|present|wreath|spooky|pumpkin|grave|tombstone|"
                      r"candy|lantern|festive|newyear"),
    ("rail",          r"rail|track|tram|subway|tunnel|locomotive|wagon"),
    ("signage",       r"sign|signage|billboard|banner|poster|label|marker|arrow|"
                      r"notice|advert"),
]

# Pack-name hints: a pack's own name is the strongest category signal.
PACK_CATEGORY = [
    (r"furniture", "furniture"),
    (r"building|town|city|castle|house|village|tower|brick|marble|hexagon|urban|"
     r"suburban|commercial|industrial|space-station", "buildings"),
    (r"character|characters|blocky|protagonist|survivor|retro-fantasy", "characters"),
    (r"pet|animal|nature|forest|cave|watercraft", "nature-creatures"),
    (r"car|train|race|toy-car|road|coaster|boat|skate|golf|platformer|arcade|arena",
     "vehicles-games"),
    (r"food|market|survival|holiday|pirate|graveyard|space|factory|blaster|dungeon|"
     r"prototype|mini", "props-environments"),
]


def load_sources():
    with io.open(os.path.join(ROOT, "sources.json"), encoding="utf-8") as f:
        return json.load(f)


def classify_pack(pack):
    p = pack.lower()
    for rx, cat in PACK_CATEGORY:
        if re.search(rx, p):
            return cat
    return "props-environments"


def tag_model(rec, pack):
    hay = (rec.get("name", "") + " " + rec.get("dir", "") + " " + pack).lower()
    tags = set()
    for tag, body in TAG_RULES:
        # whole-word match on every alternative, plural tolerated
        if re.search(r"\b(?:" + body + r")(?:s|es)?\b", hay):
            tags.add(tag)
    return sorted(tags)


def animatability(rec):
    """What kind of animation is possible, judged from real parsed structure."""
    names = [n for n in rec.get("groupNames", []) if n and n != "default"]
    g = len(names)
    if g >= 3:
        return "per-part", g
    if g == 2:
        return "two-part", g
    if g == 1:
        return "whole-model", g
    return "whole-model", 0


def main():
    src = load_sources()
    jsonl = os.path.join(LIB, "_analysis", "models.jsonl")
    if not os.path.isfile(jsonl):
        raise SystemExit("missing %s — run AnalyzeModels first" % jsonl)

    os.makedirs(CAT, exist_ok=True)
    records = []
    for line in io.open(jsonl, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        rel = r["file"].replace("\\", "/")
        parts = rel.split("/")
        # The analyser walks <LIB>/models, so `file` is
        #   <source>/<pack>/.../<name>.obj
        source = parts[0] if len(parts) > 1 else "unknown"
        pack = parts[1] if len(parts) > 2 else source
        r["source"] = source
        r["pack"] = pack
        r["id"] = "%s/%s/%s" % (source, pack, r["name"])
        r["category"] = classify_pack(pack)
        r["tags"] = tag_model(r, pack)
        mode, n = animatability(r)
        r["animMode"] = mode
        r["animatableParts"] = n
        r["usable"] = bool(r.get("parseOk") and not r.get("empty") and r.get("triangles", 0) > 0)
        r["textured"] = any((m.get("texture") or "").strip() for m in r.get("materialDetail", []))
        r["license"] = src["licenses"].get(source, {}).get("spdx", "UNKNOWN")
        records.append(r)

    usable = [r for r in records if r["usable"]]
    rejected = [r for r in records if not r["usable"]]

    # ---- write the agent-facing compact index -------------------------------
    compact = []
    for r in usable:
        compact.append({
            "id": r["id"],
            "name": r["name"],
            "source": r["source"],
            "pack": r["pack"],
            "category": r["category"],
            "tags": r["tags"],
            "tri": r["triangles"],
            "grp": r["groups"],
            "anim": r["animMode"],
            "uv": r["hasUV"],
            "tex": r["textured"],
            "size": [r["sizeX"], r["sizeY"], r["sizeZ"]],
            "file": r["file"],
            "bytes": r["bytes"],
        })
    compact.sort(key=lambda x: x["id"])

    with io.open(os.path.join(CAT, "index.min.json"), "w", encoding="utf-8") as f:
        json.dump({"count": len(compact), "models": compact}, f,
                  ensure_ascii=False, separators=(",", ":"))

    with io.open(os.path.join(CAT, "models.jsonl"), "w", encoding="utf-8") as f:
        for r in sorted(records, key=lambda x: x["id"]):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with io.open(os.path.join(CAT, "models.csv"), "w", encoding="utf-8") as f:
        f.write("id,name,source,pack,category,tags,triangles,vertices,groups,animMode,"
                "hasUV,textured,sizeX,sizeY,sizeZ,bytes,file\n")
        for r in sorted(usable, key=lambda x: x["id"]):
            f.write('%s,"%s",%s,%s,%s,"%s",%d,%d,%d,%s,%s,%s,%.3f,%.3f,%.3f,%d,%s\n' % (
                r["id"], r["name"], r["source"], r["pack"], r["category"],
                " ".join(r["tags"]), r["triangles"], r["vertices"], r["groups"],
                r["animMode"], r["hasUV"], r["textured"],
                r["sizeX"], r["sizeY"], r["sizeZ"], r["bytes"], r["file"]))

    # ---- inverted tag index -------------------------------------------------
    inv = defaultdict(list)
    for r in usable:
        for t in r["tags"]:
            inv[t].append(r["id"])
    with io.open(os.path.join(CAT, "tags.json"), "w", encoding="utf-8") as f:
        json.dump({k: sorted(v) for k, v in sorted(inv.items())}, f, ensure_ascii=False)

    # ---- per-category / per-pack markdown ----------------------------------
    bycat = defaultdict(list)
    bypack = defaultdict(list)
    for r in usable:
        bycat[r["category"]].append(r)
        bypack["%s/%s" % (r["source"], r["pack"])].append(r)

    os.makedirs(os.path.join(CAT, "by-category"), exist_ok=True)
    for cat, rs in sorted(bycat.items()):
        rs.sort(key=lambda x: (x["triangles"], x["id"]))
        with io.open(os.path.join(CAT, "by-category", cat + ".md"), "w", encoding="utf-8") as f:
            f.write("# %s — %d models\n\n" % (cat, len(rs)))
            f.write("| id | tri | size (blocks) | anim | tags |\n|---|---|---|---|---|\n")
            for r in rs:
                f.write("| `%s` | %d | %.1f×%.1f×%.1f | %s | %s |\n" % (
                    r["id"], r["triangles"], r["sizeX"], r["sizeY"], r["sizeZ"],
                    r["animMode"], " ".join(r["tags"][:6])))

    os.makedirs(os.path.join(CAT, "by-pack"), exist_ok=True)
    for pk, rs in sorted(bypack.items()):
        rs.sort(key=lambda x: x["id"])
        fn = pk.replace("/", "__") + ".md"
        with io.open(os.path.join(CAT, "by-pack", fn), "w", encoding="utf-8") as f:
            f.write("# %s — %d models\n\n" % (pk, len(rs)))
            f.write("| model | tri | groups | size (blocks) | textured |\n|---|---|---|---|---|\n")
            for r in rs:
                f.write("| `%s` | %d | %d | %.2f×%.2f×%.2f | %s |\n" % (
                    r["name"], r["triangles"], r["groups"],
                    r["sizeX"], r["sizeY"], r["sizeZ"], "yes" if r["textured"] else "no"))

    # ---- stats --------------------------------------------------------------
    tris = sorted(r["triangles"] for r in usable)
    sizes = [r["bytes"] for r in usable]
    src_count = Counter(r["source"] for r in usable)
    cat_count = Counter(r["category"] for r in usable)
    anim_count = Counter(r["animMode"] for r in usable)
    tag_count = Counter(t for r in usable for t in r["tags"])

    def med(a):
        return a[len(a) // 2] if a else 0

    with io.open(os.path.join(CAT, "STATS.md"), "w", encoding="utf-8") as f:
        f.write("# Library statistics (measured)\n\n")
        f.write("| metric | value |\n|---|---|\n")
        f.write("| models parsed | %d |\n" % len(records))
        f.write("| models USABLE | %d |\n" % len(usable))
        f.write("| models rejected (unusable) | %d |\n" % len(rejected))
        f.write("| total triangles | %d |\n" % sum(tris))
        f.write("| median triangles | %d |\n" % med(tris))
        f.write("| max triangles | %d |\n" % (tris[-1] if tris else 0))
        f.write("| within 30k budget | %d |\n" % sum(1 for t in tris if t <= BUDGET_TRIS))
        f.write("| total OBJ bytes | %d |\n" % sum(sizes))
        f.write("\n## by source\n\n| source | models |\n|---|---|\n")
        for k, v in src_count.most_common():
            f.write("| %s | %d |\n" % (k, v))
        f.write("\n## by category\n\n| category | models |\n|---|---|\n")
        for k, v in cat_count.most_common():
            f.write("| %s | %d |\n" % (k, v))
        f.write("\n## animation capability (from parsed o/g groups)\n\n")
        f.write("| mode | models | meaning |\n|---|---|---|\n")
        meaning = {"per-part": "3+ named parts — per-part keyframe animation",
                   "two-part": "2 named parts — e.g. a hinged door",
                   "whole-model": "no named parts — whole-model transform only"}
        for k, v in anim_count.most_common():
            f.write("| %s | %d | %s |\n" % (k, v, meaning.get(k, "")))
        f.write("\n## top tags\n\n| tag | models |\n|---|---|\n")
        for k, v in tag_count.most_common(40):
            f.write("| %s | %d |\n" % (k, v))

    # ---- rejected models (quality gate) ------------------------------------
    with io.open(os.path.join(CAT, "rejected.jsonl"), "w", encoding="utf-8") as f:
        for r in sorted(rejected, key=lambda x: x["id"]):
            reason = ("unparsable" if not r.get("parseOk")
                      else ("no-triangles" if r.get("triangles", 0) == 0 else "empty"))
            f.write(json.dumps({"id": r["id"], "file": r["file"], "bytes": r["bytes"],
                                "reason": reason}, ensure_ascii=False) + "\n")

    # ---- credits ------------------------------------------------------------
    authors = {
        "kenney": ("Kenney", "https://kenney.nl/assets/category:3D"),
        "kaykit": ("Kay Lousberg", "https://kaylousberg.com/game-assets"),
        "quaternius": ("Quaternius", "https://quaternius.com"),
        "polypizza": ("various Poly Pizza contributors", "https://poly.pizza"),
    }
    with io.open(os.path.join(CAT, "CREDITS.md"), "w", encoding="utf-8") as f:
        f.write("# Credits\n\n")
        f.write("Every model in this library is **CC0 1.0** — attribution is NOT "
                "required. The authors are listed here as a matter of good practice.\n\n")
        f.write("| source | author | models | homepage |\n|---|---|---|---|\n")
        for k in sorted(src_count, key=lambda x: -src_count[x]):
            a, u = authors.get(k, (k, ""))
            f.write("| `%s` | %s | %d | %s |\n" % (k, a, src_count[k], u))
        f.write("\n## Packs\n\n| pack | models |\n|---|---|\n")
        for k, v in sorted(bypack.items()):
            f.write("| `%s` | %d |\n" % (k, len(v)))

    print("records=%d usable=%d rejected=%d" % (len(records), len(usable), len(rejected)))
    print("categories:", dict(cat_count))
    print("anim:", dict(anim_count))


if __name__ == "__main__":
    main()
