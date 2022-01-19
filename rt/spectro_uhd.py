# -*- coding:utf-8 -*-
########################################################################################################################
# Author: Jerome ODIER
# Email: jerome@odier.xyz
# URL: http://odier.xyz/
#
# Radio Telescope
#
# Copyright (c) 2022-XXXX Jérôme Odier
########################################################################################################################

try:
    from gnuradio import uhd
except ModuleNotFoundError as e:
    print(e.__str__())

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

class spectro_uhd(gr.top_block):

    ####################################################################################################################

    def __init__(self, bandwidth=2e6, clk_src='internal', fft_bins=2048, frequency=1420e6, int_time=1, rx_gain=30):
        gr.top_block.__init__(self, "Spectro UHD", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.bandwidth = bandwidth
        self.clk_src = clk_src
        self.fft_bins = fft_bins
        self.frequency = frequency
        self.int_time = int_time
        self.rx_gain = rx_gain

        ##################################################
        # Blocks
        ##################################################
        self.spectro_0 = spectro(
            bandwidth=bandwidth,
            fft_bins=fft_bins,
            int_time=1,
        )
        self.blocks_zeromq_pub_sink_0_0 = zeromq.pub_sink(gr.sizeof_gr_complex, 1, 'tcp://*:50000', 100, False, -1, '')
        self.blocks_zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_float, fft_bins, 'tcp://*:50001', 100, False, -1, '')
        self.blocks_uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.blocks_uhd_usrp_source_0.set_clock_source(clk_src, 0)
        self.blocks_uhd_usrp_source_0.set_samp_rate(bandwidth)
        self.blocks_uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.blocks_uhd_usrp_source_0.set_center_freq(frequency, 0)
        self.blocks_uhd_usrp_source_0.set_antenna('RX2', 0)
        self.blocks_uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.blocks_integrate_xx_0 = blocks.integrate_cc(100, 1)
        self.blocks_correctiq_0 = blocks.correctiq()


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_correctiq_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_correctiq_0, 0), (self.spectro_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_zeromq_pub_sink_0_0, 0))
        self.connect((self.blocks_uhd_usrp_source_0, 0), (self.blocks_correctiq_0, 0))
        self.connect((self.spectro_0, 0), (self.blocks_zeromq_pub_sink_0, 0))


    ####################################################################################################################

    def get_bandwidth(self):
        return self.bandwidth

    ####################################################################################################################

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.blocks_uhd_usrp_source_0.set_samp_rate(self.bandwidth)
        self.spectro_0.set_bandwidth(self.bandwidth)

    ####################################################################################################################

    def get_clk_src(self):
        return self.clk_src

    ####################################################################################################################

    def set_clk_src(self, clk_src):
        self.clk_src = clk_src

    ####################################################################################################################

    def get_fft_bins(self):
        return self.fft_bins

    ####################################################################################################################

    def set_fft_bins(self, fft_bins):
        self.fft_bins = fft_bins
        self.spectro_0.set_fft_bins(self.fft_bins)

    ####################################################################################################################

    def get_frequency(self):
        return self.frequency

    ####################################################################################################################

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.blocks_uhd_usrp_source_0.set_center_freq(self.frequency, 0)

    ####################################################################################################################

    def get_int_time(self):
        return self.int_time

    ####################################################################################################################

    def set_int_time(self, int_time):
        self.int_time = int_time

    ####################################################################################################################

    def get_rx_gain(self):
        return self.rx_gain

    ####################################################################################################################

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.blocks_uhd_usrp_source_0.set_gain(self.rx_gain, 0)

########################################################################################################################
