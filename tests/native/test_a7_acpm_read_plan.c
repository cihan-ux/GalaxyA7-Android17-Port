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
	/* Two matching responses cannot be safely attributed to one read. */
	replies[3].word[0] = request.request.word[0];
	replies[3].word[1] = (0x44U << A7_ACPM_READ_RESPONSE_VALUE_SHIFT);
	assert(a7_acpm_match_s2mpu08_read_reply(&request, replies, 4, 3, 2,
						&decision) == -1);
	assert(memcmp(&decision, &previous, sizeof(decision)) == 0);
	replies[3].word[0] = (6U << 16) | 0x14fU;
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

static void test_mock_read_lifecycle(void)
{
	struct a7_acpm_read_plan request = {0};
	struct a7_acpm_read_plan wrong;
	struct a7_acpm_read_lifecycle state = {0}, before;
	struct s2mpu08_a7_acpm_frame replies[4] = {{{0}}};

	request.channel_id = 2;
	request.sequence = 7;
	request.request.word[0] = (7U << 16) | 0x14fU;
	request.doorbell_offset = A7_ACPM_DOORBELL_INTGR0_OFFSET;
	request.doorbell_value = 0x40000U;

	/* Restarting an in-flight session must fail without altering state. */
	assert(a7_acpm_begin_read_lifecycle(&request, 0xfffffff0U, 40, &state) == 0);
	before = state;
	assert(a7_acpm_begin_read_lifecycle(&request, 0xfffffff1U, 40, &state) == -1);
	assert(memcmp(&before, &state, sizeof(state)) == 0);

	/* Not-yet-received response at t=5 is 21ms after wraparound. */
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 0, 5) == 0);
	assert(state.state == A7_ACPM_WAIT_PENDING);
	assert(state.last_observed_ms == 5U);
	before = state;
	/* A backwards clock sample is invalid and must not expire this read. */
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 0, 4) == -1);
	assert(memcmp(&before, &state, sizeof(state)) == 0);
	/* A wildly distant sample is also ambiguous: reject, do not expire. */
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 0, 0x80000005U) == -1);
	assert(memcmp(&before, &state, sizeof(state)) == 0);
	replies[0].word[0] = request.request.word[0];
	replies[0].word[1] = (0x55U << A7_ACPM_READ_RESPONSE_VALUE_SHIFT);

	/* Exact timeout boundary wins even if a matching reply is visible. */
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 1, 0x18U) == 0);
	assert(state.state == A7_ACPM_WAIT_EXPIRED);
	assert(state.response_value == 0);
	before = state;
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 1, 0x19U) ==
		A7_ACPM_WAIT_ALREADY_DONE);
	assert(memcmp(&before, &state, sizeof(state)) == 0);

	/* Never reuse sequence 7 while its late reply is unaccounted for. */
	before = state;
	assert(state.quarantined_sequence_low & (1U << 7));
	assert(a7_acpm_begin_read_lifecycle(&request, 100, 20, &state) == -1);
	assert(memcmp(&before, &state, sizeof(state)) == 0);
	/* A new non-quarantined sequence can start. */
	request.sequence = 8;
	request.request.word[0] = (8U << 16) | 0x14fU;
	replies[0].word[0] = request.request.word[0];
	assert(a7_acpm_begin_read_lifecycle(&request, 100, 20, &state) == 0);
	assert(state.quarantined_sequence_low & (1U << 7));
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 1, 105) == 0);
	assert(state.state == A7_ACPM_WAIT_SUCCESS);
	assert(state.last_observed_ms == 105U);
	assert(state.response_value == 0x55U && state.firmware_status == 0);

	/* Firmware errors must not expose data as successful PMIC reads. */
	assert(a7_acpm_begin_read_lifecycle(&request, 200, 20, &state) == 0);
	replies[0].word[1] = (3U << A7_ACPM_READ_RESPONSE_STATUS_SHIFT) |
			     (0x77U << A7_ACPM_READ_RESPONSE_VALUE_SHIFT);
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 1, 201) == 0);
	assert(state.state == A7_ACPM_WAIT_FIRMWARE_ERR);
	assert(state.firmware_status == 3 && state.response_value == 0);

	/* Stale sequence or wrong register must remain pending. */
	assert(a7_acpm_begin_read_lifecycle(&request, 300, 20, &state) == 0);
	replies[0].word[0] = (7U << 16) | 0x14fU;
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 1, 301) == 0);
	assert(state.state == A7_ACPM_WAIT_PENDING);
	replies[0].word[0] = (8U << 16) | 0x100U;
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 1, 302) == 0);
	assert(state.state == A7_ACPM_WAIT_PENDING);

	/* Wrong request identity and malformed snapshots fail closed. */
	wrong = request;
	wrong.request.word[0] ^= 1U;
	before = state;
	assert(a7_acpm_advance_read_lifecycle(
		&state, &wrong, replies, 4, 0, 1, 303) == -1);
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, NULL, 4, 0, 1, 303) == -1);
	assert(memcmp(&before, &state, sizeof(state)) == 0);
	/* Excessive elapsed time must expire instead of accepting stale data. */
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, replies, 4, 0, 1, 321) == 0);
	assert(state.state == A7_ACPM_WAIT_EXPIRED);
	assert(state.last_observed_ms == 321U);
	assert(state.quarantined_sequence_low & (1U << 8));
	assert(state.quarantined_sequence_low & (1U << 7));
	assert(a7_acpm_begin_read_lifecycle(&request, 500, 20, &state) == -1);
	assert(a7_acpm_begin_read_lifecycle(&request, 500, 0, &state) == -1);
	assert(a7_acpm_begin_read_lifecycle(&request, 500, 60001, &state) == -1);
	/* Also cover high bitmap: sequence 63 times out and cannot be reused. */
	request.sequence = 63;
	request.request.word[0] = (63U << 16) | 0x14fU;
	assert(a7_acpm_begin_read_lifecycle(&request, 700, 1, &state) == 0);
	assert(a7_acpm_advance_read_lifecycle(
		&state, &request, NULL, 0, 0, 0, 701) == 0);
	assert(state.state == A7_ACPM_WAIT_EXPIRED);
	assert(state.quarantined_sequence_high & (1U << 31));
	assert(a7_acpm_begin_read_lifecycle(&request, 800, 10, &state) == -1);
	/* Non-quarantined 32 remains usable while 7, 8 and 63 stay blocked. */
	request.sequence = 32;
	request.request.word[0] = (32U << 16) | 0x14fU;
	assert(a7_acpm_begin_read_lifecycle(&request, 800, 10, &state) == 0);
	assert(state.quarantined_sequence_low & (1U << 7));
	assert(state.quarantined_sequence_low & (1U << 8));
	assert(state.quarantined_sequence_high & (1U << 31));
	puts("PASS: low/high six-bit sequence quarantine, timeout, wrap, late reply and firmware error");
}

static void test_mock_safe_sequence_allocation(void)
{
	struct a7_acpm_read_lifecycle state = {0};
	unsigned int chosen = 0xabcdefU;

	/* Legacy counter wraps 63 -> 1 and starts at 1 after 0. */
	assert(a7_acpm_next_unquarantined_sequence(&state, 0, &chosen) == 0);
	assert(chosen == 1);
	assert(a7_acpm_next_unquarantined_sequence(&state, 63, &chosen) == 0);
	assert(chosen == 1);

	/* Distinct quarantine masks for low 1..31 and high 32..63. */
	state.quarantined_sequence_low = (1U << 7) | (1U << 8);
	assert(a7_acpm_next_unquarantined_sequence(&state, 6, &chosen) == 0);
	assert(chosen == 9);
	state.quarantined_sequence_high = 1U << 31;
	assert(a7_acpm_next_unquarantined_sequence(&state, 62, &chosen) == 0);
	assert(chosen == 1);

	/* No available sequence must not invent a successful transaction. */
	state.quarantined_sequence_low = 0xfffffffeU;
	state.quarantined_sequence_high = 0xffffffffU;
	chosen = 0xabcdefU;
	assert(a7_acpm_next_unquarantined_sequence(&state, 11, &chosen) == -1);
	assert(chosen == 0xabcdefU);
	/* One remaining high-number slot must be discovered after wrap. */
	state.quarantined_sequence_high &= ~(1U << 31);
	assert(a7_acpm_next_unquarantined_sequence(&state, 1, &chosen) == 0);
	assert(chosen == 63);

	/* No allocation while another request remains pending. */
	state.state = A7_ACPM_WAIT_PENDING;
	state.timeout_ms = 10;
	chosen = 0xabcdefU;
	assert(a7_acpm_next_unquarantined_sequence(&state, 0, &chosen) == -1);
	assert(chosen == 0xabcdefU);
	assert(a7_acpm_next_unquarantined_sequence(&state, 64, &chosen) == -1);
	assert(a7_acpm_next_unquarantined_sequence(NULL, 0, &chosen) == -1);
	assert(a7_acpm_next_unquarantined_sequence(&state, 0, NULL) == -1);
	puts("PASS: offline 1..63 ACPM sequence allocator skips quarantine and fails closed on exhaustion");
}

static void test_offline_atomic_read_begin(void)
{
	struct a7_legacy_framework_prefix fw = {0};
	struct a7_legacy_ipc_channel ch = {0};
	struct a7_acpm_read_lifecycle life = {0}, prior_life;
	struct a7_acpm_read_plan plan = {0}, prior_plan;
	unsigned int sequence = 12345U, prior_sequence;
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
	life.quarantined_sequence_low = (1U << 7) | (1U << 8);

	/* The new session picks 9 after skipped timed-out IDs 7 and 8. */
	assert(a7_acpm_prepare_begin_s2mpu08_read(
		&fw, &ch, 1, 0x4f, 6, 2, 1, 200, 30,
		&life, &plan, &sequence) == 0);
	assert(sequence == 9 && plan.sequence == 9);
	assert(plan.queue_entry_offset == 0x220);
	assert(plan.request.word[0] == ((9U << 16) | 0x14fU));
	assert(life.state == A7_ACPM_WAIT_PENDING);
	assert(life.sequence == 9 && life.start_ms == 200);
	assert(life.quarantined_sequence_low & (1U << 7));
	assert(life.quarantined_sequence_low & (1U << 8));
	prior_life = life;
	prior_plan = plan;
	prior_sequence = sequence;

	/* No overwrite while a request is outstanding. */
	assert(a7_acpm_prepare_begin_s2mpu08_read(
		&fw, &ch, 1, 0x4f, 9, 2, 1, 210, 30,
		&life, &plan, &sequence) == -1);
	assert(memcmp(&prior_life, &life, sizeof(life)) == 0);
	assert(memcmp(&prior_plan, &plan, sizeof(plan)) == 0);
	assert(sequence == prior_sequence);

	/* After expiry, the same sequence becomes quarantined; use 10. */
	assert(a7_acpm_advance_read_lifecycle(
		&life, &plan, NULL, 0, 0, 0, 230) == 0);
	assert(life.state == A7_ACPM_WAIT_EXPIRED);
	assert(life.quarantined_sequence_low & (1U << 9));

	/*
	 * While no session is pending, test real full-ring and invalid-timeout
	 * rejection, not merely rejection because an earlier read is active.
	 * None of the caller-visible outputs may change.
	 */
	prior_life = life;
	prior_plan = plan;
	prior_sequence = sequence;
	assert(a7_acpm_prepare_begin_s2mpu08_read(
		&fw, &ch, 1, 0x4f, 9, 1, 2, 305, 30,
		&life, &plan, &sequence) == -1);
	assert(a7_acpm_prepare_begin_s2mpu08_read(
		&fw, &ch, 1, 0x4f, 9, 2, 1, 305, 0,
		&life, &plan, &sequence) == -1);
	assert(memcmp(&prior_life, &life, sizeof(life)) == 0);
	assert(memcmp(&prior_plan, &plan, sizeof(plan)) == 0);
	assert(sequence == prior_sequence);

	assert(a7_acpm_prepare_begin_s2mpu08_read(
		&fw, &ch, 1, 0x4f, 9, 2, 1, 300, 30,
		&life, &plan, &sequence) == 0);
	assert(sequence == 10 && life.sequence == 10);
	assert(life.state == A7_ACPM_WAIT_PENDING);
	prior_life = life;
	prior_plan = plan;
	prior_sequence = sequence;
	assert(a7_acpm_prepare_begin_s2mpu08_read(
		&fw, &ch, 1, 0x4f, 10, 2, 1, 305, 30,
		&life, &plan, &sequence) == -1);
	assert(memcmp(&prior_life, &life, sizeof(life)) == 0);
	assert(memcmp(&prior_plan, &plan, sizeof(plan)) == 0);
	assert(sequence == prior_sequence);
	assert(a7_acpm_prepare_begin_s2mpu08_read(
		&fw, &ch, 1, 0x4f, 10, 2, 1, 305, 30,
		&life, NULL, &sequence) == -1);
	puts("PASS: synthetic PMIC read start composes sequence, bounded ring, and lifecycle atomically");
}


static void test_lifecycle_corruption_and_cross_session_clock(void)
{
	struct a7_acpm_read_plan req = {0};
	struct a7_acpm_read_lifecycle life = {0}, previous;
	unsigned int chosen = 0xaabbccddU;

	req.channel_id = A7_ACPM_PMIC_CHANNEL;
	req.sequence = 7;
	req.request.word[0] = (7U << 16) | 0x14fU;
	req.doorbell_offset = A7_ACPM_DOORBELL_INTGR0_OFFSET;
	req.doorbell_value = 0x40000U;

	/* A corrupted state enum may not be treated as a terminal session. */
	life.state = 99;
	previous = life;
	assert(a7_acpm_begin_read_lifecycle(&req, 100, 20, &life) == -1);
	assert(a7_acpm_next_unquarantined_sequence(&life, 0, &chosen) == -1);
	assert(chosen == 0xaabbccddU);
	assert(memcmp(&previous, &life, sizeof(life)) == 0);

	/* A non-empty but timeout-less struct is not fresh/zero-initialized. */
	memset(&life, 0, sizeof(life));
	life.sequence = 7;
	assert(a7_acpm_begin_read_lifecycle(&req, 100, 20, &life) == -1);

	memset(&life, 0, sizeof(life));
	assert(a7_acpm_begin_read_lifecycle(&req, 1000, 20, &life) == 0);
	/* A synthetic reply completing at time 1005. */
	{
		struct s2mpu08_a7_acpm_frame response[2] = {{{0}}};
		response[0].word[0] = req.request.word[0];
		response[0].word[1] = 0x5aU << A7_ACPM_READ_RESPONSE_VALUE_SHIFT;
		assert(a7_acpm_advance_read_lifecycle(
			&life, &req, response, 2, 0, 1, 1005) == 0);
	}
	assert(life.state == A7_ACPM_WAIT_SUCCESS);

	/* Future read identity uses seq=8. Starting before prior completion
	 * or >=2^31ms away violates the fake-clock provenance.
	 */
	req.sequence = 8;
	req.request.word[0] = (8U << 16) | 0x14fU;
	previous = life;
	assert(a7_acpm_begin_read_lifecycle(&req, 1004, 20, &life) == -1);
	assert(a7_acpm_begin_read_lifecycle(
		&req, 1005U + 0x80000000U, 20, &life) == -1);
	assert(memcmp(&previous, &life, sizeof(life)) == 0);
	assert(a7_acpm_begin_read_lifecycle(&req, 1006, 20, &life) == 0);
	assert(life.state == A7_ACPM_WAIT_PENDING);

	/* A malformed pending response must not alter state. */
	life.firmware_status = 3;
	previous = life;
	assert(a7_acpm_advance_read_lifecycle(
		&life, &req, NULL, 0, 0, 0, 1010) == -1);
	assert(memcmp(&previous, &life, sizeof(life)) == 0);

	/* A fake expired state with no quarantine is equally invalid. */
	life.state = A7_ACPM_WAIT_EXPIRED;
	life.firmware_status = 0;
	previous = life;
	assert(a7_acpm_next_unquarantined_sequence(&life, 8, &chosen) == -1);
	assert(memcmp(&previous, &life, sizeof(life)) == 0);
	puts("PASS: invalid ACPM lifecycle state and cross-session clock regressions rejected");
}

int main(void)
{
	test_lifecycle_corruption_and_cross_session_clock();
	test_offline_atomic_read_begin();
	test_mock_safe_sequence_allocation();
	test_mock_read_lifecycle();
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
