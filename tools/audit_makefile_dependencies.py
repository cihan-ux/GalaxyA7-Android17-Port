"""Offline Makefile dependency scanner for Samsung Exynos7885 source audits.

Reads source text only: never expands variables, executes Make or downloads files.
Results are a syntactic inventory across all branches, not evaluated Make state.
"""
import argparse
import json
import re
from pathlib import Path

# Match complete operands, never substrings of a dynamic expression or glob.
PATH_PATTERN = re.compile(r"[A-Za-z0-9_.+-]+(?:/[A-Za-z0-9_.+-]+)*")
MAKE_DIRECTIVES = re.compile(r"^ *(?:(?:-?include|sinclude)(?:\s+|$)|\$\(call\s+inherit-product(?:-if-exists)?\s*,)")
INCLUDE = re.compile(r"^ *(include|-include|sinclude)\s+(.+)$")
INHERIT = re.compile(r"^ *\$\(call\s+(inherit-product(?:-if-exists)?)\s*,\s*(.*)\)\s*$")
REQUIRED_LINARO = frozenset({
    "hardware/samsung_slsi-linaro/config/BoardConfig7885.mk",
    "device/samsung_slsi/sepolicy/sepolicy.mk",
})
REQUIRED_BSP = frozenset({"device/samsung_slsi/sepolicy/sepolicy.mk"})

# Only known file-valued Make variables; arbitrary assignments are not dependencies.
PATH_VARIABLES = frozenset({"BOARD_CUSTOM_BOOTIMG_MK", "TARGET_CUSTOM_DTBTOOL"})
PATH_ASSIGNMENT = re.compile(r"^ *([A-Z][A-Z0-9_]*)\s*(?::=|\?=|\+=|=)\s*(.*?)\s*$")


def logical_lines(text):
    """Yield (first physical line number, text) with Make continuations folded.

    Comments are removed after folding, so an escaped newline in a comment does
    not expose its following physical line as a new directive. Recipe lines
    retain their tab prefix and are deliberately excluded by directive regexes.
    """
    if not isinstance(text, str):
        raise TypeError("Makefile source must be text")
    pending = ""
    start = 1
    for number, physical in enumerate(text.splitlines(), 1):
        if not pending:
            start = number
        trailing = len(physical) - len(physical.rstrip("\\"))
        if trailing % 2:
            pending += physical[:-1] + " "
            continue
        line = pending + physical
        pending = ""
        # Escaped hashes are unsupported path syntax; do not shorten such a path.
        line = re.split(r"(?<!\\)#", line, maxsplit=1)[0]
        yield start, line
    if pending:
        yield start, pending + "\\"  # Unterminated continuation requires review.


def literal_path(value):
    """Accept a complete relative path with no Make syntax or traversal."""
    return bool(PATH_PATTERN.fullmatch(value)) and not ({".", ".."} & set(value.split("/")))


def _operands(value):
    """Split an include list, retaining whitespace inside Make expressions."""
    result, current, closes = [], [], []
    index = 0
    while index < len(value):
        char = value[index]
        if char == "$" and index + 1 < len(value) and value[index + 1] in "({":
            opener = value[index + 1]
            closes.append(")" if opener == "(" else "}")
            current.extend((char, opener))
            index += 2
            continue
        if closes and char == closes[-1]:
            closes.pop()
        if char.isspace() and not closes:
            if current:
                result.append("".join(current))
                current = []
        else:
            current.append(char)
        index += 1
    if current:
        result.append("".join(current))
    return result


def _dependencies(text, path_variables=PATH_VARIABLES):
    for number, line in logical_lines(text):
        include, inherit, assignment = INCLUDE.match(line), INHERIT.match(line), PATH_ASSIGNMENT.match(line)
        if include:
            directive, value = include.groups()
            values = _operands(value)
            yield number, "include" if values else "unsupported", directive != "include", values or [line.strip()]
        elif inherit:
            directive, value = inherit.groups()
            yield number, "inherit", directive.endswith("-if-exists"), [value.strip()]
        elif assignment and assignment.group(1) in path_variables:
            value = assignment.group(2)
            if value:
                # This variable can select a built host tool rather than a file.
                kind = "host_tool" if (assignment.group(1) == "TARGET_CUSTOM_DTBTOOL"
                                       and re.fullmatch(r"[A-Za-z0-9_+-]+", value)) else "assignment"
                yield number, kind, False, [value]
        elif MAKE_DIRECTIVES.match(line):
            # A recognized prefix with unsupported/truncated syntax must not vanish.
            yield number, "unsupported", False, [line.strip()]


def declared_slsi_variant(text):
    variants = set()
    for _, line in logical_lines(text):
        match = PATH_ASSIGNMENT.match(line)
        if match and match.group(1) == "TARGET_SLSI_VARIANT":
            if "+=" in line:
                return None
            variants.add(match.group(2))
    return variants.pop() if len(variants) == 1 and variants <= {"linaro", "bsp"} else None


def referenced_paths(text):
    """Literal include/inherit operands, including syntactically optional ones."""
    return {value for _, kind, _, values in _dependencies(text)
            if kind in {"include", "inherit"} for value in values if literal_path(value)}


def configured_file_paths(text):
    """Complete literal paths assigned to allowlisted file-valued variables."""
    return {value for _, kind, _, values in _dependencies(text)
            if kind == "assignment" for value in values if literal_path(value)}


def all_file_dependencies(text):
    return referenced_paths(text) | configured_file_paths(text)


def dependency_report(text, available_paths=(), available_tools=()):
    """Separate required/optional literals from expressions requiring review.

    Conditional branches and assignment precedence are not evaluated. Availability
    must be a verified file inventory, not a repository name or directory prefix.
    """
    required, optional, dynamic, review, host_tools = set(), set(), set(), set(), set()
    for number, kind, is_optional, values in _dependencies(text):
        for value in values:
            if kind == "host_tool":
                host_tools.add(value)
            elif kind != "unsupported" and literal_path(value):
                (optional if is_optional else required).add(value)
            elif "$" in value:
                dynamic.add(number)
            else:
                review.add(number)
    # A required occurrence takes precedence over an optional occurrence.
    optional -= required
    available = set(available_paths)
    return {
        "required_paths": sorted(required),
        "optional_paths": sorted(optional),
        "missing_required_paths": sorted(required - available),
        "missing_optional_paths": sorted(optional - available),
        "dynamic_lines": sorted(dynamic),
        "review_lines": sorted(review),
        "host_tool_names": sorted(host_tools),
        "missing_host_tools": sorted(host_tools - set(available_tools)),
    }


def dynamic_dependency_lines(text):
    return dependency_report(text)["dynamic_lines"]


def unresolved_file_dependencies(text, available_paths):
    return all_file_dependencies(text) - set(available_paths)


def unresolved_paths(text, available_paths):
    return referenced_paths(text) - set(available_paths)


def source_gate(text, available_paths, required):
    """Check explicit required references only; does not establish buildability."""
    report = dependency_report(text, available_paths)
    return (set(required) <= set(report["required_paths"])
            and not (set(required) - set(available_paths))
            and not report["dynamic_lines"] and not report["review_lines"]
            and not report["missing_host_tools"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("makefile", type=Path, help="Local Makefile; read-only")
    parser.add_argument("--available-list", type=Path, required=True, help="One verified file path per line")
    parser.add_argument("--available-tools", type=Path, help="One verified host tool module name per line")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable inventory")
    parser.add_argument("--strict", action="store_true", help="Exit 1 for missing required paths or expressions needing review")
    args = parser.parse_args(argv)
    try:
        available = {x.strip() for x in args.available_list.read_text(encoding="utf-8").splitlines()
                     if x.strip() and not x.lstrip().startswith("#")}
        available_tools = set()
        if args.available_tools:
            available_tools = {x.strip() for x in args.available_tools.read_text(encoding="utf-8").splitlines()
                               if x.strip() and not x.lstrip().startswith("#")}
        report = dependency_report(args.makefile.read_text(encoding="utf-8"), available, available_tools)
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, sort_keys=True, indent=2))
    else:
        for path in report["missing_required_paths"]:
            print("UNRESOLVED:", path)
        for path in report["missing_optional_paths"]:
            print("OPTIONAL_MISSING:", path)
        for line_number in report["dynamic_lines"]:
            print("DYNAMIC_REVIEW_REQUIRED: line", line_number)
        for line_number in report["review_lines"]:
            print("SYNTAX_REVIEW_REQUIRED: line", line_number)
        for name in report["missing_host_tools"]:
            print("HOST_TOOL_UNRESOLVED:", name)
        print("Static inventory across all branches; does not establish Android 17 build compatibility.")
    blocked = (report["missing_required_paths"] or report["dynamic_lines"]
               or report["review_lines"] or report["missing_host_tools"])
    return int(bool(args.strict and blocked))


if __name__ == "__main__":
    raise SystemExit(main())
