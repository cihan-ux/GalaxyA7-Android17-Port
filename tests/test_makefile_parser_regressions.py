"""Whole-source and adversarial regressions for the read-only Make inventory."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_makefile_dependencies import (
    all_file_dependencies, configured_file_paths, dependency_report,
    dynamic_dependency_lines, main, referenced_paths, source_gate,
)
from audit_exynos7885_build_paths import assignment_dependencies, direct_dependency_report

FIXTURES = ROOT / "tests/fixtures/upstream"


class MakefileParserRegressionTests(unittest.TestCase):
    def test_full_common_board_includes_lineage_policy_and_host_tool(self):
        source = (FIXTURES / "common/BoardConfigCommon.mk").read_text(encoding="utf-8")
        report = dependency_report(source)
        self.assertEqual(report["required_paths"], [
            "device/lineage/sepolicy/exynos/sepolicy.mk",
            "device/samsung_slsi/sepolicy/sepolicy.mk",
            "hardware/samsung/mkbootimg.mk",
            "hardware/samsung_slsi-linaro/config/BoardConfig7885.mk",
        ])
        self.assertEqual(report["host_tool_names"], ["dtbhtoolExynos"])
        self.assertNotIn("dtbhtoolExynos", all_file_dependencies(source))
        self.assertEqual(report["dynamic_lines"], [])
        build = direct_dependency_report(source)
        self.assertEqual(build["assigned_paths"]["TARGET_KERNEL_SOURCE"], "kernel/samsung/exynos7885")
        self.assertEqual(build["host_tool_names"], ["dtbhtoolExynos"])

    def test_full_device_product_finds_frameworks_dependency(self):
        source = (FIXTURES / "device/device.mk").read_text(encoding="utf-8")
        self.assertEqual(referenced_paths(source), {
            "frameworks/native/build/phone-xhdpi-4096-dalvik-heap.mk",
            "device/samsung/exynos7885-common/exynos7885.mk",
            "vendor/samsung/a7y18lte/a7y18lte-vendor.mk",
        })

    def test_full_product_reports_platform_variable_lines(self):
        source = (FIXTURES / "device/lineage_a7y18lte.mk").read_text(encoding="utf-8")
        self.assertEqual(dynamic_dependency_lines(source), [8, 9])
        self.assertEqual(referenced_paths(source), {
            "device/samsung/a7y18lte/device.mk",
            "vendor/lineage/config/common_full_phone.mk",
        })

    def test_full_common_product_ignores_cfi_directory(self):
        source = (FIXTURES / "common/exynos7885.mk").read_text(encoding="utf-8")
        self.assertEqual(all_file_dependencies(source), {
            "hardware/samsung_slsi-linaro/config/config.mk",
            "vendor/samsung/exynos7885-common/exynos7885-common-vendor.mk",
        })

    def test_full_slsi_sources_share_include_but_select_different_composers(self):
        historical = (FIXTURES / "slsi18/BoardConfig7885.mk").read_text(encoding="utf-8")
        modern = (FIXTURES / "slsi-config/BoardConfig7885.mk").read_text(encoding="utf-8")
        common = "hardware/samsung_slsi-linaro/config/BoardConfigCommon.mk"
        self.assertIn(common, referenced_paths(historical))
        self.assertIn(common, referenced_paths(modern))
        self.assertRegex(historical, r"(?m)^BOARD_HWC_VERSION\s*:=\s*libhwc2\.1\s*$")
        self.assertRegex(modern, r"(?m)^BOARD_HWC_VERSION\s*:=\s*hwc3\s*$")

    def test_dynamic_path_does_not_become_a_literal_prefix_or_suffix(self):
        for source in [
            "include hardware/samsung/$(TARGET).mk",
            "include $(ROOT)/hardware/samsung/file.mk",
            "include ${ROOT}/hardware/samsung/file.mk",
            "BOARD_CUSTOM_BOOTIMG_MK := hardware/samsung/$(TARGET).mk",
            "$(call inherit-product, $(wildcard hardware/samsung/*.mk))",
        ]:
            with self.subTest(source=source):
                self.assertEqual(all_file_dependencies(source), set())
                self.assertEqual(dynamic_dependency_lines(source), [1])

    def test_literal_and_dynamic_operands_on_same_include_are_separated(self):
        report = dependency_report("include hardware/samsung/one.mk $(call foo, hardware/samsung/two.mk)")
        self.assertEqual(report["required_paths"], ["hardware/samsung/one.mk"])
        self.assertEqual(report["dynamic_lines"], [1])

    def test_wildcards_and_traversal_are_reported_for_review(self):
        source = "include hardware/samsung/*.mk\ninclude hardware/samsung/../other.mk"
        self.assertEqual(referenced_paths(source), set())
        self.assertEqual(dependency_report(source)["review_lines"], [1, 2])

    def test_continued_include_keeps_start_line_and_each_literal(self):
        source = "# preface\ninclude \\\n    hardware/samsung/one.mk \\\n    hardware/samsung/two.mk $(ROOT)/three.mk\n"
        report = dependency_report(source)
        self.assertEqual(report["required_paths"], ["hardware/samsung/one.mk", "hardware/samsung/two.mk"])
        self.assertEqual(report["dynamic_lines"], [2])

    def test_continued_assignment_is_recognized_by_both_scanners(self):
        source = "TARGET_KERNEL_SOURCE := \\\n    kernel/samsung/exynos7885\nBOARD_CUSTOM_BOOTIMG_MK := \\\n    hardware/samsung/mkbootimg.mk"
        self.assertEqual(assignment_dependencies(source)["TARGET_KERNEL_SOURCE"], "kernel/samsung/exynos7885")
        self.assertEqual(configured_file_paths(source), {"hardware/samsung/mkbootimg.mk"})

    def test_continued_comment_does_not_expose_fake_include(self):
        source = "# ignored \\\ninclude hardware/samsung/fake.mk\ninclude hardware/samsung/real.mk # $(IGNORED)"
        self.assertEqual(referenced_paths(source), {"hardware/samsung/real.mk"})
        self.assertEqual(dynamic_dependency_lines(source), [])

    def test_recipe_and_similarly_named_function_are_not_directives(self):
        source = "\tinclude hardware/samsung/recipe.mk\n$(call inherit-product-other, vendor/samsung/fake.mk)\ninclude_other hardware/samsung/fake.mk"
        self.assertEqual(all_file_dependencies(source), set())

    def test_optional_includes_are_distinct_from_required(self):
        source = "-include device/samsung/optional.mk\nsinclude vendor/samsung/optional.mk\n$(call inherit-product-if-exists, vendor/samsung/product.mk)\ninclude hardware/samsung/required.mk"
        report = dependency_report(source)
        self.assertEqual(report["required_paths"], ["hardware/samsung/required.mk"])
        self.assertEqual(len(report["missing_optional_paths"]), 3)
        self.assertFalse(source_gate(source, {"device/samsung/optional.mk"}, {"device/samsung/optional.mk"}))

    def test_required_occurrence_takes_precedence(self):
        source = "-include hardware/samsung/one.mk\ninclude hardware/samsung/one.mk"
        report = dependency_report(source)
        self.assertEqual(report["optional_paths"], [])
        self.assertEqual(report["missing_required_paths"], ["hardware/samsung/one.mk"])

    def test_directory_inventory_does_not_resolve_required_file(self):
        report = dependency_report("include hardware/samsung/mkbootimg.mk", {"hardware/samsung"})
        self.assertEqual(report["missing_required_paths"], ["hardware/samsung/mkbootimg.mk"])

    def test_single_letter_make_variables_require_review(self):
        self.assertEqual(dynamic_dependency_lines("include $x/file.mk"), [1])

    def test_host_tool_can_be_verified_separately_from_file_inventory(self):
        source = "TARGET_CUSTOM_DTBTOOL := dtbhtoolExynos"
        report = dependency_report(source, available_tools={"dtbhtoolExynos"})
        self.assertEqual(report["missing_host_tools"], [])
        self.assertEqual(report["required_paths"], [])

    def test_alternative_kernel_paths_are_all_reported_as_candidates(self):
        source = "ifeq ($(VARIANT),a)\nTARGET_KERNEL_SOURCE := kernel/samsung/one\nelse\nTARGET_KERNEL_SOURCE := kernel/samsung/two\nendif"
        report = direct_dependency_report(source, {"kernel/samsung/two"})
        self.assertEqual(report["assigned_path_candidates"]["TARGET_KERNEL_SOURCE"], ["kernel/samsung/one", "kernel/samsung/two"])
        self.assertEqual(report["unresolved_assigned_paths"], ["kernel/samsung/one"])

    def test_dynamic_kernel_path_is_reported(self):
        report = direct_dependency_report("TARGET_KERNEL_SOURCE := $(KERNEL_PATH)")
        self.assertEqual(report["assigned_paths"], {})
        self.assertEqual(report["dynamic_lines"], [1])

    def test_unsupported_kernel_paths_remain_visible_for_review(self):
        for value in ["kernel/a*/b", "../../bad", "kernel/samsung/../other", "kernel/one kernel/two", "/kernel/samsung/exynos7885", "unsupported-root/source"]:
            with self.subTest(value=value):
                report = direct_dependency_report("# preface\nTARGET_KERNEL_SOURCE := " + value)
                self.assertEqual(report["assigned_paths"], {})
                self.assertEqual(report["assigned_path_candidates"], {})
                self.assertEqual(report["review_lines"], [2])
                self.assertEqual(report["dynamic_lines"], [])

    def test_unsupported_continued_kernel_assignment_retains_start_line(self):
        source = "# preface\nTARGET_KERNEL_SOURCE := \\\n    kernel/samsung/*\n"
        self.assertEqual(direct_dependency_report(source)["review_lines"], [2])

    def test_malformed_and_unterminated_operands_do_not_silently_pass(self):
        for source in ["include", "-include", "sinclude", "include ", "include hardware/samsung/a.mk \\", "$(call inherit-product, vendor/samsung/a.mk"]:
            with self.subTest(source=source):
                report = dependency_report(source)
                self.assertTrue(report["review_lines"] or report["dynamic_lines"])

    def test_strict_cli_has_useful_exit_status_and_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            makefile, inventory = Path(directory) / "BoardConfig.mk", Path(directory) / "files.txt"
            inventory.write_text("  # verified file inventory\nhardware/samsung/present.mk\n", encoding="utf-8")
            makefile.write_text("include hardware/samsung/missing.mk", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = main([str(makefile), "--available-list", str(inventory), "--json", "--strict"])
            self.assertEqual(status, 1)
            self.assertEqual(json.loads(output.getvalue())["missing_required_paths"], ["hardware/samsung/missing.mk"])
            makefile.write_text("include hardware/samsung/present.mk\n-include hardware/samsung/optional.mk", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(makefile), "--available-list", str(inventory), "--strict"]), 0)


if __name__ == "__main__":
    unittest.main()
