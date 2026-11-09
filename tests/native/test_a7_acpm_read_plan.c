/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "exynos7885-acpm-read-plan-lab.h"

int main(void)
{
	struct a7_legacy_framework_prefix fw = {0};
	struct a7_legacy_ipc_channel ch = {0};
	struct a7_acpm_read_plan plan, previous;
	unsigned int seq;

	fw.ipc_channels = 0x900;
	fw.ipc_ap_max = 4;
	ch.id = 2;
	ch.type = A7_ACPM_QUEUE_TYPE;
	ch.ap_poll = 1;
	ch.ch.q_len = 4;
	ch.ch.q_elem_size = 16;
	ch.ch.rx_rear = 0x100;
	ch.ch.rx_front = 0x104;
	ch.ch.tx_rear = 0x108;
	ch.ch.tx_front = 0x10c;
	ch.ch.rx_base = 0x200;
	ch.ch.tx_base = 0x400;

	for (seq = 1; seq <= 63; seq++) {
		assert(a7_acpm_prepare_s2mpu08_read(
			       &fw, &ch, 2, 1, 0x4f, seq, 2, 1, &plan) == 0);
		assert(plan.queue_entry_offset == 0x220U);
		assert(plan.next_front == 3);
		assert(plan.channel_id == 2);
		assert(plan.sequence == seq);
		assert(plan.doorbell_offset == 0x08);
		assert(plan.doorbell_value == 0x40000U);
		assert(plan.request.word[0] ==
		       (seq << 16) + 0x14fU);
		assert(plan.request.word[1] == 0U);
	}
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0x00, 1, 3, 1, &plan) == 0);
	assert(plan.queue_entry_offset == 0x230U);
	assert(plan.next_front == 0U);
	assert(plan.request.word[0] == 0x10000U);

	previous = plan;
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 0, 2, 1, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 64, 2, 1, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 1, 0, 0, 1, 2, 1, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 4, 0, 1, 2, 1, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 256, 1, 2, 1, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 1, 1, 2, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 1, 4, 0, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 1, 0, 4, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       NULL, &ch, 2, 0, 0, 1, 0, 0, &plan) == -1);
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 1, 0, 0, NULL) == -1);
	ch.ch.q_elem_size = 20;
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 1, 0, 0, &plan) == -1);
	ch.ch.q_elem_size = 16;
	ch.type = A7_ACPM_BUFFER_TYPE;
	assert(a7_acpm_prepare_s2mpu08_read(
		       &fw, &ch, 2, 0, 0, 1, 0, 0, &plan) == -1);
	ch.type = A7_ACPM_QUEUE_TYPE;
	assert(memcmp(&previous, &plan, sizeof(plan)) == 0);
	puts("PASS: 63 read sequence frames, ring wrap, full queue and invalid offsets in ordinary RAM");
	puts("No memory-mapped IO, firmware, real mailbox send, voltage control or bootability.");
	return 0;
}
