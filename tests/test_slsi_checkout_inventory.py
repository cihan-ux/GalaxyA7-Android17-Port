import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_slsi_namespaces import checkout_inventory, DEFAULT_CONFIG

CONFIG = DEFAULT_CONFIG.read_text(encoding="utf-8")
BASE = "hardware/samsung_slsi-linaro"

class CheckoutNamespaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_empty_checkout_reports_five_missing(self):
        self.assertEqual(len(checkout_inventory(CONFIG, self.root)["unresolved"]), 5)

    def test_existing_directories_are_counted(self):
        (self.root / BASE / "graphics").mkdir(parents=True)
        result = checkout_inventory(CONFIG, self.root)
        self.assertEqual(result["present"], [BASE + "/graphics"])
        self.assertEqual(len(result["unresolved"]), 4)

    def test_regular_file_is_not_directory(self):
        path = self.root / BASE / "graphics"
        path.parent.mkdir(parents=True)
        path.write_text("not a directory")
        self.assertIn(BASE + "/graphics", checkout_inventory(CONFIG, self.root)["unresolved"])

    def test_symlinked_namespace_is_unsafe(self):
        outside = self.root / "external"
        outside.mkdir()
        base = self.root / BASE
        base.mkdir(parents=True)
        (base / "graphics").symlink_to(outside, target_is_directory=True)
        result = checkout_inventory(CONFIG, self.root)
        self.assertIn(BASE + "/graphics", result["unsafe_symlinks"])
        self.assertIn(BASE + "/graphics", result["unresolved"])

    def test_symlinked_parent_is_unsafe(self):
        actual = self.root / "actual"
        (actual / "graphics").mkdir(parents=True)
        (self.root / "hardware").mkdir()
        (self.root / "hardware" / "samsung_slsi-linaro").symlink_to(actual, target_is_directory=True)
        self.assertIn(BASE + "/graphics", checkout_inventory(CONFIG, self.root)["unsafe_symlinks"])

    def test_nonexistent_checkout_fails(self):
        with self.assertRaises(FileNotFoundError):
            checkout_inventory(CONFIG, self.root / "missing")
