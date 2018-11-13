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

from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbActionTestCase(base.DbTestCase):

    def setUp(self):
        super(DbActionTestCase, self).setUp()
        self.fake_action_0 = common.get_fake_action_0()
        self.freezer_action_0 = self.fake_action_0.get('freezer_action')

    def test_add_and_get_action(self):
        action_doc = copy.deepcopy(self.fake_action_0)
        action_id = self.dbapi.add_action(user_id=self.fake_action_0.
                                          get('user_id'),
                                          doc=action_doc,
                                          project_id="myproject")
        self.assertIsNotNone(action_id)

        result = self.dbapi.get_action(project_id="myproject",
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
                                          project_id="myproject")
        self.assertIsNotNone(action_id)

        result = self.dbapi.delete_action(project_id="myproject",
                                          user_id=self.fake_action_0.
                                          get('user_id'),
                                          action_id=action_id)

        self.assertIsNotNone(result)

        self.assertEqual(result, action_id)

        result = self.dbapi.get_action(project_id="myproject",
                                       user_id=self.fake_action_0.
                                       get('user_id'),
                                       action_id=action_id)

        self.assertEqual(len(result), 0)
