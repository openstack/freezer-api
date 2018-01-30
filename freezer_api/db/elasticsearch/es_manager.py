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


import elasticsearch
from oslo_config import cfg
from oslo_log import log
import six

from freezer_api.common import db_mappings


CONF = cfg.CONF
LOG = log.getLogger(__name__)

DEFAULT_INDEX = 'freezer'
DEFAULT_REPLICAS = 0


class ElasticSearchManager(object):
    """
    Managing ElasticSearch mappings operations
    Sync: create mappings
    Update: Update mappings
    remove: deletes the mappings
    show: print out all the mappings
    """

    def __init__(self, **options):
        self.mappings = db_mappings.get_mappings().copy()
        self.conf = options.copy()
        self.index = self.conf['index']

        self.elk = elasticsearch.Elasticsearch(**options)
        # check if the cluster is up or not !
        if not self.elk.ping():
            raise Exception('ElasticSearch cluster is not available. '
                            'Cannot ping it')
        # clear the index cache
        try:
            self.elk.indices.clear_cache(index=self.conf['index'])
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
        if self.conf['select_mapping']:
            if self.conf['select_mapping'] not in self.mappings.keys():
                raise Exception(
                    'Selected mappings {0} does not exists. Please, choose '
                    'one of {1}'.format(self.conf['select_mapping'],
                                        self.mappings.keys()
                                        )
                )
            mappings[self.conf['select_mapping']] = \
                self.mappings.get(self.conf['select_mapping'])
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
        if self.conf.get('erase'):
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
                    self.conf['number_of_replicas'] or DEFAULT_REPLICAS
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
        self.delete_index()

    def update_mappings(self):
        """
        Update mappings
        :return: dict
        """
        self.conf['yes'] = True
        return self.db_sync()

    def show_mappings(self):
        """
        Print existing mappings in an index
        :return: dict
        """
        # check if index doesn't exist return
        if not self._check_index_exists(index=self.index):
            LOG.debug("Index {0} doesn't exists.".format(self.index))
            return
        return self.elk.indices.get_mapping(index=self.index)

    def update_settings(self):
        """
        Update number of replicas
        :return: dict
        """
        body = {
            'number_of_replicas':
                self.conf['number_of_replicas'] or DEFAULT_REPLICAS
        }
        return self.elk.indices.put_settings(body=body, index=self.index)

    def prompt(self, message):
        """
        Helper function that is being used to ask the user for confirmation
        :param message: Message to be printed (To ask the user to confirm ...)
        :return: True or False
        """
        if self.conf['yes']:
            return self.conf['yes']
        while True:
            ans = six.input(message)
            if ans.lower() == 'y':
                return True
            elif ans.lower() == 'n':
                return False
