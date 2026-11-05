#!/usr/bin/env python3
"""Read-only inventory of Samsung SLSI Soong namespaces, not a build validator."""
import argparse
import json
import re
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "tests/fixtures/upstream/slsi18/config.mk"
NAMESPACE = re.compile(r"^hardware/samsung_slsi-linaro/[a-z0-9_-]+$")

def namespaces(text):
    """Extract literal namespace tokens from PRODUCT_SOONG_NAMESPACES += blocks."""
    found = set()
    active = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("PRODUCT_SOONG_NAMESPACES"):
            if not re.match(r"^PRODUCT_SOONG_NAMESPACES\s*\+=", line):
                active = False
                continue
            active = True
            line = line.split("+=", 1)[1].strip()
        elif not active:
            continue
        continued = line.endswith("\\")
        tokens = line.rstrip("\\").split()
        for token in tokens:
            if NAMESPACE.fullmatch(token):
                found.add(token)
            elif token.startswith("hardware/") or "$" in token:
                raise ValueError(f"Unresolved namespace expression: {token}")
        active = continued
    return sorted(found)

def inventory(config, known_paths):
    required = namespaces(config)
    known = set(known_paths)
    return {"required_namespaces": required,
            "present": sorted(set(required) & known),
            "unresolved": sorted(set(required) - known),
            "warning": "Repository discovery and namespace presence do not establish module or Android 17 compatibility"}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--available-list", type=Path, required=True,
                        help="Verified checked-out namespace directory paths, one per line")
    parser.add_argument("--strict", action="store_true", help="Return 1 when namespaces are missing")
    args = parser.parse_args(argv)
    available = [line.strip() for line in args.available_list.read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
    result = inventory(args.config.read_text(encoding="utf-8"), available)
    print(json.dumps(result, indent=2))
    return int(args.strict and bool(result["unresolved"]))

if __name__ == "__main__":
    raise SystemExit(main())
