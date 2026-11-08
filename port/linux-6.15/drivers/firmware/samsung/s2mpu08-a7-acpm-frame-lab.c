// SPDX-License-Identifier: GPL-2.0-only
/*
 * Source-backed, pure read-packet encoder for SM-A750F S2MPU08.
 * NOT an ACPM backend. No physical read, write, update, or driver probe.
 *
 * Pinned old Samsung exynos_acpm_read_reg(): word0=(type<<8)|reg,
 * word1=FUNC_READ(0); legacy A7 gets IPC channel 2 from DTS.
 * Modern GS101 ACPM shares these low command fields but its controller
 * requires distinct SoC-compatible and SRAM/channel support.
 */
#include "s2mpu08-a7-acpm-frame-lab.h"

/* Refuse builds where the command words have the wrong width. */
typedef char a7_acpm_word_must_be_32_bits[(sizeof(unsigned int) == 4) ? 1 : -1];

int s2mpu08_a7_acpm_pack_read(unsigned int transport_channel,
			      unsigned int pmic_type, unsigned int reg,
			      struct s2mpu08_a7_acpm_frame *frame)
{
	if (!frame || transport_channel != A7_ACPM_TRANSPORT_CHANNEL ||
	    (pmic_type != A7_ACPM_TOP_TYPE &&
	     pmic_type != A7_ACPM_PMIC_TYPE) ||
	    reg > A7_ACPM_REG_MASK)
		return A7_ACPM_INVALID;

	frame->word[0] = (A7_ACPM_PMIC_WIRE_CHANNEL << 12) |
			 ((pmic_type & A7_ACPM_TYPE_MASK) << 8) | reg;
	frame->word[1] = A7_ACPM_PMIC_READ_FUNCTION;
	frame->word[2] = 0;
	frame->word[3] = 0;
	return 0;
}

int s2mpu08_a7_acpm_unpack_read(const struct s2mpu08_a7_acpm_frame *frame,
				unsigned char *value)
{
	unsigned int result;
	if (!frame || !value)
		return A7_ACPM_INVALID;

	result = (frame->word[1] >> A7_ACPM_RESPONSE_STATUS_SHIFT) &
		 A7_ACPM_REG_MASK;
	if (result)
		return -(int)result;

	*value = (unsigned char)
		((frame->word[1] >> A7_ACPM_RESPONSE_VALUE_SHIFT) &
		 A7_ACPM_REG_MASK);
	return 0;
}
