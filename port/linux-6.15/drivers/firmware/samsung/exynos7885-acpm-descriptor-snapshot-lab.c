// SPDX-License-Identifier: GPL-2.0-only
/* Two ordinary-RAM images; bounded, read-only A7 ACPM descriptor decoder. */
#include "exynos7885-acpm-descriptor-snapshot-lab.h"

_Static_assert(sizeof(unsigned int) == 4, "ACPM SRAM uses 32-bit words");
_Static_assert(sizeof(struct a7_legacy_ipc_channel) == 72,
	       "old channel descriptor must be 72 bytes");

/*
 * The legacy firmware uses a prefix, descriptor array, queue payloads,
 * and four separately stored queue indices. Each has its own owner.
 * A bounded-but-overlapping layout is unsafe even for offline planning:
 * require all eight occupied regions to be disjoint.
 */
struct a7_acpm_region {
	unsigned int offset;
	unsigned int bytes;
};

static int a7_regions_disjoint(const struct a7_acpm_region *regions,
			       unsigned int n, unsigned int size_bytes)
{
	unsigned int i, j;

	for (i = 0; i < n; i++) {
		if (!regions[i].bytes || regions[i].offset > size_bytes ||
		    regions[i].bytes > size_bytes - regions[i].offset)
			return 0;
		for (j = 0; j < i; j++) {
			if (regions[i].offset <
			    regions[j].offset + regions[j].bytes &&
			    regions[j].offset <
			    regions[i].offset + regions[i].bytes)
				return 0;
		}
	}
	return 1;
}

static unsigned int a7_read_le32(const unsigned char *base,
				 unsigned int offset)
{
	return (unsigned int)base[offset] |
	       ((unsigned int)base[offset + 1U] << 8) |
	       ((unsigned int)base[offset + 2U] << 16) |
	       ((unsigned int)base[offset + 3U] << 24);
}

static int a7_same_bytes(const unsigned char *a, const unsigned char *b,
			 unsigned int offset, unsigned int count)
{
	unsigned int i;

	for (i = 0; i < count; i++) {
		if (a[offset + i] != b[offset + i])
			return 0;
	}
	return 1;
}

static int a7_same_index(const unsigned char *a, const unsigned char *b,
			 unsigned int offset, unsigned int qlen,
			 unsigned int *index)
{
	unsigned int first = a7_read_le32(a, offset);
	unsigned int second = a7_read_le32(b, offset);

	if (first != second || first >= qlen)
		return 0;
	*index = first;
	return 1;
}

int a7_acpm_snapshot_pmic_descriptor(
	const unsigned char *first, const unsigned char *second,
	unsigned int size_bytes, struct a7_acpm_descriptor_snapshot *out)
{
	struct a7_acpm_descriptor_snapshot result = {0};
	struct a7_legacy_framework_prefix *fw = &result.framework;
	struct a7_legacy_ipc_channel *ch = &result.pmic_channel;
	unsigned int array_offset, count, offset, words[18], i;

	if (!first || !second || first == second || !out ||
	    size_bytes != A7_ACPM_SRAM_BYTES)
		return A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR;

	/* Both firmware prefixes must agree before using a derived offset. */
	if (!a7_same_bytes(first, second, A7_ACPM_INITDATA_OFFSET,
			   sizeof(*fw)))
		return A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR;
	fw->plugins = a7_read_le32(first, A7_ACPM_INITDATA_OFFSET);
	fw->num_plugins = a7_read_le32(first, A7_ACPM_INITDATA_OFFSET + 4U);
	fw->ipc_channels = a7_read_le32(first, A7_ACPM_INITDATA_OFFSET + 8U);
	fw->num_ipc_channels = a7_read_le32(first, A7_ACPM_INITDATA_OFFSET + 12U);
	fw->pid_framework = a7_read_le32(first, A7_ACPM_INITDATA_OFFSET + 16U);
	fw->pid_max = a7_read_le32(first, A7_ACPM_INITDATA_OFFSET + 20U);
	fw->ipc_ap_max = a7_read_le32(first, A7_ACPM_INITDATA_OFFSET + 24U);

	if (a7_acpm_validate_fw_prefix(fw, size_bytes, &array_offset,
					&count))
		return A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR;

	/* Prefix validation bounds the complete array and checks count > 2. */
	offset = array_offset + A7_ACPM_PMIC_CHANNEL * sizeof(*ch);
	if (!a7_same_bytes(first, second, offset, sizeof(*ch)))
		return A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR;
	for (i = 0; i < 18U; i++)
		words[i] = a7_read_le32(first, offset + i * 4U);

	ch->id = words[0];
	ch->field = words[1];
	ch->owner = (int)words[2];
	ch->type = words[3];
	ch->ch.rx_rear = words[4];
	ch->ch.rx_front = words[5];
	ch->ch.rx_base = words[6];
	ch->ch.rx_indr_buf = words[7];
	ch->ch.rx_indr_buf_base = words[8];
	ch->ch.rx_indr_buf_size = words[9];
	ch->ch.tx_rear = words[10];
	ch->ch.tx_front = words[11];
	ch->ch.tx_base = words[12];
	ch->ch.q_len = words[13];
	ch->ch.q_elem_size = words[14];
	ch->ch.credit = words[15];
	ch->ch.mbox_addr = words[16];
	ch->ap_poll = words[17];
	if (ch->type != A7_ACPM_LEGACY_QUEUE_TYPE ||
	    a7_acpm_validate_pmic_channel(ch, size_bytes, &result.layout) ||
	    result.layout.mlen != 16U)
		return A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR;

	/*
	 * Validate ownership geometry before trusting indirect indices. ABI
	 * bounds alone would allow an index to alias a queue, another index,
	 * the firmware prefix, or the descriptor array itself.
	 * Queue byte multiplication is safe after validate_pmic_channel().
	 */
	{
		unsigned int queue_bytes = result.layout.qlen * result.layout.mlen;
		const struct a7_acpm_region regions[] = {
			{ A7_ACPM_INITDATA_OFFSET, (unsigned int)sizeof(*fw) },
			{ array_offset, count * (unsigned int)sizeof(*ch) },
			{ ch->ch.rx_base, queue_bytes },
			{ ch->ch.tx_base, queue_bytes },
			{ ch->ch.rx_rear, 4U },
			{ ch->ch.rx_front, 4U },
			{ ch->ch.tx_rear, 4U },
			{ ch->ch.tx_front, 4U },
		};

		if (!a7_regions_disjoint(regions,
				(unsigned int)(sizeof(regions) / sizeof(regions[0])),
				size_bytes))
			return A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR;
	}

	/* The ABI validator has already checked all index words are in SRAM. */
	if (!a7_same_index(first, second, ch->ch.rx_rear, result.layout.qlen,
			   &result.ap_tx_rear) ||
	    !a7_same_index(first, second, ch->ch.rx_front, result.layout.qlen,
			   &result.ap_tx_front) ||
	    !a7_same_index(first, second, ch->ch.tx_rear, result.layout.qlen,
			   &result.ap_rx_rear) ||
	    !a7_same_index(first, second, ch->ch.tx_front, result.layout.qlen,
			   &result.ap_rx_front))
		return A7_ACPM_DESCRIPTOR_SNAPSHOT_ERROR;

	result.descriptor_offset = offset;
	*out = result;
	return 0;
}
