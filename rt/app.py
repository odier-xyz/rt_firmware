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

import os, sys, time, flask, psutil, serial, signal, threading, subprocess

from .spectro_uhd_1  import spectro_uhd_1
from .spectro_uhd_2  import spectro_uhd_2
from .spectro_osmo_1 import spectro_osmo_1
from .spectro_osmo_2 import spectro_osmo_2

########################################################################################################################

CLK_SRC_VALUES = {
    'internal',
    'external',
}
CLK_SRC_DEFAULT = 'internal'

FFT_BINS_MIN = 0
FFT_BINS_MAX = 8192
FFT_BINS_DEFAULT = 4096

BANDWIDTH_MIN = 200_000.0
BANDWIDTH_MAX = 56_000_000.0
BANDWIDTH_DEFAULT = 2_000_000.0

FREQUENCY_MIN = 70_000_000.0
FREQUENCY_MAX = 6_000_000_000.0
FREQUENCY_DEFAULT = 1_420_000_000.0

INT_TIME_MIN = 1
INT_TIME_MAX = 100
INT_TIME_DEFAULT = 1

RX_GAIN_MIN = 0.0
RX_GAIN_MAX = 76.0
RX_GAIN_DEFAULT = 30.0

########################################################################################################################
# GPSDO                                                                                                                #
########################################################################################################################

class GPSDOThread(threading.Thread):

    ####################################################################################################################

    def __init__(self, port = '/dev/ttyACM0', baudrate = 38400):

        ################################################################################################################

        threading.Thread.__init__(self)

        ################################################################################################################

        self.serial = serial.Serial(port = port, baudrate = baudrate, timeout = 0)

        self.serial.flushInput()

        self.alive = True

    ####################################################################################################################

    def run(self):

        while self.alive:

            ############################################################################################################

            try:

                line = self.serial.readline().decode('utf-8')

                if line.startswith('$GPGGA'):

                    parts = line.split(',')

                    if len(parts) == 15 and parts[3] == 'N' and parts[5] == 'E':

                        current_time = '{}:{}:{}'.format(
                            parts[1][0: 2],
                            parts[1][2: 4],
                            parts[1][4: 6]
                        )

                        current_latitude = parts[2]
                        current_longitude = parts[4]
                        current_altitude = parts[9]
                        current_satellite = parts[7]

                        print('time', current_time, 'latitude', current_latitude, 'longitude', current_longitude, 'altitude', current_altitude, 'current_satellite', current_satellite)

            except:

                pass

            ############################################################################################################

            try:

                time.sleep(0.1)

            except:

                pass

    ####################################################################################################################

    def stop(self):

        self.alive = False

        self.serial.close()

        print(self.alive)

########################################################################################################################

curr_gpsdo = GPSDOThread()

#curr_gpsdo.start()

########################################################################################################################
# SPECTRO                                                                                                              #
########################################################################################################################

curr_spectro = None

########################################################################################################################

class SpectroThread(threading.Thread):

    ####################################################################################################################

    def __init__(self, clk_src, fft_bins, bandwidth, frequency, int_time, rx_gain):

        ################################################################################################################

        threading.Thread.__init__(self)

        ################################################################################################################

        interface = str(flask.request.args.get('interface', 'uhd'))

        channels  = int(flask.request.args.get('channels' ,  '1' ))

        ################################################################################################################

        if channels == 2:

            if   interface == 'uhd':

                self.block = spectro_uhd_2(
                    clk_src = clk_src,
                    fft_bins = fft_bins,
                    bandwidth = bandwidth,
                    frequency = frequency,
                    int_time = int_time,
                    rx_gain = rx_gain
                )

            elif interface == 'rtl':

                self.block = spectro_osmo_2(
                    clk_src = clk_src,
                    fft_bins = fft_bins,
                    bandwidth = bandwidth,
                    frequency = frequency,
                    int_time = int_time,
                    rx_gain = rx_gain
                )

        else:

            if   interface == 'uhd':

                self.block = spectro_uhd_1(
                    clk_src = clk_src,
                    fft_bins = fft_bins,
                    bandwidth = bandwidth,
                    frequency = frequency,
                    int_time = int_time,
                    rx_gain = rx_gain
                )

            elif interface == 'rtl':

                self.block = spectro_osmo_1(
                    clk_src = clk_src,
                    fft_bins = fft_bins,
                    bandwidth = bandwidth,
                    frequency = frequency,
                    int_time = int_time,
                    rx_gain = rx_gain
                )

    ####################################################################################################################

    def run(self):

        try:

            self.block.start()
            self.block.wait()

        except Exception as e:

            print(e.__str__())

    ####################################################################################################################

    def stop(self):

        self.block.stop()
        self.block.wait()

########################################################################################################################
# WEB APPLICATION                                                                                                      #
########################################################################################################################

app = flask.Flask(__name__)

########################################################################################################################
# WEB APPLICATION ROUTES                                                                                               #
########################################################################################################################

@app.route('/', methods = ['GET'])
@app.route('/rt/status', methods = ['GET'])
def route_st_status():

    ####################################################################################################################

    cpu_info = {}

    try:

        for line in subprocess.check_output('lscpu').decode().replace('\t', '').split('\n'):

            parts = line.split(':', 1)

            if len(parts) == 2:

                key = parts[0].strip()
                val = parts[1].strip()

                cpu_info[key] = val

    except Exception as e:

        print(e.__str__())

    ####################################################################################################################

    mem_info = psutil.virtual_memory()

    ####################################################################################################################

    try:

        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:

            cpu_temp = float(f.read()) / 1000.0

    except:

        cpu_temp = 0.0000000000000 / 1000.0

    ####################################################################################################################

    if curr_spectro is None:

        spectro = {
            'status': 'stopped',
            'clk_src': None,
            'fft_bins': None,
            'bandwidth': None,
            'frequency': None,
            'int_time': None,
            'rx_gain': None,
        }

    else:

        spectro = {
            'status': 'started',
            'clk_src': curr_spectro.block.get_clk_src(),
            'fft_bins': curr_spectro.block.get_fft_bins(),
            'bandwidth': curr_spectro.block.get_bandwidth(),
            'frequency': curr_spectro.block.get_frequency(),
            'int_time': curr_spectro.block.get_int_time(),
            'rx_gain': curr_spectro.block.get_rx_gain(),
        }

    ####################################################################################################################

    return flask.jsonify({
        'timestamp': time.time(),
        'machine': {
            'cpu_arch': cpu_info.get('Architecture'),
            'cpu_count': int(cpu_info.get('CPU(s)', os.cpu_count())),
            'cpu_max_mhz': float(cpu_info.get('CPU max MHz', 0)),
            'cpu_min_mhz': float(cpu_info.get('CPU min MHz', 0)),
            'cpu_temp': cpu_temp,
            'mem_total': mem_info.total,
            'mem_free': 0x000000000000 + mem_info.available,
            'mem_used': mem_info.total - mem_info.available,
        },
        'noise-source': {
            'status': 'stopped',
		},
		'frontend': {
			'temp': 0.00,
		},
		'backend': {
			'temp': 0.00,
		},
        'spectro': spectro,
		'obs': {
			'temp': 0.00,
			'humi': 0.00,
			'gps_lat': 0.00,
			'gps_lon': 0.00,
			'gps_height': 0.00,
		},
    })

########################################################################################################################

@app.route('/rt/noise-source/enable', methods = ['GET'])
def route_rt_noise_source_enable():

    return route_st_status()

########################################################################################################################

@app.route('/rt/noise-source/disable', methods = ['GET'])
def route_rt_noise_source_disable():

    return route_st_status()

########################################################################################################################

@app.route('/rt/spectro/start', methods = ['GET'])
def route_rt_spectro_start():

    global curr_spectro

    ####################################################################################################################

    clk_src = str(flask.request.args.get('clk_src', ''))

    if clk_src not in CLK_SRC_VALUES:

        clk_src = CLK_SRC_DEFAULT

    ####################################################################################################################

    try:

        fft_bins = int(flask.request.args.get('fft_bins', ''))

        if   fft_bins < FFT_BINS_MIN:
            fft_bins = FFT_BINS_MIN
        elif fft_bins > FFT_BINS_MAX:
            fft_bins = FFT_BINS_MAX

    except ValueError as e:

        fft_bins = FFT_BINS_DEFAULT

    ####################################################################################################################

    try:

        bandwidth = float(flask.request.args.get('bandwidth', ''))

        if   bandwidth < BANDWIDTH_MIN:
            bandwidth = BANDWIDTH_MIN
        elif bandwidth > BANDWIDTH_MAX:
            bandwidth = BANDWIDTH_MAX

    except ValueError as e:

        bandwidth = BANDWIDTH_DEFAULT

    ####################################################################################################################

    try:

        frequency = float(flask.request.args.get('frequency', ''))

        if   frequency < FREQUENCY_MIN:
            frequency = FREQUENCY_MIN
        elif frequency > FREQUENCY_MAX:
            frequency = FREQUENCY_MAX

    except ValueError as e:

        frequency = FREQUENCY_DEFAULT

    ####################################################################################################################

    try:

        int_time = int(flask.request.args.get('int_time', ''))

        if   int_time < INT_TIME_MIN:
            int_time = INT_TIME_MIN
        elif int_time > INT_TIME_MAX:
            int_time = INT_TIME_MAX

    except ValueError as e:

        int_time = INT_TIME_DEFAULT

    ####################################################################################################################

    try:

        rx_gain = float(flask.request.args.get('rx_gain', ''))

        if   rx_gain < RX_GAIN_MIN:
            rx_gain = RX_GAIN_MIN
        elif rx_gain > RX_GAIN_MAX:
            rx_gain = RX_GAIN_MAX

    except ValueError as e:

        rx_gain = RX_GAIN_DEFAULT

    ####################################################################################################################

    if curr_spectro is None:

        try:

            curr_spectro = SpectroThread(
                clk_src = clk_src,
                fft_bins = fft_bins,
                bandwidth = bandwidth,
                frequency = frequency,
                int_time = int_time,
                rx_gain = rx_gain,
            )

            curr_spectro.start()

        except Exception as e:

            curr_spectro = None

            return flask.jsonify({
                'status': 'error',
                'message': e.__str__(),
                'timestamp': time.time(),
            }), 500

    ####################################################################################################################

    return route_st_status()

########################################################################################################################

@app.route('/rt/spectro/stop', methods = ['GET'])
def route_rt_spectro_stop():

    global curr_spectro

    ####################################################################################################################

    if curr_spectro is not None:

        try:

            curr_spectro.stop()
            curr_spectro.join()

            curr_spectro = None

        except Exception as e:

            curr_spectro = None

            return flask.jsonify({
                'status': 'error',
                'message': e.__str__(),
                'timestamp': time.time(),
            }), 500

    ####################################################################################################################

    return route_st_status()

########################################################################################################################

@app.route('/rt/reboot', methods = ['GET'])
def route_rt_reboot():

    threading.Timer(1, lambda: os.system('shutdown -r now')).start()

    return flask.jsonify({
        'status': 'success',
        'timestamp': time.time(),
    }), 200

########################################################################################################################

@app.route('/rt/poweroff', methods = ['GET'])
def route_rt_poweroff():

    threading.Timer(1, lambda: os.system('shutdown -h now')).start()

    return flask.jsonify({
        'status': 'success',
        'timestamp': time.time(),
    }), 200

########################################################################################################################
# SIGNALS                                                                                                              #
########################################################################################################################

def sig_handler(sig = None, frame = None):

    if curr_spectro is not None:

        curr_spectro.stop()
        curr_spectro.join()

    curr_gpsdo.stop()
    curr_gpsdo.join()

    print('\nBye.')

    sys.exit(0)

########################################################################################################################

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

########################################################################################################################
