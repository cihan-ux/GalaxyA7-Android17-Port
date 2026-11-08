/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdio.h>
#include "s2mpu08-a7-acpm-frame-lab.h"

int main(void)
{
	unsigned int type, reg;
	struct s2mpu08_a7_acpm_frame cmd = {{0}};
	unsigned char result = 0xaa;
	for (type = 0; type <= 1; type++) {
		for (reg = 0; reg <= 255; reg++) {
			assert(s2mpu08_a7_acpm_pack_read(2, type, reg, &cmd) == 0);
			assert(cmd.word[0] == (type << 8) + reg);
			assert(cmd.word[1] == 0);
			assert(cmd.word[2] == 0 && cmd.word[3] == 0);
		}
	}
	cmd.word[0] = 0x12345678U;
	assert(s2mpu08_a7_acpm_pack_read(0, 1, 0, &cmd) < 0);
	assert(cmd.word[0] == 0x12345678U);
	assert(s2mpu08_a7_acpm_pack_read(3, 1, 0, &cmd) < 0);
	assert(s2mpu08_a7_acpm_pack_read(2, 2, 0, &cmd) < 0);
	assert(s2mpu08_a7_acpm_pack_read(2, 1, 256, &cmd) < 0);
	assert(s2mpu08_a7_acpm_pack_read(2, 1, 0, NULL) < 0);

	cmd.word[1] = (0x5aU << 8);
	assert(s2mpu08_a7_acpm_unpack_read(&cmd, &result) == 0);
	assert(result == 0x5aU);
	cmd.word[1] = (2U << 24) | (0x88U << 8);
	assert(s2mpu08_a7_acpm_unpack_read(&cmd, &result) == -2);
	assert(result == 0x5aU); /* failed read must not overwrite output */
	assert(s2mpu08_a7_acpm_unpack_read(NULL, &result) < 0);
	assert(s2mpu08_a7_acpm_unpack_read(&cmd, NULL) < 0);
	puts("PASS: 512 real C read-packet vectors, negative inputs and reply status; NO physical I/O");
	return 0;
}
