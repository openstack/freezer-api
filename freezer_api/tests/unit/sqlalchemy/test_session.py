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


"""Tests for manipulating job via the DB API"""

import copy

from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbSessionTestCase(base.DbTestCase):

    def setUp(self):
        super(DbSessionTestCase, self).setUp()
        self.fake_session_0 = common.get_fake_session_0()
        self.fake_session_0.pop('session_id')

    def test_add_and_get_session(self):
        session_doc = copy.deepcopy(self.fake_session_0)
        session_id = self.dbapi.add_session(project_id=self.fake_session_0.
                                            get('project_id'),
                                            user_id=self.fake_session_0.
                                            get('user_id'),
                                            doc=session_doc)
        self.assertIsNotNone(session_id)
        result = self.dbapi.get_session(project_id=self.fake_session_0.
                                        get('project_id'),
                                        user_id=self.fake_session_0.
                                        get('user_id'),
                                        session_id=session_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.get('session_tag'),
                         self.fake_session_0.get('session_tag'))
        self.assertEqual(result.get('description'),
                         self.fake_session_0.get('description'))
        self.assertEqual(result.get('hold_off'),
                         self.fake_session_0.get('hold_off'))
        self.assertEqual(result.get('time_start'),
                         self.fake_session_0.get('time_start'))
        self.assertEqual(result.get('time_end'),
                         self.fake_session_0.get('time_end'))
        self.assertEqual(result.get('user_id'),
                         self.fake_session_0.get('user_id'))
        self.assertEqual(result.get('project_id'),
                         self.fake_session_0.get('project_id'))
        self.assertEqual(result.get('schedule'),
                         self.fake_session_0.get('schedule'))

    def test_add_and_delete_session(self):
        session_doc = copy.deepcopy(self.fake_session_0)
        session_id = self.dbapi.add_session(project_id=self.fake_session_0.
                                            get('project_id'),
                                            user_id=self.fake_session_0.
                                            get('user_id'),
                                            doc=session_doc)
        self.assertIsNotNone(session_id)

        result = self.dbapi.delete_session(project_id=self.fake_session_0.
                                           get('project_id'),
                                           user_id=self.fake_session_0.
                                           get('user_id'),
                                           session_id=session_id)

        self.assertIsNotNone(result)
        self.assertEqual(result, session_id)
        result = self.dbapi.get_session(project_id=self.fake_session_0.
                                        get('project_id'),
                                        user_id=self.fake_session_0.
                                        get('user_id'),
                                        session_id=session_id)
        self.assertEqual(len(result), 0)
