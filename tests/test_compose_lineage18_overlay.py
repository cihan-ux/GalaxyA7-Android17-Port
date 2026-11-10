"""Tests for safely overlaying immutable A7 source pins on LineageOS 18.1."""

import sys
import tempfile
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compose_lineage18_overlay import RESEARCH, make_overlay, main


class A7SourceOverlayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / "platform.xml"

    def write_base(self, projects="", remotes=""):
        self.base.write_text("<manifest>" + remotes + projects + "</manifest>", encoding="utf-8")

    def test_all_13_pinned_sources_are_retained(self):
        self.write_base()
        overlay, stats = make_overlay(self.base)
        self.assertEqual(stats["pinned_projects"], 13)
        self.assertEqual(stats["overridden_platform_paths"], 0)
        self.assertEqual(len(overlay.findall("project")), 13)
        self.assertTrue(all(len(p.get("revision")) == 40 for p in overlay.findall("project")))

    def test_platform_collision_is_removed_before_replacement(self):
        self.write_base('<project path="hardware/samsung" name="LineageOS/android_hardware_samsung"/>'
                        '<project path="system/core" name="LineageOS/android_system_core"/>')
        overlay, stats = make_overlay(self.base)
        self.assertEqual(stats["overridden_platform_paths"], 1)
        remove = overlay.findall("remove-project")
        self.assertEqual(len(remove), 1)
        self.assertEqual(remove[0].get("name"), "LineageOS/android_hardware_samsung")
        self.assertEqual(stats["pinned_projects"], 13)
        self.assertFalse(any(p.get("path") == "system/core" for p in overlay.findall("project")))

    def test_collision_with_shared_project_name_fails_closed(self):
        self.write_base('<project path="hardware/samsung" name="same"/>'
                        '<project path="hardware/other" name="same"/>')
        with self.assertRaisesRegex(ValueError, "ambiguous remove-project"):
            make_overlay(self.base)

    def test_conflicting_remote_fails_closed(self):
        self.write_base(remotes='<remote name="exynos7885-dev" fetch="https://wrong.example/"/>')
        with self.assertRaisesRegex(ValueError, "conflicting remote"):
            make_overlay(self.base)

    def test_identical_remote_is_not_redeclared(self):
        self.write_base(remotes='<remote name="exynos7885-dev" fetch="https://github.com/exynos7885-dev/"/>')
        overlay, _ = make_overlay(self.base)
        self.assertEqual([r.get("name") for r in overlay.findall("remote")], ["lineageos"])

    def test_duplicate_platform_path_fails_closed(self):
        self.write_base('<project path="hardware/samsung" name="first"/>'
                        '<project path="hardware/samsung" name="second"/>')
        with self.assertRaisesRegex(ValueError, "duplicate project path"):
            make_overlay(self.base)

    def test_invalid_research_revision_rejected(self):
        self.write_base()
        original = RESEARCH.read_text()
        broken = Path(self.temp.name) / "unpinned.xml"
        broken.write_text(original.replace(
            "f17643ba01010c45b628d5acb8f48350ded61606", "lineage-18.1"))
        with self.assertRaisesRegex(ValueError, "floating or invalid"):
            make_overlay(self.base, broken)

    def test_cli_writes_parseable_local_manifest(self):
        self.write_base()
        out = Path(self.temp.name) / ".repo/local_manifests/a7.xml"
        self.assertEqual(main(["--base", str(self.base), "--out", str(out)]), 0)
        self.assertEqual(len(ET.parse(out).getroot().findall("project")), 13)

    def test_cli_refuses_overwrite_of_base_xml(self):
        self.write_base()
        self.assertEqual(main(["--base", str(self.base), "--out", str(self.base)]), 1)

    def test_no_mutation_to_research_manifest(self):
        self.write_base()
        before = RESEARCH.read_bytes()
        make_overlay(self.base)
        self.assertEqual(RESEARCH.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
