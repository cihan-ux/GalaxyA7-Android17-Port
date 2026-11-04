"""Historical branch evidence inventory, read-only and offline.

A failed branch lookup is recorded as unverified, not proof a branch never existed.
"""
from dataclasses import dataclass

COMPONENTS = ("config", "exynos", "exynos5", "graphics", "interfaces", "openmax")
BRANCHES = ("lineage-18.1", "lineage-19.1")

@dataclass(frozen=True)
class BranchEvidence:
    component: str
    branch: str
    verified_sha: str | None = None

EVIDENCE = tuple(BranchEvidence(component, branch) for component in COMPONENTS for branch in BRANCHES)

def valid_sha(value):
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value)

def verified(entry):
    return entry.component in COMPONENTS and entry.branch in BRANCHES and valid_sha(entry.verified_sha)

def historical_coverage(entries=EVIDENCE):
    return {c: any(verified(x) and x.component == c for x in entries) for c in COMPONENTS}

if __name__ == "__main__":
    for component, has_verified_pin in historical_coverage().items():
        print(f"{component}: {'PIN VERIFIED' if has_verified_pin else 'UNVERIFIED'}")
    print("No repository imported and no phone accessed.")
