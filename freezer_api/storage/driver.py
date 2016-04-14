"""
(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.

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

import logging
import os

from oslo_config import cfg

from freezer_api.common import _i18n
from freezer_api.storage import elastic

CONF = cfg.CONF


def get_elk_opts():
    storage_opts = [
        cfg.StrOpt('db',
                   default='elasticsearch',
                   help='specify the storage db to use (default: elasticsearch'),
        # use of 'endpoint' parameter name is deprecated, please use 'hosts'
        cfg.StrOpt('endpoint',
                   default='',
                   help='specify the storage hosts (deprecated, use "hosts"'),
        cfg.StrOpt('hosts',
                   default='http://localhost:9200',
                   help='specify the storage hosts'),
        cfg.StrOpt('index',
                   default='freezer',
                   help='specify the name of the elasticsearch index'),
        cfg.IntOpt('timeout',
                   default=60,
                   help='specify the connection timeout'),
        cfg.IntOpt('retries',
                   default=20,
                   help='number of retries to allow before raising and error'),
        cfg.BoolOpt('use_ssl',
                    default=False,
                    help='explicitly turn on SSL'),
        cfg.BoolOpt('verify_certs',
                    default=False,
                    help='turn on SSL certs verification'),
        cfg.StrOpt('ca_certs',
                   default=None,
                   help='path to CA certs on disk'),
        cfg.IntOpt('number_of_replicas',
                   default=2,
                   help='Number of replicas for elk cluster. Default is 2. '
                        'Use 0 for no replicas')
    ]
    return storage_opts


def register_elk_opts():
    opt_group = cfg.OptGroup(name='storage',
                             title='Freezer Storage Engine')
    CONF.register_group(opt_group)
    CONF.register_opts(get_elk_opts(), opt_group)


def get_options():
    if CONF.storage.ca_certs:
        if not os.path.isfile(CONF.storage.ca_certs):
            raise Exception('Elasticsearch configuration error: '
                            'CA_certs file not found ({0})'
                            .format(CONF.storage.ca_certs))

    hosts = CONF.storage.endpoint or CONF.storage.hosts
    if not hosts:
        raise Exception('Elasticsearch configuration error: no host specified')

    opts = dict(CONF.storage)
    opts.pop('endpoint')
    opts['hosts'] = hosts.split(',')
    return opts


def get_db():
    opts = get_options()
    db_engine = opts.pop('db')
    if db_engine == 'elasticsearch':
        logging.debug(_i18n._LI('Elastichsearch config options: %s') % str(opts))
        db = elastic.ElasticSearchEngine(**opts)
    else:
        raise Exception(_i18n._('Database Engine %s not supported') % db_engine)
    return db
