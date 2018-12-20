# -*- encoding: utf-8 -*-
# (c) Copyright 2018 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest

import elasticsearch
import mock
from mock import patch

from freezer_api.common import exceptions
from freezer_api.storage import elasticv2 as elastic
from freezer_api.tests.unit import common


class TypeManagerV2(unittest.TestCase):
    def setUp(self):
        self.mock_es = mock.Mock()
        self.type_manager = elastic.TypeManagerV2(self.mock_es,
                                                  'base_doc_type',
                                                  'freezer')

    def test_get_base_search_filter(self):
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        q = self.type_manager.get_base_search_filter(project_id='tecs',
                                                     user_id='my_user_id',
                                                     search=my_search)
        expected_q = [
            {
                'term': {
                    'project_id': 'tecs'
                }
            },
            {
                'term': {
                    'user_id': 'my_user_id'
                }
            },
            {
                'query': {
                    'bool': {
                        'must_not': [],
                        'must': [
                            {
                                'match': {
                                    'some_field': 'some text'
                                }
                            },
                            {
                                'match': {
                                    'description': 'some other text'
                                }
                            }
                        ]
                    }
                }
            }
        ]
        self.assertEqual(expected_q, q)

    def test_get_ok(self):
        self.mock_es.get.return_value = common.fake_job_0_elasticsearch_found
        res = self.type_manager.get(project_id='tecs',
                                    user_id=common.fake_job_0_user_id,
                                    doc_id=common.fake_job_0_job_id)
        self.assertEqual(common.fake_job_0, res)

    def test_get_raise_DocumentNotFound_when_doc_not_found(self):
        self.mock_es.get.side_effect = elasticsearch.TransportError(
            'regular test failure')
        self.assertRaises(exceptions.DocumentNotFound, self.type_manager.get,
                          project_id='tecs',
                          user_id=common.fake_job_0_user_id,
                          doc_id=common.fake_job_0_job_id)

    def test_get_raise_StorageEngineError_when_db_raises(self):
        self.mock_es.get.side_effect = Exception('regular test failure')
        self.assertRaises(exceptions.StorageEngineError, self.type_manager.get,
                          project_id='tecs',
                          user_id=common.fake_job_0_user_id,
                          doc_id=common.fake_job_0_job_id)

    def test_get_raises_AccessForbidden_when_user_id_not_match(self):
        self.mock_es.get.return_value = common.fake_job_0_elasticsearch_found
        self.assertRaises(exceptions.AccessForbidden, self.type_manager.get,
                          project_id='tecs',
                          user_id='obluraschi',
                          doc_id=common.fake_job_0_job_id)

    def test_search_ok(self):
        self.mock_es.search.return_value = common.fake_data_0_elasticsearch_hit
        expected_q = {
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            'must': [
                                {
                                    'term': {
                                        'project_id': 'tecs'
                                    }
                                },
                                {
                                    'term': {
                                        'user_id': 'my_user_id'
                                    }
                                },
                                {
                                    'query': {
                                        'bool': {
                                            'must_not': [],
                                            'must': [
                                                {
                                                    'match': {
                                                        'some_field':
                                                            'some text'
                                                    }
                                                },
                                                {
                                                    'match': {
                                                        'description':
                                                            'some other text'
                                                    }
                                                }]}}}
                            ]}}}}}
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.type_manager.search(project_id='tecs',
                                       user_id='my_user_id',
                                       doc_id='mydocid',
                                       search=my_search, offset=7, limit=19)
        self.mock_es.search.assert_called_with(index='freezer',
                                               doc_type='base_doc_type',
                                               size=19, from_=7,
                                               body=expected_q)
        self.assertEqual([common.fake_data_0_backup_metadata], res)

    def test_search_raise_StorageEngineError_when_search_raises(self):
        self.mock_es.search.side_effect = Exception('regular test failure')
        self.assertRaises(exceptions.StorageEngineError,
                          self.type_manager.search, project_id='tecs',
                          user_id='my_user_id', doc_id='mydocid')

    def test_insert_ok(self):
        self.mock_es.index.return_value = {'created': True, '_version': 15}
        test_doc = {'test_key_412': 'test_value_412', '_version': 5}
        res = self.type_manager.insert(doc=test_doc)
        self.assertEqual((True, 15), res)
        self.mock_es.index.assert_called_with(index='freezer',
                                              doc_type='base_doc_type',
                                              body=test_doc, id=None)

    def test_insert_raise_StorageEngineError_on_ES_Exception(self):
        self.mock_es.index.side_effect = Exception('regular test failure')
        test_doc = {'test_key_412': 'test_value_412', '_version': 5}
        self.assertRaises(exceptions.StorageEngineError,
                          self.type_manager.insert, doc=test_doc)
        self.mock_es.index.assert_called_with(index='freezer',
                                              doc_type='base_doc_type',
                                              body=test_doc, id=None)

    def test_insert_raise_StorageEngineError_on_ES_TransportError_exception(
            self):
        self.mock_es.index.side_effect = elasticsearch.TransportError(
            500, 'regular test failure'
        )
        test_doc = {'test_key_412': 'test_value_412', '_version': 5}
        self.assertRaises(exceptions.StorageEngineError,
                          self.type_manager.insert, doc=test_doc)
        self.mock_es.index.assert_called_with(index='freezer',
                                              doc_type='base_doc_type',
                                              body=test_doc, id=None)

    def test_insert_raise_DocumentExists_on_ES_TransportError409_exception(
            self):
        self.mock_es.index.side_effect = elasticsearch.TransportError(
            409, 'regular test failure'
        )
        test_doc = {'test_key_412': 'test_value_412', '_version': 5}
        self.assertRaises(exceptions.DocumentExists, self.type_manager.insert,
                          doc=test_doc)
        self.mock_es.index.assert_called_with(index='freezer',
                                              doc_type='base_doc_type',
                                              body=test_doc, id=None)

    @patch('freezer_api.storage.elasticv2.elasticsearch.Elasticsearch')
    def test_delete_raises_StorageEngineError_on_scan_exception(
            self, mock_elasticsearch):
        doc_id = 'mydocid345'
        mock_elasticsearch.search.side_effect = Exception(
            'regular test failure')
        self.assertRaises(exceptions.StorageEngineError,
                          self.type_manager.delete, project_id='tecs',
                          user_id='my_user_id', doc_id=doc_id)

    @patch('freezer_api.storage.elasticv2.elasticsearch.Elasticsearch')
    def test_delete_raises_StorageEngineError_on_delete_exception(
            self, mock_elasticsearch):
        doc_id = 'mydocid345'
        mock_elasticsearch.search.return_value = [
            {'_id': 'cicciopassamilolio'}]
        self.mock_es.delete.side_effect = Exception('regular test failure')
        self.assertRaises(exceptions.StorageEngineError,
                          self.type_manager.delete, project_id='tecs',
                          user_id='my_user_id', doc_id=doc_id)

    def test_delete_return_none_when_nothing_is_deleted(self):
        doc_id = 'mydocid345'
        ret_data = {"hits": {"hits": []}}
        self.mock_es.search.return_value = ret_data
        res = self.type_manager.delete(project_id='tecs',
                                       user_id='my_user_id', doc_id=doc_id)
        self.assertIsNone(res, 'invalid res {0}'.format(res))

    def test_delete_return_correct_id_on_success(self):
        doc_id = 'mydocid345'
        ret_data = {"hits": {"hits": [{
            "_id": "cicciopassamilolio"
        }]}}
        self.mock_es.search.return_value = ret_data
        res = self.type_manager.delete(project_id='tecs',
                                       user_id='my_user_id', doc_id=doc_id)
        self.assertEqual(
            'cicciopassamilolio', res, 'invalid res {0}'.format(res)
        )


class TestBackupManagerV2(unittest.TestCase):
    def setUp(self):
        self.mock_es = mock.Mock()
        self.backup_manager = elastic.BackupTypeManagerV2(self.mock_es,
                                                          'backups')

    def test_get_search_query(self):
        my_search = {'match': [{'backup_name': 'my_backup'}, {'mode': 'fs'}],
                     "time_before": 1428510506,
                     "time_after": 1428510506
                     }
        q = self.backup_manager.get_search_query(project_id='tecs',
                                                 user_id='my_user_id',
                                                 doc_id='my_doc_id',
                                                 search=my_search)
        expected_q = {
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            'must': [
                                {
                                    'term': {
                                        'project_id': 'tecs'
                                    }
                                },
                                {
                                    'term': {
                                        'user_id': 'my_user_id'
                                    }
                                },
                                {
                                    'query': {
                                        'bool': {
                                            'must_not': [],
                                            'must': [
                                                {
                                                    'match': {
                                                        'backup_name':
                                                            'my_backup'
                                                    }
                                                },
                                                {
                                                    'match': {
                                                        'mode': 'fs'
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                },
                                {
                                    'term': {
                                        'backup_id': 'my_doc_id'
                                    }
                                },
                                {
                                    'range': {
                                        'timestamp': {
                                            'gte': 1428510506
                                        }
                                    }
                                },
                                {
                                    'range': {
                                        'timestamp': {
                                            'lte': 1428510506
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        self.assertEqual(expected_q, q)


class ClientTypeManagerV2(unittest.TestCase):
    def setUp(self):
        self.mock_es = mock.Mock()
        self.client_manager = elastic.ClientTypeManagerV2(self.mock_es,
                                                          'clients')

    def test_get_search_query(self):
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        q = self.client_manager.get_search_query(project_id='tecs',
                                                 user_id='my_user_id',
                                                 doc_id='my_doc_id',
                                                 search=my_search)
        expected_q = {
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            'must': [
                                {
                                    'term': {
                                        'project_id': 'tecs'
                                    }
                                },
                                {
                                    'term': {
                                        'user_id': 'my_user_id'
                                    }
                                },
                                {
                                    'query': {
                                        'bool': {
                                            'must_not': [],
                                            'must': [
                                                {
                                                    'match': {
                                                        'some_field':
                                                            'some text'
                                                    }
                                                },
                                                {
                                                    'match': {
                                                        'description':
                                                            'some other text'
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                },
                                {
                                    'term': {
                                        'client.client_id': 'my_doc_id'
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        self.assertEqual(expected_q, q)
