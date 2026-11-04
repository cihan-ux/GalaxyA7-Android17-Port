"""Audit direct literal Makefile references and assignment-backed build dependencies.

Offline and read-only. Deliberately does not expand Make variables or execute Make.
"""
import re
from audit_makefile_dependencies import referenced_paths

ASSIGNMENT_KEYS = frozenset({
    "BOARD_CUSTOM_BOOTIMG_MK",
    "TARGET_CUSTOM_DTBTOOL",
    "TARGET_KERNEL_SOURCE",
})
ASSIGNMENT = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*(?::=|\?=|=)\s*(.*?)\s*$")

def assignment_dependencies(text):
    result = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0]
        m = ASSIGNMENT.match(line)
        if not m or m.group(1) not in ASSIGNMENT_KEYS:
            continue
        key, value = m.groups()
        if value.startswith(("hardware/", "kernel/")) and "$" not in value and " " not in value:
            result[key] = value
    return result

def direct_dependency_report(text, known_paths=()):
    includes = referenced_paths(text)
    assignments = assignment_dependencies(text)
    known = set(known_paths)
    return {
        "includes": sorted(includes),
        "unresolved_includes": sorted(includes - known),
        "assigned_paths": assignments,
        "unresolved_assigned_paths": sorted(set(assignments.values()) - known),
    }

if __name__ == "__main__":
    sample = """include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk
BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk
TARGET_KERNEL_SOURCE := kernel/samsung/exynos7885
"""
    print(direct_dependency_report(sample))
