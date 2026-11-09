// SPDX-License-Identifier: GPL-2.0-only
/*
 * Compile-time cross-version Exynos7885 ACPM SRAM ABI compatibility proof.
 * This is NOT a kernel device driver and makes NO hardware accesses.
 */
#include "exynos7885-acpm-sram-abi-lab.h"

#define ABI_OFFSET(t, f) __builtin_offsetof(t, f)
#define ABI_ASSERT(c, msg) _Static_assert(c, msg)

/* We assume 32-bit little-endian u32 firmware values, not C pointers. */
ABI_ASSERT(sizeof(unsigned int) == 4, "ACPM firmware words must be 32 bits");
ABI_ASSERT(sizeof(int) == 4, "ACPM owner is a 32-bit signed field");
ABI_ASSERT(sizeof(struct a7_legacy_framework_prefix) == 28, "old prefix size");
ABI_ASSERT(sizeof(struct a7_modern_framework_prefix) == 28, "new prefix size");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_framework_prefix, ipc_channels) ==
	   ABI_OFFSET(struct a7_modern_framework_prefix, chans),
	   "firmware IPC channel array pointer offset differs");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_framework_prefix, ipc_ap_max) ==
	   ABI_OFFSET(struct a7_modern_framework_prefix, num_chans),
	   "old AP channel count must align with modern count (word 6)");

ABI_ASSERT(sizeof(struct a7_legacy_channel_info) == 52,
	   "old channel_info is 13 32-bit words");
ABI_ASSERT(sizeof(struct a7_legacy_ipc_channel) == 72,
	   "old channel descriptor must be 18 words");
ABI_ASSERT(sizeof(struct a7_modern_ipc_channel) == 72,
	   "modern channel descriptor must be 18 words");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, id) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, id), "id mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.rx_rear) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, rx_rear), "rx_rear mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.rx_front) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, rx_front), "rx_front mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.rx_base) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, rx_base), "rx_base mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.tx_rear) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, tx_rear), "tx_rear mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.tx_front) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, tx_front), "tx_front mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.tx_base) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, tx_base), "tx_base mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.q_len) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, qlen), "queue depth mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ch.q_elem_size) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, mlen), "message size mismatch");
ABI_ASSERT(ABI_OFFSET(struct a7_legacy_ipc_channel, ap_poll) ==
	   ABI_OFFSET(struct a7_modern_ipc_channel, poll_completion),
	   "poll mode offset mismatch");

/* Check that an offset/byte count fits SRAM without wraparound. */
static int a7_inside_sram(unsigned int offset, unsigned int bytes,
			  unsigned int size_bytes)
{
	return !(offset & 3U) && bytes &&
	       offset <= size_bytes && bytes <= size_bytes - offset;
}

int a7_acpm_validate_fw_prefix(const struct a7_legacy_framework_prefix *fw,
				unsigned int size_bytes,
				unsigned int *channel_array_offset,
				unsigned int *channel_count)
{
	unsigned int count, offset;

	if (!fw || !channel_array_offset || !channel_count ||
	    size_bytes != A7_ACPM_SRAM_BYTES ||
	    A7_ACPM_INITDATA_OFFSET > size_bytes - sizeof(*fw))
		return A7_ACPM_ABI_ERROR;
	count = fw->ipc_ap_max;
	offset = fw->ipc_channels;
	if (count <= A7_ACPM_PMIC_CHANNEL ||
	    count > size_bytes / sizeof(struct a7_legacy_ipc_channel) ||
	    !a7_inside_sram(offset,
			    count * sizeof(struct a7_legacy_ipc_channel),
			    size_bytes))
		return A7_ACPM_ABI_ERROR;

	*channel_array_offset = offset;
	*channel_count = count;
	return 0;
}

int a7_acpm_validate_pmic_channel(const struct a7_legacy_ipc_channel *ch,
				   unsigned int size_bytes,
				   struct a7_acpm_queue_layout *out)
{
	unsigned int count, bytes;
	if (!ch || !out || size_bytes != A7_ACPM_SRAM_BYTES ||
	    ch->id != A7_ACPM_PMIC_CHANNEL || ch->ap_poll > 1)
		return A7_ACPM_ABI_ERROR;
	count = ch->ch.q_len;
	if (count < 2 || ch->ch.q_elem_size < 16 ||
	    (ch->ch.q_elem_size & 3U) ||
	    count > size_bytes / ch->ch.q_elem_size)
		return A7_ACPM_ABI_ERROR;
	bytes = count * ch->ch.q_elem_size;
	if (!a7_inside_sram(ch->ch.rx_rear, 4, size_bytes) ||
	    !a7_inside_sram(ch->ch.rx_front, 4, size_bytes) ||
	    !a7_inside_sram(ch->ch.tx_rear, 4, size_bytes) ||
	    !a7_inside_sram(ch->ch.tx_front, 4, size_bytes) ||
	    !a7_inside_sram(ch->ch.rx_base, bytes, size_bytes) ||
	    !a7_inside_sram(ch->ch.tx_base, bytes, size_bytes))
		return A7_ACPM_ABI_ERROR;

	/* Legacy APM RX is application CPU TX; modern code uses same inversion. */
	out->ap_tx_base = ch->ch.rx_base;
	out->ap_rx_base = ch->ch.tx_base;
	out->qlen = count;
	out->mlen = ch->ch.q_elem_size;
	out->polling = ch->ap_poll;
	return 0;
}
