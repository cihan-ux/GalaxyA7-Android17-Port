/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Galaxy A7 (2018) read-only ACPM PMIC command-word research.
 * No mailbox, firmware, regulator, device binding, or physical I/O.
 * Legacy A7 transport channel 2 != zero-valued PMIC wire channel field.
 */
#ifndef S2MPU08_A7_ACPM_FRAME_LAB_H
#define S2MPU08_A7_ACPM_FRAME_LAB_H

#define A7_ACPM_TRANSPORT_CHANNEL      2U
#define A7_ACPM_PMIC_WIRE_CHANNEL      0U
#define A7_ACPM_TOP_TYPE              0U
#define A7_ACPM_PMIC_TYPE             1U
#define A7_ACPM_PMIC_READ_FUNCTION     0U
#define A7_ACPM_NUM_COMMAND_WORDS      4U
#define A7_ACPM_REG_MASK              0xffU
#define A7_ACPM_TYPE_MASK             0x0fU
#define A7_ACPM_RESPONSE_VALUE_SHIFT   8U
#define A7_ACPM_RESPONSE_STATUS_SHIFT 24U
#define A7_ACPM_INVALID              (-1)

/* All fields are unsigned int, 32-bit on Linux AArch64 and test host. */
struct s2mpu08_a7_acpm_frame {
	unsigned int word[A7_ACPM_NUM_COMMAND_WORDS];
};

/* Only constructs a READ packet; never sends it to a device. */
int s2mpu08_a7_acpm_pack_read(unsigned int transport_channel,
			      unsigned int pmic_type, unsigned int reg,
			      struct s2mpu08_a7_acpm_frame *frame);

/* Only decodes a pre-existing REPLY; never reads hardware. */
int s2mpu08_a7_acpm_unpack_read(const struct s2mpu08_a7_acpm_frame *frame,
				unsigned char *value);
#endif
