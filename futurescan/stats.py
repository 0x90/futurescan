#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'

from datetime import datetime


class FutureScanStats(object):

    def __init__(self, stime=None, total=0):
        self.stime = stime if stime is not None else datetime.now()
        self.ftime = None
        self.done = 0
        self.total = total
        self.errors = 0

    @property
    def remaining(self):
        return self.total - self.done

    @property
    def percentage(self):
        return '{percent:.2%}'.format(percent=float(self.done) / self.total)

    def start(self):
        self.stime = datetime.now()
    #
    # def parse(self, response=None, exception=None):
    #     self.done += 1
    #     if response is None or exception is not None:
    #         self.errors += 1

    def finish(self):
        self.ftime = datetime.now()

    def __str__(self):
        return 'Started: %s\nFinished: %s\nTotal:%s\nDone: %s\nErrors: %s' % \
               (self.stime, self.ftime, self.total, self.done, self.errors)

if __name__ == '__main__':
    pass