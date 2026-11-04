"""Offline historical SLSI candidate inventory with exact verified branch-head SHAs.

These are lineage-19.1 branch HEADs from a different chipset family (8890/8895).
They are NOT approved as Exynos7885/LineageOS18.1 or Android17 dependencies.
"""
from dataclasses import dataclass

SHAS = {
    "config": "99f70404432d35b38eef86d29a68858ae55559b1",
    "exynos": "c04e384bc671c8aa490dfb031af5fc5551490b28",
    "exynos5": "dd2f9115c2fcb8767a9766da898f06b657872997",
    "graphics": "400aaac267c6e5a8f8a3ad747d9b64a2d2cd281a",
    "openmax": "509019f59bf3de7633e0914718a7d001fd84888d",
}
REQUIRED = frozenset({"config", "exynos", "exynos5", "graphics", "interfaces", "openmax"})
CONFIRMED_ABSENT = frozenset({"BoardConfig7885.mk"})  # 404 at pinned 8890q config commit

@dataclass(frozen=True)
class HistoricalCandidate:
    owner: str = "8890q"
    branch: str = "lineage-19.1"
    chipset_7885_config_verified: bool = False
    interface_dependency_verified: bool = False
    baseline_compatibility_verified: bool = False

def valid_sha(sha):
    return isinstance(sha, str) and len(sha) == 40 and all(x in "0123456789abcdef" for x in sha)

def eligible(candidate=HistoricalCandidate()):
    return (candidate.chipset_7885_config_verified
            and candidate.interface_dependency_verified
            and candidate.baseline_compatibility_verified
            and REQUIRED <= SHAS.keys()
            and all(valid_sha(sha) for sha in SHAS.values()))

if __name__ == "__main__":
    for name, sha in SHAS.items():
        print(f"VERIFIED HISTORICAL BRANCH HEAD: {name} {sha}")
    print("UNRESOLVED:", ", ".join(sorted(REQUIRED - SHAS.keys())))
    print("NOT APPROVED for SM-A750F / Exynos7885 / Android17:", not eligible())
