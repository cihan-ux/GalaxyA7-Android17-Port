"""Synthetic ZIP regression tests; no proprietary ROM files are required."""

import hashlib
from io import StringIO
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from inspect_lineage18_ota import inspect_ota, main


class Lineage18OTAInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.zip"

    def zip(self, entries):
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in entries:
                archive.writestr(name, content)
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def test_block_ota_and_public_build_metadata(self):
        digest = self.zip([
            ("META-INF/com/android/metadata",
             "ota-type=BLOCK\npre-device=a7y18lte\npost-sdk-level=30\n"
             "post-security-patch-level=2026-11-01\nprivate-serial=HIDDEN\n"),
            ("system.new.dat.br", b"opaque binary"),
            ("system.transfer.list", b"1\n"),
            ("vendor.new.dat.br", b"opaque vendor"),
            ("vendor/etc/private-user.txt", b"never report this"),
        ])
        result = inspect_ota(self.path, digest, self.path.stat().st_size)
        self.assertEqual(result["packaging"], "block_ota")
        self.assertEqual(result["partition_names"], ["system", "vendor"])
        self.assertEqual(result["public_metadata"]["pre-device"], "a7y18lte")
        self.assertNotIn("private-serial", str(result))
        self.assertNotIn("private-user", str(result))
        self.assertNotIn("opaque", str(result))
        self.assertEqual(result["archive"]["sha256"], digest)

    def test_payload_ota_takes_precedence(self):
        self.zip([("payload.bin", b"opaque"), ("payload_properties.txt", "FILE_HASH=X")])
        result = inspect_ota(self.path)
        self.assertEqual(result["packaging"], "payload_ota")
        self.assertIn("standard OTA metadata not found", result["warnings"])

    def test_single_image_and_file_tree_layouts(self):
        self.zip([("boot.img", b"image")])
        self.assertEqual(inspect_ota(self.path)["packaging"], "image_ota")
        self.zip([("system/build.prop", b"ro.test=1")])
        self.assertEqual(inspect_ota(self.path)["packaging"], "file_tree_ota")
        self.assertEqual(inspect_ota(self.path)["recognized_entries"], [])

    def test_checksum_mismatch_blocks_inventory_output(self):
        self.zip([("boot.img", b"image")])
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main([str(self.path), "--expected-sha256", "0" * 64])
        self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("SHA-256 mismatch", stderr.getvalue())

    def test_size_mismatch_blocks_inventory(self):
        self.zip([("boot.img", b"image")])
        with self.assertRaisesRegex(ValueError, "size does not match"):
            inspect_ota(self.path, expected_size=1)

    def test_reject_unsafe_paths_and_duplicate_names(self):
        for bad in ["../boot.img", "/boot.img", "vendor\\boot.img", "a//boot.img"]:
            with self.subTest(bad=bad):
                self.zip([(bad, b"data")])
                with self.assertRaisesRegex(ValueError, "unsafe or duplicate"):
                    inspect_ota(self.path)
        self.zip([("boot.img", b"A"), ("boot.img", b"B")])
        with self.assertRaisesRegex(ValueError, "unsafe or duplicate"):
            inspect_ota(self.path)

    def test_metadata_size_cap(self):
        self.zip([("META-INF/com/android/metadata", b"A" * 65537)])
        with self.assertRaisesRegex(ValueError, "metadata exceeds"):
            inspect_ota(self.path)

    def test_unknown_zip_does_not_leak_entry_names(self):
        self.zip([("some/private/personal-identifier.txt", b"secret")])
        report = inspect_ota(self.path)
        self.assertEqual(report["packaging"], "unknown")
        self.assertNotIn("personal-identifier", json.dumps(report))
        self.assertNotIn("secret", json.dumps(report))

    def test_invalid_zip_returns_nonzero(self):
        self.path.write_bytes(b"not zip")
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(main([str(self.path)]), 1)


if __name__ == "__main__":
    unittest.main()
