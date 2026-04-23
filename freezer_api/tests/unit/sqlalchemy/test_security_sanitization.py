# Copyright 2026, Cleura AB.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_db import exception as db_exc
from unittest import mock

from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.db.sqlalchemy import api as sqlalchemy_api
from freezer_api.db.sqlalchemy import models
from freezer_api.tests.unit.sqlalchemy import base


class TestDBSecuritySanitization(base.DbTestCase):

    def test_add_tuple_sanitizes_duplicate_entry(self):
        fake_tuple = mock.MagicMock()
        fake_tuple.save.side_effect = \
            db_exc.DBDuplicateEntry("Raw SQL Error Data")

        ex = self.assertRaises(freezer_api_exc.DocumentExists,
                               sqlalchemy_api.add_tuple, fake_tuple)

        self.assertNotIn("Raw SQL Error Data", str(ex))
        self.assertEqual(
            "Document with the specified ID already exists.", ex.message
        )

    def test_add_tuple_sanitizes_db_error(self):
        fake_tuple = mock.MagicMock()
        fake_tuple.save.side_effect = db_exc.DBError("Sensitive DB Info")

        ex = self.assertRaises(freezer_api_exc.StorageEngineError,
                               sqlalchemy_api.add_tuple, fake_tuple)

        self.assertNotIn("Sensitive DB Info", str(ex))
        self.assertEqual("Database operation failed.", ex.message)

    def test_update_tuple_sanitizes_duplicate_entry(self):
        patch_path = 'freezer_api.db.sqlalchemy.api.model_query'
        with mock.patch(patch_path) as mock_query:
            mock_res = mock_query.return_value.filter_by.return_value
            mock_res.filter_by.return_value.update.side_effect = \
                db_exc.DBDuplicateEntry("Violated Constraint Details")

            ex = self.assertRaises(freezer_api_exc.DocumentExists,
                                   sqlalchemy_api.update_tuple,
                                   models.Action, 'user1', 'id1', {})

            self.assertNotIn("Violated Constraint Details", str(ex))
            self.assertEqual("Update failed: document already exists.",
                             ex.message)

    def test_delete_job_sanitizes_db_error(self):
        patch_path = 'freezer_api.db.sqlalchemy.api.model_query'
        with mock.patch(patch_path) as mock_query:
            mock_res = mock_query.return_value.filter_by.return_value
            mock_res.first.side_effect = \
                db_exc.DBError("Secret internal structure")

            ex = self.assertRaises(freezer_api_exc.StorageEngineError,
                                   sqlalchemy_api.delete_job, 'user1', 'job1')

            self.assertNotIn("Secret internal structure", str(ex))
            self.assertEqual("Database operation failed.", ex.message)

    @mock.patch('freezer_api.db.sqlalchemy.api.get_tuple')
    def test_add_action_uses_global_check(self, mock_get_tuple):
        mock_get_tuple.return_value = []
        doc = {'freezer_action': {'action': 'backup'},
               'action_id': 'unique-id'}

        sqlalchemy_api.add_action('user1', doc, 'proj1')

        mock_get_tuple.assert_called_with(
            tablename=models.Action, user_id=None,
            tuple_id='unique-id', project_id=None,
            all_projects=True
        )

    @mock.patch('freezer_api.db.sqlalchemy.api.get_job')
    @mock.patch('freezer_api.db.sqlalchemy.api.check_job_client')
    def test_add_job_uses_global_check(self, mock_check, mock_get_job):
        mock_get_job.return_value = {}
        doc = {'job_actions': [], 'job_id': 'job-uuid', 'client_id': 'c1'}

        sqlalchemy_api.add_job('user1', doc, 'proj1')

        mock_get_job.assert_called_with(
            project_id=None, user_id=None,
            job_id='job-uuid', all_projects=True
        )
