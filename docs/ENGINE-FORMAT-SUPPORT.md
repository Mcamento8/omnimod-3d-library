# تدقيق: دعم النماذج ثلاثية الأبعاد + رفعها من الوكلاء

**التاريخ:** 2026-09-22 · **النطاق:** OmniMod (Eaglercraft 1.8 + جسر Forge 1.20.1) · **النوع:** تدقيق كود + قياس فعلي

---

## 0. الحكم السريع (الجواب المباشر على السؤال)

| السؤال | الجواب |
|---|---|
| هل يوجد نظام يمكّن الوكيل الخارجي من رفع نماذج ثلاثية الأبعاد؟ | **نعم** — نظام `OMNI3D` بمسارات HTTP مخصّصة. |
| هل يقبل **كل** الصيغ؟ | **لا.** |
| ما الصيغة المطلوبة؟ | **Wavefront OBJ (نص ASCII)** — إلزامية. مع **MTL** اختياري (ألوان `Kd` / نسيج `map_Kd`) و**PNG** للنسيج. |
| هل يقبل glTF / GLB / FBX / STL / DAE / USDZ / PLY؟ | **لا** — في مسار نماذج العالم. مرفوضة (تصل كـ«نموذج فارغ»). |
| هل هذه الصيغ موجودة في اللعبة أصلاً؟ | نعم، لكن في **أنظمة أخرى لا يصلها الوكيل** (انظر §1). |

> **الخلاصة بجملة واحدة:** الوكيل يرفع **صيغة واحدة فقط: OBJ**. أي صيغة أخرى يجب تحويلها إلى OBJ قبل الرفع.

---

## 1. الأنظمة الأربعة للنماذج في المحرك (خريطة كاملة)

المحرك يقرأ **أربع عائلات** من صيغ النماذج، لكن كل واحدة في نظام منفصل بمصدر مختلف:

| # | النظام | الصيغة المقبولة | من يستطيع التزويد | تدخل العالم؟ | يقدر الوكيل يرفعها؟ |
|---|---|---|---|---|---|
| 1 | **OMNI3D** نماذج العالم | `.obj` + `.mtl` + `.png` | الوكيل (HTTP) · المود · أوامر `/omni3d` | ✅ نعم (كيان `omni3d:world_model`) | ✅ **نعم — OBJ فقط** |
| 2 | **نماذج JSON الماينكرافت** | `models/block/*.json` · `models/item/*.json` (عناصر `elements`/`parent`/`textures`) | المود المثبّت · حزمة الموارد | ✅ كتل وآيتمات | ❌ لا (لا مسار رفع؛ تُبنى عبر المود/الحزمة) |
| 3 | **GeckoLib / Bedrock geometry** | `.geo.json` | المود المثبّت (`assets/**`) | ✅ كيانات/آيتمات/ديكور | ❌ لا |
| 4 | **جلود اللاعبين ثلاثية الأبعاد** | `.gltf` + `.bin` · `.glb` · `.geo.json` · حزمة ZIP | اللاعب من واجهة اللعبة · مزوّد سكينات خارجي | ❌ (جسم اللاعب فقط) | ❌ لا |

**مهم:** وجود مُحلّل glTF في المحرك **لا يعني** أن الوكيل يقدر يرفع glTF إلى العالم — المُحلّل مخصّص لجلود اللاعبين، ومدخله واجهة اللعبة أو مزوّد سكينات، وليس نقطة HTTP.

---

## 2. مسار الوكيل بالتفصيل — نظام OMNI3D

### 2.1 المسارات السبعة (`AgentLinkRoutes.java:121-127`)

| الطريقة | المسار | الوظيفة |
|---|---|---|
| `GET` | `/omni/model3d/list` | النماذج المسجّلة + الموضوعة في العالم |
| `POST` | `/omni/model3d/upload` | **رفع نموذج OBJ** |
| `POST` | `/omni/model3d/place` | وضع نسخة في العالم (بتصادم وأنيميشن وتفاعل) |
| `POST` | `/omni/model3d/configure` | تعديل نسخة موضوعة (حجم/دوران/تصادم/تفاعل) |
| `POST` | `/omni/model3d/animate` | تشغيل مقطع أنيميشن |
| `POST` | `/omni/model3d/remove` | إزالة |
| `GET` | `/omni/model3d/profile` | ملف تعريف النموذج + إحصاءات الشبكة |

### 2.2 عقد الرفع (`AgentLinkMinecraftBackend.java:2675-2722`)

```jsonc
POST /omni/model3d/upload
{
  "world":  "test",            // اختياري إن كان عالم شغّال
  "name":   "my_house",        // إلزامي — أحرف/أرقام/-/_ فقط
  "obj":    "v 0 0 0\nf 1 2 3",// إلزامي (نص) — أو "objB64" (base64)
  "mtl":    "newmtl m\nKd 1 0 0", // اختياري — أو "mtlB64"
  "profile": { "scale": 1.0, "collision": "auto", "animations": {}, "interact": [] }
}
```

- **حد الحجم:** `objText.length() > 8*1024*1024` → رفض `too_large` (**8 ميغابايت نص OBJ**).
- **التخزين:** `worlds/<world>/models3d/<name>.obj` + `.mtl` + `.obj.model3d.json` (داخل حفظة العالم).
- **المعرّف:** `omni3d:<name>`.
- **الوحدة:** 1 وحدة OBJ = 1 بلوك. `scale` يضاعف الشبكة **والتصادم** معاً.
- **إصلاح المحاور:** `axisFix` — الافتراضي `flip_xz` (دوران 180° حول Y، مطابق لتصدير Blockbench).

### 2.3 الأوامر في اللعبة (`CommandOmni3D.java`)

`/omni3d` — صلاحية 2 (تعمل من الشات وكوماند بلوك والوكيل):
`place · remove · list · info · models · interaction · attack · animate · scale · rotate · move · collision · binditem · unbinditem`

### 2.4 النسيج (PNG) — كيف يصل

`/omni/model3d/upload` **لا يقبل PNG**. النسيج يُربط عبر `map_Kd` في MTL، ويُقرأ من:
1. مخزن العالم `worlds/<world>/models3d/*.png` — والوكيل يكتبه عبر
   `POST /omni/mapfiles/write {root:"worlds", path:"<world>/models3d/tex.png", encoding:"base64"}`
   (المسار **غير محمي**: الحماية تشمل فقط `level.dat`, `session.lock`, `region/`, `_dev/state/`).
2. حزمة موارد العالم (نماذج المودات).
   إن فُقد النسيج → يسقط للون المادة `Kd` (لا انهيار).

---

## 3. مصادر النماذج الثلاثة

| المصدر | الطريقة | المعرّف |
|---|---|---|
| رفع من الوكيل | `POST /omni/model3d/upload` | `omni3d:<name>` |
| مود 1.20.1 مثبّت | يضع `assets/<ns>/models3d/*.obj` (+ `.obj.model3d.json` + `.mtl` + `.png`) داخل الـJAR؛ يستخرجها `ModManager` ويسجّلها `Omni3DRuntime.scanPackModels` | `<ns>:<name>` |
| موجود في العالم | مخزن `models3d/` يُمسح عند دخول العالم (`scanWorldStore`) | كما رُفع |

---

## 4. القيود الحقيقية (بصراحة — GAPs)

| القيد | التفصيل |
|---|---|
| **صيغة واحدة** | OBJ فقط. لا glTF/GLB/FBX/STL/DAE/USDZ/PLY في مسار العالم. |
| **لا رفع نسيج في نقطة النموذج** | PNG يحتاج `mapfiles/write` منفصلاً (أو مود). |
| **لا أداة MCP مخصّصة** | قائمة الـMCP = 57 أداة، **لا يوجد** `omni_model3d_*`. الوكيل ينادي HTTP مباشرة (الـMCP يوثّق المسارات في سياق الماب و`MAP_DEV_MASTER_GUIDE` §14 فقط). |
| **8 ميغابايت** | سقف نص OBJ لكل رفع. |
| **ميزانية الأداء** | ≤30k مثلث للنموذج، ≤150k في المشهد، `collisionResolution 1.0` (2.0 للنماذج >150 بلوك). |
| **لا تحويل تلقائي** | لا يوجد مُحوِّل داخل اللعبة من صيغة إلى OBJ. |

---

## 5. الأدلة المقاسة (قياس فعلي، لا ادّعاء)

### 5.1 حزمة JVM على كود المصدر الحالي

`tmp_objfmt_harness/Harness.java` — تُصرّف **ملفات المصدر الحالية** (`ObjModelLoader.java` + `ObjModelData.java`) وتشغّلها على JDK 17:

```
PASS | OBJ plain triangle                | tris=1 groups=1
PASS | OBJ quad face -> 2 tris           | tris=2
PASS | OBJ 5-gon -> 3 tris               | tris=3
PASS | OBJ negative indices              | tris=1
PASS | OBJ v//vn no-UV                   | tris=1
PASS | OBJ o/g groups + usemtl + Kd      | groups=2 mats=2
PASS | axisFix none vs flip_xz           | raw.minX=5.0  flip.minX=-6.0
PASS | reject gltf (not OBJ)             | tris=0
PASS | reject fbx  (not OBJ)             | tris=0
PASS | reject stl  (not OBJ)             | tris=0
PASS | reject dae  (not OBJ)             | tris=0
PASS | reject geo.json (not OBJ)         | tris=0
PASS | reject glb  (not OBJ)             | tris=0
PASS | phantom f-lines -> 0 tris & isEmpty()
PASS | null OBJ -> empty (no crash)
PASS | empty OBJ -> empty (no crash)
INFO | Modular Village corpus | objs=142 parsed_ok=142 empty=0 threw=0 totalTris=28478
PASS | real corpus parses (>=90%) | 142/142
TOTAL PASS=17 FAIL=0
```

**الدلالة:** المُحلّل يقبل OBJ بكل أشكاله الواقعية (مثلثات، رباعيات، مضلّعات، فهارس سالبة، بدون UV، مجموعات `o/g`، مواد `usemtl`/`Kd`) و**يرفض** الصيغ الأخرى. الأصول المرجعية الحقيقية (Modular Village: 142 ملف OBJ، 28,478 مثلثاً) تُحلَّل 100% بلا فشل.

### 5.2 بوابة التصريف وفحص الأقواس

- `javac 17` على الملفات المعدّلة ضد أصناف المحرك المبنية → **نجح بلا أخطاء**.
- `_omnimod_scan/_brace_check.py` → **ALL BALANCED**.

---

## 6. عيب حقيقي اكتُشف وأُصلح أثناء التدقيق

**العيب (phantom group):** ملف **غير OBJ** (مثل STL) سطره `facet normal 0 0 1` يبدأ بحرف `f`، فيُعامل كسطر وجه. الرمز `1` يُحسب فهرس رأس صالحاً فيُنشئ **مجموعة عرض فارغة (0 مثلثات)**. وبما أن فحص الفراغ كان `groups.isEmpty()` فقط، كان النموذج يُعدّ **غير فارغ** ويُسجَّل كنموذج **غير مرئي** بدل أن يُرفض كـ«ليس OBJ».

**الإصلاح (عام، لا يخصّ موداً):**
- `ObjModelLoader.java` — لا تُنشأ مجموعة إلا إذا كان للوجه **≥3 رؤوس محلولة**.
- `ObjModelData.isEmpty()` — صارت `groups.isEmpty() || totalTriangles() == 0` (الفراغ = «لا هندسة قابلة للرسم»).

**القياس البعدي:** نفس الحزمة التي فشلت (`reject stl` = FAIL، `phantom` = FAIL) صارت **PASS=17 FAIL=0** بعد الإصلاح.

---

## 7. إذا أردت رفع صيغة أخرى — العملية الصحيحة

لا يوجد مُحوِّل داخل اللعبة. المسار الواقعي:

```
glTF / GLB / FBX / STL / DAE / Blend
        │  (خارج اللعبة)
        ▼
   Blender  :  File ▸ Export ▸ Wavefront (.obj)
              ✔ Triangulate   ✔ Write Normals   ✔ Write Materials (MTL)
              ✔ وحدة واحدة = 1 متر لتصبح 1 بلوك
   أو  assimp:  assimp export model.glb model.obj
        │
        ▼
   POST /omni/model3d/upload  { name, obj, mtl }
   POST /omni/mapfiles/write  { root:"worlds", path:"<world>/models3d/tex.png", encoding:"base64" }
   POST /omni/model3d/place   { model:"omni3d:<name>", x, y, z, scale }
```

**ملاحظة معمارية:** إضافة دعم glTF **لنماذج العالم** ممكنة تقنياً (المُحلّل موجود أصلاً في `GltfAssetParser.java` لجلود اللاعبين)، لكنها **غير موجودة الآن** في مسار OMNI3D، وليست نقطة ربط قائمة. لا تدّعِ غير ذلك.

---

## 8. ملفات مرجعية

- `sources/main/java/net/lax1dude/eaglercraft/v1_8/omni3d/` — كل نظام OMNI3D (13 ملفاً، 5,326 سطراً).
- `docs/project_map/43_OMNI3D_MODEL_PIPELINE.md` — خط الأنابيب الكامل.
- `docs/project_map/18_CUSTOM_3D_ITEM_RENDER_PIPELINE.md` · `19_GECKOLIB_ENTITY_RENDER_PIPELINE.md` · `01_ITEM_MODEL_PIPELINE.md` · `03_BLOCK_RENDERING_PIPELINE.md`.
- عقد الوكيل داخل اللعبة: `agent/12_OMNI_3D_MODELS.md` (يُخدَم لكل ماب، v8).
- الأداة: `tmp_objfmt_harness/Harness.java`.

---

*تدقيق مُنتَج بقياس فعلي على كود المصدر. لم يُدّعَ أي سلوك بلا دليل مقاس.*
