# -*- coding:utf-8 -*-
########################################################################################################################

import os, json, time, flask, psutil, threading, subprocess

from .spectro import spectro

########################################################################################################################
# SPECTRO                                                                                                              #
########################################################################################################################

class SpectroThread(threading.Thread):

    ####################################################################################################################

    def __init__(self, bandwidth, frequency, gain):

        threading.Thread.__init__(self)

        self.block = spectro(
            bandwidth = bandwidth,
            frequency = frequency,
            gain = gain
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

spectrometer = None
bandwidth = None
frequency = None
gain = None

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

    for line in subprocess.check_output('lscpu').decode().replace('\t', '').split('\n'):

        parts = line.split(':', 1)

        if len(parts) == 2:

            key = parts[0].strip()
            val = parts[1].strip()

            cpu_info[key] = val

    ####################################################################################################################

    mem_info = psutil.virtual_memory()

    ####################################################################################################################

    if spectrometer is None:

        return flask.jsonify({
            'status': 'stopped',
            'timestamp': time.time(),
            'bandwidth': (((None))),
            'frequency': (((None))),
            'gain': None,
            'cpu_arch': cpu_info['Architecture'],
            'cpu_count': int(cpu_info['CPU(s)']),
            'cpu_max_mhz': float(cpu_info['CPU max MHz']),
            'cpu_min_mhz': float(cpu_info['CPU min MHz']),
            'mem_total': mem_info.total,
            'mem_free': 0x000000000000 + mem_info.available,
            'mem_used': mem_info.total - mem_info.available,
        }), 200

    else:

        return flask.jsonify({
            'status': 'started',
            'timestamp': time.time(),
            'bandwidth': bandwidth,
            'frequency': frequency,
            'gain': gain,
            'cpu_arch': cpu_info['Architecture'],
            'cpu_count': int(cpu_info['CPU(s)']),
            'cpu_max_mhz': float(cpu_info['CPU max MHz']),
            'cpu_min_mhz': float(cpu_info['CPU min MHz']),
            'mem_total': mem_info.total,
            'mem_free': 0x000000000000 + mem_info.available,
            'mem_used': mem_info.total - mem_info.available,
        }), 200

########################################################################################################################

@app.route('/rt/start', methods = ['GET'])
def route_st_start():

    global spectrometer
    global bandwidth
    global frequency
    global gain

    ####################################################################################################################

    try:
        bandwidth = int(flask.request.args.get('bandwidth', '20000000'))
    except ValueError as e:
        bandwidth = 20000000

    try:
        frequency = int(flask.request.args.get('frequency', '1420000000'))
    except ValueError as e:
        frequency = 1420000000

    try:
        gain = int(flask.request.args.get('gain', '30'))
    except ValueError as e:
        gain = 30

    ####################################################################################################################

    if spectrometer is None:

        try:

            spectrometer = SpectroThread(
                bandwidth = bandwidth,
                frequency = frequency,
                gain = gain
            )

            spectrometer.start()

        except Exception as e:

            spectrometer = None

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

@app.route('/rt/stop', methods = ['GET'])
def route_rt_stop():

    global spectrometer
    global bandwidth
    global frequency
    global gain

    ####################################################################################################################

    if spectrometer is not None:

        try:

            spectrometer.stop()
            spectrometer.join()

            spectrometer = None
            bandwidth = None
            frequency = None
            gain = None

        except Exception as e:

            spectrometer = None

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
