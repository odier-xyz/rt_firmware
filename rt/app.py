# -*- coding:utf-8 -*-
########################################################################################################################

import os, sys, time, flask, psutil, signal, threading, subprocess

from .spectro import spectro

########################################################################################################################

BANDWIDTH_MIN = 200_000.0
BANDWIDTH_MAX = 56_000_000.0
BANDWIDTH_DEFAULT = 4_000_000.0

FREQUENCY_MIN = 70_000_000.0
FREQUENCY_MAX = 6_000_000_000.0
FREQUENCY_DEFAULT = 1_420_000_000.0

RX_GAIN_MIN = 0.0
RX_GAIN_MAX = 76.0
RX_GAIN_DEFAULT = 38.0

########################################################################################################################
# SPECTRO                                                                                                              #
########################################################################################################################

curr_spectro = None

########################################################################################################################

class SpectroThread(threading.Thread):

    ####################################################################################################################

    def __init__(self, bandwidth, frequency, rx_gain):

        threading.Thread.__init__(self)

        self.block = spectro(
            bandwidth = bandwidth,
            frequency = frequency,
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

    if curr_spectro is None:

        spectro = {
            'status': 'stopped',
            'bandwidth': None,
            'frequency': None,
            'rx_gain': None,
        }

    else:

        spectro = {
            'status': 'stopped',
            'bandwidth': curr_spectro.block.get_bandwidth(),
            'frequency': curr_spectro.block.get_frequency(),
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
            'mem_total': mem_info.total,
            'mem_free': 0x000000000000 + mem_info.available,
            'mem_used': mem_info.total - mem_info.available,
        },
        'spectro': spectro,
    })

########################################################################################################################

@app.route('/rt/spectro/start', methods = ['GET'])
def route_st_spectro_start():

    global curr_spectro

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
                bandwidth = bandwidth,
                frequency = frequency,
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

    return flask.jsonify({
        'status': 'success',
        'timestamp': time.time(),
    }), 200

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

    return flask.jsonify({
        'status': 'success',
        'timestamp': time.time(),
    }), 200

########################################################################################################################

@app.route('/rt/reboot', methods = ['GET'])
def route_rt_reboot():

    threading.Timer(1, lambda: os.system('shutdown -r now')).start()

    return flask.jsonify({
        'status': 'success',
        'timestamp': time.time(),
    }), 200

########################################################################################################################

@app.route('/rt/halt', methods = ['GET'])
def route_rt_halt():

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

    print('\nBye.')

    sys.exit(0)

########################################################################################################################

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

########################################################################################################################
