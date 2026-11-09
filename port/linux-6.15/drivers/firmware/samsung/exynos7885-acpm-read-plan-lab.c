// SPDX-License-Identifier: GPL-2.0-only
/*
 * Offline read-only S2MPU08 request planner for pinned Samsung Exynos7885.
 * No MMIO, mailbox API, raw memory pointers, firmware calls or device binding.
 * Real IPC concurrency/timing/ownership and PMIC power control unimplemented.
 */
#include "exynos7885-acpm-read-plan-lab.h"

_Static_assert(sizeof(unsigned int) == 4, "ACPM commands are 32-bit");
_Static_assert(sizeof(struct s2mpu08_a7_acpm_frame) == 16,
	       "PMIC read command uses four 32-bit words");

/*
 * The pinned historical ACPM IPC code puts 1..63 in bits 21:16, then
 * advances the firmware AP TX front and sends (BIT(channel)<<16) to
 * INTGR0=0x08. This function only computes those values in ordinary RAM.
 */
int a7_acpm_prepare_s2mpu08_read(
	const struct a7_legacy_framework_prefix *framework,
	const struct a7_legacy_ipc_channel *channel,
	unsigned int transport_channel,
	unsigned int pmic_type, unsigned int reg, unsigned int seq,
	unsigned int front, unsigned int rear,
	struct a7_acpm_read_plan *out)
{
	struct a7_acpm_queue_layout layout;
	struct s2mpu08_a7_acpm_frame frame;
	struct a7_acpm_read_plan plan;
	unsigned int count, array_offset, next_front, slot_offset;

	if (!framework || !channel || !out ||
	    transport_channel != A7_ACPM_PMIC_CHANNEL ||
	    channel->type != A7_ACPM_QUEUE_TYPE ||
	    seq < A7_ACPM_READ_SEQUENCE_MIN ||
	    seq > A7_ACPM_READ_SEQUENCE_MAX ||
	    a7_acpm_validate_fw_prefix(framework, A7_ACPM_SRAM_BYTES,
					 &array_offset, &count) != 0 ||
	    a7_acpm_validate_pmic_channel(channel, A7_ACPM_SRAM_BYTES,
					   &layout) != 0 ||
	    layout.mlen != sizeof(frame) || front >= layout.qlen ||
	    rear >= layout.qlen)
		return A7_ACPM_READ_PLAN_ERROR;

	/* A nonempty queue must not be overwritten when front+1 == rear. */
	next_front = (front + 1U) % layout.qlen;
	if (next_front == rear)
		return A7_ACPM_READ_PLAN_ERROR;

	if (s2mpu08_a7_acpm_pack_read(transport_channel, pmic_type, reg,
				     &frame) != 0 ||
	    frame.word[0] & (63U << A7_ACPM_READ_SEQUENCE_SHIFT))
		return A7_ACPM_READ_PLAN_ERROR;

	/* The validated queue layout proves all qlen*mlen bytes are in SRAM. */
	slot_offset = layout.ap_tx_base + front * layout.mlen;
	if (slot_offset > A7_ACPM_SRAM_BYTES - sizeof(frame))
		return A7_ACPM_READ_PLAN_ERROR;

	frame.word[0] |= seq << A7_ACPM_READ_SEQUENCE_SHIFT;
	plan.queue_entry_offset = slot_offset;
	plan.next_front = next_front;
	plan.channel_id = transport_channel;
	plan.sequence = seq;
	plan.doorbell_offset = A7_ACPM_DOORBELL_INTGR0_OFFSET;
	plan.doorbell_value = (1U << channel->id) << 16;
	plan.request = frame;
	*out = plan; /* Failure has no partial caller-visible writes. */
	return 0;
}

/*
 * Source-derived simulation of legacy check_response(): compare the six-bit
 * request sequence, then plan its ring dequeue. We additionally require
 * type/register parity to fail closed against stale or unrelated frames.
 * Do not implement firmware IRQ acknowledgement or queue mutation here.
 */
int a7_acpm_match_s2mpu08_read_reply(
	const struct a7_acpm_read_plan *request,
	const struct s2mpu08_a7_acpm_frame *ring,
	unsigned int ring_count, unsigned int rear, unsigned int front,
	struct a7_acpm_reply_decision *out)
{
	struct a7_acpm_reply_decision decision;
	unsigned int position, scanned, word, status;
	const unsigned int seq_mask = 0x3fU << A7_ACPM_READ_SEQUENCE_SHIFT;

	if (!request || !ring || !out || ring_count < 2 ||
	    ring_count > A7_ACPM_SRAM_BYTES / sizeof(*ring) ||
	    rear >= ring_count || front >= ring_count ||
	    request->channel_id != A7_ACPM_PMIC_CHANNEL ||
	    request->sequence < A7_ACPM_READ_SEQUENCE_MIN ||
	    request->sequence > A7_ACPM_READ_SEQUENCE_MAX ||
	    request->request.word[0] !=
		((request->request.word[0] & ~seq_mask) |
		 (request->sequence << A7_ACPM_READ_SEQUENCE_SHIFT)))
		return A7_ACPM_READ_PLAN_ERROR;

	position = rear;
	for (scanned = 0; position != front && scanned < ring_count; scanned++) {
		word = ring[position].word[0];
		if (((word & seq_mask) >> A7_ACPM_READ_SEQUENCE_SHIFT) ==
		    request->sequence &&
		    (word & 0x0fffU) == (request->request.word[0] & 0x0fffU)) {
			status = (ring[position].word[1] >>
				  A7_ACPM_READ_RESPONSE_STATUS_SHIFT) &
				 A7_ACPM_READ_RESPONSE_BYTE_MASK;
			decision.matched_index = position;
			decision.next_rear = (rear + 1U) % ring_count;
			decision.requires_rear_swap = position != rear;
			decision.would_clear_irq_if_empty =
				decision.next_rear == front;
			decision.firmware_status = status;
			/* An error reply does not supply a trusted PMIC value. */
			decision.response_value = status ? 0 :
				((ring[position].word[1] >>
				  A7_ACPM_READ_RESPONSE_VALUE_SHIFT) &
				 A7_ACPM_READ_RESPONSE_BYTE_MASK);
			*out = decision;
			return 0;
		}
		position = (position + 1U) % ring_count;
	}
	/* Missing matching response, including an empty synthetic queue. */
	return A7_ACPM_REPLY_NOT_FOUND;
}

/*
 * Pure-memory lifecycle model for request/reply and a synthetic monotonic
 * unsigned 32-bit millisecond clock. No actual firmware timing is asserted.
 */
int a7_acpm_begin_read_lifecycle(
	const struct a7_acpm_read_plan *request,
	unsigned int start_ms, unsigned int timeout_ms,
	struct a7_acpm_read_lifecycle *lifecycle)
{
	struct a7_acpm_read_lifecycle next;
	unsigned int seq_mask = 0x3fU << A7_ACPM_READ_SEQUENCE_SHIFT;

	if (!request || !lifecycle || !timeout_ms ||
	    timeout_ms > A7_ACPM_WAIT_TIMEOUT_MAX_MS ||
	    request->channel_id != A7_ACPM_PMIC_CHANNEL ||
	    request->sequence < A7_ACPM_READ_SEQUENCE_MIN ||
	    request->sequence > A7_ACPM_READ_SEQUENCE_MAX ||
	    request->doorbell_offset != A7_ACPM_DOORBELL_INTGR0_OFFSET ||
	    request->doorbell_value != (1U << A7_ACPM_PMIC_CHANNEL) << 16 ||
	    ((request->request.word[0] & seq_mask) >>
	     A7_ACPM_READ_SEQUENCE_SHIFT) != request->sequence ||
	    (lifecycle->state == A7_ACPM_WAIT_PENDING &&
	     lifecycle->timeout_ms) ||
	    (request->sequence < 32U ?
	     (lifecycle->quarantined_sequence_low &
	      (1U << request->sequence)) :
	     (lifecycle->quarantined_sequence_high &
	      (1U << (request->sequence - 32U)))))
		return A7_ACPM_READ_PLAN_ERROR;

	next.state = A7_ACPM_WAIT_PENDING;
	next.sequence = request->sequence;
	next.command_word0 = request->request.word[0];
	next.start_ms = start_ms;
	next.last_observed_ms = start_ms;
	next.timeout_ms = timeout_ms;
	next.firmware_status = 0;
	next.response_value = 0;
	next.quarantined_sequence_low = lifecycle->quarantined_sequence_low;
	next.quarantined_sequence_high = lifecycle->quarantined_sequence_high;
	*lifecycle = next;
	return 0;
}

int a7_acpm_advance_read_lifecycle(
	struct a7_acpm_read_lifecycle *lifecycle,
	const struct a7_acpm_read_plan *request,
	const struct s2mpu08_a7_acpm_frame *reply_ring,
	unsigned int ring_count, unsigned int rear, unsigned int front,
	unsigned int observed_ms)
{
	struct a7_acpm_reply_decision matched;
	unsigned int elapsed, since_last;
	int result;

	if (!lifecycle || !request || !lifecycle->timeout_ms ||
	    lifecycle->timeout_ms > A7_ACPM_WAIT_TIMEOUT_MAX_MS ||
	    lifecycle->sequence != request->sequence ||
	    lifecycle->command_word0 != request->request.word[0] ||
	    request->channel_id != A7_ACPM_PMIC_CHANNEL)
		return A7_ACPM_READ_PLAN_ERROR;

	if (lifecycle->state != A7_ACPM_WAIT_PENDING)
		return A7_ACPM_WAIT_ALREADY_DONE;

	/*
	 * A backwards sample (or an observation > 2^31ms ahead) is
	 * indistinguishable from wraparound under a naive u32 subtract.
	 * Do not falsely expire the request or trust a reply on that sample.
	 * Both total age and consecutive time increments must remain bounded.
	 */
	since_last = observed_ms - lifecycle->last_observed_ms;
	elapsed = observed_ms - lifecycle->start_ms;
	if (since_last >= 0x80000000U || elapsed >= 0x80000000U)
		return A7_ACPM_READ_PLAN_ERROR;

	if (elapsed >= lifecycle->timeout_ms) {
		lifecycle->last_observed_ms = observed_ms;
		lifecycle->state = A7_ACPM_WAIT_EXPIRED;
		lifecycle->firmware_status = 0;
		lifecycle->response_value = 0;
		/*
		 * A timed-out firmware reply may still arrive. Block this
		 * six-bit sequence instead of aliasing a later PMIC read.
		 */
		if (lifecycle->sequence < 32U)
			lifecycle->quarantined_sequence_low |=
				1U << lifecycle->sequence;
		else
			lifecycle->quarantined_sequence_high |=
				1U << (lifecycle->sequence - 32U);
		return 0;
	}

	result = a7_acpm_match_s2mpu08_read_reply(
		request, reply_ring, ring_count, rear, front, &matched);
	if (result == A7_ACPM_REPLY_NOT_FOUND) {
		lifecycle->last_observed_ms = observed_ms;
		return 0;
	}
	if (result != 0)
		return A7_ACPM_READ_PLAN_ERROR;

	lifecycle->last_observed_ms = observed_ms;
	lifecycle->firmware_status = matched.firmware_status;
	lifecycle->response_value = matched.firmware_status ?
		0 : matched.response_value;
	lifecycle->state = matched.firmware_status ?
		A7_ACPM_WAIT_FIRMWARE_ERR : A7_ACPM_WAIT_SUCCESS;
	return 0;
}

/*
 * 6-bit sequence allocator for the offline model. Since the real firmware
 * increments a 1..63 counter, this models wraparound but refuses any number
 * that can still alias a timed-out response. Eventually all 63 IDs might
 * be unavailable; in that case fail closed without modifying *out.
 */
int a7_acpm_next_unquarantined_sequence(
	const struct a7_acpm_read_lifecycle *lifecycle,
	unsigned int previous_sequence, unsigned int *next_sequence)
{
	unsigned int candidate, checked, mask;

	if (!lifecycle || !next_sequence ||
	    previous_sequence > A7_ACPM_READ_SEQUENCE_MAX ||
	    (lifecycle->state == A7_ACPM_WAIT_PENDING &&
	     lifecycle->timeout_ms))
		return A7_ACPM_READ_PLAN_ERROR;

	candidate = previous_sequence;
	for (checked = 0; checked < A7_ACPM_READ_SEQUENCE_MAX; checked++) {
		candidate++;
		if (candidate > A7_ACPM_READ_SEQUENCE_MAX)
			candidate = A7_ACPM_READ_SEQUENCE_MIN;
		mask = candidate < 32U ?
			(lifecycle->quarantined_sequence_low &
			 (1U << candidate)) :
			(lifecycle->quarantined_sequence_high &
			 (1U << (candidate - 32U)));
		if (!mask) {
			*next_sequence = candidate;
			return 0;
		}
	}

	return A7_ACPM_READ_PLAN_ERROR;
}
