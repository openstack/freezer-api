# (c) Copyright 2018 ZTE Corporation.
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

"""Tests for manipulating Action via the DB API"""

import copy
import mock
from mock import patch

from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbActionTestCase(base.DbTestCase):

    def setUp(self):
        super(DbActionTestCase, self).setUp()
        self.fake_action_0 = common.get_fake_action_0()
        self.fake_action_2 = common.get_fake_action_2()
        self.fake_action_3 = common.get_fake_action_3()
        self.freezer_action_0 = self.fake_action_0.get('freezer_action')
        self.freezer_action_2 = self.fake_action_2.get('freezer_action')
        self.fake_project_id = self.fake_action_0.get('project_id')
        self.fake_user_id = self.fake_action_0.get('user_id')
        self.fake_action_id = common.get_fake_action_id()

    def test_add_and_get_action(self):
        action_doc = copy.deepcopy(self.fake_action_0)
        action_id = self.dbapi.add_action(user_id=self.fake_action_0.
                                          get('user_id'),
                                          doc=action_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(action_id)

        result = self.dbapi.get_action(project_id=self.fake_project_id,
                                       user_id=self.fake_action_0.
                                       get('user_id'),
                                       action_id=action_id)

        self.assertIsNotNone(result)

        self.assertEqual(result.get('max_retries'),
                         self.fake_action_0.get('max_retries'))

        self.assertEqual(result.get('max_retries_interval'),
                         self.fake_action_0.get('max_retries_interval'))

        freezer_action = result.get('freezer_action')

        self.assertEqual(freezer_action.get('action'),
                         self.freezer_action_0.get('action'))

        self.assertEqual(freezer_action.get('backup_name'),
                         self.freezer_action_0.get('backup_name'))

        self.assertEqual(freezer_action.get('container'),
                         self.freezer_action_0.get('container'))

        self.assertEqual(freezer_action.get('src_file'),
                         self.freezer_action_0.get('src_file'))

        self.assertEqual(freezer_action.get('mode'),
                         self.freezer_action_0.get('mode'))

    def test_add_and_delete_action(self):
        action_doc = copy.deepcopy(self.fake_action_0)
        action_id = self.dbapi.add_action(user_id=self.fake_action_0.
                                          get('user_id'),
                                          doc=action_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(action_id)

        result = self.dbapi.delete_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_0.
                                          get('user_id'),
                                          action_id=action_id)

        self.assertIsNotNone(result)

        self.assertEqual(result, action_id)

        result = self.dbapi.get_action(project_id=self.fake_project_id,
                                       user_id=self.fake_action_0.
                                       get('user_id'),
                                       action_id=action_id)

        self.assertEqual(len(result), 0)

    def test_add_and_update_action(self):
        action_doc = copy.deepcopy(self.fake_action_0)
        action_id = self.dbapi.add_action(user_id=self.fake_action_0.
                                          get('user_id'),
                                          doc=action_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(action_id)

        patch_doc = copy.deepcopy(self.fake_action_2)

        result = self.dbapi.update_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_2.
                                          get('user_id'),
                                          patch_doc=patch_doc,
                                          action_id=action_id)

        self.assertIsNotNone(result)

        self.assertEqual(result, action_id)

        result = self.dbapi.get_action(project_id=self.fake_project_id,
                                       user_id=self.fake_action_2.
                                       get('user_id'),
                                       action_id=action_id)

        self.assertEqual(result.get('max_retries'),
                         self.fake_action_2.get('max_retries'))

        self.assertEqual(result.get('max_retries_interval'),
                         self.fake_action_2.get('max_retries_interval'))

        freezer_action = result.get('freezer_action')

        self.assertEqual(freezer_action.get('action'),
                         self.freezer_action_2.get('action'))

    def test_add_and_replace_action(self):
        action_doc = copy.deepcopy(self.fake_action_0)
        action_id = self.dbapi.add_action(user_id=self.fake_action_0.
                                          get('user_id'),
                                          doc=action_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(action_id)

        patch_doc = copy.deepcopy(self.fake_action_2)

        result = self.dbapi.replace_action(project_id=self.fake_project_id,
                                           user_id=self.fake_action_2.
                                           get('user_id'),
                                           doc=patch_doc,
                                           action_id=action_id)

        self.assertIsNotNone(result)

        self.assertEqual(result, action_id)

        result = self.dbapi.get_action(project_id=self.fake_project_id,
                                       user_id=self.fake_action_2.
                                       get('user_id'),
                                       action_id=action_id)

        self.assertEqual(result.get('max_retries'),
                         self.fake_action_2.get('max_retries'))

        self.assertEqual(result.get('max_retries_interval'),
                         self.fake_action_2.get('max_retries_interval'))

        freezer_action = result.get('freezer_action')

        self.assertEqual(freezer_action.get('action'),
                         self.freezer_action_2.get('action'))

        patch_doc1 = copy.deepcopy(self.fake_action_0)

        result = self.dbapi.replace_action(project_id=self.fake_project_id,
                                           user_id=self.fake_action_2.
                                           get('user_id'),
                                           doc=patch_doc1,
                                           action_id=self.fake_action_id)
        self.assertIsNotNone(result)
        result = self.dbapi.get_action(project_id=self.fake_project_id,
                                       user_id=self.fake_action_2.
                                       get('user_id'),
                                       action_id=self.fake_action_id)
        self.assertEqual(result.get('action_id'), self.fake_action_id)

    def test_add_and_search_action(self):
        count = 0
        actionids = []
        while(count < 20):
            doc = copy.deepcopy(self.fake_action_3)
            action_id = common.get_fake_action_id()
            doc['action_id'] = action_id
            result = self.dbapi.add_action(user_id=self.fake_action_3.
                                           get('user_id'),
                                           doc=doc,
                                           project_id=self.fake_project_id)
            self.assertIsNotNone(result)
            self.assertEqual(result, action_id)
            actionids.append(action_id)
            count += 1

        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=10,
                                          offset=0)

        self.assertIsNotNone(result)

        self.assertEqual(len(result), 10)

        for index in range(len(result)):
            actionmap = result[index]
            self.assertEqual(actionids[index], actionmap['action_id'])

    def test_action_list_with_search_match_and_match_not(self):
        count = 0
        actionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_action_3)
            action_id = common.get_fake_action_id()
            doc['action_id'] = action_id
            if count in [0, 4, 8, 12, 16]:
                doc['max_retries'] = 10
                if count in [4, 12]:
                    doc['freezer_action']['mode'] = 'nova'
            result = self.dbapi.add_action(user_id=self.fake_action_3.
                                           get('user_id'),
                                           doc=doc,
                                           project_id=self.fake_project_id)

            self.assertIsNotNone(result)
            self.assertEqual(result, action_id)
            actionids.append(action_id)
            count += 1

        search_opt = {'match_not': [{'mode': 'nova'}],
                      'match': [{'max_retries': 10}]}
        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=20,
                                          offset=0,
                                          search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        for index in range(len(result)):
            actionmap = result[index]
            self.assertEqual(10, actionmap['max_retries'])
            self.assertEqual('fs',
                             actionmap['freezer_action']['mode'])

    def test_action_list_with_search_match_list(self):
        count = 0
        actionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_action_3)
            action_id = common.get_fake_action_id()
            doc['action_id'] = action_id
            if count in [0, 4, 8, 12, 16]:
                doc['max_retries'] = 10
                if count in [4, 12]:
                    doc['freezer_action']['mode'] = 'nova'
            result = self.dbapi.add_action(user_id=self.fake_action_3.
                                           get('user_id'),
                                           doc=doc,
                                           project_id=self.fake_project_id)

            self.assertIsNotNone(result)
            self.assertEqual(result, action_id)
            actionids.append(action_id)
            count += 1

        search_opt = {'match': [{'max_retries': 10},
                                {'mode': 'nova'}]}
        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=20,
                                          offset=0,
                                          search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            actionmap = result[index]
            self.assertEqual(10, actionmap['max_retries'])
            self.assertEqual('nova',
                             actionmap['freezer_action']['mode'])

    def test_action_list_with_search_match_not_list(self):
        count = 0
        actionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_action_3)
            action_id = common.get_fake_action_id()
            doc['action_id'] = action_id
            if count in [0, 4, 8, 12, 16]:
                doc['max_retries'] = 10
                if count in [4, 12]:
                    doc['freezer_action']['mode'] = 'nova'
            result = self.dbapi.add_action(user_id=self.fake_action_3.
                                           get('user_id'),
                                           doc=doc,
                                           project_id=self.fake_project_id)

            self.assertIsNotNone(result)
            self.assertEqual(result, action_id)
            actionids.append(action_id)
            count += 1

        search_opt = {'match_not':
                      [{'mode': 'nova'},
                       {'max_retries': 5}]}
        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=20,
                                          offset=0,
                                          search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        for index in range(len(result)):
            actionmap = result[index]
            self.assertEqual(10, actionmap['max_retries'])
            self.assertEqual('fs',
                             actionmap['freezer_action']['mode'])

    def test_action_list_with_search_with_all_opt_one_match(self):
        count = 0
        actionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_action_3)
            action_id = common.get_fake_action_id()
            doc['action_id'] = action_id
            if count in [0, 4, 8, 12, 16]:
                doc['max_retries'] = 10
            result = self.dbapi.add_action(user_id=self.fake_action_3.
                                           get('user_id'),
                                           doc=doc,
                                           project_id=self.fake_project_id)

            self.assertIsNotNone(result)
            self.assertEqual(result, action_id)
            actionids.append(action_id)
            count += 1

        search_opt = {'match': [{'_all': '[{"max_retries": 10}]'}]}
        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=20,
                                          offset=0,
                                          search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        for index in range(len(result)):
            actionmap = result[index]
            self.assertEqual(10, actionmap['max_retries'])

    def test_action_list_with_search_with_all_opt_two_matchs(self):
        count = 0
        actionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_action_3)
            action_id = common.get_fake_action_id()
            doc['action_id'] = action_id
            if count in [0, 4, 8, 12, 16]:
                doc['max_retries'] = 10
                if count in [4, 12]:
                    doc['freezer_action']['mode'] = 'nova'
            result = self.dbapi.add_action(user_id=self.fake_action_3.
                                           get('user_id'),
                                           doc=doc,
                                           project_id=self.fake_project_id)

            self.assertIsNotNone(result)
            self.assertEqual(result, action_id)
            actionids.append(action_id)
            count += 1

        search_opt = {'match':
                      [{'_all':
                        '[{"max_retries": 10}, '
                        '{"mode": "nova"}]'}]}
        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=20,
                                          offset=0,
                                          search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            actionmap = result[index]
            self.assertEqual(10, actionmap['max_retries'])
            self.assertEqual('nova',
                             actionmap['freezer_action']['mode'])

    def test_action_list_with_search_with_error_all_opt_return_alltuples(self):
        count = 0
        actionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_action_3)
            action_id = common.get_fake_action_id()
            doc['action_id'] = action_id
            if count in [0, 4, 8, 12, 16]:
                doc['max_retries'] = 10
            result = self.dbapi.add_action(user_id=self.fake_action_3.
                                           get('user_id'),
                                           doc=doc,
                                           project_id=self.fake_project_id)

            self.assertIsNotNone(result)
            self.assertEqual(result, action_id)
            actionids.append(action_id)
            count += 1

        search_opt = {'match': [{'_all': '{"max_retries": 10}'}]}
        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=20,
                                          offset=0,
                                          search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)
        search_opt = {'match': [{'_all': 'max_retries=10'}]}
        result = self.dbapi.search_action(project_id=self.fake_project_id,
                                          user_id=self.fake_action_3.
                                          get('user_id'),
                                          limit=20,
                                          offset=0,
                                          search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)

    @patch('freezer_api.db.sqlalchemy.api.get_action')
    def test_raise_add_action(self, mock_get_action):
        mock_get_action.return_value = mock.MagicMock()
        self.assertRaises(freezer_api_exc.DocumentExists,
                          self.dbapi.add_action, self.fake_user_id,
                          self.fake_action_0,
                          project_id=self.fake_project_id)
