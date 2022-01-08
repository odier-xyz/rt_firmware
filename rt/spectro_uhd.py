# -*- coding:utf-8 -*-
########################################################################################################################

import correctiq

from gnuradio import gr
from gnuradio import uhd
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

class spectro_uhd(gr.top_block):

    ####################################################################################################################

    def __init__(self, bandwidth = 2e6, channels = 4096, frequency = 1420e6, rx_gain = 30, t_sample = 1):
        gr.top_block.__init__(self, "Spectro UHD")

        ##################################################
        # Parameters
        ##################################################
        self.bandwidth = bandwidth
        self.channels = channels
        self.frequency = frequency
        self.rx_gain = rx_gain
        self.t_sample = t_sample

        ##################################################
        # Blocks
        ##################################################
        self.spectro_0 = spectro(
            bandwidth = frequency,
            channels = channels,
            t_sample = 1,
        )
        self.correctiq_correctiq_0 = correctiq.correctiq()
        self.blocks_zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_float, channels, 'tcp://*:50005', 100, False, -1)
        self.blocks_uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format = "fc32",
                args = '',
                channels = list(range(0,1)),
            ),
        )
        self.blocks_uhd_usrp_source_0.set_center_freq(frequency, 0)
        self.blocks_uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.blocks_uhd_usrp_source_0.set_antenna('RX2', 0)
        self.blocks_uhd_usrp_source_0.set_samp_rate(bandwidth)
        self.blocks_uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_uhd_usrp_source_0, 0), (self.correctiq_correctiq_0, 0))
        self.connect((self.correctiq_correctiq_0, 0), (self.spectro_0, 0))
        self.connect((self.spectro_0, 0), (self.blocks_zeromq_pub_sink_0, 0))


    ####################################################################################################################

    def get_bandwidth(self):
        return self.bandwidth

    ####################################################################################################################

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.blocks_uhd_usrp_source_0.set_samp_rate(self.bandwidth)

    ####################################################################################################################

    def get_channels(self):
        return self.channels

    ####################################################################################################################

    def set_channels(self, channels):
        self.channels = channels
        self.spectro_0.set_channels(self.channels)

    ####################################################################################################################

    def get_frequency(self):
        return self.frequency

    ####################################################################################################################

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.blocks_uhd_usrp_source_0.set_center_freq(self.frequency, 0)
        self.spectro_0.set_bandwidth(self.frequency)

    ####################################################################################################################

    def get_rx_gain(self):
        return self.rx_gain

    ####################################################################################################################

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.blocks_uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    ####################################################################################################################

    def get_t_sample(self):
        return self.t_sample

    ####################################################################################################################

    def set_t_sample(self, t_sample):
        self.t_sample = t_sample

########################################################################################################################
