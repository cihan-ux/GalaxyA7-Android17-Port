// SPDX-License-Identifier: GPL-2.0-only
/*
 * Exynos7885 AP2APM mailbox doorbell: non-integrated Linux 6.15 prototype.
 *
 * Derived from Samsung's pinned Exynos7885 ACPM IPC register header and
 * modern Exynos mailbox architecture. There is NO DTS node with this
 * intentionally non-production compatible. No Kconfig/Makefile integration:
 * build only as an explicit research object, NEVER as bootable kernel.
 *
 * This prototype is NOT ready for MMIO use on actual hardware until
 * Exynos7885-specific ACPM firmware/IRQ/clock/DTS validation is complete.
 */
#include <linux/bitops.h>
#include <linux/clk.h>
#include <linux/err.h>
#include <linux/io.h>
#include <linux/mailbox_controller.h>
#include <linux/mailbox/exynos-message.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <linux/slab.h>

#define EXYNOS7885_ACPM_INTGR0 0x0008
/* INTGR1=0x1c is not the AP->APM request register. */
#define EXYNOS7885_ACPM_INTMR0 0x0010
#define EXYNOS7885_ACPM_INTMR1 0x0024
#define EXYNOS7885_ACPM_MAX_CHANNELS 16U

struct exynos7885_acpm_mbox {
	void __iomem *regs;
	struct mbox_controller controller;
};

/* Samsung legacy apm_interrupt_gen(id) writes (1 << id) << 16 to INTGR0. 
 * This is AP->APM; INTGR1 sends in the opposite direction.
 * No live firmware/channel validation; this driver remains unbound. */
static int exynos7885_acpm_send(struct mbox_chan *chan, void *data)
{
	struct exynos7885_acpm_mbox *mb =
		dev_get_drvdata(chan->mbox->dev);
	const struct exynos_mbox_msg *msg = data;

	if (!mb || !msg || msg->chan_id >= EXYNOS7885_ACPM_MAX_CHANNELS ||
	    msg->chan_type != EXYNOS_MBOX_CHAN_TYPE_DOORBELL ||
	    chan != &chan->mbox->chans[msg->chan_id])
		return -EINVAL;

	writel(BIT(msg->chan_id) << 16, mb->regs + EXYNOS7885_ACPM_INTGR0);
	return 0;
}

static const struct mbox_chan_ops exynos7885_acpm_ops = {
	.send_data = exynos7885_acpm_send,
};

static struct mbox_chan *
exynos7885_acpm_of_xlate(struct mbox_controller *mbox,
			 const struct of_phandle_args *args)
{
	unsigned int id;

	/*
	 * The prototype requires an explicit one-cell firmware channel ID.
	 * Never hand out an arbitrary free channel: send_data() must match
	 * the same ID before writing the AP->APM doorbell.
	 * No production DT binding exists for this prototype.
	 */
	if (args->args_count != 1)
		return ERR_PTR(-EINVAL);
	id = args->args[0];
	if (id >= EXYNOS7885_ACPM_MAX_CHANNELS)
		return ERR_PTR(-EINVAL);
	return &mbox->chans[id];
}

/*
 * Intentionally *not* the legacy samsung,exynos-acpm-ipc binding:
 * that node represents the historical monolithic protocol controller.
 * No DTS or DT binding in this repository exposes the prototype string.
 */
static const struct of_device_id exynos7885_acpm_mbox_of_match[] = {
	{ .compatible = "samsung,exynos7885-acpm-mbox-prototype" },
	{ }
};
MODULE_DEVICE_TABLE(of, exynos7885_acpm_mbox_of_match);

static int exynos7885_acpm_mbox_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct exynos7885_acpm_mbox *mb;
	struct mbox_controller *ctl;
	struct mbox_chan *channels;
	struct clk *clock;
	unsigned int i;

	mb = devm_kzalloc(dev, sizeof(*mb), GFP_KERNEL);
	if (!mb)
		return -ENOMEM;

	channels = devm_kcalloc(dev, EXYNOS7885_ACPM_MAX_CHANNELS,
				sizeof(*channels), GFP_KERNEL);
	if (!channels)
		return -ENOMEM;

	mb->regs = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(mb->regs))
		return PTR_ERR(mb->regs);

	/* The pinned old ACPM IPC DT does not have a named "pclk". */
	clock = devm_clk_get_optional_enabled(dev, "pclk");
	if (IS_ERR(clock))
		return dev_err_probe(dev, PTR_ERR(clock),
				     "Cannot enable optional ACPM mailbox clock\n");

	ctl = &mb->controller;
	ctl->dev = dev;
	ctl->num_chans = EXYNOS7885_ACPM_MAX_CHANNELS;
	ctl->chans = channels;
	ctl->ops = &exynos7885_acpm_ops;
	ctl->of_xlate = exynos7885_acpm_of_xlate;
	for (i = 0; i < EXYNOS7885_ACPM_MAX_CHANNELS; i++)
		channels[i].mbox = ctl;

	platform_set_drvdata(pdev, mb);

	/*
	 * Historical Exynos7885 code writes polling channel masks to INTMR1,
	 * not to GS101's INTMR0. Do not modify either mask before A7 firmware
	 * interrupt semantics and the DT ownership model are validated.
	 */
	return devm_mbox_controller_register(dev, ctl);
}

static struct platform_driver exynos7885_acpm_mbox_prototype_driver = {
	.probe = exynos7885_acpm_mbox_probe,
	.driver = {
		.name = "exynos7885-acpm-mbox-prototype",
		.of_match_table = exynos7885_acpm_mbox_of_match,
	},
};
module_platform_driver(exynos7885_acpm_mbox_prototype_driver);

MODULE_DESCRIPTION("Non-integrated Exynos7885 ACPM mailbox prototype: compiler research only");
MODULE_LICENSE("GPL");
