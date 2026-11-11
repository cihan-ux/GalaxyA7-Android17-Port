#!/usr/bin/env python3
"""Safely stage A7's 12L product files in the pinned *source* device checkout.

This does not build a ROM, access a phone or copy vendor binaries. Refuses
to overwrite any edited checkout, wrong commit, or unexpected Git origin.
"""
import argparse
import difflib
from pathlib import Path
import subprocess
import sys

from check_lineage19_port import ROOT, validate

BASELINE_SHA = "f17643ba01010c45b628d5acb8f48350ded61606"
BASELINE_ORIGIN = "https://github.com/exynos7885-dev/device_samsung_a7y18lte"
STAGE = ROOT / "port/lineage-19.1/device/samsung/a7y18lte"
FILES = ("AndroidProducts.mk", "lineage_a7y18lte.mk")
REQUIRED = ("BoardConfig.mk", "device.mk", "manifest.xml", "Android.bp")

def git(tree: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(tree), *args],
                            check=True, capture_output=True, text=True)
    return result.stdout.strip()

def checkout_problem(head: str, remote: str, status: str) -> str | None:
    if head != BASELINE_SHA:
        return "wrong device tree source commit; expected " + BASELINE_SHA
    if remote.removesuffix(".git").rstrip("/") != BASELINE_ORIGIN:
        return "unexpected Git origin; refuse non-reviewed device source"
    if status:
        return "device tree has uncommitted changes; refuse to overwrite"
    return None

def stage(tree: Path, apply: bool) -> int:
    tree = tree.expanduser().resolve()
    if not tree.is_dir():
        raise ValueError("device checkout does not exist")
    if Path(git(tree, "rev-parse", "--show-toplevel")).resolve() != tree:
        raise ValueError("--tree must point to the device Git repository root")
    problem = checkout_problem(git(tree, "rev-parse", "HEAD"),
                               git(tree, "remote", "get-url", "origin"),
                               git(tree, "status", "--porcelain"))
    if problem:
        raise ValueError(problem)
    for name in (*FILES, *REQUIRED):
        path = tree / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing or symlinked device file: " + name)
    sources = [(tree / name, (STAGE / name).read_bytes()) for name in FILES]
    errors = validate((ROOT / "manifests/lineage-19.1-a7y18lte-local.xml").read_text(),
                      (STAGE / FILES[0]).read_text(), (STAGE / FILES[1]).read_text())
    if errors:
        raise ValueError("staged product guard failed: " + "; ".join(errors))
    # Do not write until every prerequisite and both staged files are checked.
    for dest, content in sources:
        old = dest.read_bytes()
        if old == content:
            raise ValueError("checkout already contains a staged product: " + dest.name)
        print("".join(difflib.unified_diff(
            old.decode("utf-8").splitlines(keepends=True),
            content.decode("utf-8").splitlines(keepends=True),
            fromfile="baseline/" + dest.name, tofile="lineage19/" + dest.name)))
    if apply:
        for dest, content in sources:
            dest.write_bytes(content)
        changed = set(git(tree, "diff", "--name-only").splitlines())
        if changed != set(FILES):
            raise ValueError("unexpected files modified after staging: " + str(changed))
        git(tree, "diff", "--check")
        print("PASS: pinned LineageOS 18.1 device tree staged for 19.1 product config")
    else:
        print("PASS: dry-run only; use --apply to write exactly two product files")
    print("LIMIT: no Android 12L compilation, vendor verification or device boot")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True,
                        help="root of pinned exynos7885-dev A7 source tree")
    parser.add_argument("--apply", action="store_true",
                        help="apply two source-only product overlays after safety checks")
    args = parser.parse_args()
    try:
        return stage(args.tree, args.apply)
    except (ValueError, OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
