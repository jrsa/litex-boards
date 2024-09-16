#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Derek Mulcahy <derekmulcahy@gmail.com>
# Copyright (c) 2019-2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst - FIXME: A placeholder for an external clock
    ("clk100", 0, Pins("H16"), IOStandard("LVCMOS33")),

    # Leds - FIXME: A placeholder for an external LED
    ("user_led", 0, Pins("G14"), IOStandard("LVCMOS33")),

    # UART - FIXME: A placeholder for an external UART
    ("serial", 0,
        Subsignal("tx", Pins("D19")),
        Subsignal("rx", Pins("D20")),
        IOStandard("LVCMOS33"),
    ),

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
]

# Connectors ---------------------------------------------------------------------------------------
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

_connectors = [
    ("ja1", "- - - G14 E18 D20 E19 D19 - - F16 B20 F17 C20 - - E17 A20 D18 B19 - - F19 G20 F20 G19 - - J20 G18 H20 G17 - - J18 H17 H18 H16 - -"),
    ("ja2", "- - - J15 L14 J16 L15 K16 - - M14 G15 M15 H15 - - N15 J14 N16 K14 - - L19 J19 L20 K19 - - M17 M20 M18 M19 - - L16 K18 L17 K17 - -"),
    ("jb1", "- - - T19 T11 U12 T10 T12 - - P14 W13 R14 V12 - - U13 T14 V13 T14 - - T16 Y17 U17 Y16 - - W14 W15 Y14 V15 - - U14 U19 U15 U18 - -"),
    ("jb2", "- - - R19 N17 P16 P18 P15 - - T17 R17 R18 R16 - - V17 W19 V18 W18 - - T20 W16 U20 V16 - - V20 Y19 W20 Y18 - - N20 P19 P20 N18 - -"),
    ("jc1", "- - - V5  U7  U10 V7  T9  - - T5  Y13 U5  Y12 - - V11 W6  V10 V6  - - V8  Y11 W8  W11 - - U9  W9  U8  W10 - - Y9  Y6  Y8  Y7  - -"),
    # ("xadc", "N15 L14 K16 K14 N16 L15 J16 J14"),
    # ("mrcc", "H17 H16 K18 K17 U19 U18 P19 N18 Y6 Y7"),
    # ("srcc", "J18 H18 L16 L17 U14 U15 N20 P20 Y9 Y8"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    # The clock speed depends on the PS7 PLL configuration for the FCLK_CLK0 signal.
    default_clk_name   = "clk100"
    default_clk_freq   = 100e6

    def __init__(self, variant="z7-10", toolchain="vivado"):
        device = {
            "z7-10": "xc7z010-clg400-1",
            "z7-20": "xc7z020-clg400-3"
        }[variant]
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
