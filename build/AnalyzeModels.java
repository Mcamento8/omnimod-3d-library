import java.io.BufferedWriter;
import java.io.File;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

import net.lax1dude.eaglercraft.v1_8.omni3d.ObjModelData;
import net.lax1dude.eaglercraft.v1_8.omni3d.ObjModelLoader;

/**
 * AnalyzeModels — walk a directory of Wavefront OBJ files and emit ONE JSON
 * record per model, using the REAL OmniMod OMNI3D parser (ObjModelLoader).
 *
 * This is the point: the metadata describes what the ENGINE actually sees after
 * parsing, not what a generic third-party tool would report. An agent that reads
 * this catalogue can therefore decide whether a model is usable in OmniMod
 * WITHOUT downloading it.
 *
 * Fields that matter for selection:
 *   triangles            - render + collision cost
 *   groups / groupNames  - how many independently animatable parts the model has
 *                          (>1 means per-part animation is possible)
 *   materials / textures - what it will look like; whether a PNG is required
 *   hasUV / hasNormals   - texture-mapping and lighting quality
 *   bounds / size        - real world size in BLOCKS (1 OBJ unit == 1 block)
 *   fitsBudget           - <= 30000 triangles (OmniMod per-model budget)
 *   parseOk / empty      - whether the engine can load it at all
 *
 * Usage:
 *   java AnalyzeModels <modelsRoot> <outJsonl> [axisFix]
 */
public final class AnalyzeModels {

    private static final int BUDGET_TRIS = 30000;
    private static final String DEFAULT_AXIS = "flip_xz";

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("usage: AnalyzeModels <modelsRoot> <outJsonl> [axisFix]");
            System.exit(2);
        }
        File root = new File(args[0]);
        File out = new File(args[1]);
        String axis = args.length > 2 ? args[2] : DEFAULT_AXIS;

        List<File> objs = new ArrayList<File>();
        collect(root, objs);
        objs.sort(new Comparator<File>() {
            public int compare(File a, File b) {
                return a.getAbsolutePath().compareTo(b.getAbsolutePath());
            }
        });

        BufferedWriter w = new BufferedWriter(new OutputStreamWriter(
                new FileOutputStream(out), StandardCharsets.UTF_8));
        int ok = 0, empty = 0, failed = 0;
        for (int i = 0; i < objs.size(); ++i) {
            File f = objs.get(i);
            String rec = analyze(root, f, axis);
            if (rec == null) {
                failed++;
            } else {
                w.write(rec);
                w.write("\n");
                if (rec.contains("\"parseOk\":false") || rec.contains("\"empty\":true")) {
                    empty++;
                } else {
                    ok++;
                }
            }
            if ((i + 1) % 500 == 0) {
                System.out.println("  ... " + (i + 1) + "/" + objs.size());
                w.flush();
            }
        }
        w.close();
        System.out.println("ANALYZED total=" + objs.size() + " usable=" + ok
                + " emptyOrFailed=" + empty + " thrown=" + failed);
    }

    private static void collect(File dir, List<File> out) {
        File[] kids = dir.listFiles();
        if (kids == null) {
            return;
        }
        for (File k : kids) {
            if (k.isDirectory()) {
                collect(k, out);
            } else if (k.getName().toLowerCase().endsWith(".obj")) {
                out.add(k);
            }
        }
    }

    private static String analyze(File root, File f, String axis) {
        try {
            String text = new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8);
            String base = f.getName().substring(0, f.getName().length() - 4);
            File mtlFile = new File(f.getParentFile(), base + ".mtl");
            String mtlText = mtlFile.isFile()
                    ? new String(Files.readAllBytes(mtlFile.toPath()), StandardCharsets.UTF_8)
                    : null;

            ObjModelData d = ObjModelLoader.parse(base, text, mtlText, axis);

            String rel = relativize(root, f);
            String relDir = rel.contains("/") ? rel.substring(0, rel.lastIndexOf('/')) : "";

            int groups = d.groups.size();
            int tris = d.totalTriangles();
            int verts = 0;
            boolean anyUV = false, anyNrm = false;
            int emptyGroups = 0;
            List<String> groupNames = new ArrayList<String>();
            for (int i = 0; i < d.groups.size(); ++i) {
                ObjModelData.ObjDisplayGroup g = d.groups.get(i);
                verts += g.positions.size() / 3;
                if (!g.uvs.isEmpty()) anyUV = true;
                if (!g.normals.isEmpty()) anyNrm = true;
                if (g.triangleCount() == 0) emptyGroups++;
                if (!groupNames.contains(g.groupName)) groupNames.add(g.groupName);
            }

            StringBuilder sb = new StringBuilder(1024);
            sb.append('{');
            kv(sb, "file", rel, true);
            kv(sb, "dir", relDir, false);
            kv(sb, "name", base, false);
            kn(sb, "bytes", f.length());
            kv(sb, "sha256", sha256(f), false);
            kb(sb, "parseOk", d != null);
            kb(sb, "empty", d.isEmpty());
            kn(sb, "triangles", tris);
            kn(sb, "vertices", verts);
            kn(sb, "groups", groups);
            kn(sb, "emptyGroups", emptyGroups);
            kb(sb, "hasUV", anyUV);
            kb(sb, "hasNormals", anyNrm);
            kb(sb, "fitsBudget", tris > 0 && tris <= BUDGET_TRIS);
            kb(sb, "multiGroup", groupNames.size() > 1);
            ka(sb, "groupNames", groupNames);
            ka(sb, "objectGroups", d.objectGroupNames);

            List<String> mats = new ArrayList<String>(d.materials.keySet());
            ka(sb, "materials", mats);
            sb.append(",\"materialDetail\":[");
            int mi = 0;
            for (Map.Entry<String, ObjModelData.ObjMaterial> e : d.materials.entrySet()) {
                ObjModelData.ObjMaterial m = e.getValue();
                if (mi++ > 0) sb.append(',');
                sb.append('{');
                kv(sb, "name", m.name, true);
                kf(sb, "r", m.r); kf(sb, "g", m.g); kf(sb, "b", m.b); kf(sb, "alpha", m.alpha);
                kb(sb, "doubleSided", m.doubleSided);
                kv(sb, "texture", m.textureRef == null ? "" : m.textureRef, false);
                sb.append('}');
            }
            sb.append(']');

            kf(sb, "minX", d.minX); kf(sb, "minY", d.minY); kf(sb, "minZ", d.minZ);
            kf(sb, "maxX", d.maxX); kf(sb, "maxY", d.maxY); kf(sb, "maxZ", d.maxZ);
            kf(sb, "sizeX", d.sizeX()); kf(sb, "sizeY", d.sizeY()); kf(sb, "sizeZ", d.sizeZ());
            kf(sb, "maxHorizontal", d.maxHorizontal());
            kb(sb, "flatLike", d.sizeY() < 0.06F && d.maxHorizontal() > 0.5F);
            sb.append('}');
            return sb.toString();
        } catch (Throwable t) {
            System.err.println("FAIL " + f + " : " + t);
            return null;
        }
    }

    private static String relativize(File root, File f) {
        String r = root.getAbsolutePath().replace('\\', '/');
        String a = f.getAbsolutePath().replace('\\', '/');
        if (a.startsWith(r)) {
            a = a.substring(r.length());
            if (a.startsWith("/")) a = a.substring(1);
        }
        return a;
    }

    private static String sha256(File f) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] b = md.digest(Files.readAllBytes(f.toPath()));
            StringBuilder sb = new StringBuilder(b.length * 2);
            for (int i = 0; i < b.length; ++i) {
                sb.append(Character.forDigit((b[i] >> 4) & 0xF, 16));
                sb.append(Character.forDigit(b[i] & 0xF, 16));
            }
            return sb.toString();
        } catch (Throwable t) {
            return "";
        }
    }

    // ---- tiny JSON writers (no dependencies, TeaVM-free) ----

    /** Writes a quoted JSON key (with the separating comma when not first). */
    private static void key(StringBuilder sb, String k, boolean first) {
        if (!first) sb.append(',');
        sb.append('"'); esc(sb, k); sb.append("\":");
    }

    private static void kv(StringBuilder sb, String k, String v, boolean first) {
        key(sb, k, first);
        sb.append('"'); esc(sb, v == null ? "" : v); sb.append('"');
    }

    private static void kn(StringBuilder sb, String k, long v) {
        key(sb, k, false); sb.append(v);
    }

    private static void kf(StringBuilder sb, String k, float v) {
        key(sb, k, false);
        if (Float.isNaN(v) || Float.isInfinite(v)) {
            sb.append('0');
        } else {
            sb.append(Math.round(v * 1000.0F) / 1000.0F);
        }
    }

    private static void kb(StringBuilder sb, String k, boolean v) {
        key(sb, k, false); sb.append(v);
    }

    private static void ka(StringBuilder sb, String k, List<String> v) {
        key(sb, k, false); sb.append('[');
        for (int i = 0; i < v.size(); ++i) {
            if (i > 0) sb.append(',');
            sb.append('"'); esc(sb, v.get(i)); sb.append('"');
        }
        sb.append(']');
    }

    private static void esc(StringBuilder sb, String s) {
        for (int i = 0; i < s.length(); ++i) {
            char c = s.charAt(i);
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20) {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
            }
        }
    }
}
