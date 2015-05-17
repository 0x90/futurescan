#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'


# Basic dependencies
from sys import exit
from cookielib import MozillaCookieJar
from os import path
import logging
import signal

# external libs
from concurrent import futures
import requesocks
from requests import adapters
from cookies import Cookies
from fake_useragent import UserAgent

# own libs
from futurescan import file_to_list
from futurescan import get_full_url
from futurescan import FutureScanStats
from futurescan import FutureScanOutput
from futurescan import Torify


class DummyScan(object):

    def __init__(self, args):
        self.args = args
        self.stats = FutureScanStats()
        self.out = FutureScanOutput(args)
        self._stop = False

    def stop(self):
        self._stop = True


class SynScan(DummyScan):
    pass


class IcmpScan(DummyScan):
    pass


class HttpScan(DummyScan):

    def __init__(self, args):
        super(HttpScan, self).__init__(args)
        self.session = requesocks.session()

        adapters.DEFAULT_RETRIES = self.args.max_retries
        self.tor = None
        if self.args.tor:
            self.out.log("Enabling TOR")
            self.tor = Torify()
            self.session.proxies = {'http': 'socks5://127.0.0.1:9050',
                                    'https': 'socks5://127.0.0.1:9050'}
            if self.args.check_tor:
                # Check TOR
                self.out.log("Checking IP via TOR")
                rip, tip = self.tor.check_ip(verbose=True)
                if tip is None:
                    self.out.log('TOR is not working properly!', logging.ERROR)
                    exit(-1)

        if self.args.cookies is not None:
            if path.exists(self.args.cookies) and path.isfile(self.args.cookies):
                self.cookies = MozillaCookieJar(self.args.cookies)
                self.cookies.load()
            else:
                # self.out.log('Could not find cookie file: %s' % self.args.load_cookies, logging.ERROR)
                self.cookies = Cookies.from_request(self.args.cookies)
        else:
            self.cookies = None

        self.ua = UserAgent() if self.args.user_agent is None else self.args.user_agent

    def filter(self, response):
        if response is None:
            return False

        # Filter responses and save responses that are matching ignore, allow rules
        if (self.args.allow is None and self.args.ignore is None) or \
                (self.args.allow is not None and response.status_code in self.args.allow) or \
                (self.args.ignore is not None and response.status_code not in self.args.ignore):
            # TODO: add regex search
            return True

        return False

    def scan_url(self, url):
        # TODO: add options
        r = None
        ex = None
        try:
            r = self.session.get(url)
        except Exception as e:
            ex = e
        finally:
            self.cb_response(url, r, ex)
        return r, ex

    def scan_host(self, host, urls):
        res = []

        for u in urls:
            url = get_full_url(host, u)
            r, ex = self.scan_url(url)
            self.out.logger.write_response(url, r, ex)
            if self.filter(r):
                self.out.write(url, r, ex)
                res.append((url, r, ex))
        return res

    def cb_scan_done(self, future):
        pass

    def cb_response(self, url, reponse, exception):
        pass


class FutureScan(HttpScan):

    def __init__(self, args):
        super(FutureScan, self).__init__(args)
        self.executor = futures.ThreadPoolExecutor(max_workers=args.threads)
        self.hosts = file_to_list(args.hosts, 'Hosts file not found!')
        self.urls = file_to_list(args.urls, 'Urls file not found!')
        self.tor = Torify()

    def signal_handler(self, sig, frame):
        self.out.log('Ctrl+C caught. Stopping...')
        self.stop()

    def run(self):
        self.out.start()
        self.out.log('Starting scan agains %i hosts %i urls' %
                     (len(self.hosts), len(self.urls)))
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGQUIT, self.signal_handler)

        self.stats.total = len(self.hosts)
        self.stats.start()

        future_to_host = {}
        for host in self.hosts:
            future = self.executor.submit(self.scan_host, host, self.urls)
            future.add_done_callback(self.cb_scan_done)
            future_to_host[future] = host

        for future in futures.as_completed(future_to_host):
            host = future_to_host[future]
            try:
                r = future.result()
                # self.out.log('Host %s scanned Result = %s' % (host, r))
                self.stats.done += 1

                if r is None:
                    self.out.log('Error while scanning host %s ' % host)
                    self.stats.errors += 1
            except Exception as exc:
                self.out.log('%r generated an exception: %s' % (host, exc))
                pass

        # Summary
        self.stats.finish()
        self.out.log('\nSummary:\n%s' % self.stats)

        # Wait for logger to stop.
        self.out.logger.stop()
