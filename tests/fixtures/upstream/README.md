# Source evidence fixtures

These complete upstream source files are inputs to offline audits. They are not
a build tree. No proprietary vendor files or Samsung binaries are included.

`manifest.json` records immutable repository revisions, upstream paths, exact
byte lengths, SHA-256 digests, and Git blob object IDs. The blob IDs and byte
lengths were checked against the GitHub Git Trees API at the recorded revisions;
the local files were then checked against those objects. `url` and `raw_url`
allow independent retrieval. `manifest_project` binds device/common/kernel
fixtures to the three-project research XML. Other entries are explicitly scoped
as source, candidate, or target evidence; inclusion does not approve a dependency
for a build manifest.

Run from any directory:

```sh
python3 /path/to/GalaxyA7-Android17-Port/tools/check_source_evidence.py
```

This verifies local integrity without networking or executing Makefiles. It
cannot independently authenticate upstream while offline: a reviewer must check
the recorded commit/path/object IDs against upstream when updating the inventory.
Retrieve exact bytes from each immutable `raw_url`, preserve line endings and
notices, compare to the corresponding Git Trees API blob, then review both the
source change and provenance update. Never update only a digest to silence a
failure.

The device repository's Apache 2.0 license text is retained in `device/LICENSE`;
Apache source headers are unchanged. XML manifests inherit that repository
license. Kernel `COPYING` is retained with the Linux Makefile and defconfig.
Target allocator's Blueprint inherits its upstream package license; the other
target Blueprints include Apache headers. These file-level declarations do not
clear licenses or redistribution rights for entire dependency repositories.
