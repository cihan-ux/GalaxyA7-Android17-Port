/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * SM-A750F ACPM SRAM ABI probe, in-memory data only.
 * Pinned Samsung Exynos7885 legacy firmware layout vs Linux 6.15 ACPM.
 * No ioremap, register writes, firmware messages or driver registration.
 */
#ifndef A7_ACPM_SRAM_ABI_LAB_H
#define A7_ACPM_SRAM_ABI_LAB_H

#define A7_ACPM_SRAM_BYTES       0x1b000U
#define A7_ACPM_INITDATA_OFFSET  0x4b80U
#define A7_ACPM_PMIC_CHANNEL     2U
#define A7_ACPM_ABI_ERROR       (-1)

/* Only the relevant first seven u32 fields of historical acpm_framework. */
struct a7_legacy_framework_prefix {
	unsigned int plugins;
	unsigned int num_plugins;
	unsigned int ipc_channels;
	unsigned int num_ipc_channels;
	unsigned int pid_framework;
	unsigned int pid_max;
	unsigned int ipc_ap_max;
};

/* Linux 6.15 GS101 acpm_shmem structure from pinned exynos-acpm.c. */
struct a7_modern_framework_prefix {
	unsigned int reserved[2];
	unsigned int chans;
	unsigned int reserved1[3];
	unsigned int num_chans;
};

/* Samsung legacy channel_info, including unused indirection information. */
struct a7_legacy_channel_info {
	unsigned int rx_rear;
	unsigned int rx_front;
	unsigned int rx_base;
	unsigned int rx_indr_buf;
	unsigned int rx_indr_buf_base;
	unsigned int rx_indr_buf_size;
	unsigned int tx_rear;
	unsigned int tx_front;
	unsigned int tx_base;
	unsigned int q_len;
	unsigned int q_elem_size;
	unsigned int credit;
	unsigned int mbox_addr;
};

/* Full old firmware IPC channel, before any driver-local interpretation. */
struct a7_legacy_ipc_channel {
	unsigned int id;
	unsigned int field;
	int owner;
	unsigned int type;
	struct a7_legacy_channel_info ch;
	unsigned int ap_poll;
};

/* Linux 6.15 struct acpm_chan_shmem: same offsets for key queue fields. */
struct a7_modern_ipc_channel {
	unsigned int id;
	unsigned int reserved[3];
	unsigned int rx_rear;
	unsigned int rx_front;
	unsigned int rx_base;
	unsigned int reserved1[3];
	unsigned int tx_rear;
	unsigned int tx_front;
	unsigned int tx_base;
	unsigned int qlen;
	unsigned int mlen;
	unsigned int reserved2[2];
	unsigned int poll_completion;
};

struct a7_acpm_queue_layout {
	unsigned int ap_tx_base;
	unsigned int ap_rx_base;
	unsigned int qlen;
	unsigned int mlen;
	unsigned int polling;
};

/*
 * Only validates a CALLER-SUPPLIED, already decoded snapshot.
 * Firmware SRAM is never mapped or dereferenced by this code.
 * The returned offsets cannot be used for physical I/O without a
 * separately validated A7-specific controller/DT/firmware integration.
 */
int a7_acpm_validate_fw_prefix(const struct a7_legacy_framework_prefix *fw,
				unsigned int size_bytes,
				unsigned int *channel_array_offset,
				unsigned int *channel_count);
int a7_acpm_validate_pmic_channel(const struct a7_legacy_ipc_channel *ch,
				   unsigned int size_bytes,
				   struct a7_acpm_queue_layout *out);
#endif
