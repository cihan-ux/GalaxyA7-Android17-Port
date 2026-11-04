"""Compare independently sourced Exynos7885 historical board constants offline.

These are *source configurations*, not measurements of the user's SM-A750F.
"""
PINNED_A7 = {"boot":33554432,"cache":262144000,"recovery":39845888,"system":4093640704}
ALTERNATE_UNIVERSAL7885 = {"boot":33554432,"cache":209715200,"recovery":39845888,"system":3833593856}
PINNED_SLSI_VARIANT = "linaro"
ALTERNATE_SLSI_VARIANT = "bsp"

def differences(a=PINNED_A7, b=ALTERNATE_UNIVERSAL7885):
    return {key:(a.get(key),b.get(key)) for key in a.keys() | b.keys() if a.get(key)!=b.get(key)}

def compatible_without_device_evidence():
    return False

if __name__=="__main__":
    for key, (current, alternative) in sorted(differences().items()):
        print(f"CONFLICT {key}: pinned={current} alternative={alternative}")
    print(f"CONFLICT SLSI variant: {PINNED_SLSI_VARIANT} vs {ALTERNATE_SLSI_VARIANT}")
    print("BLOCKED: no measured SM-A750F partition topology or build compatibility")
