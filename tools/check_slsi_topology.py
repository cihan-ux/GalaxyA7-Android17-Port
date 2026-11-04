"""Read-only offline representation of split SLSI BSP dependency topology."""
SLSI_ROOT = "hardware/samsung_slsi-linaro/"
REQUIRED = frozenset({
    SLSI_ROOT + "config",
    SLSI_ROOT + "exynos",
    SLSI_ROOT + "exynos5",
    SLSI_ROOT + "graphics",
    SLSI_ROOT + "interfaces",
    SLSI_ROOT + "openmax",
})
DISCOVERED = frozenset({SLSI_ROOT + "config"})

def missing_paths(discovered=DISCOVERED):
    return REQUIRED - set(discovered)

def complete(discovered=DISCOVERED):
    return not missing_paths(discovered)

if __name__ == "__main__":
    print("Candidate paths found:", len(DISCOVERED))
    for path in sorted(missing_paths()):
        print("UNRESOLVED:", path)
    print("No claim of build compatibility or Android 17 support.")
