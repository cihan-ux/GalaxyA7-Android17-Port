"""Offline SLSI repository candidate inventory; discovery != build compatibility."""
from dataclasses import dataclass

@dataclass(frozen=True)
class SourceLead:
    owner: str
    repository: str
    observed_default_branch: str
    required_baseline: str = "lineage-18.1"
    exact_baseline_commit_verified: bool = False
    license_review_complete: bool = False
    integration_verified: bool = False

LEADS = (
    SourceLead("LineageOS", "android_hardware_samsung_slsi-linaro_interfaces", "lineage-24.0"),
    SourceLead("LineageOS", "android_hardware_samsung_slsi-linaro_config", "lineage-24.0"),
    SourceLead("8890q", "android_hardware_samsung_slsi-linaro_exynos", "lineage-20"),
    SourceLead("8890q", "android_hardware_samsung_slsi-linaro_exynos5", "lineage-20"),
    SourceLead("8890q", "android_hardware_samsung_slsi-linaro_graphics", "lineage-20"),
    SourceLead("8890q", "android_hardware_samsung_slsi-linaro_openmax", "lineage-20"),
)

def ready(lead):
    return (lead.exact_baseline_commit_verified and lead.license_review_complete
            and lead.integration_verified)

if __name__ == "__main__":
    for lead in LEADS:
        print(f"{'READY' if ready(lead) else 'BLOCKED'} {lead.owner}/{lead.repository} default={lead.observed_default_branch}")
    print("Current default branches are not evidence of historical branch availability.")
