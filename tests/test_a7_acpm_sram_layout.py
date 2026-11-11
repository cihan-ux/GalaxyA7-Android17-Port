"""Fail closed on historical/new ACPM firmware ABI field order changes."""
import unittest
from tools.check_a7_acpm_sram_layout import audit, fields

OLD = """
struct acpm_framework {
 u32 plugins; u32 num_plugins; u32 ipc_channels; u32 num_ipc_channels;
 u32 pid_framework; u32 pid_max; u32 ipc_ap_max;
};
struct channel_info {
 u32 rx_rear; u32 rx_front; u32 rx_base; u32 rx_indr_buf;
 u32 rx_indr_buf_base; u32 rx_indr_buf_size; u32 tx_rear;
 u32 tx_front; u32 tx_base; u32 q_len; u32 q_elem_size;
 u32 credit; u32 mbox_addr;
};
struct ipc_channel {
 u32 id; u32 field; s32 owner; u32 type;
 struct channel_info ch; u32 ap_poll;
};
"""
NEW = """
struct acpm_shmem {
 u32 reserved[2]; u32 chans; u32 reserved1[3]; u32 num_chans;
};
struct acpm_chan_shmem {
 u32 id; u32 reserved[3]; u32 rx_rear; u32 rx_front; u32 rx_base;
 u32 reserved1[3]; u32 tx_rear; u32 tx_front; u32 tx_base;
 u32 qlen; u32 mlen; u32 reserved2[2]; u32 poll_completion;
};
"""
LAB = """
sizeof(struct a7_legacy_ipc_channel) == 72
sizeof(struct a7_modern_ipc_channel) == 72
ch.q_elem_size
poll_completion
a7_acpm_validate_pmic_channel
"""


class SramAbiTests(unittest.TestCase):
    def test_mock_matches_pinned_wire_abi(self):
        self.assertEqual(audit(OLD, NEW, LAB), [])

    def test_reject_changed_old_queue_fields(self):
        self.assertTrue(audit(OLD.replace("u32 tx_base;", "u32 changed_base;"), NEW, LAB))

    def test_reject_missing_modern_array_field(self):
        self.assertTrue(audit(OLD, NEW.replace("u32 num_chans;", "u32 other;"), LAB))

    def test_reject_removed_static_guards(self):
        self.assertTrue(audit(OLD, NEW, LAB.replace("== 72", "== 68")))

    def test_reject_real_mailbox_access(self):
        self.assertTrue(audit(OLD, NEW, LAB + "\nmbox_send_message(chan, msg);"))

    def test_parse_nested_struct_property(self):
        self.assertEqual(fields(OLD, "ipc_channel"), ["id", "field", "owner", "type", "ch", "ap_poll"])


if __name__ == "__main__":
    unittest.main()
