#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from futurescan.scan import FutureScan


def main():
    parser = ArgumentParser('httpscan', description='Multithreaded HTTP scanner',
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            fromfile_prefix_chars='@')

    # Main options
    parser.add_argument('hosts', help='hosts file')
    parser.add_argument('urls', help='urls file')

    # Scan options
    group = parser.add_argument_group('HTTP scan options')
    group.add_argument('-t', '--timeout', type=int, default=5, help='response timeout')
    group.add_argument('-T', '--threads', type=int, default=5, help='threads count')
    group.add_argument('-d', '--daemon', action='store_true', help='daemonize scan')
    group.add_argument('-mR', '--max-retries', type=int, default=3, help='Max retries for the request')
    group.add_argument('-mE', '--max-errors', type=int, default=5, help='max errors count per host')

    # HTTP options
    group = parser.add_argument_group('HTTP options')
    group.add_argument('-M', '--method', default='GET', help='HTTP method to use')
    group.add_argument('-H', '--use-head', action='store_true', help='use HEAD requests if possible for fast scan')
    group.add_argument('-A', '--auth', help='HTTP Auth user:password')
    group.add_argument('-C', '--cookies', help='cookies to send during scan (files also allowed)')
    group.add_argument('-U', '--user-agent', help='User-Agent to use (random by default)')
    group.add_argument('-F', '--follow-redirects', action='store_true', help='follow redirects')
    group.add_argument('-r', '--referer', help='referer URL')
    group.add_argument('-R', '--request', help='load request from file (POST/PUT/etc..)')

    # Proxy options
    group = parser.add_argument_group('Proxy options')
    group.add_argument('-p', '--proxy', help='HTTP/SOCKS proxy to use (http://user:pass@127.0.0.1:8080)')
    group.add_argument('--tor', action='store_true', help='Use TOR as SOCKS proxy')
    group.add_argument('--check-tor', action='store_true', help='Check IP via TOR')

    # Advnaced options
    group = parser.add_argument_group('Advanced scan options')
    group.add_argument('-I', '--icmp', action='store_true', help='use ICMP scan  host')
    group.add_argument('-S', '--syn', action='store_true', help='use SYN scan host')
    group.add_argument('-P', '--ports', nargs='+', type=int, help='ports to scan')
    group.add_argument('-e', '--eval', help='eval python expression with found url (DANGEROUS)')
    group.add_argument('-E', '--exec', help='execute cmd with found url (DANGEROUS)')

    # Filter/search options
    group = parser.add_argument_group('Filter/search options')
    group.add_argument('-a', '--allow', required=False, nargs='+', type=int,
                       help='allow following HTTP response status(es)')
    group.add_argument('-i', '--ignore', required=False, nargs='+', type=int,
                       help='ignore following HTTP response status(es)')
    group.add_argument('-f', '--find', help='try to find text in response')

    # Output options
    group = parser.add_argument_group('Output options')
    group.add_argument('-oD', '--output-dump', help='save found files to dump directory')
    group.add_argument('-oC', '--output-csv', help='output results to CSV file')
    group.add_argument('-oJ', '--output-json', help='output results to JSON file')
    group.add_argument('-oM', '--output-mongo', help='output results to MongoDB')
    group.add_argument('-oS', '--output-sql',
                       help='output results to database via SQLAlchemy (postgres://user@localhost/db)')

    # Debug and logging options
    group = parser.add_argument_group('Debug and logging options')
    group.add_argument('-l', '--log', help='debug log path')
    group.add_argument('-L', '--elk', help='write to ELK stack')
    group.add_argument('-D', '--debug', help='write program debug output to file')

    # Parse args and run scanner
    args = parser.parse_args()
    fs = FutureScan(args)
    fs.run()

if __name__ == '__main__':
    main()