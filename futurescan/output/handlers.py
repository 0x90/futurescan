#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


class OutputHanlder(object):

    def __init__(self, args):
        self.args = args

    @staticmethod
    def _kwargs_to_params(**kwargs):
        return {'url': kwargs['url'],
                'status': kwargs['status'],
                'length': kwargs['length'],
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
            # self.out.log(
            #     "Exception while getting content length for URL: %s Exception: %s" % (url, str(exception)),
            #     logging.ERROR)
            length = 0

        res.update({
            'status': response.status_code,
            'length': length,
        })
        return res


class JsonHandler(OutputHanlder):

    def __init__(self, args):
        super(JsonHandler, self).__init__(args)
        self.json = io.open(self.args.output_json, 'w', encoding='utf-8')

    def write(self, **kwargs):
        # TODO: bugfix appending json
        self.json.write(unicode(dumps(self._kwargs_to_params(**kwargs), ensure_ascii=False)))


class DbHandler(OutputHanlder):

    def __init__(self, args):
        super(DbHandler, self).__init__(args)
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
        # TODO: check if url exists in table
        params = self._kwargs_to_params(**kwargs)
        self.engine.execute(self.scan_table.insert().execution_options(autocommit=True), params)


class CsvHandler(OutputHanlder):

    def __init__(self, args):
        super(CsvHandler, self).__init__(args)
        # TODO: check if file exists
        self.csv = writer(open(args.output_csv, 'wb'), delimiter=';', quoting=QUOTE_ALL)
        self.csv.writerow(['url', 'status', 'length', 'headers'])

    def write(self, **kwargs):
        self.csv.writerow([kwargs['url'], kwargs['status'], kwargs['length'], str(kwargs['response'].headers)])


class DumpHandler(OutputHanlder):

    def __init__(self, args):
        super(DumpHandler, self).__init__(args)
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
            # self.out.log('Failed to get content for %s Exception: %s' % (kwargs['url'], str(exception)))
            return

        # Save contents to file
        with open(filename, 'wb') as f:
            f.write(content)


def get_output_handlers(args):
    handlers = []
    if args.output_sql:
        handlers.append(DbHandler)

    if args.output_dump:
        handlers.append(DumpHandler)

    if args.output_json:
        handlers.append(JsonHandler(args))

    if args.output_csv:
        handlers.append(CsvHandler(args))

    return handlers