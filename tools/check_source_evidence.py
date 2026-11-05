#!/usr/bin/env python3
"""Verify local source fixtures and their immutable upstream provenance offline.

This checks recorded bytes and manifest pins, not upstream availability, licenses
of entire repositories, build completeness, or Android compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "tests/fixtures/upstream"
DEFAULT_RESEARCH_MANIFEST = REPO_ROOT / "manifests/lineage-18.1-research.xml"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SCOPES = {"source-evidence", "candidate-only", "target-evidence"}
# Explicit metadata-only pins. These have been checked through separate GitHub
# source-tree CI, but do not have checked-in byte-for-byte source fixtures.
# Do not silently treat these as source-evidence.
METADATA_ONLY_PATHS = frozenset({
    "device/lineage/sepolicy",
    "device/samsung_slsi/sepolicy",
    "hardware/samsung",
    "hardware/samsung_slsi-linaro/config",
    "hardware/samsung_slsi-linaro/exynos",
    "hardware/samsung_slsi-linaro/exynos5",
    "hardware/samsung_slsi-linaro/graphics",
    "hardware/samsung_slsi-linaro/openmax",
    "vendor/samsung/a7y18lte",
    "vendor/samsung/exynos7885-common",
})



def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and not any(x in {"", ".", ".."} for x in value.split("/"))


def verify_evidence(root=DEFAULT_ROOT, research_manifest=DEFAULT_RESEARCH_MANIFEST):
    """Return actionable errors; never fetch URLs or execute fixture contents."""
    root = Path(root).resolve()
    errors = []
    try:
        data = json.loads((root / "manifest.json").read_text(encoding="utf-8"),
                          object_pairs_hook=_unique_object)
        xml = ET.parse(research_manifest).getroot()
    except (OSError, ValueError, ET.ParseError) as exc:
        return [f"Cannot read evidence inventory: {exc}"]
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("research_only") is not True:
        return ["Expected research-only evidence schema_version 1"]
    files = data.get("files")
    if not isinstance(files, list) or not files:
        return ["Evidence files must be a non-empty list"]
    projects = {p.get("path"): p for p in xml.findall("project")}
    remotes = {r.get("name"): r.get("fetch", "") for r in xml.findall("remote")}
    seen = set()
    bound_projects = set()
    for index, entry in enumerate(files):
        label = f"files[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected object")
            continue
        string_keys = ("fixture", "repository", "revision", "path", "blob_sha",
                       "sha256", "url", "raw_url", "license", "scope")
        if any(not isinstance(entry.get(key), str) for key in string_keys):
            errors.append(f"{label}: required provenance fields must be strings")
            continue
        if entry.get("manifest_project") is not None and not isinstance(entry["manifest_project"], str):
            errors.append(f"{label}: manifest_project must be a string or null")
            continue
        name = entry.get("fixture")
        if not _relative_path(name) or not _relative_path(entry.get("path")):
            errors.append(f"{label}: fixture and upstream path must be relative, without traversal")
            continue
        label = name
        if name in seen:
            errors.append(f"{label}: duplicate fixture entry")
        seen.add(name)
        revision = entry.get("revision", "")
        repository = entry.get("repository", "")
        if not isinstance(revision, str) or not HEX40.fullmatch(revision):
            errors.append(f"{label}: revision must be an immutable lowercase Git SHA")
        if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository):
            errors.append(f"{label}: invalid owner/repository")
        if "proprietary" in repository.lower() or "proprietary" in name.lower():
            errors.append(f"{label}: proprietary vendor artifacts are excluded")
        path = entry["path"]
        for key, host, separator in (("url", "https://github.com", "/blob/"),
                                     ("raw_url", "https://raw.githubusercontent.com", "/")):
            expected = f"{host}/{repository}{separator}{revision}/{path}"
            if entry.get(key) != expected:
                errors.append(f"{label}: {key} must identify the recorded revision and path")
        if entry.get("license") not in {"Apache-2.0", "GPL-2.0-only"}:
            errors.append(f"{label}: source license declaration missing or unsupported")
        if entry.get("scope") not in SCOPES:
            errors.append(f"{label}: evidence scope missing or unsupported")
        project_path = entry.get("manifest_project")
        if project_path is not None:
            project = projects.get(project_path)
            if project is None:
                errors.append(f"{label}: manifest project absent: {project_path}")
            else:
                bound_projects.add(project_path)
                remote = remotes.get(project.get("remote"), "")
                expected_repo_url = remote.rstrip("/") + "/" + project.get("name", "")
                if (project.get("revision") != revision or
                        expected_repo_url.removesuffix(".git") != "https://github.com/" + repository):
                    errors.append(f"{label}: provenance does not match research manifest project")
        local = root / name
        if not local.resolve().is_relative_to(root) or local.is_symlink():
            errors.append(f"{label}: fixture escapes evidence directory or is a symlink")
            continue
        try:
            content = local.read_bytes()
            decoded = content.decode("utf-8")
            if "\0" in decoded:
                raise ValueError("NUL byte is not source text")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{label}: cannot read UTF-8 source: {exc}")
            continue
        if type(entry.get("bytes")) is not int or entry["bytes"] != len(content):
            errors.append(f"{label}: byte count mismatch")
        digest = entry.get("sha256", "")
        if not isinstance(digest, str) or not HEX64.fullmatch(digest) or hashlib.sha256(content).hexdigest() != digest:
            errors.append(f"{label}: SHA-256 mismatch")
        blob = hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()
        recorded_blob = entry.get("blob_sha", "")
        if not isinstance(recorded_blob, str) or not HEX40.fullmatch(recorded_blob) or blob != recorded_blob:
            errors.append(f"{label}: Git blob SHA mismatch")
    metadata_only = METADATA_ONLY_PATHS & set(projects)
    missing_projects = set(projects) - bound_projects - metadata_only
    if missing_projects:
        errors.append("No source evidence for manifest projects: " + ", ".join(sorted(missing_projects)))
    for path in sorted(metadata_only):
        project = projects[path]
        revision = project.get("revision", "")
        if not HEX40.fullmatch(revision):
            errors.append(f"{path}: metadata-only pin must use immutable SHA")
    extra = {p.relative_to(root).as_posix() for p in root.rglob("*")
             if p.is_file() and p.name not in {"manifest.json", "README.md"}} - seen
    if extra:
        errors.append("Unrecorded fixture files: " + ", ".join(sorted(extra)))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--research-manifest", type=Path, default=DEFAULT_RESEARCH_MANIFEST)
    args = parser.parse_args(argv)
    errors = verify_evidence(args.root, args.research_manifest)
    for error in errors:
        print("ERROR:", error)
    if not errors:
        print("Source fixture integrity and research pins verified (offline).")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
