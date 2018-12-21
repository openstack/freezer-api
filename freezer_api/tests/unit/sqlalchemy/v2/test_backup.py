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

"""Tests for manipulating Backup via the DB API"""


import copy
import mock
from mock import patch

from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbBackupTestCase(base.DbTestCase):

    def setUp(self):
        super(DbBackupTestCase, self).setUp()
        self.fake_backup_metadata = common.get_fake_backup_metadata()
        self.fake_user_id = common.fake_data_0_user_id
        self.fake_user_name = common.fake_data_0_user_name
        self.fake_project_id = common.fake_data_0_project_id

    def test_add_and_get_backup(self):
        backup_doc = copy.deepcopy(self.fake_backup_metadata)
        backup_id = self.dbapi.add_backup(user_id=self.fake_user_id,
                                          user_name=self.fake_user_name,
                                          doc=backup_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(backup_id)

        result = self.dbapi.get_backup(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       backup_id=backup_id)
        self.assertIsNotNone(result)

        self.assertEqual(result.get('user_name'),
                         self.fake_user_name)

        self.assertEqual(result.get('client_id'),
                         self.fake_backup_metadata.get('client_id'))

        self.assertEqual(result.get('user_id'),
                         self.fake_user_id)

        backup_metadata = result.get('backup_metadata')

        self.assertEqual(backup_metadata,
                         self.fake_backup_metadata)

    def test_add_and_delete_backup(self):
        backup_doc = copy.deepcopy(self.fake_backup_metadata)
        backup_id = self.dbapi.add_backup(user_id=self.fake_user_id,
                                          user_name=self.fake_user_name,
                                          doc=backup_doc,
                                          project_id=self.fake_project_id)

        self.assertIsNotNone(backup_id)

        result = self.dbapi.delete_backup(project_id=self.fake_project_id,
                                          user_id=self.fake_user_id,
                                          backup_id=backup_id)

        self.assertIsNotNone(result)

        self.assertEqual(result, backup_id)

        result = self.dbapi.get_backup(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       backup_id=backup_id)
        self.assertEqual(len(result), 0)

    def test_add_and_search_backup(self):
        count = 0
        backupids = []
        while (count < 20):
            backup_doc = copy.deepcopy(self.fake_backup_metadata)
            backup_id = self.dbapi.add_backup(user_id=self.fake_user_id,
                                              user_name=self.fake_user_name,
                                              doc=backup_doc,
                                              project_id=self.fake_project_id)

            self.assertIsNotNone(backup_id)
            backupids.append(backup_id)
            count += 1

        result = self.dbapi.search_backup(project_id=self.fake_project_id,
                                          user_id=self.fake_user_id,
                                          limit=10,
                                          offset=0)

        self.assertIsNotNone(result)

        self.assertEqual(len(result), 10)

        for index in range(len(result)):
            backupmap = result[index]
            self.assertEqual(backupids[index], backupmap['backup_id'])

    @patch('freezer_api.common.elasticv2_utils.BackupMetadataDoc')
    @patch('freezer_api.common.utils.BackupMetadataDoc')
    def test_raise_add_backup(self, mock1_BackupMetadataDoc,
                              mock_BackupMetadataDoc):
        mock1_BackupMetadataDoc().is_valid.return_value = None
        mock_BackupMetadataDoc().is_valid.return_value = None
        mock_doc = mock.MagicMock()
        self.assertRaises(freezer_api_exc.BadDataFormat,
                          self.dbapi.add_backup, self.fake_user_id, '12343',
                          mock_doc,
                          project_id=self.fake_project_id)
