"""Regression checks for the historical, non-flashable LineageOS 18.1 USB source delta."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references/lineage18-a7y18lte-20261108.json"


class WorkingLineage18USBReferenceTests(unittest.TestCase):
    def setUp(self):
        self.meta = json.loads(REF.read_text(encoding="utf-8"))
        self.patch = ROOT / self.meta["kernel_source"]["reference_patch"]

    def test_release_metadata_is_model_specific_and_has_asset_digest(self):
        self.assertEqual(self.meta["target"]["codename"], "a7y18lte")
        self.assertEqual(self.meta["target"]["model"], "SM-A750F")
        self.assertEqual(self.meta["release"]["version"], "18.1")
        self.assertEqual(self.meta["release"]["size_bytes"], 742826234)
        self.assertEqual(len(bytes.fromhex(self.meta["release"]["sha256"])), 32)
        self.assertEqual(self.meta["kernel_source"]["base_commit"],
                         "6020dfa8315134187f07ca903c9d2ed7ee0256f5")
        self.assertEqual(self.meta["kernel_source"]["usb_resume_fix_commit"],
                         "2a074fb85d78d065df5c529d7c0d748454bcaa3a")

    def test_reference_patch_changes_only_legacy_usb_resume_callback(self):
        p = self.patch.read_text(encoding="utf-8")
        self.assertIn("Subject: [PATCH] usb: dwc3: gadget: release spin lock", p)
        self.assertIn("diff --git a/drivers/usb/dwc3/gadget.c b/drivers/usb/dwc3/gadget.c", p)
        self.assertEqual(sum(line.startswith("diff --git ") for line in p.splitlines()), 1)
        additions = [line[1:] for line in p.splitlines() if line.startswith("+") and not line.startswith("+++")]
        removals = [line for line in p.splitlines() if line.startswith("-") and not line.startswith("---")]
        self.assertEqual(additions, ["\t\tspin_unlock(&dwc->lock);", "\t\tspin_lock(&dwc->lock);"])
        self.assertFalse(removals)
        self.assertLess(p.index("+\t\tspin_unlock(&dwc->lock);"),
                        p.index(" \t\tdwc->gadget_driver->resume(&dwc->gadget);"))
        self.assertLess(p.index(" \t\tdwc->gadget_driver->resume(&dwc->gadget);"),
                        p.index("+\t\tspin_lock(&dwc->lock);"))

    @unittest.skipUnless(shutil.which("git"), "git is needed for patch applicability probe")
    def test_git_apply_on_pinned_legacy_function_context(self):
        # The exact seven-line hunk is from upstream kernel parent 6020dfa8.
        # This is a syntax/context test, NOT a full kernel build.
        original = (
            "\t */\n\n"
            "\tif (dwc->gadget_driver && dwc->gadget_driver->resume) {\n"
            "\t\tdwc->gadget_driver->resume(&dwc->gadget);\n"
            "\t}\n"
            "}\n\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "drivers/usb/dwc3/gadget.c"
            dst.parent.mkdir(parents=True)
            dst.write_text("\n" * 2992 + original, encoding="utf-8")
            checked = subprocess.run(["git", "apply", "--check", str(self.patch)],
                                     cwd=tmp, capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            applied = subprocess.run(["git", "apply", str(self.patch)],
                                     cwd=tmp, capture_output=True, text=True)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            after = dst.read_text(encoding="utf-8")
            self.assertIn("\t\tspin_unlock(&dwc->lock);\n"
                          "\t\tdwc->gadget_driver->resume(&dwc->gadget);\n"
                          "\t\tspin_lock(&dwc->lock);", after)


if __name__ == "__main__":
    unittest.main()
