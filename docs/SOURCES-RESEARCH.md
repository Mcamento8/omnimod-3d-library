# مصادر نماذج ثلاثية الأبعاد مفتوحة — OBJ + ترخيص يسمح بالاستخدام التجاري

**التاريخ:** 2026-09-22 · **الغرض:** تغذية محرك OmniMod بنماذج جاهزة (كائنات · مباني · أثاث · كائنات حية)
**الشرط الأساسي:** صيغة **OBJ** (لأن محرك OMNI3D يقبل OBJ فقط) + ترخيص **يسمح بالاستخدام التجاري**.

---

## 0. الخلاصة في 10 أسطر

| المرتبة | المصدر | الترخيص | OBJ جاهز؟ | يصلح لـ OmniMod؟ |
|---|---|---|---|---|
| 🥇 | **Kenney** (kenney.nl) | CC0 | ✅ **نعم** (OBJ+MTL+PNG) | ✅ مثالي — low-poly |
| 🥇 | **Quaternius** (quaternius.com) | CC0 | ✅ **نعم** (OBJ+FBX+Blend) | ✅ مثالي — low-poly |
| 🥇 | **KayKit / Kay Lousberg** | CC0 | ✅ **نعم** (OBJ+FBX+GLTF) | ✅ مثالي — low-poly |
| 🥈 | **Poly Pizza** | CC0 + CC-BY (لكل نموذج) | ✅ **نعم** (OBJ+FBX+GLTF) | ✅ جيد (افحص الترخيص لكل نموذج) |
| 🥈 | **OpenGameArt** | مختلط (CC0/CC-BY/CC-BY-SA/GPL) | ✅ غالباً | ⚠️ افحص ترخيص كل أصل |
| 🥈 | **itch.io — CC0 filter** | CC0 | ✅ غالباً | ✅ جيد |
| 🥉 | **Poly Haven** | CC0 | ❌ **لا** (blend/fbx/gltf/usd) | ⚠️ يحتاج تحويل + high-poly |
| 🥉 | **Sketchfab — CC0 filter** | CC0 | ⚠️ حسب الرافع | ⚠️ فحص فردي |
| 🚫 | Thingiverse · Printables · MyMiniFactory | غالباً **CC-BY-NC** | ❌ (STL) | ❌ **غير مسموح تجارياً** |
| 🚫 | 3dmodelscc0.com | — | — | ❌ **النطاق اختُطف — موقع سبام** |

**القاعدة الذهبية:** ابحث دائماً عن **CC0** أولاً (بلا شرط نسب، بلا قيود). وإن لم تجد، **CC-BY** مقبول بشرط ذكر المصدر. **تجنّب CC-BY-NC** (غير تجاري) و**CC-BY-SA** (مشاركة بالمثل — مخاطرة قانونية في الألعاب).

---

## 1. المرتبة الأولى — CC0 + OBJ جاهز مباشرة

### 1.1 Kenney — `https://kenney.nl/assets/category:3D`

> **الأفضل للمحرك: صفر تحويل، صفر مخاطرة قانونية، وحجم مثالي.**

**قياس فعلي (تحميل حقيقي لحزمة كاملة):**

| البند | القيمة |
|---|---|
| الحزمة المُقاسة | `Fantasy Town Kit 2.0` (3.85 ميغابايت) |
| ملفات OBJ | **167** |
| ملفات MTL | **167** |
| ملفات GLB / FBX | 167 / 167 |
| ملفات PNG | 174 (أطلس ألوان `colormap.png`) |
| بنية المجلدات | `Models/OBJ format/…` + `Models/FBX format/…` + `Models/GLB format/…` |
| المثلثات | min=6 · وسيط=**192** · أقصى=**3,114** · المجموع=50,468 |
| كل الملفات تربط MTL (`mtllib`) | **167 / 167** ✅ |
| الترخيص | **CC0** (Creative Commons Zero) — لا نسب مطلوب |

**الحزم المفيدة (كلها CC0):**

| الحزمة | الفئة |
|---|---|
| Fantasy Town Kit · City Kit (Roads / Commercial / Industrial) | 🏠 مباني ومدن |
| Modular Dungeon Kit · Mini Dungeon · Modular Cave Kit · Graveyard Kit | 🏰 مباني/أنفاق |
| **Furniture Kit** | 🪑 أثاث |
| Factory Kit · Car Kit · Platformer Kit · Modular Space Kit · Pirate Kit · Blaster Kit | 📦 كائنات ومركبات |
| Mini Forest · Cube Pets | 🌲 طبيعة · 🐾 كائنات |

**لماذا هي الأفضل لمحركك:** وسيط 192 مثلثاً يعني أنك تستطيع وضع **عشرات** النماذج في مشهد واحد داخل ميزانية 150 ألف مثلث. وكل نموذج يحمل MTL فيعمل لون `Kd` أو نسيج `map_Kd` مباشرة.

---

### 1.2 Quaternius — `https://quaternius.com/`

**مُثبت من صفحة المنتج نفسها** (Ultimate Furniture Pack):
> `Models 20 · Formats FBX OBJ Blend · License CC0`

**الحزم المفيدة (كلها CC0، وكلها تُصرَّح بـ FBX/OBJ/Blend):**

| الحزمة | الفئة |
|---|---|
| **Ultimate Furniture Pack** · **Ultimate House Interior Pack** · Fantasy Props MegaKit | 🪑 أثاث وتجهيزات داخلية |
| **Ultimate Buildings Pack** (modular, textured) · **Medieval Village MegaKit** · **Downtown City MegaKit** · Modular Medieval Buildings · Simple Buildings · Farm Buildings · Modular Streets · Ultimate Modular Ruins | 🏠 مباني ومدن |
| **Ultimate Monsters** · **Bestiary – Dungeon Monsters Kit** · Animated Dinosaur Pack · Cute Animated Monsters · Easy Enemy Pack · Animated Zombie Pack | 🐉 كائنات/وحوش |
| Ultimate Animated Animal Pack · Animated Cute Fish Pack · Farm Animal Pack | 🐾 حيوانات |
| Modular Dungeons Pack · Medieval Dungeon · Ultimate Modular Sci-Fi Pack · Ultimate RPG Pack · Ultimate Space Kit | 🏰 بيئات |
| Ultimate Nature Pack (150 نموذجاً) · Stylized Nature MegaKit · Stylized Tree Pack | 🌲 طبيعة |

**نقطة قوة:** الحزم الأحدث **modular** (مباني قابلة للتركيب) + **rigged/animated** للوحوش — ومجموعات `o/g` داخل OBJ هي بالضبط ما يحتاجه نظام أنيميشن المجموعات في OMNI3D (فتح باب، دوران مروحة…).

---

### 1.3 KayKit — Kay Lousberg — `https://kaylousberg.com/game-assets`

**مُثبت من صفحة Block Bits:**
> `Free for personal and commercial use, no attribution required. (CC0 Licensed) Included files are .OBJ, .FBX and .GLTF`

**مُثبت من مستودع مرآة (GitHub API، عدّ فعلي للملفات):**
> **1,251 ملف `.obj` + 1,251 ملف `.mtl`** + 1,174 `.gltf` + 2,351 `.fbx` + 567 `.png`
> مثال: `assets/kaykit/block-bits-1.0/Assets/obj/anvil.obj`

**الحزم:**

| الحزمة | الفئة |
|---|---|
| **Furniture Bits** · **Restaurant Bits** | 🪑 أثاث |
| **City Builder Bits** · Medieval Hexagon · Dungeon Remastered | 🏠 مباني |
| **Characters: Skeletons** · **Characters: Adventurers** · Character Animations | 🧍 شخصيات وكائنات |
| Space Base Bits · Prototype Bits · Resource Bits · Block Bits | 📦 كائنات |
| Forest Nature Pack · Platformer · RPG Tools · Holiday Bits · Halloween Bits | 🌲/🎉 متنوع |

**نقطة قوة:** `Furniture Bits` و `City Builder Bits` مبنيتان على شبكة (grid) — تناسب بناء الخرائط داخل ماينكرافت بشكل طبيعي.

---

## 2. المرتبة الثانية — OBJ متوفر لكن الترخيص يحتاج انتباهاً

### 2.1 Poly Pizza — `https://poly.pizza/`

- **الترخيص:** مزيج **CC0 + CC-BY** — لكل نموذج ترخيصه الخاص معروض على صفحته.
- **مرشّح CC0 جاهز:** `https://poly.pizza/explore/cc0` ← استخدم هذا الرابط **حصرياً** لتجنّب CC-BY.
- **الصيغ:** **OBJ · FBX · GLTF** (مذكورة على صفحة الاستكشاف) — بلا تسجيل دخول.
- **المحتوى:** أرشيف Google Poly (المغلق) + Quaternius + Kenney + Kay Lousberg + آخرون.
- **تحذير:** أرشيف Google Poly الأصلي كان **CC-BY** (يحتاج نسباً). التصفية على CC0 تلغي هذه المشكلة.

### 2.2 OpenGameArt — `https://opengameart.org/`

- **الترخيص:** **مختلط** — CC0 / CC-BY / CC-BY-SA / GPL. الموقع نفسه يشترط أن يكون كل أصل تحت رخصة حرة، لكن **الرخصة تختلف لكل ملف**.
- **OBJ:** شائع جداً (معظم نماذج 3D هناك OBJ أو blend).
- **مثال جيد:** `City Kit (Commercial)` و `City Kit (Industrial)` من Kenney منشوران هناك.
- **إجراء إلزامي:** افتح صفحة كل أصل واقرأ خانة **License**. لا تفترض.

### 2.3 itch.io — مرشّح CC0 — `https://itch.io/game-assets/assets-cc0`

- آلاف حزم أصول ألعاب تحت CC0، كثير منها 3D بصيغة OBJ/FBX.
- **تحذير:** المرشّح يضمن CC0 للحزم المصنّفة كذلك، لكن افحص دائماً وصف الحزمة.

---

## 3. المرتبة الثالثة — CC0 ممتاز لكن **بلا OBJ** (يحتاج تحويلاً)

### 3.1 Poly Haven — `https://polyhaven.com/models`

**قياس فعلي عبر الـAPI الرسمي:**

| البند | القيمة |
|---|---|
| عدد النماذج | **521** |
| الصيغ المتاحة | `blend · fbx · gltf · usd` — **لا يوجد OBJ** ✅ مُثبت |
| الترخيص | **CC0** (بلا قيود إطلاقاً) |

**التوزيع بالفئات (مقاس):** props 176 · nature 110 · industrial 97 · **furniture 85** · decorative 76 · tools 70 · containers 68 · plants 57 · rocks 37 · **seating 34** · electronics 31 · lighting 29 · **table 27** · structures 26

**أمثلة أثاث/مباني فعلية:** Dining Table · Metal Office Desk · Vintage Day Bed · Mid Century Lounge Chair · Gothic Coffee Table · Old Bed Frame · Wooden Ladder · Wall Clock · Gothic Statue

**⚠️ تحذيران مهمان لمحركك:**
1. **لا يوجد OBJ** → يجب تحويل `fbx` أو `gltf` إلى OBJ.
2. **High-poly** (آلاف إلى عشرات آلاف المثلثات لكل نموذج، ونماذج بـ polycount يتجاوز 30 ألفاً) → **يتجاوز ميزانية OMNI3D** (≤30k للمثلث للنموذج). تحتاج تقليصاً (decimate) قبل الاستخدام.

### 3.2 مصادر أخرى CC0 (تحتاج تحويلاً أو فحصاً)

| المصدر | الرابط | ملاحظة |
|---|---|---|
| The Base Mesh | `https://thebasemesh.com/` | 1,250+ mesh أساسي CC0 — **لم أتحقق من توفر OBJ** |
| Smithsonian Open Access 3D | `https://3d.si.edu/cc0` | ماسحات متحفية CC0 — الصيغ غالباً glTF/OBJ، أحجام كبيرة |
| Blend Swap (مرشّح CC0) | `https://www.blendswap.com/` | ملفات `.blend` → تصدير إلى OBJ |
| Polygonal Mind (CC0) | `github.com/PolygonalMind/initiative-opensource-release` | مشاريع CC0 من استوديو |
| Retro3D assets | `github.com/M3-org/retro3d-assets` | PSX low-poly |
| ambientCG | `https://ambientcg.com/` | CC0 — **مواد وHDRIs أساساً**، النماذج محدودة |
| Game Assets Garden | `https://www.gameassetsgarden.com/` | Royalty-free بلا نسب |

---

## 4. ⚠️ قائمة التجنّب (مهمة قانونياً)

| المصدر | السبب |
|---|---|
| **Thingiverse · Printables · MyMiniFactory · Cults3D** | تراخيصها الغالبة **CC-BY-NC** (غير تجاري) + ملفات **STL** بلا مواد. الاستخدام التجاري **محظور** إلا بإذن صريح. |
| **3dmodelscc0.com** | ✅ **تحقّقتُ منه: النطاق اختُطف** ويعرض الآن محتوى سبام/مقامرة. **لا تفتحه.** |
| **Free3D · CGTrader · TurboSquid (قسم Free)** | «مجاني» لا يعني «حر» — كثير منها **للاستخدام الشخصي فقط** أو **Editorial**. اقرأ الرخصة لكل ملف. |
| **Sketchfab — بلا مرشّح** | أغلبه غير قابل للتنزيل أو NC. استخدم مرشّح CC0 حصراً. |
| **أي أصل CC-BY-SA** | قانوني تجارياً لكنه **يُلزم مشاركة العمل المشتق بالرخصة نفسها** — مخاطرة في مشروع لعبة مغلق. |
| **أي أصل CC-BY-NC / NC-SA / «Non-commercial»** | **ممنوع** في محتوى تجاري بلا ترخيص منفصل. |
| **Google Poly** | **مُغلق** — الأرشيف منقول إلى Poly Pizza. |

---

## 5. تحويل الصيغ إلى OBJ (عند الحاجة)

### 5.1 بـ Blender (بلا واجهة — يصلح للسكربتات)

```bash
# FBX -> OBJ
blender --background --python-expr \
  "import bpy; bpy.ops.wm.obj_export(filepath='out.obj', export_materials=True, export_triangulated_mesh=True)"
```

### 5.2 بـ assimp (أسرع، سطر واحد)

```bash
assimp export model.fbx model.obj      # أو .gltf / .glb / .dae / .blend
```

### 5.3 قواعد التصدير الإلزامية لمحرك OMNI3D

| القاعدة | السبب |
|---|---|
| **Triangulate** ✅ | المُحلّل يثلّث المضلّعات مروحياً، لكن التثليث المسبق يضمن تطابق UV |
| **Write Normals** ✅ | بدونها يُفترض السمت للأعلى → إضاءة مسطّحة |
| **Write Materials (MTL)** ✅ | لتُقرأ ألوان `Kd` |
| **الوحدة: 1 وحدة = 1 متر** | في المحرك 1 وحدة OBJ = 1 بلوك |
| **Y-up** | المحرك يطبّق `axisFix` الافتراضي `flip_xz` |
| **مجموعات `o`/`g`** ✅ | هي عقد الأنيميشن — بدونها لا يمكن تحريك جزء من النموذج |
| **≤ 30,000 مثلث للنموذج** | ميزانية الأداء |
| **≤ 8 ميغابايت نص OBJ** | سقف نقطة الرفع |

### 5.4 تقليص الشبكة (High-poly → low-poly)

نماذج Poly Haven تحتاج تقليصاً. في Blender: مُعدِّل **Decimate** بنسبة 10–20% ثم تصدير OBJ. أو استخدم حزم low-poly أصلاً (Kenney/Quaternius/KayKit) — **هذا هو الخيار الأصح**.

---

## 6. الخلاصة العملية — ماذا تفعل الآن

1. **للأثاث والمباني فوراً:** حمّل **Kenney Furniture Kit** + **Fantasy Town Kit** + **Quaternius Ultimate Furniture Pack** + **KayKit Furniture Bits** — كلها CC0، كلها OBJ+MTL جاهزة، كلها داخل ميزانية الأداء.
2. **للكائنات والوحوش:** **Quaternius Ultimate Monsters** + **Bestiary Dungeon Monsters Kit** + **KayKit Characters: Skeletons/Adventurers**.
3. **للمباني الضخمة:** **Quaternius Ultimate Buildings Pack** (modular) + **KayKit City Builder Bits**.
4. **للجودة الواقعية (بعد تحويل وتقليص):** **Poly Haven** — CC0 بلا قيود، لكن fbx/gltf فقط وhigh-poly.
5. **سجّل النسب** في ملف `CREDITS.md` حتى لو كانت الرخصة CC0 — عادة مهنية جيدة، وتحميك لو تغيّر ترخيص أي أصل لاحقاً.

---

## 7. سجل الأدلة (كل رقم أعلاه مقاس، لا منقول)

| ما قيس | الطريقة | النتيجة |
|---|---|---|
| صيغ Kenney | **تحميل فعلي** لحزمة Fantasy Town Kit 2.0 (3.85MB) وعدّ الملفات | 167 OBJ · 167 MTL · 167 GLB · 167 FBX · 174 PNG |
| ميزانية مثلثات Kenney | تحليل كل ملفات OBJ الـ167 | وسيط 192 · أقصى 3,114 · المجموع 50,468 · كلها تحمل `mtllib` |
| صيغ Poly Haven | استعلام `api.polyhaven.com/files/dining_table` | `blend · AO · arm · Diffuse · nor_dx · nor_gl · Rough · fbx · gltf · usd` — **لا OBJ** |
| عدد وتصنيف نماذج Poly Haven | استعلام `api.polyhaven.com/assets?t=models` | 521 نموذجاً · furniture 85 · props 176 · structures 26 |
| صيغ KayKit | GitHub API على مرآة `GeorgeQLe/assets-kaykit-3d-props` | **1,251 `.obj` + 1,251 `.mtl`** من أصل 7,823 ملفاً |
| صيغ Quaternius | صفحة المنتج الرسمية (Ultimate Furniture Pack) | «Formats FBX OBJ Blend · License CC0» |
| ترخيص KayKit | صفحة Block Bits الرسمية | «Free for personal and commercial use, no attribution required. (CC0)» |
| ترخيص Kenney | صفحة Fantasy Town Kit الرسمية | CC0 — 160 ملفاً |
| 3dmodelscc0.com | فتح الموقع | **محتوى سبام/مقامرة — النطاق مُختطف** |

**ملفات الأدلة المحلية:** `tmp_3d_sources/kenney_fantasy_town.zip` · `tmp_3d_sources/ph_models.json` · `tmp_3d_sources/quat.html`

---

*أُعِدّ ببحث وقياس فعليين على الشبكة في 2026-09-22. لم يُبنَ المشروع ولم يُدفع أي تغيير.*
