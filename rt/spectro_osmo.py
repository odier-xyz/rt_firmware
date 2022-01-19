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
    import osmosdr
except ModuleNotFoundError as e:
    print(e.__str__())

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

class spectro_osmo(gr.top_block):

    ####################################################################################################################

    def __init__(self, bandwidth=2e6, clk_src='external', fft_bins=2048, frequency=1420e6, int_time=1, rx_gain=30):
        gr.top_block.__init__(self, "Spectro OsmoSDR", catch_exceptions=True)

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
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex * 1, bandwidth,True)
        self.blocks_integrate_xx_0 = blocks.integrate_cc(100, 1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(bandwidth, analog.GR_COS_WAVE, frequency, 0.001, 0, 0)
        self.analog_fastnoise_source_x_0 = analog.fastnoise_source_c(analog.GR_GAUSSIAN, 0.001, 0, 8192)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_zeromq_pub_sink_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.spectro_0, 0))
        self.connect((self.spectro_0, 0), (self.blocks_zeromq_pub_sink_0, 0))


    ####################################################################################################################

    def get_bandwidth(self):
        return self.bandwidth

    ####################################################################################################################

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.analog_sig_source_x_0.set_sampling_freq(self.bandwidth)
        self.blocks_throttle_0.set_sample_rate(self.bandwidth)
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
        self.analog_sig_source_x_0.set_frequency(self.frequency)

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

########################################################################################################################
