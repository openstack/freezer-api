#!/usr/bin/env python2
"""
Copyright 2015 Hewlett-Packard

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from __future__ import print_function
import argparse
import json
import os
import re
from six.moves import configparser
from six.moves import input
import sys

import requests

from freezer_api.common import db_mappings


DEFAULT_CONF_PATH = '/etc/freezer/freezer-api.conf'
DEFAULT_ES_SERVER_PORT = 9200
DEFAULT_INDEX = 'freezer'
DEFAULT_REPLICAS = 0


class MergeMappingException(Exception):
    pass


class NumberOfReplicasException(Exception):
    pass


class ElasticSearchEngine(object):
    def __init__(self, es_url, es_index, args):
        self.es_url = es_url
        self.es_index = es_index
        self.args = args
        self.exit_code = os.EX_OK

    def verbose_print(self, message, level=1):
        if self.args.verbose >= level:
            print(message)

    def set_number_of_replicas(self, n):
        if self.number_of_replicas_match(n):
            print('Number of replicas matches. '
                  'Current value is {0}'.format(n))
        else:
            self.askput_number_of_replicas(n)

    def number_of_replicas_match(self, n):
        url = '{0}/{1}/_settings'.format(self.es_url,
                                         self.es_index)
        self.verbose_print('GET {0}\n'.format(url))
        r = requests.get(url)
        if r.status_code != requests.codes.OK:
            raise Exception("ERROR {0}: {1}".format(r.status_code, r.text))
        self.verbose_print("response: {0}".format(r))
        settings_dict = r.json()
        current_n = int(settings_dict[self.es_index]['settings']
                        ['index']['number_of_replicas'])
        self.verbose_print("Current replica number: {0}".format(current_n))
        return current_n == int(n)

    def askput_number_of_replicas(self, n):
        if self.args.test_only:
            print("Number of replicas don't match")
            self.exit_code = os.EX_DATAERR
            return
        prompt_message = ('Number of replicas needs to be '
                          'updated to {0}. '
                          'Proceed ? (y/n)'
                          .format(n))
        if not self.proceed(prompt_message, self.args.yes):
            return

        url = '{0}/{1}/_settings'.format(self.es_url, self.es_index)
        body_dict = {"number_of_replicas": int(n)}
        self.verbose_print('PUT {0}\n{1}'.format(url, body_dict))
        r = requests.put(url, data=json.dumps(body_dict))
        self.verbose_print("response: {0}".format(r))
        if r.status_code == requests.codes.OK:
            print("Replica number set to {0}".format(self.args.replicas))
        else:
            raise NumberOfReplicasException('Error setting the replica '
                                            'number, {0}: {1}'
                                            .format(r.status_code, r.text))

    def put_mappings(self, mappings):
        self.check_index_exists()
        for es_type, mapping in mappings.items():
            if self.mapping_match(es_type, mapping):
                print('{0}/{1} MATCHES'.format(self.es_index, es_type))
            else:
                self.askput_mapping(es_type, mapping)
        return self.exit_code

    def check_index_exists(self):
        url = '{0}/{1}'.format(self.es_url, self.es_index)
        r = requests.post(url)
        if r.status_code not in [requests.codes.OK,
                                 requests.codes.BAD_REQUEST]:
            raise Exception('Unable to check/create index {0}. '
                            'ERROR {1}'.format(url, r.status_code))

    def mapping_match(self, es_type, mapping):
        url = '{0}/{1}/_mapping/{2}'.format(self.es_url,
                                            self.es_index,
                                            es_type)
        self.verbose_print("Getting mappings: http GET {0}".format(url))
        r = requests.get(url)
        self.verbose_print("response: {0}".format(r))
        if r.status_code == requests.codes.NOT_FOUND:
            return False
        if r.status_code != requests.codes.OK:
            raise Exception("ERROR {0}: {1}".format(r.status_code, r.text))
        current_mappings = r.json().get(self.es_index, {}).get('mappings', {})
        return mapping == current_mappings.get(es_type, {})

    def askput_mapping(self, es_type, mapping):
        if self.args.test_only:
            print('{0}/{1} DOES NOT MATCH'.format(self.es_index, es_type))
            self.exit_code = os.EX_DATAERR
            return
        prompt_message = ('{0}/{1}/{2} needs to be updated. '
                          'Proceed ? (y/n)'
                          .format(self.es_url,
                                  self.es_index,
                                  es_type))
        if not self.proceed(prompt_message, self.args.yes):
            return

        self.verbose_print('Trying to upload mappings ...')
        try:
            self.put_mapping(es_type, mapping)
        except MergeMappingException as e:
            self.verbose_print('Unable to merge mappings.')
            self.verbose_print(e, 2)
        else:
            print("Mappings updated")
            return

        if self.args.yes and not self.args.erase:
            # explicit consent to update without explicit consent to erase:
            # do not erase type and return error code
            self.exit_code = os.EX_DATAERR
            print('{0}/{1} DOES NOT MATCH. '
                  'Need explicit consent to erase types'
                  .format(self.es_index, es_type))
            return
        prompt_message = ('Type {0}/{1}/{2} needs to be deleted. '
                          'Proceed (y/n) ? '.format(self.es_url,
                                                    self.es_index,
                                                    es_type))
        if not self.proceed(prompt_message, self.args.erase):
            return

        self.verbose_print('Deleting type {0}'.format(es_type))
        self.delete_type(es_type)
        self.verbose_print('Uploading mappings ...')
        self.put_mapping(es_type, mapping)

    def delete_type(self, es_type):
        url = '{0}/{1}/{2}'.format(self.es_url, self.es_index, es_type)
        self.verbose_print("DELETE {0}".format(url))
        r = requests.delete(url)
        self.verbose_print("response: {0}".format(r))
        if r.status_code not in [requests.codes.OK, requests.codes.NOT_FOUND]:
            raise Exception('Type removal error {0}: '
                            '{1}'.format(r.status_code, r.text))

    def put_mapping(self, es_type, mapping):
        url = '{0}/{1}/_mapping/{2}'.format(self.es_url,
                                            self.es_index,
                                            es_type)
        self.verbose_print('PUT {0}'.format(url))
        r = requests.put(url, data=json.dumps(mapping))
        self.verbose_print("response: {0}".format(r))
        if r.status_code == requests.codes.OK:
            print("Type {0} mapping created".format(url))
        else:
            raise MergeMappingException('Type mapping creation error {0}: '
                                        '{1}'.format(r.status_code, r.text))

    def proceed(self, message, assume_yes=False):
        if assume_yes:
            return True
        while True:
            selection = input(message)
            if selection.upper() == 'Y':
                return True
            elif selection.upper() == 'N':
                return False


def get_args(mapping_choices):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'host', action='store', default='', nargs='?',
        help='The DB host address[:port], default "localhost"')
    arg_parser.add_argument(
        '-p', '--port', action='store', type=int,
        help=('The DB server port '
              '(default: {0})'.format(DEFAULT_ES_SERVER_PORT)),
        dest='port', default=0)
    arg_parser.add_argument(
        '-m', '--mapping', action='store',
        help=('Specific mapping to upload. Valid choices: {0}'
              .format(','.join(mapping_choices))),
        choices=mapping_choices,
        dest='select_mapping', default='')
    arg_parser.add_argument(
        '-i', '--index', action='store',
        help='The DB index (default "{0}")'.format(DEFAULT_INDEX),
        dest='index')
    arg_parser.add_argument(
        '-y',  '--yes', action='store_true',
        help="Automatic confirmation to update mappings and "
             "number-of-replicas",
        dest='yes', default=False)
    arg_parser.add_argument(
        '-e',  '--erase', action='store_true',
        help=("Enable index deletion in case mapping update "
              "fails due to incompatible changes"),
        dest='erase', default=False)
    arg_parser.add_argument(
        '-v',  '--verbose', action='count',
        help="Verbose",
        dest='verbose', default=False)
    arg_parser.add_argument(
        '-t',  '--test-only', action='store_true',
        help="Test the validity of the mappings, but take no action",
        dest='test_only', default=False)
    arg_parser.add_argument(
        '-c', '--config-file', action='store',
        help='Config file with the db information',
        dest='config_file', default='')
    arg_parser.add_argument(
        '-r', '--replicas', action='store',
        help='Set the value for the number replicas in the DB index '
             '(default {0} when not specified here nor in config file)'
             .format(DEFAULT_REPLICAS),
        dest='replicas', default=False)
    return arg_parser.parse_args()


def find_config_file():
    cwd_config = os.path.join(os.getcwd(), 'freezer-api.conf')
    for config_file_path in [cwd_config, DEFAULT_CONF_PATH]:
        if os.path.isfile(config_file_path):
            return config_file_path


def parse_config_file(fname):
    """
    Read host URL from config-file

    :param fname: config-file path
    :return: (host, port, db_index, number_of_replicas)
    """
    if not fname:
        return None, 0, None, 0

    host, port, index, number_of_replicas = None, 0, None, 0

    config = configparser.ConfigParser()
    config.read(fname)
    try:
        if config.has_option('storage', 'endpoint'):
            endpoint = config.get('storage', 'endpoint')
        elif config.has_option('storage', 'hosts'):
            endpoint = config.get('storage', 'hosts')
        else:
            endpoint = ''
        match = re.search(r'^http://([^:]+):([\d]+)', endpoint)
        if match:
            host = match.group(1)
            port = int(match.group(2))
    except Exception:
        pass
    try:
        index = config.get('storage', 'index')
    except Exception:
        pass
    try:
        number_of_replicas = int(config.get('storage', 'number_of_replicas'))
    except Exception:
        pass
    return host, port, index, number_of_replicas


def get_db_params(args):
    """
    Extracts the db configuration parameters either from the provided
    command line arguments or searching in the default freezer-api config
    file /etc/freezer/freezer-api.conf

    :param args: argparsed command line arguments
    :return: (elasticsearch_url, elastichsearch_index, number_of_replicas)
    """
    conf_fname = args.config_file or find_config_file()

    if args.verbose:
        print("using config file: {0}".format(conf_fname))

    conf_host, conf_port, conf_db_index, number_of_replicas = \
        parse_config_file(conf_fname)

    # host lookup
    #   1) host arg (before ':')
    #   2) config file provided
    #   3) string 'localhost'
    host = args.host or conf_host or 'localhost'
    host = host.split(':')[0]

    # port lookup
    #   1) port arg
    #   2) host arg (after ':')
    #   3) config file provided
    #   4) DEFAULT_ES_SERVER_PORT
    match_port = None
    match = re.search(r':(\d+)$', args.host)
    if match:
        match_port = match.groups()[0]

    port = args.port or match_port or conf_port or DEFAULT_ES_SERVER_PORT

    elasticsearch_url = 'http://{0}:{1}'.format(host, port)

    # index lookup
    # 1) index args
    # 2) config file
    # 3) string DEFAULT_INDEX
    elasticsearch_index = args.index or conf_db_index or DEFAULT_INDEX

    return elasticsearch_url, elasticsearch_index, number_of_replicas


def main():
    print("Using the freezer-db-init script is deprecated. Please use "
          "freezer-manage instead.")
    mappings = db_mappings.get_mappings()

    args = get_args(mapping_choices=mappings.keys())

    elasticsearch_url, elasticsearch_index, elasticsearch_replicas = \
        get_db_params(args)

    number_of_replicas = int(args.replicas or
                             elasticsearch_replicas or
                             DEFAULT_REPLICAS)

    es_manager = ElasticSearchEngine(es_url=elasticsearch_url,
                                     es_index=elasticsearch_index,
                                     args=args)
    if args.verbose:
        print("  db url: {0}".format(elasticsearch_url))
        print("db index: {0}".format(elasticsearch_index))

    if args.select_mapping:
        mappings = {args.select_mapping: mappings[args.select_mapping]}

    try:
        es_manager.put_mappings(mappings)
        es_manager.set_number_of_replicas(number_of_replicas)
    except Exception as e:
        print("ERROR {0}".format(e))
        return os.EX_DATAERR

    return es_manager.exit_code

if __name__ == '__main__':
    sys.exit(main())
