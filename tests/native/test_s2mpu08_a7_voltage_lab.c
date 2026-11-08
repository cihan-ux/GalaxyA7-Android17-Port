/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Host-executable C logic test of actual kernel research voltage helpers. */
#include <assert.h>
#include <stdio.h>
#include "s2mpu08-a7-voltage-lab.h"

int main(void)
{
	unsigned int index;
	for (index = 0; index <= 48; index++) {
		int uv = s2mpu08_a7_sel_to_voltage(S2MPU08_A7_LDO35_ID, index);
		assert(uv >= 1800000 && uv <= 3000000);
		assert(s2mpu08_a7_voltage_to_sel(S2MPU08_A7_LDO35_ID,
						  (unsigned int)uv) == (int)index);
	}
	for (index = 0; index <= 63; index++) {
		int uv = s2mpu08_a7_sel_to_voltage(S2MPU08_A7_LDO2_ID, index);
		assert(uv >= 1800000 && uv <= 3375000);
		assert(s2mpu08_a7_voltage_to_sel(S2MPU08_A7_LDO2_ID,
						  (unsigned int)uv) == (int)index);
	}
	assert(s2mpu08_a7_voltage_to_sel(S2MPU08_A7_LDO2_ID, 1799999U) == -1);
	assert(s2mpu08_a7_voltage_to_sel(S2MPU08_A7_LDO2_ID, 1800001U) == -1);
	assert(s2mpu08_a7_voltage_to_sel(S2MPU08_A7_LDO2_ID, 3375001U) == -1);
	assert(s2mpu08_a7_voltage_to_sel(S2MPU08_A7_LDO35_ID, 3025000U) == -1);
	assert(s2mpu08_a7_sel_to_voltage(S2MPU08_A7_LDO35_ID, 49U) == -1);
	assert(s2mpu08_a7_sel_to_voltage(S2MPU08_A7_LDO2_ID, 64U) == -1);
	assert(s2mpu08_a7_voltage_to_sel(36U, 1800000U) == -1);
	assert(s2mpu08_a7_sel_to_voltage(0U, 0U) == -1);
	assert(s2mpu08_a7_needs_rev0_ldo_guard(0U, 35U));
	assert(s2mpu08_a7_needs_rev0_ldo_guard(0U, 36U));
	assert(!s2mpu08_a7_needs_rev0_ldo_guard(1U, 35U));
	assert(!s2mpu08_a7_needs_rev0_ldo_guard(0U, 2U));
	printf("PASS: 113 source-derived LDO2/LDO35 selectors, board voltage caps and rev0 guard\n");
	return 0;
}
