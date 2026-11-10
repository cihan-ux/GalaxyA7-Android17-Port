/* SPDX-License-Identifier: GPL-2.0-only */
#include "exynos7885-acpm-snapshot-lab.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void)
{
	unsigned char *a = calloc(1, A7_ACPM_SRAM_BYTES);
	unsigned char *b = calloc(1, A7_ACPM_SRAM_BYTES);
	struct a7_legacy_framework_prefix fw = { 0 };
	struct a7_legacy_ipc_channel ch = { 0 };
	struct a7_acpm_snapshot out, saved;
	const unsigned int base = 0x5000U;
	const unsigned int off = base + 2U * sizeof(ch);
	assert(a && b);
	fw.ipc_channels = base;
	fw.ipc_ap_max = 3;
	ch.id = 2;
	ch.type = 1;
	ch.ch.q_len = 4;
	ch.ch.q_elem_size = 16;
	ch.ch.rx_rear = 0x7000;
	ch.ch.rx_front = 0x7004;
	ch.ch.tx_rear = 0x7008;
	ch.ch.tx_front = 0x700c;
	ch.ch.rx_base = 0x8000;
	ch.ch.tx_base = 0x9000;
	memcpy(a + A7_ACPM_INITDATA_OFFSET, &fw, sizeof(fw));
	memcpy(a + off, &ch, sizeof(ch));
	memcpy(b, a, A7_ACPM_SRAM_BYTES);
	assert(a7_acpm_snapshot_pmic(a, b, A7_ACPM_SRAM_BYTES, &out) == 0);
	assert(out.descriptor_offset == off && out.channel_count == 3);
	saved = out;
	b[off + 4] ^= 1;
	assert(a7_acpm_snapshot_pmic(a, b, A7_ACPM_SRAM_BYTES, &out) == -1);
	assert(memcmp(&out, &saved, sizeof(out)) == 0);
	b[off + 4] ^= 1;
	b[A7_ACPM_INITDATA_OFFSET + 8] ^= 1;
	assert(a7_acpm_snapshot_pmic(a, b, A7_ACPM_SRAM_BYTES, &out) == -1);
	b[A7_ACPM_INITDATA_OFFSET + 8] ^= 1;
	fw.ipc_channels = A7_ACPM_SRAM_BYTES - 4;
	memcpy(a + A7_ACPM_INITDATA_OFFSET, &fw, sizeof(fw));
	memcpy(b, a, A7_ACPM_SRAM_BYTES);
	assert(a7_acpm_snapshot_pmic(a, b, A7_ACPM_SRAM_BYTES, &out) == -1);
	assert(a7_acpm_snapshot_pmic(a, b, A7_ACPM_SRAM_BYTES - 1, &out) == -1);
	assert(memcmp(&out, &saved, sizeof(out)) == 0);
	free(a); free(b);
	puts("PASS: offline ACPM descriptor snapshots and bounds");
	return 0;
}
