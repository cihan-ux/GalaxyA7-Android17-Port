"""Pure-memory A7 ACPM read planner remains disconnected from hardware."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_a7_acpm_read_plan import SRC, HDR, audit


class ReadPlanSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SRC.read_text()
        cls.header = HDR.read_text()

    def test_original_offline_lifecycle(self):
        self.assertEqual(audit(self.source, self.header), [])

    def test_reject_accidental_mailbox_send(self):
        self.assertTrue(audit(self.source + "\nmbox_send_message(chan, data);", self.header))

    def test_reject_irq_mask_mmio(self):
        self.assertTrue(audit(self.source + "\nwritel(BIT(2), regs);", self.header))

    def test_reject_accepting_buffer_as_queue(self):
        self.assertTrue(audit(
            self.source.replace("channel->type != A7_ACPM_QUEUE_TYPE",
                                "channel->type != A7_ACPM_BUFFER_TYPE"), self.header))

    def test_reject_missing_response_sequence_and_register_match(self):
        self.assertTrue(audit(
            self.source.replace(
                "(word & 0x0fffU) == (request->request.word[0] & 0x0fffU)",
                "(word & 0x0fffU) != (request->request.word[0] & 0x0fffU)"),
            self.header))

    def test_reject_unsafe_response_queue_mutation(self):
        self.assertTrue(audit(
            self.source + "\nmemmove(queue + 1, queue, 4);", self.header))

    def test_reject_removed_lifecycle_timeout(self):
        self.assertTrue(audit(
            self.source.replace("elapsed >= lifecycle->timeout_ms",
                                "elapsed < lifecycle->timeout_ms"),
            self.header))

    def test_reject_dropping_timeout_sequence_quarantine(self):
        self.assertTrue(audit(
            self.source.replace(
                "lifecycle->quarantined_sequence_low |=",
                "lifecycle->quarantined_sequence_low ="),
            self.header))

    def test_reject_real_sleep_or_clock_api(self):
        self.assertTrue(audit(self.source + "\nmsleep(20);", self.header))

    def test_reject_wrong_doorbell(self):
        self.assertTrue(audit(self.source, self.header.replace(
            "A7_ACPM_DOORBELL_INTGR0_OFFSET 0x0008U",
            "A7_ACPM_DOORBELL_INTGR0_OFFSET 0x001cU")))

    def test_reject_missing_bounds(self):
        self.assertTrue(audit(self.source.replace(
            "next_front == rear", "next_front == 9"), self.header))
        self.assertTrue(audit(self.source.replace(
            "layout.mlen != sizeof(frame)", "layout.mlen < sizeof(frame)"), self.header))

    def test_reject_wrong_sequence_placement(self):
        self.assertTrue(audit(self.source.replace(
            "seq << A7_ACPM_READ_SEQUENCE_SHIFT", "seq << 12U"), self.header))


if __name__ == "__main__":
    unittest.main()
