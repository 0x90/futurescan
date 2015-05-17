#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'

from sys import exit
from Queue import Empty
import logging
from httplib import HTTPConnection
from requests import packages
from futurescan.helper import DummyThreadQueue
from colorama import Fore, init
from humanize import naturalsize
from futurescan.helper import str_now
from BeautifulSoup import BeautifulSoup


def set_requests_debug_logging(debug=False):
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
        init()

        if args.log is not None:
            self.logger = logging.getLogger('future_scan_logger')
            self.logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
            # handler = logging.StreamHandler() if args.log is None else \
            #     logging.FileHandler(args.log)
            handler = logging.FileHandler(args.log)
            handler.setFormatter(
                logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s',
                                  datefmt='%d.%m.%Y %H:%M:%S'))
            self.logger.addHandler(handler)
        else:
            self.logger = None

    def write(self, msg, level=logging.INFO):
        self.queue.put((msg, level))

    def _write(self, msg, level=logging.INFO):
        if self.logger is None:
            print(msg)
        else:
            if level == logging.INFO:
                self.logger.info(msg)
            elif level == logging.DEBUG:
                self.logger.debug(msg)
            elif level == logging.ERROR:
                self.logger.error(msg)
            elif level == logging.WARNING:
                self.logger.warning(msg)

    def write_response(self, url, response, exception):
        if url is None or response is None:
            return
        try:
            html = BeautifulSoup(response.content)
            title = html.find('title').contents[0]
        except:
            title = None

        # TODO: add detailed stats
        status = response.status_code
        length = int(response.headers['content-length']) if 'content-length' in response.headers else len(
                response.content)
        out = '[%s]\t[%i]\t%s ' % (str_now(), status, url)
        if exception is not None:
            out += 'error: (%s)' % str(exception)
        else:
            out += 'title: %s length: %s' % (title, naturalsize(length))
        if status == 200:
            print(Fore.GREEN + out + Fore.RESET)
        elif 400 <= status < 500 or status == -1:
            print(Fore.RED + out + Fore.RESET)
        else:
            print(Fore.YELLOW + out + Fore.RESET)

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
