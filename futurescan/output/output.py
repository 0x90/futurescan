#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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
            # if e is None and r:
            #     self.logger.write('%s\t%s\t%s' % (u, r.status_code, e))
            # else:
            #     self.logger.write('%s\t%s\t%s' % (u, r.status_code, e))
            for h in self.handlers:
                h.write(u, r, e)

    def stop(self):
        self.logger.stop()
        self._stop = True

    def write(self, url, response, exception):
        self.queue.put((url, response, exception))

    def log(self, msg, level=logging.INFO):
        self.logger.write(msg, level)

    def critical(self, msg):
        self.log(msg, logging.CRITICAL)


