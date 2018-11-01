# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from oslo_config import cfg
from oslo_log import log

from freezer_api.common import db_mappings
from freezer_api.db import base as db_base
from freezer_api.db.elasticsearch import es_manager
from freezer_api.storage import elastic as db_session_v1
from freezer_api.storage import elasticv2 as db_session_v2

CONF = cfg.CONF
LOG = log.getLogger(__name__)
DEFAULT_INDEX = 'freezer'
DEFAULT_REPLICAS = 0

_BACKEND_MAPPING = {'sqlalchemy': 'freezer_api.db.sqlalchemy.api'}


class ElasticSearchDB(db_base.DBDriver):
    _ES_OPTS = [
        cfg.ListOpt('hosts',
                    default=['http://127.0.0.1:9200'],
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
                   help='path to CA certs on disk'),
        cfg.IntOpt('number_of_replicas',
                   default=0,
                   help='Number of replicas for elk cluster. Default is 0. '
                        'Use 0 for no replicas. This should be set to (number '
                        'of node in the ES cluter -1).'),
        cfg.StrOpt('mapping',
                   dest='select_mapping',
                   default='',
                   help='Specific mapping to upload. Valid choices: {0}'
                   .format(','.join(db_mappings.get_mappings()))),
        cfg.BoolOpt('erase',
                    dest='erase',
                    default=False,
                    help='Enable index deletion in case mapping update fails '
                         'due to incompatible changes'
                    ),
        cfg.StrOpt('test-only',
                   dest='test_only',
                   default=False,
                   help='Test the validity of the mappings, but take no action'
                   )
    ]

    def __init__(self, backend):
        super(ElasticSearchDB, self).__init__(backend)
        grp = cfg.OptGroup(backend)
        CONF.register_group(grp)
        CONF.register_opts(self._ES_OPTS, group=backend)
        # CONF.register_cli_opts(self._ES_CLI_OPTS)

        self.conf = CONF.get(backend)
        self.index = self.conf.index or DEFAULT_INDEX
        self._engine = None
        self._manage_engine = None

    def get_engine(self):
        if not self._engine:
            if CONF.enable_v1_api:
                self._engine = db_session_v1.\
                    ElasticSearchEngine(self.backend)
            else:
                self._engine = db_session_v2.\
                    ElasticSearchEngineV2(self.backend)
        return self._engine

    def get_api(self):
        return self.get_engine()

    def get_manage_engine(self):
        opts = dict(self.conf.items())
        self._manage_engine = es_manager.ElasticSearchManager(**opts)
        return self._manage_engine

    def db_sync(self):
        if not self._manage_engine:
            self._manage_engine = self.get_manage_engine()
        self._manage_engine.update_mappings()

    def db_remove(self):
        if not self._manage_engine:
            self._manage_engine = self.get_manage_engine()
        self._manage_engine.remove_mappings()

    def db_show(self):
        if not self._manage_engine:
            self._manage_engine = self.get_manage_engine()
        return self._manage_engine.show_mappings()

    def name(self):
        return "ElasticSearch"
