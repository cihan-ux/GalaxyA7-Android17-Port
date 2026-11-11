// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * Initial Linux 6.15 source port: voltage-only S2MPU08 regulator metadata.
 *
 * NO platform driver, NO PMIC bind, NO ACPM writes, NO voltage-changing ops.
 * This file is compiled explicitly by research CI and is NEVER auto-enabled.
 * SM-A750F S2MPU08 / LDO35-rev0 implementation remains BLOCKED.
 */
#include <linux/regulator/driver.h>
#include "s2mpu08-a7-voltage-lab.h"

/* The only implemented operations calculate voltages without I/O. */
static const struct regulator_ops s2mpu08_a7_lab_ops = {
	.list_voltage = regulator_list_voltage_linear,
	.map_voltage = regulator_map_voltage_linear,
};

/*
 * Source-proven selector metadata for LDO2/vqmmc and LDO35/vmmc.
 * The LDO2 descriptor exposes the 64 chip selectors; LDO35 is reduced to
 * 49 values to enforce the specific SM-A750F 3.0 V board maximum.
 * The same constraints are enforced by the pure header helpers;
 * do not register these descriptors before binding is designed and safe.
 */
static const struct regulator_desc s2mpu08_a7_lab_descs[] = {
	{
		.name = "S2MPU08_LDO2_RESEARCH",
		.id = S2MPU08_A7_LDO2_LEGACY_ENUM_ID,
		.ops = &s2mpu08_a7_lab_ops,
		.type = REGULATOR_VOLTAGE,
		.min_uV = S2MPU08_A7_MIN_UV,
		.uV_step = S2MPU08_A7_STEP_UV,
		.n_voltages = S2MPU08_A7_VSEL_MASK + 1U,
		.vsel_reg = S2MPU08_A7_LDO2_VSEL_REG,
		.vsel_mask = S2MPU08_A7_VSEL_MASK,
	},
	{
		.name = "S2MPU08_LDO35_RESEARCH",
		.id = S2MPU08_A7_LDO35_LEGACY_ENUM_ID,
		.ops = &s2mpu08_a7_lab_ops,
		.type = REGULATOR_VOLTAGE,
		.min_uV = S2MPU08_A7_MIN_UV,
		.uV_step = S2MPU08_A7_STEP_UV,
		/* Limit even generic regulator voltage mapping to the A7 board. */
		.n_voltages = (S2MPU08_A7_LDO35_BOARD_MAX_UV -
			       S2MPU08_A7_MIN_UV) / S2MPU08_A7_STEP_UV + 1U,
		.vsel_reg = S2MPU08_A7_LDO35_VSEL_REG,
		.vsel_mask = S2MPU08_A7_VSEL_MASK,
	},
};

/*
 * A lookup-only research entrypoint. No consumer calls this yet.
 * In particular there is no regulator_register() or module_init().
 */
const struct regulator_desc *s2mpu08_a7_lab_get_desc(unsigned int rail)
{
	if (rail == S2MPU08_A7_LDO2_CHANNEL)
		return &s2mpu08_a7_lab_descs[0];
	if (rail == S2MPU08_A7_LDO35_CHANNEL)
		return &s2mpu08_a7_lab_descs[1];
	return NULL;
}
