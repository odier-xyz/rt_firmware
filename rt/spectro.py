#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Spectro
# GNU Radio version: 3.8.4.0

from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio import zeromq
import numpy as np


class spectro(gr.top_block):

    def __init__(self, bandwidth=2e6, frequency=1420e6, rx_gain=30, t_sample=1):
        gr.top_block.__init__(self, "Spectro")

        ##################################################
        # Parameters
        ##################################################
        self.bandwidth = bandwidth
        self.frequency = frequency
        self.rx_gain = rx_gain
        self.t_sample = t_sample

        ##################################################
        # Variables
        ##################################################
        self.channels = channels = 4096
        self.sinc_sample_locations = sinc_sample_locations = np.arange(-4.0 * np.pi / 2.0, +4.0 * np.pi / 2.0, np.pi / channels)
        self.sinc = sinc = np.sinc(sinc_sample_locations / np.pi)
        self.custom_window = custom_window = sinc * np.hamming(4 * channels)

        ##################################################
        # Blocks
        ##################################################
        self.blocks_zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_float, channels, 'tcp://*:50001', 100, False, -1)
        self.blocks_uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.blocks_uhd_usrp_source_0.set_center_freq(frequency, 0)
        self.blocks_uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.blocks_uhd_usrp_source_0.set_antenna('RX2', 0)
        self.blocks_uhd_usrp_source_0.set_samp_rate(bandwidth)
        self.blocks_uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())
        self.blocks_stream_to_vector_3 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, channels)
        self.blocks_stream_to_vector_2 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, channels)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, channels)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, channels)
        self.blocks_multiply_const_vcc_3 = blocks.multiply_const_vcc(custom_window[:+channels])
        self.blocks_multiply_const_vcc_2 = blocks.multiply_const_vcc(custom_window[1*channels: 2*channels])
        self.blocks_multiply_const_vcc_1 = blocks.multiply_const_vcc(custom_window[2*channels: 3*channels])
        self.blocks_multiply_const_vcc_0 = blocks.multiply_const_vcc(custom_window[-channels:])
        self.blocks_integrate_ff_0 = blocks.integrate_ff(int(t_sample*bandwidth/channels), channels)
        self.blocks_fft_vcc_0 = fft.fft_vcc(channels, True, window.blackmanharris(channels), True, 1)
        self.blocks_delay_3 = blocks.delay(gr.sizeof_gr_complex*1, channels*3)
        self.blocks_delay_2 = blocks.delay(gr.sizeof_gr_complex*1, channels*2)
        self.blocks_delay_1 = blocks.delay(gr.sizeof_gr_complex*1, channels*1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, channels*0)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(channels)
        self.blocks_add_vcc_0 = blocks.add_vcc(channels)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_vcc_0, 0), (self.blocks_fft_vcc_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_ff_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_delay_1, 0), (self.blocks_stream_to_vector_2, 0))
        self.connect((self.blocks_delay_2, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_delay_3, 0), (self.blocks_stream_to_vector_3, 0))
        self.connect((self.blocks_fft_vcc_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_integrate_ff_0, 0), (self.blocks_zeromq_pub_sink_0, 0))
        self.connect((self.blocks_multiply_const_vcc_0, 0), (self.blocks_add_vcc_0, 0))
        self.connect((self.blocks_multiply_const_vcc_1, 0), (self.blocks_add_vcc_0, 1))
        self.connect((self.blocks_multiply_const_vcc_2, 0), (self.blocks_add_vcc_0, 2))
        self.connect((self.blocks_multiply_const_vcc_3, 0), (self.blocks_add_vcc_0, 3))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_multiply_const_vcc_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.blocks_multiply_const_vcc_2, 0))
        self.connect((self.blocks_stream_to_vector_2, 0), (self.blocks_multiply_const_vcc_1, 0))
        self.connect((self.blocks_stream_to_vector_3, 0), (self.blocks_multiply_const_vcc_3, 0))
        self.connect((self.blocks_uhd_usrp_source_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.blocks_uhd_usrp_source_0, 0), (self.blocks_delay_1, 0))
        self.connect((self.blocks_uhd_usrp_source_0, 0), (self.blocks_delay_2, 0))
        self.connect((self.blocks_uhd_usrp_source_0, 0), (self.blocks_delay_3, 0))


    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.blocks_uhd_usrp_source_0.set_samp_rate(self.bandwidth)

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.blocks_uhd_usrp_source_0.set_center_freq(self.frequency, 0)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.blocks_uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    def get_t_sample(self):
        return self.t_sample

    def set_t_sample(self, t_sample):
        self.t_sample = t_sample

    def get_channels(self):
        return self.channels

    def set_channels(self, channels):
        self.channels = channels
        self.set_custom_window(self.sinc * np.hamming(4 * self.channels))
        self.set_sinc_sample_locations(np.arange(-4.0 * np.pi / 2.0, +4.0 * np.pi / 2.0, np.pi / self.channels))
        self.blocks_delay_0.set_dly(self.channels*0)
        self.blocks_delay_1.set_dly(self.channels*1)
        self.blocks_delay_2.set_dly(self.channels*2)
        self.blocks_delay_3.set_dly(self.channels*3)
        self.blocks_multiply_const_vcc_0.set_k(self.custom_window[-self.channels:])
        self.blocks_multiply_const_vcc_1.set_k(self.custom_window[2*self.channels: 3*self.channels])
        self.blocks_multiply_const_vcc_2.set_k(self.custom_window[1*self.channels: 2*self.channels])
        self.blocks_multiply_const_vcc_3.set_k(self.custom_window[:+self.channels])

    def get_sinc_sample_locations(self):
        return self.sinc_sample_locations

    def set_sinc_sample_locations(self, sinc_sample_locations):
        self.sinc_sample_locations = sinc_sample_locations
        self.set_sinc(np.sinc(self.sinc_sample_locations / np.pi))

    def get_sinc(self):
        return self.sinc

    def set_sinc(self, sinc):
        self.sinc = sinc
        self.set_custom_window(self.sinc * np.hamming(4 * self.channels))
        self.set_sinc(np.sinc(self.sinc_sample_locations / np.pi))

    def get_custom_window(self):
        return self.custom_window

    def set_custom_window(self, custom_window):
        self.custom_window = custom_window
        self.blocks_multiply_const_vcc_0.set_k(self.custom_window[-self.channels:])
        self.blocks_multiply_const_vcc_1.set_k(self.custom_window[2*self.channels: 3*self.channels])
        self.blocks_multiply_const_vcc_2.set_k(self.custom_window[1*self.channels: 2*self.channels])
        self.blocks_multiply_const_vcc_3.set_k(self.custom_window[:+self.channels])




def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--bandwidth", dest="bandwidth", type=eng_float, default="2.0M",
        help="Set bandwidth [default=%(default)r]")
    parser.add_argument(
        "--frequency", dest="frequency", type=eng_float, default="1.42G",
        help="Set frequency [default=%(default)r]")
    parser.add_argument(
        "--rx-gain", dest="rx_gain", type=eng_float, default="30.0",
        help="Set rx_gain [default=%(default)r]")
    parser.add_argument(
        "--t-sample", dest="t_sample", type=intx, default=1,
        help="Set t_sample [default=%(default)r]")
    return parser


def main(top_block_cls=spectro, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bandwidth=options.bandwidth, frequency=options.frequency, rx_gain=options.rx_gain, t_sample=options.t_sample)

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
