/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "exynos7885-acpm-read-plan-lab.h"


static void check_mock_reply_matching(void)
{
	struct a7_acpm_read_plan request = {0};
	struct a7_acpm_reply_decision decision, previous;
	struct s2mpu08_a7_acpm_frame replies[4] = {{{0}}};
	int rc;

	request.channel_id = 2;
	request.sequence = 7;
	request.request.word[0] = (7U << 16) | 0x14fU;
	/* Queue rear=3, front=2, wrap: indices 3, 0, 1. */
	replies[3].word[0] = (6U << 16) | 0x14fU; /* stale sequence */
	replies[0].word[0] = (7U << 16) | 0x100U; /* wrong PMIC register */
	replies[1].word[0] = request.request.word[0];
	replies[1].word[1] = (0x5aU << A7_ACPM_READ_RESPONSE_VALUE_SHIFT);
	rc = a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 3, 2,
					      &decision);
	assert(rc == 0);
	assert(decision.matched_index == 1);
	assert(decision.next_rear == 0);
	assert(decision.requires_rear_swap == 1);
	assert(decision.would_clear_irq_if_empty == 0);
	assert(decision.firmware_status == 0 && decision.response_value == 0x5aU);
	previous = decision;
	/* Error status must not expose the byte as a valid PMIC result. */
	replies[1].word[1] = (2U << A7_ACPM_READ_RESPONSE_STATUS_SHIFT) |
			     (0xefU << A7_ACPM_READ_RESPONSE_VALUE_SHIFT);
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 3, 2,
						&decision) == 0);
	assert(decision.firmware_status == 2);
	assert(decision.response_value == 0);
	previous = decision;
	/* Ignore mismatch and never alter caller's output when no match. */
	replies[1].word[0] = (8U << 16) | 0x14fU;
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 3, 2,
						&decision) == A7_ACPM_REPLY_NOT_FOUND);
	assert(memcmp(&decision, &previous, sizeof(decision)) == 0);
	/* A match at rear is the only entry and would clear an IRQ (not do so). */
	replies[3].word[0] = request.request.word[0];
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 3, 0,
						&decision) == 0);
	assert(decision.matched_index == 3 && decision.next_rear == 0);
	assert(decision.requires_rear_swap == 0);
	assert(decision.would_clear_irq_if_empty == 1);
	previous = decision;
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 0, 0,
						&decision) == A7_ACPM_REPLY_NOT_FOUND);
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 4, 0,
						&decision) == -1);
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 0, 4,
						&decision) == -1);
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 0, 0, 0,
						&decision) == -1);
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 0, 0,
						NULL) == -1);
	assert(a7_acpm_match_s2mpu08_read_reply(NULL, replies, 4, 0, 0,
						&decision) == -1);
	assert(memcmp(&decision, &previous, sizeof(decision)) == 0);
	puts("PASS: simulated ACPM read replies match sequence/type/register; wrong, stale and error responses guarded");
}

int main(void)
{
	check_mock_reply_matching();
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
