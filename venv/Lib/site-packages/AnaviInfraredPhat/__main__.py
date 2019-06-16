"""
Publishes temperature, pressure, humidity, luminosity and heat index from your Pi over 0MQ.
"""
import logging

import argparse
import sys
from json import dumps
from time import sleep

from socket import gethostname

from AnaviInfraredPhat import report_tphl_average
from pap_logger import PaPLogger, DEBUG, INFO
import zmq


def _run(param):
    """
    Publishes temperature, pressure, humidity, luminosity and heat index from your Pi over 0MQ every interval seconds.
    """
    logging.info('Starting')
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.setsockopt(zmq.CONFLATE, 1)
    socket.bind("tcp://%s:%s" % ("*", param.pub_port))
    hostname = gethostname()
    while True:
        data = dumps(report_tphl_average("localhost"))
        logging.debug(data)
        socket.send_string("{} {}".format(hostname, data))
        sleep(param.interval)


def _main():
    param = _get_args()
    level = DEBUG if param.verbose else INFO
    pap = PaPLogger(level=level, verbose_fmt=True)
    pap.log_file = "/var/logAnaviInfraredPhat.log"
    _run(param)


def _get_args():
    parser = argparse.ArgumentParser(
        description='Publishes temperature, pressure, humidity, luminosity and heat index from your Pi over 0MQ.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--pub_port", help="port for zmq publication", default=4242, type=int)
    parser.add_argument("--interval", help="publication interval in seconds", default=30, type=int)
    parser.add_argument("--verbose", help="activate debugging", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        logging.info("Exiting")
        sys.exit(0)
    except Exception:
        logging.exception("exception raised")
        sys.exit(-1)
