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

import numpy as np

from gnuradio import gr
from gnuradio import fft
from gnuradio import uhd
from gnuradio import blocks

from gnuradio.fft import window

########################################################################################################################

class spectro(gr.hier_block2):
    ####################################################################################################################

    def __init__(self, bandwidth=2e6, fft_bins=2048, int_time=1):
        gr.hier_block2.__init__(
            self, "Spectro",
                gr.io_signature(1, 1, gr.sizeof_gr_complex * 1),
                gr.io_signature(1, 1, gr.sizeof_float * fft_bins),
        )

        ##################################################
        # Parameters
        ##################################################
        self.bandwidth = bandwidth
        self.fft_bins = fft_bins
        self.int_time = int_time

        ##################################################
        # Variables
        ##################################################
        self.sinc_sample_locations = sinc_sample_locations = np.arange(-4.0 * np.pi / 2.0, +4.0 * np.pi / 2.0, np.pi / fft_bins)
        self.sinc = sinc = np.sinc(sinc_sample_locations / np.pi)
        self.custom_window = custom_window = sinc * np.hamming(4 * fft_bins)

        ##################################################
        # Blocks
        ##################################################
        self.blocks_stream_to_vector_3 = blocks.stream_to_vector(gr.sizeof_gr_complex * 1, fft_bins)
        self.blocks_stream_to_vector_2 = blocks.stream_to_vector(gr.sizeof_gr_complex * 1, fft_bins)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex * 1, fft_bins)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex * 1, fft_bins)
        self.blocks_multiply_const_vcc_3 = blocks.multiply_const_vcc(custom_window[: +fft_bins])
        self.blocks_multiply_const_vcc_2 = blocks.multiply_const_vcc(custom_window[1 * fft_bins: 2 * fft_bins])
        self.blocks_multiply_const_vcc_1 = blocks.multiply_const_vcc(custom_window[2 * fft_bins: 3 * fft_bins])
        self.blocks_multiply_const_vcc_0 = blocks.multiply_const_vcc(custom_window[-fft_bins: ])
        self.blocks_integrate_ff_0 = blocks.integrate_ff(int(int_time * bandwidth / fft_bins), fft_bins)
        self.blocks_fft_vcc_0 = fft.fft_vcc(fft_bins, True, window.blackmanharris(fft_bins), True, 1)
        self.blocks_delay_3 = blocks.delay(gr.sizeof_gr_complex * 1, fft_bins * 3)
        self.blocks_delay_2 = blocks.delay(gr.sizeof_gr_complex * 1, fft_bins * 2)
        self.blocks_delay_1 = blocks.delay(gr.sizeof_gr_complex * 1, fft_bins * 1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex * 1, fft_bins * 0)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_bins)
        self.blocks_add_vcc_0 = blocks.add_vcc(fft_bins)


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
        self.connect((self.blocks_integrate_ff_0, 0), (self, 0))
        self.connect((self.blocks_multiply_const_vcc_0, 0), (self.blocks_add_vcc_0, 0))
        self.connect((self.blocks_multiply_const_vcc_1, 0), (self.blocks_add_vcc_0, 1))
        self.connect((self.blocks_multiply_const_vcc_2, 0), (self.blocks_add_vcc_0, 2))
        self.connect((self.blocks_multiply_const_vcc_3, 0), (self.blocks_add_vcc_0, 3))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_multiply_const_vcc_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.blocks_multiply_const_vcc_2, 0))
        self.connect((self.blocks_stream_to_vector_2, 0), (self.blocks_multiply_const_vcc_1, 0))
        self.connect((self.blocks_stream_to_vector_3, 0), (self.blocks_multiply_const_vcc_3, 0))
        self.connect((self, 0), (self.blocks_delay_0, 0))
        self.connect((self, 0), (self.blocks_delay_1, 0))
        self.connect((self, 0), (self.blocks_delay_2, 0))
        self.connect((self, 0), (self.blocks_delay_3, 0))


    ####################################################################################################################

    def get_bandwidth(self):
        return self.bandwidth

    ####################################################################################################################

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth

    ####################################################################################################################

    def get_fft_bins(self):
        return self.fft_bins

    ####################################################################################################################

    def set_fft_bins(self, fft_bins):
        self.fft_bins = fft_bins
        self.set_custom_window(self.sinc * np.hamming(4 * self.fft_bins))
        self.set_sinc_sample_locations(np.arange(-4.0 * np.pi / 2.0, +4.0 * np.pi / 2.0, np.pi / self.fft_bins))
        self.blocks_delay_0.set_dly(self.fft_bins * 0)
        self.blocks_delay_1.set_dly(self.fft_bins * 1)
        self.blocks_delay_2.set_dly(self.fft_bins * 2)
        self.blocks_delay_3.set_dly(self.fft_bins * 3)
        self.blocks_multiply_const_vcc_0.set_k(self.custom_window[-self.fft_bins: ])
        self.blocks_multiply_const_vcc_1.set_k(self.custom_window[2 * self.fft_bins: 3 * self.fft_bins])
        self.blocks_multiply_const_vcc_2.set_k(self.custom_window[1 * self.fft_bins: 2 * self.fft_bins])
        self.blocks_multiply_const_vcc_3.set_k(self.custom_window[: +self.fft_bins])

    ####################################################################################################################

    def get_int_time(self):
        return self.int_time

    ####################################################################################################################

    def set_int_time(self, int_time):
        self.int_time = int_time

    ####################################################################################################################

    def get_sinc_sample_locations(self):
        return self.sinc_sample_locations

    ####################################################################################################################

    def set_sinc_sample_locations(self, sinc_sample_locations):
        self.sinc_sample_locations = sinc_sample_locations
        self.set_sinc(np.sinc(self.sinc_sample_locations / np.pi))

    ####################################################################################################################

    def get_sinc(self):
        return self.sinc

    ####################################################################################################################

    def set_sinc(self, sinc):
        self.sinc = sinc
        self.set_custom_window(self.sinc * np.hamming(4 * self.fft_bins))
        self.set_sinc(np.sinc(self.sinc_sample_locations / np.pi))

    ####################################################################################################################

    def get_custom_window(self):
        return self.custom_window

    ####################################################################################################################

    def set_custom_window(self, custom_window):
        self.custom_window = custom_window
        self.blocks_multiply_const_vcc_0.set_k(self.custom_window[-self.fft_bins: ])
        self.blocks_multiply_const_vcc_1.set_k(self.custom_window[2 * self.fft_bins: 3 * self.fft_bins])
        self.blocks_multiply_const_vcc_2.set_k(self.custom_window[1 * self.fft_bins: 2 * self.fft_bins])
        self.blocks_multiply_const_vcc_3.set_k(self.custom_window[: +self.fft_bins])

########################################################################################################################
