"""Non-destructive guards for staging LineageOS 19.1 over the 18.1 source."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from stage_lineage19_device import (  # noqa: E402
    BASELINE_SHA, BASELINE_ORIGIN, FILES, checkout_problem,
)

class DeviceStageGuards(unittest.TestCase):
    def test_exact_pin_and_origin_allowed(self):
        self.assertIsNone(checkout_problem(BASELINE_SHA, BASELINE_ORIGIN + ".git", ""))
        self.assertEqual(FILES, ("AndroidProducts.mk", "lineage_a7y18lte.mk"))

    def test_wrong_checkout_rejected(self):
        self.assertIsNotNone(checkout_problem("0" * 40, BASELINE_ORIGIN, ""))

    def test_wrong_origin_rejected(self):
        self.assertIsNotNone(checkout_problem(BASELINE_SHA, "https://github.com/other/repo.git", ""))

    def test_dirty_checkout_rejected(self):
        self.assertIsNotNone(checkout_problem(BASELINE_SHA, BASELINE_ORIGIN,
                                                " M device.mk"))

if __name__ == "__main__":
    unittest.main()
