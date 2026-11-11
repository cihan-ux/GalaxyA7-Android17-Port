# Exynos7885 Linaro/BSP dependency closure

The pinned [Exynos7885 common tree](https://github.com/exynos7885-dev/device_samsung_exynos7885-common) uses a Linaro include `hardware/samsung_slsi-linaro/config/BoardConfig7885.mk`. A separate historical [universal7885 common tree](https://github.com/MacBookPro34-comma-7/android_device_samsung_universal7885-common) uses `TARGET_SLSI_VARIANT := bsp` and `device/samsung_slsi/sepolicy/sepolicy.mk`. These are different build graphs and must not be merged solely because they share a chipset. The Linaro config candidate [Exynos2100-common](https://github.com/Exynos2100-common/android_hardware_samsung_slsi-linaro_config) has a BoardConfig7885 file, but its newer branch does not prove LineageOS18.1 compatibility.

The offline scanner `tools/audit_makefile_dependencies.py` reads local Makefile text and an explicit list of verified available files. It extracts whole literal operands from `include`, `-include`, `sinclude`, and `inherit-product` calls, plus allowlisted configured file variables. Continuations retain their first physical line number; comments and recipes are excluded. It **does not execute Makefiles**, expand variables, resolve transitive includes, evaluate conditionals/assignment precedence, inspect Soong namespaces, or claim build readiness. Results inventory all syntactic branches.

Usage:

```sh
python3 tools/audit_makefile_dependencies.py /path/to/BoardConfigCommon.mk --available-list /path/to/verified-paths.txt
python3 tools/audit_makefile_dependencies.py tests/fixtures/upstream/common/BoardConfigCommon.mk --available-list /dev/null --json --strict
python3 -m unittest discover -s tests -v
```

The second command intentionally exits **1**: an empty inventory cannot resolve four required files and the `dtbhtoolExynos` host tool. Supply verified full file paths, one per line; a directory prefix cannot resolve a file. `--available-tools` accepts a separate list of verified host module names. Optional missing literal includes are reported separately and do not fail `--strict`; dynamic or unsupported expressions require review and do fail it. Without `--strict`, the command remains an informational inventory. Invalid input files exit 2 through argparse.

Whole-operand matching avoids false literals such as `hardware/samsung/` extracted from `hardware/samsung/$(TARGET).mk`. Real source fixtures also exercise `frameworks/native/...` includes that the earlier scanner missed. `tools/audit_exynos7885_build_paths.py` separately inventories `TARGET_KERNEL_SOURCE` directories and retains all literal candidates across branches, plus unresolved expression line numbers. Its legacy `assigned_paths` field is the last literal candidate per key, not evaluated Make state.

**Current blockers:** a complete compatible SLSI set, vendor provenance and HAL/VINTF adaptation. [Matching SLSI config/sibling candidates](slsi-matching-source-discovery.md) and a Samsung boot Makefile have now been found, with [source fixtures](source-evidence-audit.md); finding those files does not validate the full checkout. Shared `device/samsung_slsi/sepolicy` remains a dependency of both inspected BSP variants. No source was added to the build manifest; no ROM build or phone operation was attempted.
