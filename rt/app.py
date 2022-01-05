# -*- coding:utf-8 -*-
########################################################################################################################

import os, json, time, flask, psutil, threading, subprocess

from .spectro import spectro
from .source import source

########################################################################################################################

BANDWIDTH_MIN = 200_000.0
BANDWIDTH_MAX = 56_000_000.0
BANDWIDTH_DEFAULT = 20_000_000.0

FREQUENCY_MIN = 70_000_000.0
FREQUENCY_MAX = 6_000_000_000.0
FREQUENCY_DEFAULT = 1_420_000_000.0

RX_GAIN_MIN = 0.0
RX_GAIN_MAX = 76.0
RX_GAIN_DEFAULT = RX_GAIN_MAX / 2.0

TX_GAIN_MIN = 0.0
TX_GAIN_MAX = 89.8
TX_GAIN_DEFAULT = TX_GAIN_MAX / 2.0

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
# SOURCE                                                                                                               #
########################################################################################################################

curr_source = None

########################################################################################################################

class SourceThread(threading.Thread):

    ####################################################################################################################

    def __init__(self, bandwidth, frequency, tx_gain):

        threading.Thread.__init__(self)

        self.block = source(
            bandwidth = bandwidth,
            frequency = frequency,
            tx_gain = tx_gain
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
            'bandwidth': curr_spectro.get_bandwidth(),
            'frequency': curr_spectro.get_frequency(),
            'rx_gain': curr_spectro.get_rx_gain(),
        }

    ####################################################################################################################

    if curr_source is None:

        source = {
            'status': 'stopped',
            'bandwidth': None,
            'frequency': None,
            'gain': None,
        }

    else:

        source = {
            'status': 'stopped',
            'bandwidth': curr_source.get_bandwidth(),
            'frequency': curr_source.get_frequency(),
            'gain': curr_source.get_tx_gain(),
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
        'source': source,
    })

########################################################################################################################

@app.route('/rt/spectro/start', methods = ['GET'])
def route_st_spectro_start():

    global curr_spectro

    ####################################################################################################################

    try:

        bandwidth = int(flask.request.args.get('bandwidth', ''))

        if   bandwidth < BANDWIDTH_MIN:
            bandwidth = BANDWIDTH_MIN
        elif bandwidth > BANDWIDTH_MAX:
            bandwidth = BANDWIDTH_MAX

    except ValueError as e:

        bandwidth = BANDWIDTH_DEFAULT

    ####################################################################################################################

    try:

        frequency = int(flask.request.args.get('frequency', ''))

        if   frequency < FREQUENCY_MIN:
            frequency = FREQUENCY_MIN
        elif frequency > FREQUENCY_MAX:
            frequency = FREQUENCY_MAX

    except ValueError as e:

        frequency = FREQUENCY_DEFAULT

    ####################################################################################################################

    try:

        rx_gain = int(flask.request.args.get('rx_gain', ''))

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

@app.route('/rt/source/start', methods = ['GET'])
def route_st_source_start():

    global curr_source

    ####################################################################################################################

    try:

        bandwidth = int(flask.request.args.get('bandwidth', ''))

        if   bandwidth < BANDWIDTH_MIN:
            bandwidth = BANDWIDTH_MIN
        elif bandwidth > BANDWIDTH_MAX:
            bandwidth = BANDWIDTH_MAX

    except ValueError as e:

        bandwidth = BANDWIDTH_DEFAULT

    ####################################################################################################################

    try:

        frequency = int(flask.request.args.get('frequency', ''))

        if   frequency < FREQUENCY_MIN:
            frequency = FREQUENCY_MIN
        elif frequency > FREQUENCY_MAX:
            frequency = FREQUENCY_MAX

    except ValueError as e:

        frequency = FREQUENCY_DEFAULT

    ####################################################################################################################

    try:

        tx_gain = float(flask.request.args.get('tx_gain', ''))

        if   tx_gain < TX_GAIN_MIN:
            tx_gain = TX_GAIN_MIN
        elif tx_gain > TX_GAIN_MAX:
            tx_gain = TX_GAIN_MAX

    except ValueError as e:

        tx_gain = TX_GAIN_DEFAULT

    ####################################################################################################################

    if curr_source is None:

        try:

            curr_source = SourceThread(
                bandwidth = bandwidth,
                frequency = frequency,
                tx_gain = tx_gain
            )

            curr_source.start()

        except Exception as e:

            curr_source = None

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

@app.route('/rt/source/stop', methods = ['GET'])
def route_rt_source_stop():

    global curr_source

    ####################################################################################################################

    if curr_source is not None:

        try:

            curr_source.stop()
            curr_source.join()

            curr_source = None

        except Exception as e:

            curr_source = None

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
