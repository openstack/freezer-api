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

from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.db.sqlalchemy import api
from freezer_api.db.sqlalchemy import models
from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class ApiTestCase(base.DbTestCase):

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.fake_job_0 = common.get_fake_job_0()
        self.fake_client_0 = common.get_fake_client_0()
        self.fake_project_id = self.fake_job_0.get('project_id')
        self.fake_user_id = self.fake_job_0.get('user_id')
        self.fake_job_id = common.get_fake_job_id()
        self.fake_action_0 = common.get_fake_action_0()
        self.fake_backup_0 = common.get_fake_backup_metadata()
        self.fake_session_0 = common.get_fake_session_0()
        self.fake_session_id = common.get_fake_session_id()

    def test_raises_model_query(self):
        session = api.get_db_session()
        session.begin()
        self.assertRaises(ValueError,
                          api.model_query, session, models.Job,
                          read_deleted='both',
                          project_id=self.fake_project_id)
        session.close()

    def test_model_query(self):
        job_doc1 = copy.deepcopy(self.fake_job_0)
        job_doc2 = copy.deepcopy(self.fake_job_0)
        self.dbapi.add_job(user_id=self.fake_user_id,
                           doc=job_doc1,
                           project_id=self.fake_project_id)
        job_id2 = self.dbapi.add_job(user_id=self.fake_user_id,
                                     doc=job_doc2,
                                     project_id=self.fake_project_id)

        result = self.dbapi.delete_job(user_id=self.fake_user_id,
                                       job_id=job_id2,
                                       project_id=self.fake_project_id)
        session = api.get_db_session()
        with session.begin():
            try:
                query = api.model_query(session, models.Job,
                                        read_deleted='no',
                                        project_id=self.fake_project_id)
                query = query.filter_by(user_id=self.fake_user_id)
                result = query.all()
                self.assertEqual(len(result), 1)

                query = api.model_query(session, models.Job,
                                        read_deleted='only',
                                        project_id=self.fake_project_id)
                query = query.filter_by(user_id=self.fake_user_id)
                result = query.all()
                self.assertEqual(len(result), 1)

                query = api.model_query(session, models.Job,
                                        read_deleted='yes',
                                        project_id=self.fake_project_id)
                query = query.filter_by(user_id=self.fake_user_id)
                result = query.all()
                self.assertEqual(len(result), 2)
            except Exception as e:
                raise freezer_api_exc.StorageEngineError(
                    message='sqlalchemy operation failed {0}'.format(e))
        session.close()
