# Galaxy A7 2018 (SM-A750F) — Android 17 port research

**Status: research-only. Not buildable or flashable.** No Android 17 ROM has been produced or tested.

Target: Samsung Galaxy A7 (2018), **a7y18lte**, Exynos 7885. Previously recorded handset baseline: Android 10, firmware A750FXXU5CVG1 (U5), Linux 4.4.177, arm64 ABI. No phone was accessed during this audit.

## Source candidates (not yet verified as a complete build set)
- [Pinned maintained LineageOS 18.1 device tree](https://github.com/exynos7885-dev/device_samsung_a7y18lte/tree/f17643ba01010c45b628d5acb8f48350ded61606)
- [Pinned common tree](https://github.com/exynos7885-dev/device_samsung_exynos7885-common/tree/f2ce8d2093711026f021cba7036334d381d455ef)
- [Pinned kernel, source version 4.4.302](https://github.com/exynos7885-dev/kernel_samsung_exynos7885/tree/6020dfa8315134187f07ca903c9d2ed7ee0256f5)
- [Alternative device tree](https://github.com/nnhra/android_device_samsung_a7y18lte)
- [Device recovery/GSI notes](https://github.com/Hari-Pi/a7y18lte-Resources)
- [LineageOS upstream](https://github.com/LineageOS/android)

## Milestones
1. Audit device, common device, kernel, vendor trees, branches and licenses.
2. Verify a working baseline and collect hardware functionality reports.
3. Assess Android 17 kernel/HAL/SELinux/partition compatibility.
4. Prepare a reviewable experimental port; no flashing instructions until recovery is verified.
5. Build on an appropriately equipped Linux machine and validate artifacts.

Do not confuse **a7y18lte** (2018) with **a7y17lte** (2017). Do not upload proprietary firmware, credentials, or personal data.

## Reproduce the research checks

Python 3.11 or later; no Python packages or Android checkout required:

```sh
python3 tools/check_research_manifest.py
python3 tools/check_source_evidence.py
python3 -m unittest discover -s tests -v
```

The tests include checksummed upstream source files, not vendor binaries. The three-project manifest is incomplete: Samsung SLSI, boot tooling, vendor provenance and a complete platform checkout remain unresolved. Passing these checks does not establish buildability.

Start with the [source evidence audit](docs/source-evidence-audit.md), [Android 17 source comparison](docs/android17-source-compatibility.md), and [development report](docs/development-report.md). The [baseline audit](docs/baseline-source-audit.md) corrects earlier notes that mixed the separate `old_device_*` repositories with the maintained pins.
