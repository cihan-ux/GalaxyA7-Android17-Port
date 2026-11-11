// SPDX-License-Identifier: GPL-2.0-only
/*
 * Validate two immutable, caller-supplied copies of a firmware SRAM window.
 * This does not read live MMIO and cannot prove atomicity of a live snapshot.
 */
#include "exynos7885-acpm-snapshot-lab.h"
#include <string.h>

#define A7_CHANNEL_TYPE_QUEUE 1U

static int copy_region(void *dst, const unsigned char *src,
		       unsigned int size, unsigned int off, unsigned int len)
{
	if (off > size || len > size - off)
		return -1;
	memcpy(dst, src + off, len);
	return 0;
}

int a7_acpm_snapshot_pmic(const unsigned char *first,
			  const unsigned char *second,
			  unsigned int size_bytes,
			  struct a7_acpm_snapshot *out)
{
	struct a7_acpm_snapshot tmp = { 0 };
	struct a7_legacy_framework_prefix fw_second;
	struct a7_legacy_ipc_channel ch_second;
	unsigned int array_offset, count, offset;

	if (!first || !second || !out || size_bytes != A7_ACPM_SRAM_BYTES)
		return -1;
	if (copy_region(&tmp.framework, first, size_bytes,
			A7_ACPM_INITDATA_OFFSET, sizeof(tmp.framework)) ||
	    copy_region(&fw_second, second, size_bytes,
			A7_ACPM_INITDATA_OFFSET, sizeof(fw_second)) ||
	    memcmp(&tmp.framework, &fw_second, sizeof(fw_second)))
		return -1;
	if (a7_acpm_validate_fw_prefix(&tmp.framework, size_bytes,
				      &array_offset, &count))
		return -1;
	/* Validate multiplication and addition before touching the buffer. */
	if (A7_ACPM_PMIC_CHANNEL >
	    (size_bytes - array_offset) / sizeof(tmp.channel))
		return -1;
	offset = array_offset + A7_ACPM_PMIC_CHANNEL * sizeof(tmp.channel);
	if (copy_region(&tmp.channel, first, size_bytes,
			offset, sizeof(tmp.channel)) ||
	    copy_region(&ch_second, second, size_bytes,
			offset, sizeof(ch_second)) ||
	    memcmp(&tmp.channel, &ch_second, sizeof(ch_second)))
		return -1;
	if (tmp.channel.type != A7_CHANNEL_TYPE_QUEUE ||
	    a7_acpm_validate_pmic_channel(&tmp.channel, size_bytes, &tmp.layout))
		return -1;
	tmp.descriptor_offset = offset;
	tmp.channel_count = count;
	*out = tmp;
	return 0;
}
