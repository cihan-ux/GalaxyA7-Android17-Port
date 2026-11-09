/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "exynos7885-acpm-sram-abi-lab.h"

int main(void)
{
	struct a7_legacy_framework_prefix fw = {0};
	struct a7_legacy_ipc_channel ch = {0};
	struct a7_modern_framework_prefix modern_fw;
	struct a7_modern_ipc_channel modern_ch;
	struct a7_acpm_queue_layout layout = {0};
	unsigned int off = 0, n = 0;

	fw.ipc_channels = 0x900;
	fw.ipc_ap_max = 4;
	memcpy(&modern_fw, &fw, sizeof(fw));
	assert(modern_fw.chans == 0x900);
	assert(modern_fw.num_chans == 4);
	assert(a7_acpm_validate_fw_prefix(&fw, A7_ACPM_SRAM_BYTES, &off, &n) == 0);
	assert(off == 0x900 && n == 4);
	fw.ipc_channels = 0x1aff0;
	assert(a7_acpm_validate_fw_prefix(&fw, A7_ACPM_SRAM_BYTES, &off, &n) == -1);
	fw.ipc_channels = 0x901;
	assert(a7_acpm_validate_fw_prefix(&fw, A7_ACPM_SRAM_BYTES, &off, &n) == -1);
	fw.ipc_channels = 0x900;
	fw.ipc_ap_max = 2;
	assert(a7_acpm_validate_fw_prefix(&fw, A7_ACPM_SRAM_BYTES, &off, &n) == -1);
	fw.ipc_ap_max = ~0U;
	assert(a7_acpm_validate_fw_prefix(&fw, A7_ACPM_SRAM_BYTES, &off, &n) == -1);
	fw.ipc_ap_max = 4;
	assert(a7_acpm_validate_fw_prefix(&fw, A7_ACPM_SRAM_BYTES - 4, &off, &n) == -1);

	ch.id = A7_ACPM_PMIC_CHANNEL;
	ch.ap_poll = 1;
	ch.ch.q_len = 4;
	ch.ch.q_elem_size = 16;
	ch.ch.rx_rear = 0x100;
	ch.ch.rx_front = 0x104;
	ch.ch.tx_rear = 0x108;
	ch.ch.tx_front = 0x10c;
	ch.ch.rx_base = 0x200;
	ch.ch.tx_base = 0x400;
	memcpy(&modern_ch, &ch, sizeof(ch));
	assert(modern_ch.id == 2);
	assert(modern_ch.rx_base == 0x200);
	assert(modern_ch.tx_base == 0x400);
	assert(modern_ch.qlen == 4 && modern_ch.mlen == 16);
	assert(modern_ch.poll_completion == 1);
	assert(a7_acpm_validate_pmic_channel(&ch, A7_ACPM_SRAM_BYTES, &layout) == 0);
	assert(layout.ap_tx_base == 0x200 && layout.ap_rx_base == 0x400);
	assert(layout.qlen == 4 && layout.mlen == 16 && layout.polling == 1);

	ch.ch.rx_base = 0x1aff0;
	assert(a7_acpm_validate_pmic_channel(&ch, A7_ACPM_SRAM_BYTES, &layout) == -1);
	ch.ch.rx_base = 0x200;
	ch.ch.q_len = ~0U;
	assert(a7_acpm_validate_pmic_channel(&ch, A7_ACPM_SRAM_BYTES, &layout) == -1);
	ch.ch.q_len = 4;
	ch.ch.q_elem_size = 15;
	assert(a7_acpm_validate_pmic_channel(&ch, A7_ACPM_SRAM_BYTES, &layout) == -1);
	ch.ch.q_elem_size = 16;
	ch.id = 1;
	assert(a7_acpm_validate_pmic_channel(&ch, A7_ACPM_SRAM_BYTES, &layout) == -1);
	ch.id = 2;
	ch.ap_poll = 2;
	assert(a7_acpm_validate_pmic_channel(&ch, A7_ACPM_SRAM_BYTES, &layout) == -1);
	assert(a7_acpm_validate_pmic_channel(NULL, A7_ACPM_SRAM_BYTES, &layout) == -1);
	assert(a7_acpm_validate_pmic_channel(&ch, A7_ACPM_SRAM_BYTES, NULL) == -1);
	puts("PASS: A7/6.15 ACPM prefix and 72-byte channel layout compatible; offsets bounded");
	return 0;
}
