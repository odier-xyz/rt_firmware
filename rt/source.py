#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Source
# GNU Radio version: 3.8.4.0

from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time


class source(gr.top_block):

    def __init__(self, bandwidth=2e6, frequency=1420e6, tx_gain=45):
        gr.top_block.__init__(self, "Source")

        ##################################################
        # Parameters
        ##################################################
        self.bandwidth = bandwidth
        self.frequency = frequency
        self.tx_gain = tx_gain

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_center_freq(frequency, 0)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_samp_rate(bandwidth)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec())
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.uhd_usrp_sink_0, 0))


    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.uhd_usrp_sink_0.set_samp_rate(self.bandwidth)

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.uhd_usrp_sink_0.set_center_freq(self.frequency, 0)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)




def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--bandwidth", dest="bandwidth", type=eng_float, default="2.0M",
        help="Set bandwidth [default=%(default)r]")
    parser.add_argument(
        "--frequency", dest="frequency", type=eng_float, default="1.42G",
        help="Set frequency [default=%(default)r]")
    parser.add_argument(
        "--tx-gain", dest="tx_gain", type=eng_float, default="45.0",
        help="Set tx_gain [default=%(default)r]")
    return parser


def main(top_block_cls=source, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bandwidth=options.bandwidth, frequency=options.frequency, tx_gain=options.tx_gain)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
