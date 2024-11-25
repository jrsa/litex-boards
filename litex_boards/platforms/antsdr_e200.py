#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2024 James Anderson <jrsa@jrsa.co>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk40", 0, Pins("K17"), IOStandard("LVCMOS18")),

    # PS7
    ("ps7_clk",   0, Pins(1)),
    ("ps7_porb",  0, Pins(1)),
    ("ps7_srstb", 0, Pins(1)),
    ("ps7_mio",   0, Pins(54)),
    ("ps7_ddram", 0,
        Subsignal("addr",    Pins(15)),
        Subsignal("ba",      Pins(3)),
        Subsignal("cas_n",   Pins(1)),
        Subsignal("ck_n",    Pins(1)),
        Subsignal("ck_p",    Pins(1)),
        Subsignal("cke",     Pins(1)),
        Subsignal("cs_n",    Pins(1)),
        Subsignal("dm",      Pins(4)),
        Subsignal("dq",      Pins(32)),
        Subsignal("dqs_n",   Pins(4)),
        Subsignal("dqs_p",   Pins(4)),
        Subsignal("odt",     Pins(1)),
        Subsignal("ras_n",   Pins(1)),
        Subsignal("reset_n", Pins(1)),
        Subsignal("we_n",    Pins(1)),
        Subsignal("vrn",     Pins(1)),
        Subsignal("vrp",     Pins(1)),
    ),


    ("eth_clocks", 0,
        Subsignal("tx", Pins("D18")),
        Subsignal("rx", Pins("H16")),
        IOStandard("LVCMOS18"),
    ),
    ("eth", 0,
        # Subsignal("rst_n",   Pins("B19")), # the hackery continues, s7rgmii module drives this incorrectly
        Subsignal("mdio",    Pins("A20")),
        Subsignal("mdc",     Pins("B20")),
        Subsignal("rx_ctl",  Pins("G17")),
        Subsignal("rx_data", Pins("F16 E17 E19 E18")),
        Subsignal("tx_ctl",  Pins("F20")),
        Subsignal("tx_data", Pins("F19 D20 D19 C20")),
        IOStandard("LVCMOS18")
    ),
    ("eth_rst", 0, Pins("B19"), IOStandard("LVCMOS18")),

    # have one led hooked up to the first gpio
    ("led", 0, Pins("V5"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("U7")),
        Subsignal("rx", Pins("V7")),
        IOStandard("LVCMOS33")
    ),
]

ps7_config = {
    "PCW_PRESET_BANK1_VOLTAGE"           : "LVCMOS 1.8V",
    "PCW_CRYSTAL_PERIPHERAL_FREQMHZ"     : "50",
    "PCW_APU_PERIPHERAL_FREQMHZ"         : "650",
    "PCW_SDIO_PERIPHERAL_FREQMHZ"        : "50",
    "PCW_FPGA0_PERIPHERAL_FREQMHZ"       : "100",
    "PCW_UIPARAM_DDR_FREQ_MHZ"           : "525",
    "PCW_UIPARAM_DDR_BUS_WIDTH"          : "16 Bit",
    "PCW_UIPARAM_DDR_PARTNO"             : "MT41J256M16 RE-125",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_0" : "0.040",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_1" : "0.058",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_2" : "-0.009",
    "PCW_UIPARAM_DDR_DQS_TO_CLK_DELAY_3" : "-0.033",
    "PCW_UIPARAM_DDR_BOARD_DELAY0"       : "0.223",
    "PCW_UIPARAM_DDR_BOARD_DELAY1"       : "0.212",
    "PCW_UIPARAM_DDR_BOARD_DELAY2"       : "0.085",
    "PCW_UIPARAM_DDR_BOARD_DELAY3"       : "0.092",
    "PCW_QSPI_PERIPHERAL_ENABLE"         : "1",
    "PCW_QSPI_GRP_SINGLE_SS_ENABLE"      : "1",
    "PCW_QSPI_GRP_FBCLK_ENABLE"          : "1",
    "PCW_ENET0_PERIPHERAL_ENABLE"        : "1",
    "PCW_ENET0_ENET0_IO"                 : "MIO 16 .. 27",
    "PCW_ENET0_GRP_MDIO_ENABLE"          : "1",
    "PCW_ENET0_GRP_MDIO_IO"              : "MIO 52 .. 53",
    "PCW_ENET0_RESET_ENABLE"             : "1",
    "PCW_ENET0_RESET_IO"                 : "MIO 9",
    "PCW_SD0_PERIPHERAL_ENABLE"          : "1",
    "PCW_SD0_GRP_CD_ENABLE"              : "1",
    "PCW_SD0_GRP_CD_IO"                  : "MIO 47",
    "PCW_UART0_PERIPHERAL_ENABLE"        : "1",
    "PCW_UART0_UART0_IO"                 : "MIO 14 .. 15",
    "PCW_USB0_PERIPHERAL_ENABLE"         : "1",
    "PCW_USB0_RESET_ENABLE"              : "1",
    "PCW_USB0_RESET_IO"                  : "MIO 46",
    "PCW_GPIO_MIO_GPIO_ENABLE"           : "1",
    "PCW_GPIO_MIO_GPIO_IO"               : "MIO",
    "PCW_GPIO_EMIO_GPIO_ENABLE"          : "0",
}

# Connectors ---------------------------------------------------------------------------------------
_connectors = [
#    ("gpio", "V5 U7 V7 T9 U10 Y7 Y6 Y6"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    # The clock speed depends on the PS7 PLL configuration for the FCLK_CLK0 signal.
    default_clk_name   = "clk100"
    default_clk_freq   = 100e6

    def __init__(self, toolchain="vivado"):
        device = "xc7z020-clg400-2"
        Xilinx7SeriesPlatform.__init__(self, device, _io,  _connectors, toolchain=toolchain)
        self.ps7_config = ps7_config
        self.default_clk_period = 1e9 / self.default_clk_freq
        self.toolchain.bitstream_commands = [
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        ]

    def create_programmer(self):
        return VivadoProgrammer(flash_part="n25q128a")

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request(self.default_clk_name, loose=True), self.default_clk_period)
