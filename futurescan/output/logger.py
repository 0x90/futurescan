#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'


from sys import exit
from Queue import Empty
import logging
from httplib import HTTPConnection
from requests import packages

from futurescan.helper import DummyThreadQueue


def set_requests_debig_logging(debug=False):
    if debug:
        # Enable requests lib debug output
        HTTPConnection.debuglevel = 5
        packages.urllib3.add_stderr_logger()
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
    else:
        # Surpress InsecureRequestWarning: Unverified HTTPS request is being made
        packages.urllib3.disable_warnings()


class LoggerThread(DummyThreadQueue):
    def __init__(self, args):
        super(LoggerThread, self).__init__(args)
        self.logger = logging.getLogger('httpscan_logger')
        self.logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
        handler = logging.StreamHandler() if args.log is None else \
            logging.FileHandler(args.logfile)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                              datefmt='%d.%m.%Y %H:%M:%S'))
        self.logger.addHandler(handler)

    def write(self, msg, level=logging.INFO):
        self.queue.put((msg, level))

    def _write(self, msg, level=logging.INFO):
        if level == logging.INFO:
            self.logger.info(msg)
        elif level == logging.DEBUG:
            self.logger.debug(msg)
        elif level == logging.ERROR:
            self.logger.error(msg)
        elif level == logging.WARNING:
            self.logger.warning(msg)

    def critical_error(self, msg):
        self._write(msg, logging.ERROR)
        exit(-1)

    def run(self):
        while True:
            try:
                m, l = self.queue.get()
                self._write(m, l)
                self.queue.task_done()
            except Empty:
                if self._stop:
                    break
