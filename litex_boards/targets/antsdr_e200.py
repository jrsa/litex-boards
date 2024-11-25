#!/usr/bin/env python3

# copied from litex_boards/targets/digilent_arty_z7.py

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 James Anderson <jrsa@jrsa.co>
# SPDX-License-Identifier: BSD-2-Clause


from migen import *

from litex.gen import *

from litex_boards.platforms import antsdr_e200
from litex.build import tools
from litex.build.xilinx import common as xil_common
from litex.build.tools import write_to_file
from litex.build.generic_platform import IOStandard, Subsignal, Pins

from litex.soc.interconnect import axi
from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, use_ps7_clk=False):
        self.rst    = Signal()
        self.cd_sys = ClockDomain()
        self.cd_idelay = ClockDomain()

        # # #

        if use_ps7_clk:
            self.comb += ClockSignal("sys").eq(ClockSignal("ps7"))
            self.comb += ResetSignal("sys").eq(ResetSignal("ps7") | self.rst)
        else:
            #raise RuntimeError("only PS7 clock is supported for system clock at the moment")

            ## this doesnt exist
            #clk125 = platform.request("clk125") 

            # i tried to make this work but
            clk40 = platform.request("clk40")
            #eth_rst_n = platform.request("eth_rst_n") # lol this is already hooked up in the liteeth phy
            #self.comb += eth_rst_n.eq(1)

            ## PLL.
            self.pll = pll = S7PLL(speedgrade=-1)
            self.comb += pll.reset.eq(self.rst)
            pll.register_clkin(clk40, 40e6)
            pll.create_clkout(self.cd_sys, sys_clk_freq)
            pll.create_clkout(self.cd_idelay, 200e6)
            # Ignore sys_clk to pll.clkin path created by SoC's rst.
            platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)
            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

        if True:  # stuff for ethernet phy clock, overlaps with NOT ps7 block above
            # s7rgmii needs this because it uses IDELAY blocks
            self.pll = pll = S7MMCM(speedgrade=-2)
            #self.comb += pll.reset.eq(self.rst)

            #clk40 = platform.request("clk40")
            #pll.register_clkin(clk40, 40e6)
            pll.register_clkin(self.cd_sys.clk, 100e6)
            pll.create_clkout(self.cd_idelay, 200e6)

            self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)
    

# BaseSoC ------------------------------------------------------------------------------------------


class BaseSoC(SoCCore):
    def __init__(self, toolchain="vivado", sys_clk_freq=125e6,
            with_led_chaser = True,
            with_ethernet = False,
            with_etherbone = False,
            ethphy_force = False,
            eth_ip = "192.168.1.50",
            **kwargs):
        platform = antsdr_e200.Platform(toolchain=toolchain)

        # CRG --------------------------------------------------------------------------------------
        use_ps7_clk = (kwargs.get("cpu_type", None) == "zynq7000")
        if use_ps7_clk:
            sys_clk_freq = 100e6

        self.crg = _CRG(platform, sys_clk_freq, use_ps7_clk)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            kwargs["integrated_sram_size"] = 0
            kwargs["with_uart"]            = False
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on ANTSDR E200", **kwargs)

        # Zynq7000 Integration ---------------------------------------------------------------------
        if kwargs.get("cpu_type", None) == "zynq7000":
            assert toolchain == "vivado", ' not tested / specific vivado cmds'

            self.cpu.set_ps7(name="Zynq",
                config={
                    **platform.ps7_config,
                    "PCW_FPGA0_PERIPHERAL_FREQMHZ" : sys_clk_freq / 1e6,
                })

            self.bus.add_region("sram", SoCRegion(
                origin = self.cpu.mem_map["sram"],
                size   = 192000)
            )
            #self.bus.add_region("rom", SoCRegion(
            #    origin = self.cpu.mem_map["rom"],
            #    size   = 256 * MEGABYTE // 8,
            #    linker = True)
            #)
            self.constants["CONFIG_CLOCK_FREQUENCY"] = 666666687 # not correct for 7020
            #self.bus.add_region("flash",  SoCRegion(origin=0xFC00_0000, size=0x4_0000, mode="rwx"))

        # Ethernet ---------------------------------------------------------------------------------
        # not working currently
        if with_ethernet or with_etherbone or ethphy_force:
            self.ethphy = LiteEthPHYRGMII(
                clock_pads          = self.platform.request("eth_clocks"),
                pads                = self.platform.request("eth"),
                #tx_delay            = 0e-9,
                with_hw_init_reset  = True,
            )

            # tying this high until i can figure out how to get liteeth to drive it correctly
            # self.comb += self.platform.request("eth_rst").eq(1)
            #self.comb += self.platform.request("eth_rst").eq(~self.crg.rst)

            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, data_width=32)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, data_width=32)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
        
            #_gpio = [
            #    [f"gpio", 0,
            #        Subsignal('led2', Pins(f"gpio:0")),
            #        Subsignal('led3', Pins(f"gpio:1")),
            #        Subsignal('led4', Pins(f"gpio:2")),
            #        Subsignal('btn2', Pins(f"gpio:3")),
            #        Subsignal('led1', Pins(f"gpio:4")),
            #        Subsignal('led5', Pins(f"gpio:5")),
            #        Subsignal('btn1', Pins(f"gpio:6")),
            #        Subsignal('btn3', Pins(f"gpio:7")),
            #        IOStandard("LVCMOS33")
            #    ]
            #]

            #platform.add_extension(_gpio)

            self.leds = LedChaser(
                pads         = platform.request_all("led"),
                sys_clk_freq = sys_clk_freq)

    def finalize(self, *args, **kwargs):
        super(BaseSoC, self).finalize(*args, **kwargs)
        if self.cpu_type != "zynq7000":
            return

        libxil_path = os.path.join(self.builder.software_dir, 'libxil')
        os.makedirs(os.path.realpath(libxil_path), exist_ok=True)
        lib = os.path.join(libxil_path, 'embeddedsw')
        if not os.path.exists(lib):
            os.system("git clone --depth 1 https://github.com/Xilinx/embeddedsw {}".format(lib))

        os.makedirs(os.path.realpath(self.builder.include_dir), exist_ok=True)
        for header in [
            'XilinxProcessorIPLib/drivers/uartps/src/xuartps_hw.h',
            'lib/bsp/standalone/src/common/xil_types.h',
            'lib/bsp/standalone/src/common/xil_assert.h',
            'lib/bsp/standalone/src/common/xil_io.h',
            'lib/bsp/standalone/src/common/xil_printf.h',
            'lib/bsp/standalone/src/common/xstatus.h',
            'lib/bsp/standalone/src/common/xdebug.h',
            'lib/bsp/standalone/src/arm/cortexa9/xpseudo_asm.h',
            'lib/bsp/standalone/src/arm/cortexa9/xreg_cortexa9.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_cache.h',
            'lib/bsp/standalone/src/arm/cortexa9/xparameters_ps.h',
            'lib/bsp/standalone/src/arm/cortexa9/xil_errata.h',
            'lib/bsp/standalone/src/arm/cortexa9/xtime_l.h',
            'lib/bsp/standalone/src/arm/common/xil_exception.h',
            'lib/bsp/standalone/src/arm/common/gcc/xpseudo_asm_gcc.h',
        ]:
            shutil.copy(os.path.join(lib, header), self.builder.include_dir)
        write_to_file(os.path.join(self.builder.include_dir, 'bspconfig.h'),
                      '#define FPU_HARD_FLOAT_ABI_ENABLED 1')
        write_to_file(os.path.join(self.builder.include_dir, 'xparameters.h'), '''
#ifndef __XPARAMETERS_H
#define __XPARAMETERS_H

#include "xparameters_ps.h"

#define STDOUT_BASEADDRESS 0xE0000000
#define XPAR_PS7_DDR_0_S_AXI_BASEADDR 0x00100000
#define XPAR_PS7_DDR_0_S_AXI_HIGHADDR 0x1FFFFFFF

#endif
''')


# Build --------------------------------------------------------------------------------------------


def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=antsdr_e200.Platform, description="LiteX SoC on ANTSDR E200")
    parser.add_target_argument("--variant",      default="z7-20",           help="Board variant (z7-20 or z7-10).")
    parser.add_target_argument("--sys-clk-freq", default=100e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-uart",  action="store_true", help="You want a UART... right?")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    ethopts.add_argument("--ethphy-force", action="store_true", help="Force insertion of ethphy for testing even though other eth options are not used.")
    parser.add_target_argument("--eth-ip",            default="192.168.1.50", help="Ethernet/Etherbone IP address.")
    parser.set_defaults(cpu_type="zynq7000")
    parser.set_defaults(no_uart=True)
    args = parser.parse_args()

    soc = BaseSoC(
        variant      = args.variant,
        toolchain    = args.toolchain,
        sys_clk_freq = args.sys_clk_freq,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        ethphy_force           = args.ethphy_force,
        eth_ip           = args.eth_ip,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.cpu_type == "zynq7000":
        soc.builder = builder
        builder.add_software_package('libxil')
        builder.add_software_library('libxil')
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"), device=1)

if __name__ == "__main__":
    main()
