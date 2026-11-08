/* SPDX-License-Identifier: GPL-2.0-or-later */
/*
 * Samsung A7 (2018) S2MPU08 LDO2/LDO35 voltage math ONLY.
 * Standalone host-testable, no register IO, no regulator registration.
 * Derived from pinned A7 source; not validated against live hardware.
 */
#ifndef S2MPU08_A7_VOLTAGE_LAB_H
#define S2MPU08_A7_VOLTAGE_LAB_H

/* Human LDO channel numbers are NOT Samsung's sparse legacy enum IDs. */
#define S2MPU08_A7_LDO2_CHANNEL          2U
#define S2MPU08_A7_LDO35_CHANNEL         35U
#define S2MPU08_A7_LDO36_CHANNEL         36U
/* Legacy enum skips inactive LDO15..LDO32 in this historical kernel. */
#define S2MPU08_A7_LDO2_LEGACY_ENUM_ID   1U
#define S2MPU08_A7_LDO35_LEGACY_ENUM_ID  16U
#define S2MPU08_A7_LDO2_VSEL_REG       0x2dU
#define S2MPU08_A7_LDO35_VSEL_REG      0x4fU
#define S2MPU08_A7_VSEL_MASK           0x3fU
#define S2MPU08_A7_ENABLE_MASK         0xc0U
#define S2MPU08_A7_MIN_UV              1800000U
#define S2MPU08_A7_STEP_UV             25000U
#define S2MPU08_A7_LDO2_BOARD_MAX_UV   3375000U
#define S2MPU08_A7_LDO35_BOARD_MAX_UV  3000000U
#define S2MPU08_A7_INVALID            (-1)

/* Deliberately restrict conversion to two A7 source-traced rails. */
static inline unsigned int s2mpu08_a7_board_max_uv(unsigned int rail)
{
	switch (rail) {
	case S2MPU08_A7_LDO2_CHANNEL:
		return S2MPU08_A7_LDO2_BOARD_MAX_UV;
	case S2MPU08_A7_LDO35_CHANNEL:
		return S2MPU08_A7_LDO35_BOARD_MAX_UV;
	default:
		return 0;
	}
}

static inline int s2mpu08_a7_voltage_to_sel(unsigned int rail,
					     unsigned int voltage_uv)
{
	unsigned int maximum = s2mpu08_a7_board_max_uv(rail);
	unsigned int delta;

	if (!maximum || voltage_uv < S2MPU08_A7_MIN_UV ||
	    voltage_uv > maximum)
		return S2MPU08_A7_INVALID;
	delta = voltage_uv - S2MPU08_A7_MIN_UV;
	if (delta % S2MPU08_A7_STEP_UV ||
	    delta / S2MPU08_A7_STEP_UV > S2MPU08_A7_VSEL_MASK)
		return S2MPU08_A7_INVALID;
	return (int)(delta / S2MPU08_A7_STEP_UV);
}

static inline int s2mpu08_a7_sel_to_voltage(unsigned int rail,
					     unsigned int selector)
{
	unsigned int value;

	if (!s2mpu08_a7_board_max_uv(rail) ||
	    selector > S2MPU08_A7_VSEL_MASK)
		return S2MPU08_A7_INVALID;
	value = S2MPU08_A7_MIN_UV + selector * S2MPU08_A7_STEP_UV;
	if (value > s2mpu08_a7_board_max_uv(rail))
		return S2MPU08_A7_INVALID;
	return (int)value;
}

/*
 * Historical rev0 LDO35/LDO36 handling is coupled and MUST be implemented
 * with a real, proven PMIC transport and atomic read/modify/write handling.
 * This predicate is only a fail-closed integration guard, NOT the workaround.
 */
static inline int s2mpu08_a7_needs_rev0_ldo_guard(unsigned int pmic_rev,
						    unsigned int rail)
{
	return pmic_rev == 0 &&
	       (rail == S2MPU08_A7_LDO35_CHANNEL || rail == S2MPU08_A7_LDO36_CHANNEL);
}
#endif
