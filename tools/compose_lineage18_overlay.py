#!/usr/bin/env python3
"""Compose pinned A7 LineageOS 18.1 sources with a resolved upstream manifest.

This outputs a repo local-manifest overlay, NOT a complete Android ROM or a
claim that every required module/vendor blob exists. No phone access.
"""
import argparse
import copy
from pathlib import Path, PurePosixPath
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "manifests/lineage-18.1-research.xml"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


def _path(project):
    return project.get("path") or project.get("name")


def _valid_path(value):
    return (bool(value) and not value.startswith("/") and "\\" not in value
            and all(part not in {"", ".", ".."} for part in value.split("/")))


def _index_projects(root):
    found = {}
    for project in root.findall("project"):
        path = _path(project)
        if not _valid_path(path):
            raise ValueError("unsafe or missing project path")
        if path in found:
            raise ValueError("duplicate project path: " + path)
        if not project.get("name"):
            raise ValueError("project missing repository name")
        found[path] = project
    return found


def make_overlay(base_path, research_path=RESEARCH):
    try:
        base = ET.parse(base_path).getroot()
        research = ET.parse(research_path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ValueError("could not parse source manifest") from exc
    if base.tag != "manifest" or research.tag != "manifest":
        raise ValueError("expected manifest root")
    base_projects = _index_projects(base)
    pinned = _index_projects(research)
    if not pinned:
        raise ValueError("research manifest contains no projects")
    base_names = {}
    for project in base_projects.values():
        base_names.setdefault(project.get("name"), []).append(_path(project))
    base_remotes = {r.get("name"): r.get("fetch") for r in base.findall("remote")}
    overlay = ET.Element("manifest")

    seen_remotes = set()
    for remote in research.findall("remote"):
        name, fetch = remote.get("name"), remote.get("fetch")
        if not name or not fetch or name in seen_remotes:
            raise ValueError("duplicate or invalid research remote")
        seen_remotes.add(name)
        if name in base_remotes and base_remotes[name] != fetch:
            raise ValueError("conflicting remote: " + name)
        if name not in base_remotes:
            overlay.append(copy.deepcopy(remote))

    # Removal of an existing project by NAME can affect multiple project
    # paths. Refuse ambiguity rather than silently dropping an unrelated tree.
    removals = []
    additions = []
    for path, project in sorted(pinned.items()):
        if not SHA40.fullmatch(project.get("revision", "")):
            raise ValueError("floating or invalid pinned revision: " + path)
        if project.get("remote") not in seen_remotes and project.get("remote") not in base_remotes:
            raise ValueError("undefined remote for " + path)
        if not _valid_path(project.get("name", "")):
            raise ValueError("unsafe repository name for " + path)
        previous = base_projects.get(path)
        if previous is not None:
            name = previous.get("name")
            if len(base_names.get(name, [])) != 1:
                raise ValueError("ambiguous remove-project by name: " + name)
            removals.append(ET.Element("remove-project", {"name": name}))
        additions.append(copy.deepcopy(project))
    for element in removals + additions:
        overlay.append(element)
    return overlay, {
        "pinned_projects": len(pinned),
        "overridden_platform_paths": len(removals),
        "added_paths": len(pinned) - len(removals),
        "paths": sorted(pinned),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path,
                        help="resolved output from repo manifest -o BEFORE installing overlay")
    parser.add_argument("--research", type=Path, default=RESEARCH)
    parser.add_argument("--out", required=True, type=Path,
                        help="destination inside .repo/local_manifests/")
    args = parser.parse_args(argv)
    try:
        overlay, stats = make_overlay(args.base, args.research)
        # Refuse writing to source manifest, or to same file as the base.
        if args.out.resolve() in {args.base.resolve(), args.research.resolve()}:
            raise ValueError("output must differ from both source manifests")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        ET.indent(overlay)
        ET.ElementTree(overlay).write(args.out, encoding="utf-8", xml_declaration=True)
    except (OSError, ValueError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    print("PINNED {} A7 repositories; {} original paths overridden; {} new paths".format(
        stats["pinned_projects"], stats["overridden_platform_paths"], stats["added_paths"]))
    print("Research checkout only; build completeness and phone compatibility unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
