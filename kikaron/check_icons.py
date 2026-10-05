#!/usr/bin/env python3
"""Fail if any shipped icon / logo artwork is still upstream's (Bitwarden's).

Upstream's hashes are taken from the pinned -bwpm tag (git blob ids) and
recorded in kikaron/upstream-icon-hashes.txt, so the check also works where
the tag is not fetched. Run by kikaron/brand.sh and before every archive.
"""
import fnmatch, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD = os.path.join(ROOT, "kikaron", "upstream-icon-hashes.txt")
TARGET_DIRS = ("Bitwarden/", "BitwardenActionExtension/", "BitwardenAutoFillExtension/",
               "BitwardenShareExtension/", "BitwardenShared/")
PATTERNS = ("*.appiconset/*", "*.icon/*", "*/logoBitwarden.imageset/*", "*/logo.imageset/*")


def artwork(path):
    return (path.startswith(TARGET_DIRS) and not path.endswith(".json")
            and any(fnmatch.fnmatch(path, p) for p in PATTERNS))


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, check=True).stdout


def upstream_hashes():
    tag = subprocess.run(["git", "-C", ROOT, "describe", "--tags", "--abbrev=0", "--match", "v*-bwpm"],
                         capture_output=True, text=True).stdout.strip()
    if tag:
        rows = []
        for line in git("ls-tree", "-r", tag).splitlines():
            meta, path = line.split("\t", 1)
            if artwork(path):
                rows.append(f"{meta.split()[2]} {path}")
        with open(RECORD, "w") as fh:
            fh.write(f"# upstream icon/logo artwork at {tag} (git blob id, path) - kikaron/check_icons.py\n")
            fh.write("\n".join(sorted(rows)) + "\n")
    with open(RECORD) as fh:
        return {line.split()[0]: line.split(" ", 1)[1].strip() for line in fh if line.strip() and not line.startswith("#")}


def main():
    upstream = upstream_hashes()
    bad = []
    for dirpath, _, files in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        if rel_dir.startswith(("build", ".git")):
            continue
        for f in files:
            rel = os.path.join(rel_dir, f)
            if not artwork(rel):
                continue
            blob = git("hash-object", rel).strip()
            if blob in upstream:
                bad.append(f"{rel} is upstream's {upstream[blob]}")
            if ".icon/" in rel and not rel.endswith("/Assets/Multipass.png"):
                bad.append(f"{rel}: unexpected layer in an Icon Composer bundle")
    if bad:
        sys.exit("icon check FAILED - upstream artwork still shipped:\n  " + "\n  ".join(bad))
    print("icon check: no upstream icon artwork left")


if __name__ == "__main__":
    main()
