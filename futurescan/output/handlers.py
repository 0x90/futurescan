#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#

__author__ = '090h'
__license__ = 'GPL'

import io
from json import dumps
from os import makedirs
from os import path
from urlparse import urlparse
from csv import writer, QUOTE_ALL

# External dependencies
from sqlalchemy_utils.functions import create_database, database_exists
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from colorama import Fore, init
from humanize import naturalsize
from futurescan.helper import str_now


class GeneralOutputHanlder(object):

    def __init__(self, args):
        self.args = args

    @staticmethod
    def _kwargs_to_params(**kwargs):
        return {'url': kwargs['url'], 'status': kwargs['status'], 'length': kwargs['length'],
                'headers': str(kwargs['response'].headers)}

    def _output_to_kwargs(self, url, response, exception):
        res = {'url': url,
               'response': response,
               'exception': exception}

        if response is None or exception is not None:
            res.update({
                'status': -1,
                'length': -1,
            })
            return res

        try:
            length = int(response.headers['content-length']) if 'content-length' in response.headers else len(
                response.text)
        except Exception as exception:
            # self.write_log(
            #     "Exception while getting content length for URL: %s Exception: %s" % (url, str(exception)),
            #     logging.ERROR)
            length = 0

        res.update({
            'status': response.status_code,
            'length': length,
        })
        return res


class JsonOutputHandler(GeneralOutputHanlder):

    def __init__(self, args):
        super(JsonOutputHandler, self).__init__(args)
        # self.json = None if self.args.output_json is None else \
        self.json = io.open(self.args.output_json, 'w', encoding='utf-8')

    def write(self, **kwargs):
        # if self.json is None:
        #     return
        # TODO: bugfix appending json
        self.json.write(unicode(dumps(self._kwargs_to_params(**kwargs), ensure_ascii=False)))


class DBOutputHandler(GeneralOutputHanlder):

    def __init__(self, args):
        super(DBOutputHandler, self).__init__(args)
        # if self.args.output_database is None:
        #     self.engine = None
        #     return

        if not database_exists(self.args.output_database):
            create_database(self.args.output_database, encoding='utf8')

        self.engine = create_engine(self.args.output_database)
        self.metadata = MetaData()
        self.scan_table = Table('httpscan', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('url', String),
                                Column('status', Integer),
                                Column('length', Integer),
                                Column('headers', String)
                                )
        self.metadata.create_all(self.engine)

    def write(self, **kwargs):
        # if self.engine is None:
        #     return

        # TODO: check if url exists in table
        params = self._kwargs_to_params(**kwargs)
        self.engine.execute(self.scan_table.insert().execution_options(autocommit=True), params)


class CSVOutputHandler(GeneralOutputHanlder):

    def __init__(self, args):
        """
            Initialise CSV output
            :return:
            """
        super(CSVOutputHandler, self).__init__(args)
        # if args.output_csv is None:
        #     self.csv = None
        # else:
        # TODO: check if file exists
        self.csv = writer(open(args.output_csv, 'wb'), delimiter=';', quoting=QUOTE_ALL)
        self.csv.writerow(['url', 'status', 'length', 'headers'])

    def write(self, **kwargs):
        if self.csv is not None:
            self.csv.writerow([kwargs['url'], kwargs['status'], kwargs['length'], str(kwargs['response'].headers)])


class DumpOutputHandler(GeneralOutputHanlder):

    def __init__(self, args):
        super(DumpOutputHandler, self).__init__(args)
        self.dump = path.abspath(self.args.dump)    # if self.args.dump is not None else None
        if not path.exists(self.dump):
            makedirs(self.dump)

    def write(self, **kwargs):
        if kwargs['response'] is None or self.dump is None:
            return

        # Generate folder and file path
        parsed = urlparse(kwargs['url'])
        host_folder = path.join(self.dump, parsed.netloc)
        p, f = path.split(parsed.path)
        folder = path.join(host_folder, p[1:])
        if not path.exists(folder):
            makedirs(folder)
        filename = path.join(folder, f)

        # Get all content
        try:
            content = kwargs['response'].content
        except Exception as exception:
            self.out.log('Failed to get content for %s Exception: %s' % (kwargs['url'], str(exception)))
            return

        # Save contents to file
        with open(filename, 'wb') as f:
            f.write(content)


class StatusOutputHandler(GeneralOutputHanlder):

    def __init__(self, args):
        super(StatusOutputHandler, self).__init__(args)
        init()

    def write(self, **kwargs):
        # TODO: add detailed stats
        # Calculate progreess
        # percentage = '{percent:.2%}'.format(percent=float(self.urls_scanned) / self.args.urls_count)
        percentage = '{percent:.2%}'.format(percent=0.2)

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


def get_output_handlers(args):
    handlers = []
    if args.output_sql:
        handlers.append(DBOutputHandler)

    if args.output_dump:
        handlers.append(DumpOutputHandler)

    if args.output_json:
        handlers.append(JsonOutputHandler(args))

    if args.output_csv:
        handlers.append(CSVOutputHandler(args))

    return handlers