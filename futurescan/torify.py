#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# TOR dummy class

__author__ = '090h'
__license__ = 'GPL'

from requests import get
import requesocks
import socks
import socket
import logging


class Torify(object):
    def __init__(self):
        self.session = requesocks.session(proxies={
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        })

    def dns_query(self, hostname):
        pass

    def hook_socket(self):
        # Can be socks4/5
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, '127.0.0.1', 9050)
        socket.socket = socks.socksocket

        # Magic!
        def getaddrinfo(*args):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
        socket.getaddrinfo = getaddrinfo
        return socket

    def get_ip(self, use_tor=True):
        url = 'http://ifconfig.me/ip'
        try:
            if use_tor:
                return self.session.get(url).text.strip()
            else:
                return get(url).text.strip()
        except Exception as e:
            logging.warning('Could not get IP. Exception: %s' % str(e))
            return None

    def check_ip(self, verbose=False):
        real_ip = self.get_ip(False)
        if real_ip is None:
            if verbose:
                logging.error("Couldn't get real IP address. Check your internet connection.")
            return None, None
        tor_ip = self.get_ip()

        if verbose:
            if tor_ip is None:
                logging.error("TOR socks proxy doesn't seem to be working.")
            elif real_ip == tor_ip:
                logging.error("TOR doesn't work! Stop to be secure.")
            else:
                logging.info('Real IP: %s TOR IP: %s' % (real_ip, tor_ip))
        return real_ip, tor_ip

    @staticmethod
    def scan(host, ports, timeout=0.5):
        if ports is None:
            return None
        opened = []
        for port in ports:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9050, True)
            socket.socket = socks.socksocket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            result = sock.connect_ex((host, port))
            if result == 0:
                opened.append(port)
            sock.close()
        return opened


def get_tor_session():
    return requesocks.session(proxies={
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'})
