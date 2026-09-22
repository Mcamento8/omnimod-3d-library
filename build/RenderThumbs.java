import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.imageio.ImageIO;

import net.lax1dude.eaglercraft.v1_8.omni3d.ObjModelData;
import net.lax1dude.eaglercraft.v1_8.omni3d.ObjModelLoader;

/**
 * RenderThumbs — software-render a preview PNG for every OBJ in the library.
 *
 * Uses the REAL OmniMod OMNI3D parser (ObjModelLoader), so what you see is what
 * the engine sees: same axis fix, same group/material split, same UV stream.
 *
 * Render: orthographic 3/4 view, z-buffered, flat-shaded, textures sampled at
 * each triangle's UV centroid (falls back to the material Kd colour when the
 * material has no map_Kd, and to mid-grey when neither exists).
 *
 * Usage: java RenderThumbs <modelsRoot> <thumbsOutDir> [size] [limitPerModel]
 * Emits: <thumbsOutDir>/<source>__<pack>__<name>.png
 *        <thumbsOutDir>/_coverage.tsv  (id TAB visiblePixelFraction)
 */
public final class RenderThumbs {

    private static final int DEFAULT_SIZE = 160;
    private static final int BG = 0xFFF2F2F4;

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("usage: RenderThumbs <modelsRoot> <outDir> [size]");
            System.exit(2);
        }
        File root = new File(args[0]);
        File out = new File(args[1]);
        int size = args.length > 2 ? Integer.parseInt(args[2]) : DEFAULT_SIZE;
        out.mkdirs();

        List<File> objs = new ArrayList<File>();
        collect(root, objs);
        StringBuilder cov = new StringBuilder();

        int done = 0, failed = 0;
        long t0 = System.currentTimeMillis();
        for (int i = 0; i < objs.size(); ++i) {
            File f = objs.get(i);
            try {
                String rel = relativize(root, f);
                String[] parts = rel.split("/");
                String source = parts.length > 1 ? parts[0] : "unknown";
                String pack = parts.length > 2 ? parts[1] : source;
                String name = f.getName().substring(0, f.getName().length() - 4);
                String id = source + "/" + pack + "/" + name;

                String text = new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8);
                String mtlText = null;
                File mtl = new File(f.getParentFile(), name + ".mtl");
                if (mtl.isFile()) {
                    mtlText = new String(Files.readAllBytes(mtl.toPath()), StandardCharsets.UTF_8);
                }
                ObjModelData d = ObjModelLoader.parse(name, text, mtlText, "flip_xz");
                if (d == null || d.isEmpty()) {
                    failed++;
                    continue;
                }
                BufferedImage img = render(d, f.getParentFile(), size);
                File png = new File(out, id.replace("/", "__") + ".png");
                ImageIO.write(img, "png", png);
                cov.append(id).append('\t').append(coverage(img)).append('\n');
                done++;
            } catch (Throwable t) {
                failed++;
            }
            if ((i + 1) % 500 == 0) {
                long dt = System.currentTimeMillis() - t0;
                System.out.println("  " + (i + 1) + "/" + objs.size() + "  (" + dt + " ms)");
            }
        }
        Files.write(new File(out, "_coverage.tsv").toPath(),
                cov.toString().getBytes(StandardCharsets.UTF_8));
        System.out.println("RENDERED ok=" + done + " failed=" + failed
                + " total=" + objs.size()
                + " in " + (System.currentTimeMillis() - t0) + " ms");
    }

    private static void collect(File dir, List<File> out) {
        File[] kids = dir.listFiles();
        if (kids == null) return;
        for (File k : kids) {
            if (k.isDirectory()) collect(k, out);
            else if (k.getName().toLowerCase().endsWith(".obj")) out.add(k);
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

    // ---------------------------------------------------------------- render

    private static final Map<String, BufferedImage> TEX_CACHE = new HashMap<String, BufferedImage>();

    private static BufferedImage loadTexture(File modelDir, String ref) {
        if (ref == null || ref.length() == 0) return null;
        String key = modelDir.getAbsolutePath() + "|" + ref;
        if (TEX_CACHE.containsKey(key)) return TEX_CACHE.get(key);
        BufferedImage img = null;
        String r = ref.replace('\\', '/');
        String[] cands = { r, "Textures/" + leaf(r), leaf(r), r + ".png", "Textures/" + leaf(r) + ".png" };
        for (String c : cands) {
            File f = new File(modelDir, c.replace("/", File.separator));
            if (f.isFile()) {
                try {
                    InputStream in = new FileInputStream(f);
                    img = ImageIO.read(in);
                    in.close();
                    if (img != null) break;
                } catch (Throwable t) { /* try next */ }
            }
        }
        if (TEX_CACHE.size() > 256) TEX_CACHE.clear();
        TEX_CACHE.put(key, img);
        return img;
    }

    private static String leaf(String p) {
        int i = p.lastIndexOf('/');
        return i >= 0 ? p.substring(i + 1) : p;
    }

    private static BufferedImage render(ObjModelData d, File modelDir, int S) {
        BufferedImage img = new BufferedImage(S, S, BufferedImage.TYPE_INT_RGB);
        int[] px = new int[S * S];
        float[] zb = new float[S * S];
        for (int i = 0; i < px.length; ++i) { px[i] = BG; zb[i] = Float.NEGATIVE_INFINITY; }

        // --- camera: azimuth 35 deg, elevation 24 deg, orthographic ---
        double az = Math.toRadians(35.0), el = Math.toRadians(24.0);
        double ca = Math.cos(az), sa = Math.sin(az), ce = Math.cos(el), se = Math.sin(el);
        // world -> view (rotate Y then X)
        double[][] R = {
            { ca, 0, sa },
            { -sa * se, ce, ca * se },
            { -sa * ce, -se, ca * ce }
        };

        float cx = (d.minX + d.maxX) * 0.5F;
        float cy = (d.minY + d.maxY) * 0.5F;
        float cz = (d.minZ + d.maxZ) * 0.5F;
        float ex = Math.max(d.sizeX(), 1e-4F);
        float ey = Math.max(d.sizeY(), 1e-4F);
        float ez = Math.max(d.sizeZ(), 1e-4F);
        float extent = Math.max(ex, Math.max(ey, ez));
        float scale = (S * 0.82F) / extent;

        // light in view space
        double[] L = { 0.35, 0.80, 0.49 };
        double ln = Math.sqrt(L[0]*L[0] + L[1]*L[1] + L[2]*L[2]);
        L[0] /= ln; L[1] /= ln; L[2] /= ln;

        for (int gi = 0; gi < d.groups.size(); ++gi) {
            ObjModelData.ObjDisplayGroup g = d.groups.get(gi);
            List<Float> P = g.positions;
            List<Float> N = g.normals;
            List<Float> U = g.uvs;
            ObjModelData.ObjMaterial mat = d.materials.get(g.materialName);
            BufferedImage tex = mat != null ? loadTexture(modelDir, mat.textureRef) : null;
            float mr = mat != null ? mat.r : 0.8F;
            float mg = mat != null ? mat.g : 0.8F;
            float mb = mat != null ? mat.b : 0.8F;

            int triCount = P.size() / 9;
            for (int t = 0; t < triCount; ++t) {
                double[] vx = new double[3], vy = new double[3], vz = new double[3];
                double[] wx = new double[3], wy = new double[3], wz = new double[3];
                for (int k = 0; k < 3; ++k) {
                    int o = t * 9 + k * 3;
                    double X = P.get(o) - cx, Y = P.get(o + 1) - cy, Z = P.get(o + 2) - cz;
                    wx[k] = X; wy[k] = Y; wz[k] = Z;
                    vx[k] = R[0][0]*X + R[0][1]*Y + R[0][2]*Z;
                    vy[k] = R[1][0]*X + R[1][1]*Y + R[1][2]*Z;
                    vz[k] = R[2][0]*X + R[2][1]*Y + R[2][2]*Z;
                }
                // face normal in world space
                double ax = wx[1]-wx[0], ay = wy[1]-wy[0], az2 = wz[1]-wz[0];
                double bx = wx[2]-wx[0], by = wy[2]-wy[0], bz = wz[2]-wz[0];
                double nx = ay*bz - az2*by, ny = az2*bx - ax*bz, nz = ax*by - ay*bx;
                double nl = Math.sqrt(nx*nx + ny*ny + nz*nz);
                if (nl < 1e-12) continue;
                nx /= nl; ny /= nl; nz /= nl;
                // to view space
                double vnx = R[0][0]*nx + R[0][1]*ny + R[0][2]*nz;
                double vny = R[1][0]*nx + R[1][1]*ny + R[1][2]*nz;
                double vnz = R[2][0]*nx + R[2][1]*ny + R[2][2]*nz;
                double lam = vnx*L[0] + vny*L[1] + vnz*L[2];
                if (lam < 0) lam = -lam * 0.55; // two-sided-ish
                double shade = 0.30 + 0.70 * Math.min(1.0, lam);

                float br = mr, bg = mg, bb = mb;
                if (tex != null && U != null && U.size() >= (t + 1) * 6) {
                    int o = t * 6;
                    float u = (U.get(o) + U.get(o + 2) + U.get(o + 4)) / 3.0F;
                    float v = (U.get(o + 1) + U.get(o + 3) + U.get(o + 5)) / 3.0F;
                    int tx = (int) (u * (tex.getWidth() - 1));
                    int ty = (int) (v * (tex.getHeight() - 1));
                    tx = Math.max(0, Math.min(tex.getWidth() - 1, tx));
                    ty = Math.max(0, Math.min(tex.getHeight() - 1, ty));
                    int c = tex.getRGB(tx, ty);
                    br = ((c >> 16) & 0xFF) / 255.0F;
                    bg = ((c >> 8) & 0xFF) / 255.0F;
                    bb = (c & 0xFF) / 255.0F;
                }
                int col = clamp8(br * shade) << 16 | clamp8(bg * shade) << 8 | clamp8(bb * shade);

                // screen coords (flip Y so +Y is up)
                double[] sx = new double[3], sy = new double[3];
                for (int k = 0; k < 3; ++k) {
                    sx[k] = S * 0.5 + vx[k] * scale;
                    sy[k] = S * 0.5 - vy[k] * scale;
                }
                fillTriangle(px, zb, S, sx, sy, vz, col);
            }
        }
        img.setRGB(0, 0, S, S, px, 0, S);
        return img;
    }

    private static int clamp8(double v) {
        int i = (int) (v * 255.0 + 0.5);
        return i < 0 ? 0 : (i > 255 ? 255 : i);
    }

    /** Barycentric fill with a z-buffer (z = depth, larger is nearer). */
    private static void fillTriangle(int[] px, float[] zb, int S,
                                     double[] sx, double[] sy, double[] vz, int col) {
        double minx = Math.min(sx[0], Math.min(sx[1], sx[2]));
        double maxx = Math.max(sx[0], Math.max(sx[1], sx[2]));
        double miny = Math.min(sy[0], Math.min(sy[1], sy[2]));
        double maxy = Math.max(sy[0], Math.max(sy[1], sy[2]));
        int x0 = (int) Math.floor(minx), x1 = (int) Math.ceil(maxx);
        int y0 = (int) Math.floor(miny), y1 = (int) Math.ceil(maxy);
        if (x0 < 0) x0 = 0;
        if (y0 < 0) y0 = 0;
        if (x1 > S - 1) x1 = S - 1;
        if (y1 > S - 1) y1 = S - 1;
        if (x1 < x0 || y1 < y0) return;

        double d = (sy[1] - sy[2]) * (sx[0] - sx[2]) + (sx[2] - sx[1]) * (sy[0] - sy[2]);
        if (Math.abs(d) < 1e-9) return;
        double inv = 1.0 / d;

        for (int y = y0; y <= y1; ++y) {
            double py = y + 0.5;
            for (int x = x0; x <= x1; ++x) {
                double pxc = x + 0.5;
                double l0 = ((sy[1] - sy[2]) * (pxc - sx[2]) + (sx[2] - sx[1]) * (py - sy[2])) * inv;
                if (l0 < -0.0001) continue;
                double l1 = ((sy[2] - sy[0]) * (pxc - sx[2]) + (sx[0] - sx[2]) * (py - sy[2])) * inv;
                if (l1 < -0.0001) continue;
                double l2 = 1.0 - l0 - l1;
                if (l2 < -0.0001) continue;
                double z = l0 * vz[0] + l1 * vz[1] + l2 * vz[2];
                int idx = y * S + x;
                if (z > zb[idx]) {
                    zb[idx] = (float) z;
                    px[idx] = col;
                }
            }
        }
    }

    /** Fraction of pixels that are not background — a cheap "shape fills the frame" signal. */
    private static String coverage(BufferedImage img) {
        int n = 0, tot = img.getWidth() * img.getHeight();
        for (int y = 0; y < img.getHeight(); ++y) {
            for (int x = 0; x < img.getWidth(); ++x) {
                if ((img.getRGB(x, y) & 0xFFFFFF) != (BG & 0xFFFFFF)) n++;
            }
        }
        return String.format("%.4f", n / (double) tot);
    }
}
