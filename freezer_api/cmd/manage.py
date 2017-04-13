"""
(c) Copyright 2015-2016 Hewlett-Packard Enterprise Development Company, L.P.

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

import json
import sys

import elasticsearch
from oslo_config import cfg
from oslo_log import log

from freezer_api import __version__ as FREEZER_API_VERSION
from freezer_api.common import config
from freezer_api.common import db_mappings
from freezer_api.storage import driver

CONF = cfg.CONF
LOG = log.getLogger(__name__)

DEFAULT_INDEX = 'freezer'
DEFAULT_REPLICAS = 0


def add_db_opts(subparser):
    parser = subparser.add_parser('db')
    parser.add_argument(
        'options',
        choices=['sync', 'update', 'remove', 'show', 'update-settings'],
        help='Create/update/delete freezer-api mappings in elk'
    )


def parse_config(mapping_choices):
    DB_INIT = [
        cfg.SubCommandOpt('db',
                          dest='db',
                          title='DB Options',
                          handler=add_db_opts
                          ),
        cfg.ListOpt('hosts',
                    default=['http://127.0.0.1:9200'],
                    help='specify the storage hosts'),
        cfg.StrOpt('mapping',
                   dest='select_mapping',
                   default='',
                   short='m',
                   help='Specific mapping to upload. Valid choices: {0}'
                   .format(','.join(mapping_choices))),
        cfg.StrOpt('index',
                   dest='index',
                   short='i',
                   default=DEFAULT_INDEX,
                   help='The DB index (default "{0}")'.format(DEFAULT_INDEX)
                   ),
        cfg.BoolOpt('yes',
                    short='y',
                    dest='yes',
                    default=False,
                    help='Automatic confirmation to update mappings and '
                         'number-of-replicas.'),
        cfg.BoolOpt('erase',
                    short='e',
                    dest='erase',
                    default=False,
                    help='Enable index deletion in case mapping update fails '
                         'due to incompatible changes'
                    ),
        cfg.StrOpt('test-only',
                   short='t',
                   dest='test_only',
                   default=False,
                   help='Test the validity of the mappings, but take no action'
                   )

    ]
    driver.register_storage_opts()
    CONF.register_cli_opts(DB_INIT)
    log.register_options(CONF)
    default_config_files = cfg.find_config_files('freezer', 'freezer-api')
    CONF(args=sys.argv[1:],
         project='freezer-api',
         default_config_files=default_config_files,
         version=FREEZER_API_VERSION
         )


class ElasticSearchManager(object):
    """
    Managing ElasticSearch mappings operations
    Sync: create mappings
    Update: Update mappings
    remove: deletes the mappings
    show: print out all the mappings
    """

    def __init__(self, mappings):
        self.mappings = mappings.copy()

        grp = cfg.OptGroup(CONF.storage.backend)
        CONF.register_group(grp)
        backend_opts = driver._get_elastic_opts(backend=CONF.storage.backend)

        CONF.register_opts(backend_opts[CONF.storage.backend],
                           group=CONF.storage.backend)

        self.conf = CONF.get(CONF.storage.backend)
        self.index = self.conf.index or DEFAULT_INDEX
        # initialize elk
        opts = dict(self.conf.items())
        self.elk = elasticsearch.Elasticsearch(**opts)
        # check if the cluster is up or not !
        if not self.elk.ping():
            raise Exception('ElasticSearch cluster is not available. '
                            'Cannot ping it')
        # clear the index cache
        try:
            self.elk.indices.clear_cache(index=self.index)
        except Exception as e:
            LOG.warning(e)

    def _check_index_exists(self, index):
        LOG.info('check if index: {0} exists or not'.format(index))
        try:
            return self.elk.indices.exists(index=index)
        except elasticsearch.TransportError:
            raise

    def _check_mapping_exists(self, mappings):
        LOG.info('check if mappings: {0} exists or not'.format(mappings))
        return self.elk.indices.exists_type(index=self.index,
                                            doc_type=mappings)

    def get_required_mappings(self):
        """
        This function checks if the user chooses a certain mappings or not.
        If the user has chosen a certain mappings it will return these mappings
        only If not it will return all mappings to be updated
        :return:
        """
        # check if the user asked to update only one mapping ( -m is provided )
        mappings = {}
        if CONF.select_mapping:
            if CONF.select_mapping not in self.mappings.keys():
                raise Exception(
                    'Selected mappings {0} does not exists. Please, choose '
                    'one of {1}'.format(CONF.select_mapping,
                                        self.mappings.keys()
                                        )
                )
            mappings[CONF.select_mapping] = \
                self.mappings.get(CONF.select_mapping)
        else:
            mappings = self.mappings
        return mappings

    def db_sync(self):
        """
        Create or update elasticsearch db mappings
        steps:
        1) check if mappings exists
        2) remove mapping if erase is passed
        3) update mappings if - y is passed
        4) if update failed ask for permission to remove old mappings
        5) try to update again
        6) if update succeeded exit :)
        :return:
        """
        # check if erase provided remove mappings first
        if CONF.erase:
            self.remove_mappings()

        # check if index does not exists create it
        if not self._check_index_exists(self.index):
            self._create_index()

        _mappings = self.get_required_mappings()
        # create/update one by one
        for doc_type, body in _mappings.items():
            check = self.create_one_mapping(doc_type, body)
            if check:
                print("Creating or Updating {0} is {1}".format(
                    doc_type, check.get('acknowledged')))
            else:
                print("Couldn't update {0}. Request returned {1}".format(
                    doc_type, check.get('acknowledged')))

    def _create_index(self):
        """
        Create the index that will allow us to put the mappings under it
        :return: {u'acknowledged': True} if success or None if index exists
        """
        if not self._check_index_exists(index=self.index):
            body = {
                'number_of_replicas':
                    self.conf.number_of_replicas or DEFAULT_REPLICAS
            }
            return self.elk.indices.create(index=self.index, body=body)

    def delete_index(self):
        return self.elk.indices.delete(index=self.index)

    def create_one_mapping(self, doc_type, body):
        """
        Create one document type and update its mappings
        :param doc_type: the document type to be created jobs, clients, backups
        :param body: the structure of the document
        :return: dict
        """
        # check if doc_type exists or not
        if self._check_mapping_exists(doc_type):
            do_update = self.prompt(
                '[[[ {0} ]]] already exists in index => {1}'
                ' <= Do you want to update it ? (y/n) '.format(doc_type,
                                                               self.index)
            )
            if do_update:
                # Call elasticsearch library and put the mappings
                return self.elk.indices.put_mapping(doc_type=doc_type,
                                                    body=body,
                                                    index=self.index
                                                    )
            else:
                return {'acknowledged': False}
        return self.elk.indices.put_mapping(doc_type=doc_type, body=body,
                                            index=self.index)

    def remove_one_mapping(self, doc_type):
        """
        Removes one mapping at a time
        :param doc_type: document type to be removed
        :return: dict
        """
        LOG.info('Removing mapping {0} from index {1}'.format(doc_type,
                                                              self.index))
        try:
            return self.elk.indices.delete_mapping(self.index,
                                                   doc_type=doc_type)
        except Exception:
            raise

    def remove_mappings(self):
        """
        Remove mappings from elasticsearch
        :return: dict
        """
        # check if index doesn't exist return
        if not self._check_index_exists(index=self.index):
            print("Index {0} doesn't exists.".format(self.index))
            return
        # remove mappings
        _mappings = self.get_required_mappings()
        for doc_type, body in _mappings.items():
            check = self.remove_one_mapping(doc_type)
            if not check:
                print("Deleting {0} is failed".format(doc_type))
            elif check:
                print("Deleting {0} is {1}".format(
                    doc_type, check.get('acknowledged')))
            else:
                print("Couldn't delete {0}. Request returned {1}".format(
                    doc_type, check.get('acknowledged')))
        del_index = self.prompt('Do you want to remove index as well ? (y/n) ')
        if del_index:
            self.delete_index()

    def update_mappings(self):
        """
        Update mappings
        :return: dict
        """
        CONF.yes = True
        return self.db_sync()

    def show_mappings(self):
        """
        Print existing mappings in an index
        :return: dict
        """
        # check if index doesn't exist return
        if not self._check_index_exists(index=self.index):
            print("Index {0} doesn't exists.".format(self.index))
            return
        print(json.dumps(self.elk.indices.get_mapping(index=self.index)))

    def update_settings(self):
        """
        Update number of replicas
        :return: dict
        """
        body = {
            'number_of_replicas':
                self.conf.number_of_replicas or DEFAULT_REPLICAS
        }
        return self.elk.indices.put_settings(body=body, index=self.index)

    def prompt(self, message):
        """
        Helper function that is being used to ask the user for confirmation
        :param message: Message to be printed (To ask the user to confirm ...)
        :return: True or False
        """
        if CONF.yes:
            return CONF.yes
        while True:
            ans = raw_input(message)
            if ans.lower() == 'y':
                return True
            elif ans.lower() == 'n':
                return False


def main():
    mappings = db_mappings.get_mappings()
    parse_config(mapping_choices=mappings.keys())
    config.setup_logging()

    if not CONF.db:
        CONF.print_help()
        sys.exit(0)

    try:
        elk = ElasticSearchManager(mappings=mappings)
        if CONF.db.options.lower() == 'sync':
            elk.db_sync()
        elif CONF.db.options.lower() == 'update':
            elk.update_mappings()
        elif CONF.db.options.lower() == 'remove':
            elk.remove_mappings()
        elif CONF.db.options.lower() == 'show':
            elk.show_mappings()
        elif CONF.db.options.lower() == 'update-settings':
            elk.update_settings()
        else:
            raise Exception('Option {0} not found !'.format(CONF.db.options))
    except Exception as e:
        LOG.error(e)
        print(e)


if __name__ == '__main__':
    sys.exit(main())
