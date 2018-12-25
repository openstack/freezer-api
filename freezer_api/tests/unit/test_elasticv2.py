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
from oslo_config import cfg

from freezer_api.common import exceptions
from freezer_api.db.elasticsearch.driver import ElasticSearchDB
from freezer_api.storage import elasticv2 as elastic
from freezer_api.tests.unit import common

CONF = cfg.CONF


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


class JobTypeManagerV2(unittest.TestCase):
    def setUp(self):
        self.mock_es = mock.Mock()
        self.job_manager = elastic.JobTypeManagerV2(self.mock_es, 'clients')

    def test_get_search_query(self):
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        q = self.job_manager.get_search_query(project_id='tecs',
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
                                {'term': {
                                    'job_id': 'my_doc_id'
                                }
                                }
                            ]}}}}}
        self.assertEqual(expected_q, q)

    def test_update_ok(self):
        self.mock_es.update.return_value = {
            u'_id': u'd6c1e00d-b9c1-4eb3-8219-1e83c02af101',
            u'_index': u'freezer',
            u'_type': u'jobs',
            u'_version': 3
        }
        res = self.job_manager.update(job_id=common.fake_job_0_job_id,
                                      job_update_doc={'status': 'sleepy'})
        self.assertEqual(3, res)
        self.mock_es.update.assert_called_with(
            index=self.job_manager.index,
            doc_type=self.job_manager.doc_type,
            id=common.fake_job_0_job_id,
            body={"doc": {'status': 'sleepy'}}
        )

    def test_update_raise_DocumentNotFound_when_not_found(self):
        self.mock_es.update.side_effect = elasticsearch.TransportError(
            'regular test failure', 1)
        self.assertRaises(exceptions.DocumentNotFound, self.job_manager.update,
                          job_id=common.fake_job_0_job_id,
                          job_update_doc={'status': 'sleepy'})

    def test_update_raise_DocumentExists_when_elasticsearch_returns_409(self):
        self.mock_es.update.side_effect = elasticsearch.TransportError(
            409, 'regular test failure'
        )
        self.assertRaises(exceptions.DocumentExists, self.job_manager.update,
                          job_id=common.fake_job_0_job_id,
                          job_update_doc={'status': 'sleepy'})

    def test_update_raise_StorageEngineError_when_db_raises(self):
        self.mock_es.update.side_effect = Exception('regular test failure')
        self.assertRaises(exceptions.StorageEngineError,
                          self.job_manager.update,
                          job_id=common.fake_job_0_job_id,
                          job_update_doc={'status': 'sleepy'})


class ActionTypeManagerV2(unittest.TestCase):
    def setUp(self):
        self.mock_es = mock.Mock()
        self.action_manager = elastic.ActionTypeManagerV2(self.mock_es,
                                                          'actions')

    def test_get_search_query(self):
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        q = self.action_manager.get_search_query(project_id='tecs',
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
                                                            'some text'}
                                                },
                                                {
                                                    'match': {
                                                        'description':
                                                            'some other text'}
                                                }
                                            ]
                                        }
                                    }
                                },
                                {
                                    'term': {
                                        'action_id': 'my_doc_id'
                                    }
                                }
                            ]}}}}}
        self.assertEqual(expected_q, q)

    def test_update_ok(self):
        self.mock_es.update.return_value = {
            u'_id': u'd6c1e00d-b9c1-4eb3-8219-1e83c02af101',
            u'_index': u'freezer',
            u'_type': u'actions',
            u'_version': 3
        }
        res = self.action_manager.update(action_id='poiuuiop7890',
                                         action_update_doc={
                                             'status': 'sleepy'})
        self.assertEqual(3, res)
        self.mock_es.update.assert_called_with(
            index=self.action_manager.index,
            doc_type=self.action_manager.doc_type,
            id='poiuuiop7890',
            body={"doc": {'status': 'sleepy'}}
        )

    def test_update_raise_DocumentNotFound_when_not_found(self):
        self.mock_es.update.side_effect = elasticsearch.TransportError(
            'regular test failure', 1)
        self.assertRaises(exceptions.DocumentNotFound,
                          self.action_manager.update,
                          action_id='asdfsadf',
                          action_update_doc={'status': 'sleepy'})

    def test_update_raise_DocumentExists_when_elasticsearch_returns_409(self):
        self.mock_es.update.side_effect = elasticsearch.TransportError(
            409, 'regular test failure'
        )
        self.assertRaises(exceptions.DocumentExists,
                          self.action_manager.update,
                          action_id='pepepepepe2321',
                          action_update_doc={'status': 'sleepy'})

    def test_update_raise_StorageEngineError_when_db_raises(self):
        self.mock_es.update.side_effect = Exception('regular test failure')
        self.assertRaises(exceptions.StorageEngineError,
                          self.action_manager.update,
                          action_id='pepepepepe2321',
                          action_update_doc={'status': 'sleepy'})


class SessionTypeManagerV2(unittest.TestCase):
    def setUp(self):
        self.mock_es = mock.Mock()
        self.session_manager = elastic.SessionTypeManagerV2(self.mock_es,
                                                            'sessions')

    def test_get_search_query(self):
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        q = self.session_manager.get_search_query(project_id='tecs',
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
                                        'session_id': 'my_doc_id'
                                    }
                                }
                            ]}}}}}
        self.assertEqual(expected_q, q)

    def test_update_ok(self):
        self.mock_es.update.return_value = {
            u'_id': u'd6c1e00d-b9c1-4eb3-8219-1e83c02af101',
            u'_index': u'freezer',
            u'_type': u'actions',
            u'_version': 3
        }
        res = self.session_manager.update(session_id='poiuuiop7890',
                                          session_update_doc={
                                              'status': 'sleepy'})
        self.assertEqual(3, res)
        self.mock_es.update.assert_called_with(
            index=self.session_manager.index,
            doc_type=self.session_manager.doc_type,
            id='poiuuiop7890',
            body={"doc": {'status': 'sleepy'}})

    def test_update_raise_DocumentNotFound_when_not_found(self):
        self.mock_es.update.side_effect = elasticsearch.TransportError(
            'regular test failure', 1)
        self.assertRaises(exceptions.DocumentNotFound,
                          self.session_manager.update,
                          session_id='asdfsadf',
                          session_update_doc={'status': 'sleepy'})

    def test_update_raise_DocumentExists_when_elasticsearch_returns_409(self):
        self.mock_es.update.side_effect = elasticsearch.TransportError(
            409, 'regular test failure'
        )
        self.assertRaises(exceptions.DocumentExists,
                          self.session_manager.update,
                          session_id='pepepepepe2321',
                          session_update_doc={'status': 'sleepy'})

    def test_update_raise_StorageEngineError_when_db_raises(self):
        self.mock_es.update.side_effect = Exception('regular test failure')
        self.assertRaises(exceptions.StorageEngineError,
                          self.session_manager.update,
                          session_id='pepepepepe2321',
                          session_update_doc={'status': 'sleepy'})


class TestElasticSearchEngineV2_backup(unittest.TestCase, ElasticSearchDB):

    @patch('freezer_api.storage.elasticv2.logging')
    @patch('freezer_api.storage.elasticv2.elasticsearch')
    def setUp(self, mock_logging, mock_elasticsearch):
        backend = 'elasticsearch'
        grp = cfg.OptGroup(backend)
        CONF.register_group(grp)
        CONF.register_opts(self._ES_OPTS, group=backend)
        mock_elasticsearch.Elasticsearch.return_value = mock.Mock()
        kwargs = {'hosts': 'http://elasticservaddr:1997'}
        self.eng = elastic.ElasticSearchEngineV2(backend=backend)
        self.eng.init(index='freezer', **kwargs)
        self.eng.backup_manager = mock.Mock()

    def test_get_backup_userid_and_backup_id_return_ok(self):
        self.eng.backup_manager.get.return_value = (
            common.fake_data_0_wrapped_backup_metadata
        )
        res = self.eng.get_backup(project_id='tecs',
                                  user_id=common.fake_data_0_user_id,
                                  backup_id=common.fake_data_0_backup_id)

        self.assertEqual(common.fake_data_0_wrapped_backup_metadata, res)
        self.eng.backup_manager.get.assert_called_with(
            project_id=common.fake_data_0_wrapped_backup_metadata
            ['project_id'],
            user_id=common.fake_data_0_wrapped_backup_metadata['user_id'],
            doc_id=common.fake_data_0_wrapped_backup_metadata['backup_id']
        )

    def test_get_backup_list_with_userid_and_search_return_list(self):
        self.eng.backup_manager.search.return_value = [
            common.fake_data_0_wrapped_backup_metadata,
            common.fake_data_1_wrapped_backup_metadata]
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.eng.search_backup(project_id='tecs',
                                     user_id=common.fake_data_0_user_id,
                                     offset=3, limit=7,
                                     search=my_search)
        self.assertEqual(
            [
                common.fake_data_0_wrapped_backup_metadata,
                common.fake_data_1_wrapped_backup_metadata
            ], res
        )
        self.eng.backup_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_data_0_wrapped_backup_metadata['user_id'],
            search=my_search,
            limit=7, offset=3)

    def test_get_backup_list_with_userid_and_search_return_empty(self):
        self.eng.backup_manager.search.return_value = []
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.eng.search_backup(project_id='tecs',
                                     user_id=common.fake_data_0_user_id,
                                     offset=3, limit=7,
                                     search=my_search)
        self.assertEqual([], res)
        self.eng.backup_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_data_0_wrapped_backup_metadata['user_id'],
            search=my_search,
            limit=7, offset=3)

    def test_get_backup_userid_and_backup_id_not_found_returns_empty(self):
        self.eng.backup_manager.get.return_value = None
        res = self.eng.get_backup(project_id='tecs',
                                  user_id=common.fake_data_0_user_id,
                                  backup_id=common.fake_data_0_backup_id)
        self.assertIsNone(res)
        self.eng.backup_manager.get.assert_called_with(
            project_id=common.fake_data_0_wrapped_backup_metadata
            ['project_id'],
            user_id=common.fake_data_0_wrapped_backup_metadata['user_id'],
            doc_id=common.fake_data_0_wrapped_backup_metadata['backup_id']
        )

    def test_add_backup_raises_when_data_is_malformed(self):
        self.assertRaises(exceptions.BadDataFormat, self.eng.add_backup,
                          project_id='tecs',
                          user_id=common.fake_data_0_user_id,
                          user_name=common.fake_data_0_user_name,
                          doc=common.fake_malformed_data_0_backup_metadata)

    def test_add_backup_ok(self):
        self.eng.backup_manager.search.return_value = []
        res = self.eng.add_backup(project_id='tecs',
                                  user_id=common.fake_data_0_user_id,
                                  user_name=common.fake_data_0_user_name,
                                  doc=common.fake_data_0_backup_metadata)
        self.assertTrue(res)

    def test_add_backup_raises_when_manager_insert_raises(self):
        self.eng.backup_manager.search.return_value = []
        self.eng.backup_manager.insert.side_effect = (
            exceptions.StorageEngineError('regular test failure')
        )
        self.assertRaises(exceptions.StorageEngineError, self.eng.add_backup,
                          project_id='tecs',
                          user_id=common.fake_data_0_user_id,
                          user_name=common.fake_data_0_user_name,
                          doc=common.fake_data_0_backup_metadata)

    def test_delete_backup_ok(self):
        self.eng.backup_manager.delete.return_value = (
            common.fake_data_0_backup_id
        )
        res = self.eng.delete_backup(project_id='tecs',
                                     user_id=common.fake_data_0_user_id,
                                     backup_id=common.fake_data_0_backup_id)
        self.assertEqual(common.fake_data_0_backup_id, res)

    def test_delete_backup_raises_when_es_delete_raises(self):
        self.eng.backup_manager.delete.side_effect = (
            exceptions.StorageEngineError()
        )
        self.assertRaises(exceptions.StorageEngineError,
                          self.eng.delete_backup,
                          project_id='tecs',
                          user_id=common.fake_data_0_user_id,
                          backup_id=common.fake_data_0_backup_id)


class TestElasticSearchEngine_client(unittest.TestCase, ElasticSearchDB):
    @patch('freezer_api.storage.elasticv2.logging')
    @patch('freezer_api.storage.elasticv2.elasticsearch')
    def setUp(self, mock_logging, mock_elasticsearch):
        backend = 'elasticsearch'
        grp = cfg.OptGroup(backend)
        CONF.register_group(grp)
        CONF.register_opts(self._ES_OPTS, group=backend)
        mock_elasticsearch.Elasticsearch.return_value = mock.Mock()
        kwargs = {'hosts': 'http://elasticservaddr:1997'}
        self.eng = elastic.ElasticSearchEngineV2(backend=backend)
        self.eng.init(index='freezer', **kwargs)
        self.eng.client_manager = mock.Mock()

    def test_get_client_userid_and_client_id_return_1elem_list_(self):
        self.eng.client_manager.search.return_value = [
            common.fake_client_entry_0]
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.eng.get_client(
            project_id='tecs',
            user_id=common.fake_client_entry_0['user_id'],
            client_id=common.fake_client_info_0['client_id'],
            offset=6, limit=15,
            search=my_search)
        self.assertEqual([common.fake_client_entry_0], res)
        self.eng.client_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_client_entry_0['user_id'],
            doc_id=common.fake_client_info_0['client_id'],
            search=my_search,
            limit=15, offset=6)

    def test_get_client_list_with_userid_and_search_return_list(self):
        self.eng.client_manager.search.return_value = [
            common.fake_client_entry_0, common.fake_client_entry_1]
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.eng.get_client(
            project_id='tecs',
            user_id=common.fake_client_entry_0['user_id'],
            offset=6, limit=15,
            search=my_search)
        self.assertEqual(
            [
                common.fake_client_entry_0,
                common.fake_client_entry_1
            ], res)
        self.eng.client_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_client_entry_0['user_id'],
            doc_id=None,
            search=my_search,
            limit=15, offset=6)

    def test_get_client_list_with_userid_and_search_return_empty_list(self):
        self.eng.client_manager.search.return_value = []
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.eng.get_client(
            project_id='tecs',
            user_id=common.fake_client_entry_0['user_id'],
            offset=6, limit=15,
            search=my_search)
        self.assertEqual([], res)
        self.eng.client_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_client_entry_0['user_id'],
            doc_id=None,
            search=my_search,
            limit=15, offset=6)

    def test_add_client_raises_when_data_is_malformed(self):
        doc = common.fake_client_info_0.copy()
        doc.pop('client_id')
        self.assertRaises(exceptions.BadDataFormat, self.eng.add_client,
                          project_id='tecs',
                          user_id=common.fake_data_0_user_name,
                          doc=doc)

    def test_add_client_raises_when_doc_exists(self):
        self.eng.client_manager.search.return_value = [
            common.fake_client_entry_0]
        self.assertRaises(exceptions.DocumentExists, self.eng.add_client,
                          project_id='tecs',
                          user_id=common.fake_data_0_user_id,
                          doc=common.fake_client_info_0)

    def test_add_client_ok(self):
        self.eng.client_manager.search.return_value = []
        res = self.eng.add_client(project_id='tecs',
                                  user_id=common.fake_data_0_user_id,
                                  doc=common.fake_client_info_0)
        self.assertEqual(common.fake_client_info_0['client_id'], res)
        self.eng.client_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_data_0_user_id,
            doc_id=common.fake_client_info_0['client_id'])

    def test_add_client_raises_when_manager_insert_raises(self):
        self.eng.client_manager.search.return_value = []
        self.eng.client_manager.insert.side_effect = (
            exceptions.StorageEngineError('regular test failure')
        )
        self.assertRaises(exceptions.StorageEngineError, self.eng.add_client,
                          project_id='tecs',
                          user_id=common.fake_data_0_user_id,
                          doc=common.fake_client_info_0)

    def test_delete_client_ok(self):
        self.eng.client_manager.delete.return_value = (
            common.fake_client_info_0['client_id']
        )
        res = self.eng.delete_client(project_id='tecs',
                                     user_id=common.fake_data_0_user_id,
                                     client_id=common.fake_client_info_0[
                                         'client_id'])
        self.assertEqual(common.fake_client_info_0['client_id'], res)

    def test_delete_client_raises_when_es_delete_raises(self):
        self.eng.client_manager.delete.side_effect = (
            exceptions.StorageEngineError()
        )
        self.assertRaises(exceptions.StorageEngineError,
                          self.eng.delete_client,
                          project_id='tecs',
                          user_id=common.fake_data_0_user_id,
                          client_id=common.fake_client_info_0['client_id'])


class TestElasticSearchEngine_job(unittest.TestCase, ElasticSearchDB):
    @patch('freezer_api.storage.elasticv2.logging')
    @patch('freezer_api.storage.elasticv2.elasticsearch')
    def setUp(self, mock_elasticsearch, mock_logging):
        backend = 'elasticsearch'
        grp = cfg.OptGroup(backend)
        CONF.register_group(grp)
        CONF.register_opts(self._ES_OPTS, group=backend)
        mock_elasticsearch.Elasticsearch.return_value = mock.Mock()
        kwargs = {'hosts': 'http://elasticservaddr:1997'}
        self.eng = elastic.ElasticSearchEngineV2(backend=backend)
        self.eng.init(index='freezer', **kwargs)
        self.eng.job_manager = mock.Mock()

    def test_get_job_userid_and_job_id_return_doc(self):
        self.eng.job_manager.get.return_value = common.get_fake_job_0()
        res = self.eng.get_job(project_id='tecs',
                               user_id=common.fake_job_0['user_id'],
                               job_id=common.fake_job_0['job_id'])
        self.assertEqual(common.fake_job_0, res)
        self.eng.job_manager.get.assert_called_with(
            project_id='tecs',
            user_id=common.fake_job_0['user_id'],
            doc_id=common.fake_job_0['job_id'])

    def test_get_job_userid_and_job_id_return_none(self):
        self.eng.job_manager.get.return_value = None
        res = self.eng.get_job(project_id='tecs',
                               user_id=common.fake_job_0['user_id'],
                               job_id=common.fake_job_0['job_id'])
        self.assertIsNone(res)
        self.eng.job_manager.get.assert_called_with(
            project_id='tecs',
            user_id=common.fake_job_0['user_id'],
            doc_id=common.fake_job_0['job_id'])

    def test_get_job_with_userid_and_search_return_list(self):
        self.eng.job_manager.search.return_value = \
            [common.fake_job_0, common.fake_job_0]
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.eng.search_job(project_id='tecs',
                                  user_id=common.fake_job_0['user_id'],
                                  offset=6, limit=15,
                                  search=my_search)
        self.assertEqual([common.fake_job_0, common.fake_job_0], res)
        self.eng.job_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_job_0['user_id'],
            search=my_search,
            limit=15, offset=6)

    def test_get_job_with_userid_and_search_return_empty_list(self):
        self.eng.job_manager.search.return_value = []
        my_search = {'match': [{'some_field': 'some text'},
                               {'description': 'some other text'}]}
        res = self.eng.search_job(project_id='tecs',
                                  user_id=common.fake_job_0['user_id'],
                                  offset=6, limit=15,
                                  search=my_search)
        self.assertEqual([], res)
        self.eng.job_manager.search.assert_called_with(
            project_id='tecs',
            user_id=common.fake_job_0['user_id'],
            search=my_search,
            limit=15, offset=6)

    @patch('freezer_api.common.elasticv2_utils.JobDoc')
    def test_add_job_ok(self, mock_jobdoc):
        mock_jobdoc.create.return_value = common.get_fake_job_0()
        self.eng.job_manager.insert.return_value = (True, 1)
        res = self.eng.add_job(project_id='tecs',
                               user_id=common.fake_job_0_user_id,
                               doc=common.get_fake_job_0())
        self.assertEqual(common.fake_job_0_job_id, res)
        self.eng.job_manager.insert.assert_called_with(
            common.fake_job_0, common.fake_job_0_job_id
        )

    def test_add_job_raises_StorageEngineError_when_manager_insert_raises(
            self):
        self.eng.job_manager.get.return_value = None
        self.eng.job_manager.insert.side_effect = (
            exceptions.StorageEngineError('regular test failure')
        )
        self.assertRaises(exceptions.StorageEngineError, self.eng.add_job,
                          project_id='tecs',
                          user_id=common.fake_job_0_user_id,
                          doc=common.get_fake_job_0())

    def test_delete_job_ok(self):
        self.eng.job_manager.delete.return_value = common.fake_job_0['job_id']
        res = self.eng.delete_job(project_id='tecs',
                                  user_id=common.fake_job_0_user_id,
                                  job_id=common.fake_job_0_job_id)
        self.assertEqual(common.fake_job_0_job_id, res)

    def test_delete_client_raises_StorageEngineError_when_es_delete_raises(
            self):
        self.eng.job_manager.delete.side_effect = (
            exceptions.StorageEngineError()
        )
        self.assertRaises(exceptions.StorageEngineError, self.eng.delete_job,
                          project_id='tecs',
                          user_id=common.fake_job_0_user_id,
                          job_id=common.fake_job_0_job_id)

    def test_update_job_raises_DocumentNotFound_when_doc_not_exists(self):
        self.eng.job_manager.get.side_effect = exceptions.DocumentNotFound(
            'regular test failure')
        patch = {'job_id': 'black_milk'}
        self.assertRaises(exceptions.DocumentNotFound, self.eng.update_job,
                          project_id='tecs',
                          user_id=common.fake_job_0_user_id,
                          job_id=common.fake_job_0_job_id,
                          patch_doc=patch)

    def test_update_job_raises_DocumentNotFound_when_update_raises(
            self):
        self.eng.job_manager.get.return_value = common.get_fake_job_0()
        patch = {'job_id': 'black_milk'}
        self.eng.job_manager.update.side_effect = exceptions.DocumentNotFound(
            'regular test failure')
        self.assertRaises(exceptions.DocumentNotFound, self.eng.update_job,
                          project_id='tecs',
                          user_id=common.fake_job_0_user_id,
                          job_id=common.fake_job_0_job_id,
                          patch_doc=patch)

    def test_update_job_returns_new_doc_version(self):
        self.eng.job_manager.get.return_value = common.get_fake_job_0()
        patch = {'job_id': 'group_four'}
        self.eng.job_manager.update.return_value = 11
        res = self.eng.update_job(project_id='tecs',
                                  user_id=common.fake_job_0_user_id,
                                  job_id=common.fake_job_0_job_id,
                                  patch_doc=patch)
        self.assertEqual(11, res)

    def test_replace_job_raises_AccessForbidden_when_job_manager_raises(
            self):
        self.eng.job_manager.get.side_effect = exceptions.AccessForbidden(
            'regular test failure')
        self.eng.job_manager.insert.return_value = (True, 3)
        self.assertRaises(exceptions.AccessForbidden, self.eng.replace_job,
                          project_id='tecs',
                          user_id=common.fake_job_0_user_id,
                          job_id=common.fake_job_0_job_id,
                          doc=common.get_fake_job_0())

    def test_replace_job_returns_ok_when_doc_is_new(self):
        self.eng.job_manager.get.side_effect = exceptions.DocumentNotFound(
            'regular test failure')
        self.eng.job_manager.insert.return_value = (True, 1)
        res = self.eng.replace_job(project_id='tecs',
                                   user_id=common.fake_job_0_user_id,
                                   job_id=common.fake_job_0_job_id,
                                   doc=common.get_fake_job_0())
        self.assertEqual(1, res)

    def test_replace_job_returns_version_1_when_doc_is_overwritten(self):
        self.eng.job_manager.get.return_value = common.get_fake_job_0()
        self.eng.job_manager.insert.return_value = (False, 3)
        res = self.eng.replace_job(project_id='tecs',
                                   user_id=common.fake_job_0_user_id,
                                   job_id=common.fake_job_0_job_id,
                                   doc=common.get_fake_job_0())
        self.assertEqual(3, res)
