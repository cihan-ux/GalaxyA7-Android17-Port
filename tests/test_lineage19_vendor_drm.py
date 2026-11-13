"""Vetted Widevine XML source presence is not proof of vendor-image inclusion."""
import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lineage19_vendor_drm import analyze

XML = """<manifest type="device"><hal format="hidl">
<name>android.hardware.drm</name>
<transport>hwbinder</transport>
<fqname>@1.3::ICryptoFactory/widevine</fqname>
<fqname>@1.3::IDrmFactory/widevine</fqname></hal></manifest>"""
BP = """prebuilt_etc_xml {
name: "manifest_android.hardware.drm@1.3-service.widevine",
src: "proprietary/vendor/etc/vintf/manifest/manifest_android.hardware.drm@1.3-service.widevine.xml",
sub_dir: "vintf/manifest",
soc_specific: true,
}"""
VENDOR = "vendor/.../bin/hw/android.hardware.drm@1.3-service.widevine:vendor/bin/hw/...\n"
COMMON = "PRODUCT_PACKAGES += android.hardware.drm@1.3-service.clearkey\n"


class DRMSourceTest(unittest.TestCase):
    def test_registered_fragment_is_not_installed_just_by_existing(self):
        result = analyze(XML, BP, VENDOR, COMMON)
        self.assertTrue(result["vendor_android_bp_prebuilt_registered"])
        self.assertFalse(result["explicit_prebuilt_module_reference_in_two_makefiles"])
        self.assertIsNone(result["fragment_confirmed_in_android_12l_output"])
        self.assertIsNone(result["runtime_drm_operational"])

    def test_reject_missing_second_fqname(self):
        with self.assertRaises(ValueError):
            analyze(XML.replace("<fqname>@1.3::IDrmFactory/widevine</fqname>", ""),
                    BP, VENDOR, COMMON)

    def test_reject_wrong_bp_install_location(self):
        with self.assertRaises(ValueError):
            analyze(XML, BP.replace('sub_dir: "vintf/manifest"', 'sub_dir: "random"'),
                    VENDOR, COMMON)

    def test_explicit_package_reference_changes_only_the_source_signal(self):
        result = analyze(XML, BP, VENDOR + "\nPRODUCT_PACKAGES += manifest_android.hardware.drm@1.3-service.widevine\n", COMMON)
        self.assertTrue(result["explicit_prebuilt_module_reference_in_two_makefiles"])
        self.assertIsNone(result["fragment_confirmed_in_android_12l_output"])


if __name__ == "__main__":
    unittest.main()
