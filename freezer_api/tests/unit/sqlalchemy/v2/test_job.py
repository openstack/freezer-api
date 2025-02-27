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
from unittest import mock
from unittest.mock import patch
from uuid import uuid4

from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbJobTestCase(base.DbTestCase):

    def setUp(self):
        super().setUp()
        self.fake_job_0 = common.get_fake_job_0()
        self.fake_job_0.pop('job_id')
        self.fake_job_2 = common.get_fake_job_2()
        self.fake_job_2.pop('job_id')
        self.fake_job_3 = common.get_fake_job_3()
        self.fake_job_3.pop('job_id')
        self.fake_project_id = self.fake_job_0.get('project_id')
        self.fake_user_id = self.fake_job_0.get('user_id')
        self.fake_job_id = common.get_fake_job_id()
        self.setup_fake_clients(self.fake_project_id)

    def test_add_and_get_job(self):
        job_doc = copy.deepcopy(self.fake_job_0)
        job_id = self.dbapi.add_job(user_id=self.fake_job_0.get('user_id'),
                                    doc=job_doc,
                                    project_id=self.fake_project_id)
        self.assertIsNotNone(job_id)
        result = self.dbapi.get_job(project_id=self.fake_project_id,
                                    user_id=self.fake_job_0.get('user_id'),
                                    job_id=job_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.get('client_id'),
                         self.fake_job_0.get('client_id'))
        self.assertEqual(result.get('description'),
                         self.fake_job_0.get('description'))
        self.assertEqual(result.get('job_actions'),
                         self.fake_job_0.get('job_actions'))
        self.assertEqual(result.get('user_id'),
                         self.fake_job_0.get('user_id'))
        self.assertEqual(result.get('job_schedule').get('status'),
                         self.fake_job_0.get('job_schedule').get('status'))
        self.assertEqual(result.get('job_schedule').get('result'),
                         self.fake_job_0.get('job_schedule').get('result'))
        self.assertEqual(result.get('job_schedule').get('schedule_date'),
                         self.fake_job_0.get('job_schedule').
                         get('schedule_date'))
        self.assertEqual(result.get('job_schedule').
                         get('schedule_interval'),
                         self.fake_job_0.get('job_schedule').
                         get('schedule_interval'))

    def test_add_and_delete_job(self):
        job_doc = copy.deepcopy(self.fake_job_0)
        job_id = self.dbapi.add_job(user_id=self.fake_job_0.get('user_id'),
                                    doc=job_doc,
                                    project_id=self.fake_project_id)
        self.assertIsNotNone(job_id)

        result = self.dbapi.delete_job(user_id=self.fake_job_0.get('user_id'),
                                       job_id=job_id,
                                       project_id=self.fake_project_id)

        self.assertIsNotNone(result)
        self.assertEqual(result, job_id)
        result = self.dbapi.get_job(project_id=self.fake_project_id,
                                    user_id=self.fake_job_0.get('user_id'),
                                    job_id=job_id)
        self.assertEqual(len(result), 0)

    def test_add_and_update_job(self):
        job_doc = copy.deepcopy(self.fake_job_0)
        job_id = self.dbapi.add_job(user_id=self.fake_job_0.get('user_id'),
                                    doc=job_doc,
                                    project_id=self.fake_project_id)
        self.assertIsNotNone(job_id)

        patch_doc = copy.deepcopy(self.fake_job_2)

        result = self.dbapi.update_job(user_id=self.fake_job_2.get('user_id'),
                                       job_id=job_id,
                                       patch_doc=patch_doc,
                                       project_id=self.fake_project_id,)
        self.assertIsNotNone(result)
        self.assertEqual(result, 0)

        result = self.dbapi.get_job(project_id=self.fake_project_id,
                                    user_id=self.fake_job_0.get('user_id'),
                                    job_id=job_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.get('client_id'),
                         self.fake_job_2.get('client_id'))
        self.assertEqual(result.get('description'),
                         self.fake_job_2.get('description'))
        self.assertEqual(result.get('job_schedule').
                         get('schedule_interval'),
                         self.fake_job_2.get('job_schedule').
                         get('schedule_interval'))
        self.assertEqual(result.get('job_actions'),
                         self.fake_job_2.get('job_actions'))

    def test_add_and_replace_job(self):
        job_doc = copy.deepcopy(self.fake_job_0)
        job_id = self.dbapi.add_job(user_id=self.fake_job_0.get('user_id'),
                                    doc=job_doc,
                                    project_id=self.fake_project_id)
        self.assertIsNotNone(job_id)

        patch_doc = copy.deepcopy(self.fake_job_2)
        result = self.dbapi.replace_job(user_id=self.
                                        fake_job_2.get('user_id'),
                                        job_id=job_id,
                                        doc=patch_doc,
                                        project_id=self.fake_project_id)

        self.assertIsNotNone(result)
        self.assertEqual(result, job_id)

        result = self.dbapi.get_job(project_id=self.fake_project_id,
                                    user_id=self.fake_job_2.get('user_id'),
                                    job_id=job_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.get('client_id'),
                         self.fake_job_2.get('client_id'))
        self.assertEqual(result.get('description'),
                         self.fake_job_2.get('description'))
        self.assertEqual(result.get('job_schedule').
                         get('schedule_interval'),
                         self.fake_job_2.get('job_schedule').
                         get('schedule_interval'))
        self.assertEqual(result.get('job_actions'),
                         self.fake_job_2.get('job_actions'))

        patch_doc1 = copy.deepcopy(self.fake_job_0)

        result = self.dbapi.replace_job(user_id=self.
                                        fake_job_2.get('user_id'),
                                        job_id=self.fake_job_id,
                                        doc=patch_doc1,
                                        project_id=self.fake_project_id)
        self.assertIsNotNone(result)
        result = self.dbapi.get_job(project_id=self.fake_project_id,
                                    user_id=self.fake_job_2.get('user_id'),
                                    job_id=self.fake_job_id)
        self.assertEqual(result.get('job_id'), self.fake_job_id)

    def test_job_list_without_search(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1

        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=10)

        self.assertIsNotNone(result)

        self.assertEqual(len(result), 10)

        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual(jobids[index], jobmap['job_id'])

    def test_job_list_all_projects_without_search(self):
        fake_project_ids = [f"tjl-project-{x}" for x in range(0, 9)]
        jobs = {}
        for project_id in fake_project_ids:
            user_id = str(uuid4())
            client_doc = common.get_fake_client(project_id, user_id)
            client_id = client_doc['client']['client_id']
            self.dbapi.add_client(
                project_id=project_id,
                user_id=user_id,
                doc=client_doc['client'],
            )
            job_doc = common.get_fake_job(project_id, user_id, client_id)
            job_id = self.dbapi.add_job(user_id=user_id,
                                        doc=job_doc,
                                        project_id=project_id)
            self.assertIsNotNone(job_id)
            jobs[job_id] = project_id
        result = self.dbapi.search_job(
            project_id=self.fake_project_id,
            user_id=user_id,
            all_projects=True,
            offset=0,
            limit=1000,
        )
        self.assertIsNotNone(result)
        # Find our jobs, ignore any others
        for job in result:
            if job['job_id'] in jobs:
                jobs.pop(job['job_id'])
        self.assertEqual(0, len(jobs))

    def test_job_list_with_search_match_and_match_not(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            if count in [0, 4, 8, 12, 16]:
                doc['client_id'] = "node1"
                if count in [4, 12]:
                    doc['job_schedule']['schedule_interval'] = '10 days'
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1
        search_opt = {'match_not': [{'schedule_interval': '10 days'}],
                      'match': [{'client_id': 'node1'}]}
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=20,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual('node1', jobmap['client_id'])
            self.assertEqual('14 days',
                             jobmap['job_schedule']['schedule_interval'])

    def test_job_list_with_search_match_list(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            if count in [0, 4, 8, 12, 16]:
                doc['client_id'] = "node1"
                if count in [4, 12]:
                    doc['job_schedule']['schedule_interval'] = '10 days'
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1
        search_opt = {'match': [{'client_id': 'node1'},
                                {'schedule_interval': '10 days'}]}
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=20,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual('node1', jobmap['client_id'])
            self.assertEqual('10 days',
                             jobmap['job_schedule']['schedule_interval'])

    def test_job_list_with_search_match_not_list(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            if count in [0, 4, 8, 12, 16]:
                doc['client_id'] = "node1"
                if count in [4, 12]:
                    doc['job_schedule']['schedule_interval'] = '10 days'
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1
        search_opt = {'match_not':
                      [{'schedule_interval': '10 days'},
                       {'client_id': 'mytenantid_myhostname2'}]}
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=20,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual('node1', jobmap['client_id'])
            self.assertEqual('14 days',
                             jobmap['job_schedule']['schedule_interval'])

    def test_job_list_with_search_with_all_opt_one_match(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            if count in [0, 4, 8, 12, 16]:
                doc['client_id'] = "node1"
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1
        search_opt = {'match': [{'_all': '[{"client_id": "node1"}]'}]}
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=20,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual('node1', jobmap['client_id'])

    def test_job_list_with_search_with_all_opt_two_matches(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            if count in [0, 4, 8, 12, 16]:
                doc['client_id'] = "node1"
            if count in [4, 12]:
                doc['job_schedule']['schedule_interval'] = '10 days'
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1
        search_opt = {'match':
                      [{'_all':
                        '[{"client_id": "node1"}, '
                        '{"schedule_interval": "10 days"}]'}]}

        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=20,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual('node1', jobmap['client_id'])
            self.assertEqual('10 days',
                             jobmap['job_schedule']['schedule_interval'])

    def test_job_list_with_search_with_error_all_opt_return_alltuples(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            if count in [0, 4, 8, 12, 16]:
                doc['client_id'] = "node1"
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1
        search_opt = {'match': [{'_all': '{"client_id": "node1"}'}]}
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=20,
                                       search=search_opt)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)
        search_opt = {'match': [{'_all': 'client_id=node1'}]}
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=20,
                                       search=search_opt)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)

    def test_job_list_with_search_and_offset_and_limit(self):
        count = 0
        jobids = []
        while (count < 20):
            doc = copy.deepcopy(self.fake_job_3)
            if count in [0, 4, 8, 12, 16]:
                doc['client_id'] = "node1"
            job_id = self.dbapi.add_job(user_id=self.fake_job_3.
                                        get('user_id'),
                                        doc=doc,
                                        project_id=self.fake_project_id)
            self.assertIsNotNone(job_id)
            jobids.append(job_id)
            count += 1
        # There are 5 records.
        search_opt = {'match': [{'_all': '[{"client_id": "node1"}]'}]}
        # First, we can get 3 tuples
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=0,
                                       limit=3,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual('node1', jobmap['client_id'])
        # Second, we can get 2 tuples
        result = self.dbapi.search_job(user_id=self.fake_job_3.
                                       get('user_id'),
                                       project_id=self.fake_project_id,
                                       offset=3,
                                       limit=3,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        for index in range(len(result)):
            jobmap = result[index]
            self.assertEqual('node1', jobmap['client_id'])

    @patch('freezer_api.db.sqlalchemy.api.get_job')
    def test_raise_add_job(self, mock_get_job):
        mock_get_job.return_value = mock.MagicMock()
        self.assertRaises(freezer_api_exc.DocumentExists,
                          self.dbapi.add_job, self.fake_user_id,
                          self.fake_job_0,
                          project_id=self.fake_project_id)
