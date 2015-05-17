#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'


import logging

from colorama import Fore, init
from humanize import naturalsize

from futurescan.output.logger import LoggerThread
from futurescan.output.handlers import get_output_handlers
from futurescan.helper import DummyThreadQueue
from futurescan.helper import str_now


class FutureScanOutput(DummyThreadQueue):

    def __init__(self, args):
        super(FutureScanOutput, self).__init__(args)
        self.logger = LoggerThread(args)
        self.handlers = get_output_handlers(args)

    def run(self):
        self.logger.start()
        while not self._stop:
            u, r, e = self.queue.get()
            self.logger.write('%s\t%s\t%s' % (u, r.status_code, e))

    def stop(self):
        self.logger.stop()
        self._stop = True

    def write(self, url, response, exception):
        self.queue.put((url, response, exception))

    def log(self, msg, level=logging.INFO):
        self.logger.write(msg, level)

    def critical(self, msg):
        self.log(msg, logging.CRITICAL)

    def _display_progress(self, **kwargs):
        # TODO: add detailed stats
        # Calculate progreess
        # percentage = '{percent:.2%}'.format(percent=float(self.urls_scanned) / self.args.urls_count)
        # percentage = self.sta
        # Generate and print colored output
        out = '[%s] [worker:%02i] [%s]\t%s -> status:%i ' % (
            str_now(), kwargs['worker'], percentage, kwargs['url'], kwargs['status'])
        if kwargs['exception'] is not None:
            out += 'error: (%s)' % str(kwargs['exception'])
        else:
            out += 'length: %s' % naturalsize(int(kwargs['length']))
        if kwargs['status'] == 200:
            print(Fore.GREEN + out + Fore.RESET)
        elif 400 <= kwargs['status'] < 500 or kwargs['status'] == -1:
            print(Fore.RED + out + Fore.RESET)
        else:
            print(Fore.YELLOW + out + Fore.RESET)
