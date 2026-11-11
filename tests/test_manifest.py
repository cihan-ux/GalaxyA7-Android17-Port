"""Offline, read-only checks for the historical source inventory."""
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_research_manifest import EXPECTED, MANIFEST, BLOCKERS, PINNED_REVISIONS, PROJECTS


class ResearchManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ET.parse(MANIFEST).getroot()
        cls.projects = cls.root.findall("project")

    def test_pinned_project_count(self):
        self.assertEqual(len(self.projects), len(EXPECTED))

    def test_remote_is_expected(self):
        remotes = {r.get("name"): r.get("fetch") for r in self.root.findall("remote")}
        self.assertEqual(remotes.get("exynos7885-dev"), "https://github.com/exynos7885-dev/")
        self.assertEqual(remotes.get("lineageos"), "https://github.com/LineageOS/")
        self.assertTrue(all(p.get("remote") == PROJECTS[p.get("path")][1] for p in self.projects))

    def test_xml_root(self):
        self.assertEqual(self.root.tag, "manifest")

    def test_unique_paths(self):
        paths = [p.get("path") for p in self.projects]
        self.assertEqual(len(paths), len(set(paths)))

    def test_expected_projects(self):
        paths = {p.get("path"): p for p in self.projects}
        for path, name in EXPECTED.items():
            self.assertIn(path, paths)
            self.assertEqual(paths[path].get("name"), name)
            self.assertEqual(paths[path].get("revision"), PINNED_REVISIONS[path])
            self.assertEqual(paths[path].get("remote"), PROJECTS[path][1])

    def test_not_misrepresented_as_android17(self):
        self.assertTrue(all(p.get("revision") == PINNED_REVISIONS[p.get("path")] for p in self.projects))

    def test_unresolved_dependencies_not_claimed(self):
        paths = {p.get("path") for p in self.projects}
        self.assertTrue(all(blocker not in paths for blocker in BLOCKERS))


if __name__ == "__main__":
    unittest.main()
