#!/usr/bin/env python3
"""Offline arithmetic audit of pinned Exynos7885 partition constants.

Source constants are not measurements of an SM-A750F handset.
No device access, writes, flashing, or network.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class PartitionPlan:
    system: int = 4093640704
    vendor: int = 419430400
    odm: int = 369098752
    super: int = 4882169856
    dynamic_group: int = 4878169856
    boot: int = 33554432
    recovery: int = 39845888
    cache: int = 262144000

def audit(plan=PartitionPlan()):
    issues = []
    physical_total = plan.system + plan.vendor + plan.odm
    if physical_total != plan.super:
        issues.append("BLOCK: sum of source block-device sizes differs from super size")
    if plan.dynamic_group > plan.super:
        issues.append("BLOCK: logical group size exceeds super size")
    if plan.super - plan.dynamic_group < 0:
        issues.append("BLOCK: negative metadata reserve")
    for name, size in vars(plan).items():
        if size <= 0:
            issues.append(f"BLOCK: non-positive {name} size")
    return {
        "physical_total": physical_total,
        "metadata_reserve": plan.super - plan.dynamic_group,
        "issues": issues,
        "device_verified": False,
    }

def main():
    result = audit()
    print("Pinned source physical partition sum:", result["physical_total"])
    print("Pinned source super metadata reserve:", result["metadata_reserve"])
    for issue in result["issues"]:
        print(issue)
    print("NOT VERIFIED: SM-A750F physical sizes, dynamic metadata, or Android 17 support")
    return 1 if result["issues"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
