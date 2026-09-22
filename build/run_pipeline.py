#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_pipeline.py — rebuild the whole library catalogue from the downloaded models.

Order matters:
  1. fetch_kenney.py / fetch_kaykit.py   download + reduce to the OBJ deliverable
  2. AnalyzeModels.java                  parse every OBJ with the ENGINE parser
  3. build_catalog.py                    classify, tag, index, per-pack docs
  4. RenderThumbs.java                   preview PNGs + coverage signal
  5. make_readme.py                      README from the measured catalogue

Steps 2 and 4 are Java and are invoked through the project's local JDK.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(ROOT)
LIB = os.path.join(PROJECT, "omnimod-3d-library")
MODELS = os.path.join(LIB, "models")
JAVA_HOME = os.path.join(PROJECT, "local-tools", "jdk-17.0.18+8")
JAVAC = os.path.join(JAVA_HOME, "bin", "javac.exe")
JAVA = os.path.join(JAVA_HOME, "bin", "java.exe")
PY = sys.executable
CLS = os.path.join(PROJECT, "sources", "android-native", "build",
                   "intermediates", "javac", "debug", "classes")
OMNI3D = os.path.join(PROJECT, "sources", "main", "java", "net", "lax1dude",
                      "eaglercraft", "v1_8", "omni3d")
BUILD_CLS = os.path.join(ROOT, "_cls")
ANALYSIS = os.path.join(LIB, "_analysis")
THUMBS = os.path.join(LIB, "thumbs")


def run(cmd, **kw):
    print("$ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        print("  -> exit %d" % r.returncode, flush=True)
    return r.returncode


def java_compile(targets):
    os.makedirs(BUILD_CLS, exist_ok=True)
    cmd = [JAVAC, "-nowarn", "-encoding", "UTF-8", "-cp", CLS, "-d", BUILD_CLS]
    cmd += targets
    cmd += [os.path.join(OMNI3D, "ObjModelLoader.java"),
            os.path.join(OMNI3D, "ObjModelData.java")]
    return run(cmd)


def main():
    steps = sys.argv[1:] or ["analyze", "catalog", "thumbs", "readme"]

    if "analyze" in steps:
        print("\n=== 2. engine analysis ===")
        if java_compile([os.path.join(ROOT, "AnalyzeModels.java")]) != 0:
            return 1
        os.makedirs(ANALYSIS, exist_ok=True)
        run([JAVA, "-cp", BUILD_CLS + os.pathsep + CLS, "AnalyzeModels",
             MODELS, os.path.join(ANALYSIS, "models.jsonl")])

    if "catalog" in steps:
        print("\n=== 3. catalogue ===")
        run([PY, os.path.join(ROOT, "build_catalog.py")])

    if "thumbs" in steps:
        print("\n=== 4. thumbnails ===")
        if java_compile([os.path.join(ROOT, "RenderThumbs.java")]) != 0:
            return 1
        os.makedirs(THUMBS, exist_ok=True)
        run([JAVA, "-cp", BUILD_CLS + os.pathsep + CLS, "RenderThumbs",
             MODELS, THUMBS, "160"])

    if "readme" in steps:
        print("\n=== 5. README ===")
        run([PY, os.path.join(ROOT, "make_readme.py")])

    print("\npipeline done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
