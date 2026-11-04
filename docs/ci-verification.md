# CI verification

## Inspected history — 2026-11-04 UTC

GitHub Actions run [41936164779](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41936164779) finished successfully on baseline commit `e38e392c71eefec6b7bce3d703bd8a9c9dbe709a`. Its 108 offline tests also passed locally before these changes.

The earlier failed run [41935247426](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41935247426) reached the test step and failed three assertions because the scanner missed `BOARD_CUSTOM_BOOTIMG_MK`. Commit `84cbb76e248952e685aaad9116b1ceed802ecf9b` fixed the regex and [41935332860](https://github.com/cihan-ux/GalaxyA7-Android17-Port/actions/runs/41935332860) passed. This was a parser regression, not an Android build failure.

That failed run also reported the `actions/checkout@v4` Node.js 20 deprecation warning. The workflow now pins Node.js 24 actions to the verified `v6` commit heads: [checkout](https://github.com/actions/checkout/blob/d23441a48e516b6c34aea4fa41551a30e30af803/action.yml) and [setup-python](https://github.com/actions/setup-python/blob/ece7cb06caefa5fff74198d8649806c4678c61a1/action.yml).

## Reproduce the checks

From the repository root with Python 3.11 or later:

```sh
python3 tools/check_research_manifest.py
python3 tools/check_source_evidence.py
python3 -m unittest discover -s tests -v
```

CI runs these commands on Python 3.11 and 3.14 using `ubuntu-24.04`, avoiding dependence on whichever system Python happens to ship in `ubuntu-latest`. Source fixture verification checks exact local bytes and provenance against the pinned research manifest; it performs no upstream download. No third-party Python packages are required by the checks.

The workflow runs on pushes and pull requests changing manifests, tools, tests (including source fixtures), documentation, the root README, or the workflow itself. It can also be started manually. The token has only `contents: read`; checkout does not persist credentials.

This is a successful **offline research-manifest validation**, not an Android build, boot test, vendor compatibility test or flashable image. The repository remains blocked on complete dependencies and device-specific partition verification.

Downloading the GitHub Actions and setting up the interpreter require normal runner network access; the validation commands themselves are offline. CI does not check out an Android source tree, extract proprietary blobs, build images, or access a phone. A passing run establishes research-tool behavior and fixture integrity only.
