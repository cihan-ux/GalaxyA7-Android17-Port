"""Audit direct literal Makefile references and assignment-backed build dependencies.

Offline and read-only. Deliberately does not expand Make variables or execute Make.
"""
from audit_makefile_dependencies import (
    PATH_ASSIGNMENT, dependency_report, literal_path, logical_lines, referenced_paths,
)

ASSIGNMENT_KEYS = frozenset({
    "BOARD_CUSTOM_BOOTIMG_MK",
    "TARGET_CUSTOM_DTBTOOL",
    "TARGET_KERNEL_SOURCE",
})
ASSIGNMENT = PATH_ASSIGNMENT

def assignment_dependencies(text):
    """Last literal candidate per key; not evaluated Make assignment state."""
    result = {}
    for _, line in logical_lines(text):
        m = ASSIGNMENT.match(line)
        if not m or m.group(1) not in ASSIGNMENT_KEYS:
            continue
        key, value = m.groups()
        if value.startswith(("hardware/", "kernel/")) and literal_path(value):
            result[key] = value
    return result

def direct_dependency_report(text, known_paths=()):
    includes = referenced_paths(text)
    assignments = assignment_dependencies(text)
    known = set(known_paths)
    report = dependency_report(text, known_paths)
    dynamic_assignments, review_assignments = set(), set()
    candidates = {}
    for number, line in logical_lines(text):
        m = ASSIGNMENT.match(line)
        if m and m.group(1) in ASSIGNMENT_KEYS:
            key, value = m.groups()
            if value.startswith(("hardware/", "kernel/")) and literal_path(value):
                candidates.setdefault(key, set()).add(value)
            elif "$" in value:
                dynamic_assignments.add(number)
            elif value and not (key == "TARGET_CUSTOM_DTBTOOL" and value in report["host_tool_names"]):
                # A rejected assignment must remain visible. In particular,
                # TARGET_KERNEL_SOURCE is directory-valued and is deliberately
                # outside the file-only scanner's variable allowlist.
                review_assignments.add(number)
    all_assigned_paths = {value for values in candidates.values() for value in values}
    return {
        "includes": sorted(includes),
        "unresolved_includes": sorted(includes - known),
        "assigned_paths": assignments,
        "assigned_path_candidates": {key: sorted(values) for key, values in sorted(candidates.items())},
        "unresolved_assigned_paths": sorted(all_assigned_paths - known),
        "dynamic_lines": sorted(set(report["dynamic_lines"]) | set(dynamic_assignments)),
        "review_lines": sorted(set(report["review_lines"]) | review_assignments),
        "host_tool_names": report["host_tool_names"],
    }

if __name__ == "__main__":
    sample = """include hardware/samsung_slsi-linaro/config/BoardConfig7885.mk
BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/mkbootimg.mk
TARGET_KERNEL_SOURCE := kernel/samsung/exynos7885
"""
    print(direct_dependency_report(sample))
