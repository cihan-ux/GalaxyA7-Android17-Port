/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "exynos7885-acpm-descriptor-snapshot-lab.h"

static unsigned char a[A7_ACPM_SRAM_BYTES], b[A7_ACPM_SRAM_BYTES];

static void put(unsigned char *data, unsigned int offset, unsigned int value)
{
	data[offset] = (unsigned char)value;
	data[offset + 1] = (unsigned char)(value >> 8);
	data[offset + 2] = (unsigned char)(value >> 16);
	data[offset + 3] = (unsigned char)(value >> 24);
}

static void fixture(void)
{
	const unsigned int base = 0x900U + 2U * 72U;
	memset(a, 0, sizeof(a));
	put(a, A7_ACPM_INITDATA_OFFSET + 8U, 0x900U);
	put(a, A7_ACPM_INITDATA_OFFSET + 24U, 4U);
	put(a, base, 2U);               /* A7 PMIC channel ID */
	put(a, base + 12U, 1U);         /* TYPE_QUEUE */
	put(a, base + 16U, 0x100U);     /* APM RX rear */
	put(a, base + 20U, 0x104U);     /* APM RX front */
	put(a, base + 24U, 0x200U);     /* APM RX base = AP TX */
	put(a, base + 40U, 0x108U);     /* APM TX rear */
	put(a, base + 44U, 0x10cU);     /* APM TX front */
	put(a, base + 48U, 0x400U);     /* APM TX base = AP RX */
	put(a, base + 52U, 4U);        /* ring depth */
	put(a, base + 56U, 16U);       /* message length */
	put(a, base + 68U, 1U);        /* polling */
	put(a, 0x100U, 1U);
	put(a, 0x104U, 2U);
	put(a, 0x108U, 0U);
	put(a, 0x10cU, 1U);
	memcpy(b, a, sizeof(a));
}

static void rejected(struct a7_acpm_descriptor_snapshot *out)
{
	struct a7_acpm_descriptor_snapshot before = *out;
	assert(a7_acpm_snapshot_pmic_descriptor(a, b, sizeof(a), out) == -1);
	assert(memcmp(out, &before, sizeof(before)) == 0);
}

int main(void)
{
	const unsigned int base = 0x900U + 2U * 72U;
	struct a7_acpm_descriptor_snapshot out, before;
	fixture();
	memset(&out, 0x5a, sizeof(out));
	assert(a7_acpm_snapshot_pmic_descriptor(a, b, sizeof(a), &out) == 0);
	assert(out.descriptor_offset == base);
	assert(out.framework.ipc_ap_max == 4U);
	assert(out.pmic_channel.id == 2U && out.pmic_channel.type == 1U);
	assert(out.layout.ap_tx_base == 0x200U && out.layout.ap_rx_base == 0x400U);
	assert(out.layout.qlen == 4U && out.layout.mlen == 16U);
	assert(out.ap_tx_rear == 1U && out.ap_tx_front == 2U);
	assert(out.ap_rx_rear == 0U && out.ap_rx_front == 1U);
	before = out;
	assert(a7_acpm_snapshot_pmic_descriptor(a, b, sizeof(a) - 1U, &out) == -1);
	assert(a7_acpm_snapshot_pmic_descriptor(NULL, b, sizeof(a), &out) == -1);
	assert(a7_acpm_snapshot_pmic_descriptor(a, a, sizeof(a), &out) == -1);
	assert(a7_acpm_snapshot_pmic_descriptor(a, NULL, sizeof(a), &out) == -1);
	assert(a7_acpm_snapshot_pmic_descriptor(a, b, sizeof(a), NULL) == -1);
	assert(memcmp(&before, &out, sizeof(out)) == 0);

	/* Mutating just the second snapshot must not publish a torn view. */
	fixture(); put(b, A7_ACPM_INITDATA_OFFSET + 24U, 5U); rejected(&out);
	fixture(); put(b, base + 56U, 20U); rejected(&out);
	fixture(); put(b, 0x104U, 3U); rejected(&out);
	/* Invalid identical snapshots must also fail. */
	fixture(); put(a, A7_ACPM_INITDATA_OFFSET + 8U, 0x1affcU);
	memcpy(b, a, sizeof(a)); rejected(&out);
	fixture(); put(a, A7_ACPM_INITDATA_OFFSET + 24U, 2U);
	memcpy(b, a, sizeof(a)); rejected(&out);
	fixture(); put(a, base, 3U); memcpy(b, a, sizeof(a)); rejected(&out);
	fixture(); put(a, base + 12U, 2U); memcpy(b, a, sizeof(a)); rejected(&out);
	fixture(); put(a, base + 56U, 20U); memcpy(b, a, sizeof(a)); rejected(&out);
	fixture(); put(a, base + 20U, A7_ACPM_SRAM_BYTES - 2U);
	memcpy(b, a, sizeof(a)); rejected(&out);
	fixture(); put(a, 0x100U, 4U); memcpy(b, a, sizeof(a)); rejected(&out);
	fixture(); put(a, base + 52U, 1U); memcpy(b, a, sizeof(a)); rejected(&out);
	assert(memcmp(&before, &out, sizeof(out)) == 0);
	puts("PASS: A7 firmware descriptor from two ordinary-RAM snapshots; bounded, stable, read-only");
	puts("NO MMIO, IRQ, mailbox, firmware write, device probe, or flashable image");
	return 0;
}
