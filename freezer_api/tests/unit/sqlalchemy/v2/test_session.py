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
        self.fake_session_2 = common.get_fake_session_2()
        self.fake_session_2.pop('session_id')
        self.fake_session_3 = common.get_fake_session_3()
        self.fake_session_3.pop('session_id')
        self.fake_session_id = common.get_fake_session_id()

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

    def test_add_and_update_session(self):
        session_doc = copy.deepcopy(self.fake_session_0)
        session_id = self.dbapi.add_session(project_id=self.fake_session_0.
                                            get('project_id'),
                                            user_id=self.fake_session_0.
                                            get('user_id'),
                                            doc=session_doc)
        self.assertIsNotNone(session_id)

        patch_doc = copy.deepcopy(self.fake_session_2)
        result = self.dbapi.update_session(user_id=self.fake_session_0.
                                           get('user_id'),
                                           session_id=session_id,
                                           patch_doc=patch_doc,
                                           project_id=self.fake_session_0.
                                           get('project_id'))
        self.assertIsNotNone(result)
        self.assertEqual(result, 0)

        result = self.dbapi.get_session(project_id=self.fake_session_0.
                                        get('project_id'),
                                        user_id=self.fake_session_0.
                                        get('user_id'),
                                        session_id=session_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.get('description'),
                         self.fake_session_2.get('description'))
        self.assertEqual(result.get('hold_off'),
                         self.fake_session_2.get('hold_off'))
        self.assertEqual(result.get('schedule').get('schedule_date'),
                         self.fake_session_2.get('schedule').
                         get('schedule_date'))

    def test_add_and_replace_session(self):
        session_doc = copy.deepcopy(self.fake_session_0)
        session_id = self.dbapi.add_session(project_id=self.fake_session_0.
                                            get('project_id'),
                                            user_id=self.fake_session_0.
                                            get('user_id'),
                                            doc=session_doc)
        self.assertIsNotNone(session_id)

        patch_doc = copy.deepcopy(self.fake_session_2)
        result = self.dbapi.replace_session(user_id=self.
                                            fake_session_2.get('user_id'),
                                            session_id=session_id,
                                            doc=patch_doc,
                                            project_id=self.fake_session_2.
                                            get('project_id'))

        self.assertIsNotNone(result)
        self.assertEqual(result, session_id)

        result = self.dbapi.get_session(project_id=self.fake_session_2.
                                        get('project_id'),
                                        user_id=self.fake_session_2.
                                        get('user_id'),
                                        session_id=session_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.get('description'),
                         self.fake_session_2.get('description'))
        self.assertEqual(result.get('hold_off'),
                         self.fake_session_2.get('hold_off'))
        self.assertEqual(result.get('schedule').get('schedule_date'),
                         self.fake_session_2.get('schedule').
                         get('schedule_date'))

        patch_doc1 = copy.deepcopy(self.fake_session_0)
        result = self.dbapi.replace_session(user_id=self.
                                            fake_session_0.get('user_id'),
                                            session_id=self.fake_session_id,
                                            doc=patch_doc1,
                                            project_id=self.fake_session_2.
                                            get('project_id'))
        self.assertIsNotNone(result)
        result = self.dbapi.get_session(project_id=self.fake_session_2.
                                        get('project_id'),
                                        user_id=self.fake_session_2.
                                        get('user_id'),
                                        session_id=self.fake_session_id)
        self.assertEqual(result.get('session_id'), self.fake_session_id)

    def test_session_list_without_search(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1

        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=10)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 10)

        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(sessionids[index], sessionmap['session_id'])

    def test_session_list_with_search_match_and_match_not(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            if count in [0, 4, 8, 12, 16]:
                doc['hold_off'] = 100
                if count in [4, 12]:
                    doc['schedule']['schedule_date'] = \
                        '2018-12-12T00:00:00'
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1
        search_opt = {'match': [{'hold_off': 100}],
                      'match_not':
                          [{'schedule_date': '2018-12-12T00:00:00'}]
                      }
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=20,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(100, sessionmap['hold_off'])
            self.assertEqual('2018-11-14T16:20:00',
                             sessionmap['schedule']['schedule_date'])

    def test_session_list_with_search_match_list(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            if count in [0, 4, 8, 12, 16]:
                doc['hold_off'] = 100
                if count in [4, 12]:
                    doc['schedule']['schedule_date'] = '2018-12-12T00:00:00'
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1
        search_opt = {'match': [{'hold_off': 100},
                                {'schedule_date': '2018-12-12T00:00:00'}]}
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=20,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(100, sessionmap['hold_off'])
            self.assertEqual('2018-12-12T00:00:00',
                             sessionmap['schedule']['schedule_date'])

    def test_session_list_with_search_match_not_list(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            if count in [0, 4, 8, 12, 16]:
                doc['hold_off'] = 100
                if count in [4, 12]:
                    doc['schedule']['schedule_date'] = '2018-12-12T00:00:00'
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1
        search_opt = {'match_not': [{'schedule_date': '2018-11-14T16:20:00'},
                                    {'hold_off': 60}]}
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=20,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(100, sessionmap['hold_off'])
            self.assertEqual('2018-12-12T00:00:00',
                             sessionmap['schedule']['schedule_date'])

    def test_session_list_with_search_with_all_opt_one_match(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            if count in [0, 4, 8, 12, 16]:
                doc['hold_off'] = 100
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1

        search_opt = {'match': [{'_all': '[{"hold_off": 100}]'}]}
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=20,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(100, sessionmap['hold_off'])

    def test_session_list_with_search_with_all_opt_two_matches(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            if count in [0, 4, 8, 12, 16]:
                doc['hold_off'] = 100
            if count in [4, 12]:
                doc['schedule']['schedule_date'] = '2018-12-12T00:00:00'
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1

        search_opt = {'match': [{'_all': '[{"hold_off": 100},'
                                         '{"schedule_date": '
                                         '"2018-12-12T00:00:00"}]'}]}
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=20,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(100, sessionmap['hold_off'])
            self.assertEqual('2018-12-12T00:00:00',
                             sessionmap['schedule']['schedule_date'])

    def test_session_list_with_search_error_all_opt_return_alltuples(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            if count in [0, 4, 8, 12, 16]:
                doc['hold_off'] = 100
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1

        search_opt = {'match': [{'_all': '{"hold_off": 100}'}]}
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=20,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)

        search_opt = {'match': [{'_all': 'hold_off=100'}]}
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=20,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)

    def test_session_list_with_search_and_offset_and_limit(self):
        count = 0
        sessionids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_session_3)
            if count in [0, 4, 8, 12, 16]:
                doc['hold_off'] = 100
            session_id = self.dbapi.add_session(project_id=self.fake_session_3.
                                                get('project_id'),
                                                user_id=self.fake_session_3.
                                                get('user_id'),
                                                doc=doc)
            self.assertIsNotNone(session_id)
            sessionids.append(session_id)
            count += 1
        # There are 5 records.
        search_opt = {'match': [{'_all': '[{"hold_off": 100}]'}]}
        # First, we can get 3 tuples
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=0,
                                           limit=3,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(100, sessionmap['hold_off'])
        # Second, we can get 2 tuples
        result = self.dbapi.search_session(user_id=self.fake_session_3.
                                           get('user_id'),
                                           project_id=self.fake_session_3.
                                           get('project_id'),
                                           offset=3,
                                           limit=3,
                                           search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            sessionmap = result[index]
            self.assertEqual(100, sessionmap['hold_off'])
