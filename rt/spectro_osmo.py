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

import osmosdr
import correctiq

from gnuradio import gr
from gnuradio import blocks
from gnuradio import zeromq

from .spectro import spectro

########################################################################################################################

class spectro_osmo(gr.top_block):

    ####################################################################################################################

    def __init__(self, bandwidth=2e6, channels=4096, frequency=1420e6, rx_gain=30, t_sample=1):
        gr.top_block.__init__(self, "Spectro OsmoSDR")

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
            bandwidth=2e6,
            channels=4096,
            t_sample=1,
        )
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(bandwidth)
        self.osmosdr_source_0.set_center_freq(frequency, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(rx_gain, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self.correctiq_correctiq_0 = correctiq.correctiq()
        self.blocks_zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_float, channels, 'tcp://*:50001', 100, False, -1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.correctiq_correctiq_0, 0), (self.spectro_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.correctiq_correctiq_0, 0))
        self.connect((self.spectro_0, 0), (self.blocks_zeromq_pub_sink_0, 0))


    ####################################################################################################################

    def get_bandwidth(self):
        return self.bandwidth

    ####################################################################################################################

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.osmosdr_source_0.set_sample_rate(self.bandwidth)

    ####################################################################################################################

    def get_channels(self):
        return self.channels

    ####################################################################################################################

    def set_channels(self, channels):
        self.channels = channels

    ####################################################################################################################

    def get_frequency(self):
        return self.frequency

    ####################################################################################################################

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.osmosdr_source_0.set_center_freq(self.frequency, 0)

    ####################################################################################################################

    def get_rx_gain(self):
        return self.rx_gain

    ####################################################################################################################

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.osmosdr_source_0.set_gain(self.rx_gain, 0)

    ####################################################################################################################

    def get_t_sample(self):
        return self.t_sample

    ####################################################################################################################

    def set_t_sample(self, t_sample):
        self.t_sample = t_sample

########################################################################################################################
