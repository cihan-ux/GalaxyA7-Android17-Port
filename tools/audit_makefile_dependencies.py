"""Offline Makefile dependency scanner for Samsung Exynos7885 source audits.

Reads local source text only. Does not download dependencies or execute Makefiles.
"""
import argparse
import re
from pathlib import Path

PATH_PATTERN = re.compile(r"(?:hardware|device|vendor)/[A-Za-z0-9_.+-]+(?:/[A-Za-z0-9_.+-]+)+")
MAKE_DIRECTIVES = re.compile(r"^\s*(?:include\s+|[-]?include\s+|\$\(call\s+inherit-product(?:-if-exists)?,)", re.M)
REQUIRED_LINARO = frozenset({
    "hardware/samsung_slsi-linaro/config/BoardConfig7885.mk",
    "device/samsung_slsi/sepolicy/sepolicy.mk",
})
REQUIRED_BSP = frozenset({
    "device/samsung_slsi/sepolicy/sepolicy.mk",
})

def declared_slsi_variant(text):
    match = re.search(r"^\s*TARGET_SLSI_VARIANT\s*:?=\s*(linaro|bsp)\s*(?:#.*)?$", text, re.M)
    return match.group(1) if match else None

def referenced_paths(text):
    if not isinstance(text, str):
        raise TypeError("Makefile source must be text")
    paths = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        if MAKE_DIRECTIVES.match(line):
            paths.update(PATH_PATTERN.findall(line))
    return paths

# Only known path-bearing Make variables; arbitrary assignments are not dependencies.
PATH_VARIABLES = frozenset({"BOARD_CUSTOM_BOOTIMG_MK", "TARGET_CUSTOM_DTBTOOL"})
PATH_ASSIGNMENT = re.compile(r"^\\s*([A-Z][A-Z0-9_]*)\\s*(?::=|\\?=|=)\\s*(.*?)\\s*$")

def configured_file_paths(text):
    """Extract literal paths from allowlisted path-valued Make variables."""
    paths = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        match = PATH_ASSIGNMENT.match(line)
        if match and match.group(1) in PATH_VARIABLES:
            paths.update(PATH_PATTERN.findall(match.group(2)))
    return paths

def all_file_dependencies(text):
    """Direct includes/inherit-product plus explicit file-valued variables."""
    return referenced_paths(text) | configured_file_paths(text)

def unresolved_file_dependencies(text, available_paths):
    return all_file_dependencies(text) - set(available_paths)

def unresolved_paths(text, available_paths):
    return referenced_paths(text) - set(available_paths)

def source_gate(text, available_paths, required):
    """Pass only when every explicitly required path is available and referenced."""
    found = referenced_paths(text)
    return set(required) <= found and not (set(required) - set(available_paths))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("makefile", type=Path, help="Locally downloaded Makefile; read-only")
    parser.add_argument("--available-list", type=Path, required=True, help="One verified path per line")
    args = parser.parse_args()
    available = {x.strip() for x in args.available_list.read_text().splitlines() if x.strip() and not x.startswith("#")}
    text = args.makefile.read_text()
    for path in sorted(unresolved_file_dependencies(text, available)):
        print("UNRESOLVED:", path)
    print("This static scan cannot establish Android 17 build compatibility.")

if __name__ == "__main__":
    main()
