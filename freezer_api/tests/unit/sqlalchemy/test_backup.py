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

from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbBackupTestCase(base.DbTestCase):

    def setUp(self):
        super(DbBackupTestCase, self).setUp()
        self.fake_backup_metadata = common.get_fake_backup_metadata()
        self.fake_user_id = common.fake_data_0_user_id
        self.fake_user_name = common.fake_data_0_user_name

    def test_add_and_get_backup(self):
        backup_doc = copy.deepcopy(self.fake_backup_metadata)
        backup_id = self.dbapi.add_backup(user_id=self.fake_user_id,
                                          user_name=self.fake_user_name,
                                          doc=backup_doc,
                                          project_id="myproject")
        self.assertIsNotNone(backup_id)

        result = self.dbapi.get_backup(project_id="myproject",
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
