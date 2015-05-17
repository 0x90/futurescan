#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'

from urlparse import urlsplit
import socket
import logging
from sys import exit
from os import path
from dns import resolver
from requests_oauthlib import OAuth1
from datetime import datetime
from threading import Thread
from Queue import Queue


class DummyThreadQueue(Thread):

    def __init__(self, args):
        super(DummyThreadQueue, self).__init__()
        self.args = args
        self._stop = False
        self.daemon = True
        self.queue = Queue()

    # def run(self):
    #     self.logger.start()
    #     self.stats.start()
    #
    #     while not self._stop:
    #         u, r, e = self.queue.get()
    #         self.logger.write('%s\t%s\t%s' % (u, r.status_code, e))

    def stop(self):
        self._stop = True

# class DummyScanThread(DummyThreadQueue):
#
#     def __init__(self):
#         self.stats


def file_to_list(filename, dedup=True, strict=True, error_msg=None):

    if not path.exists(filename) or not path.isfile(filename):
        if error_msg is not None:
            logging.error(error_msg)
        if strict:
            exit(-1)
        return None

    # Preparing lines list
    lines = filter(lambda line: line is not None and len(line) > 0, open(filename).read().split('\n'))
    return deduplicate(lines) if dedup else lines


def str_now(fmt='%d.%m.%Y %H:%M:%S'):
    """
    Current datetime to string
    :param fmt: format string for output
    :return: string for current datetime
    """
    return datetime.now().strftime(fmt)


def deduplicate(seq):
    """
    Deduplicate list
    :param seq: list to deduplicate
    :return: deduplicated list
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def host_to_url(host):
    # TODO: rewrite this dummy shit
    if host.lower().startswith('http'):
        return host

    for p in [443, 8443]:
        if ':%i' % p in host:
            return 'https://%s' % host

    return 'http://%s' % host


def hosts_to_domain_dict(hosts):
    domains = [url_to_domain(host) for host in hosts]
    return dict(map(lambda d: (domain_to_ip(d), d), domains))


def hosts_to_port_dict(hosts):
    ports_dict = {}
    for host, port in [parse_url(host) for host in hosts]:
        if port in ports_dict:
            ports_dict[port].append(url_to_ip(host))
        else:
            ports_dict[port] = [url_to_ip(host)]

    return ports_dict


def parse_url(url):
    parsed = urlsplit(url)
    return parsed[1].split(':')[0] if '://' in url else url, parsed.port


def url_to_ip(url):
    return domain_to_ip(url_to_domain(url))


def generate_url(host, port):
    # TODO: rewrite this dummy shit
    domain = url_to_domain(host) if '://' in host else host
    prefix = 'https://' if port in [443, 8443] else 'http://'
    return '%s%s:%i' % (prefix, domain, port)


def url_to_domain(url):
    return urlsplit(url)[1].split(':')[0] if '://' in url else url


def domain_to_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None


def domain_to_ip_list(domain):
    return [rdata for rdata in resolver.query(domain, 'A')]


def get_full_url(host, url):
        furl = ''
        if not host.lower().startswith('http'):
            if ':' in host:
                items = host.split(':')
                hostname, port = items[0], int(items[1])
                if port in [443, 8443]:
                    furl = 'https://' + host
            else:
                furl = 'http://' + host
        else:
            furl = host

        if host.endswith('/') or url.startswith('/'):
            return furl + url
        else:
            return furl + '/' + url

def get_oauth():
    oauth = OAuth1("xxxxxx",
                client_secret="zzzxxxx",
                resource_owner_key="xxxxxxxxxxxxxxxxxx",
                resource_owner_secret="xxxxxxxxxxxxxxxxxxxx")
    return oauth

if __name__ == '__main__':
    pass