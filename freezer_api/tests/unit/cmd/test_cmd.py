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

import sys
import unittest
from unittest import mock

from oslo_config import cfg

from freezer_api.cmd import manage as freezer_manage

CONF = cfg.CONF


class TestFreezerApiCmd(unittest.TestCase):
    """Unit test cases for python modules under freezer/cmd."""
    def setUp(self):
        super(TestFreezerApiCmd, self).setUp()

    def tearDown(self):
        super(TestFreezerApiCmd, self).tearDown()
        CONF.reset()
        CONF.unregister_opt(cfg.StrOpt('db'))

    @mock.patch("freezer_api.db.manager.get_db_driver")
    def test_db_sync(self, mock_get_db_driver):
        db_driver = mock_get_db_driver("elasticsearch", backend="")
        db_driver.db_sync.return_value = mock.MagicMock()
        sys.argv = ["freezer-manage", "db", "sync"]
        freezer_manage.main()
        self.assertTrue(db_driver.db_sync.called)

    @mock.patch("freezer_api.db.manager.get_db_driver")
    def test_db_update(self, mock_get_db_driver):
        db_driver = mock_get_db_driver("elasticsearch", backend="")
        db_driver.db_sync.return_value = mock.MagicMock()
        sys.argv = ["freezer-manage", "db", "update"]
        freezer_manage.main()
        self.assertTrue(db_driver.db_sync.called)

    @mock.patch("freezer_api.db.manager.get_db_driver")
    def test_db_remove(self, mock_get_db_driver):
        db_driver = mock_get_db_driver("elasticsearch", backend="")
        db_driver.db_remove.return_value = mock.MagicMock()
        sys.argv = ["freezer-manage", "db", "remove"]
        freezer_manage.main()
        self.assertTrue(db_driver.db_remove.called)

    @mock.patch("freezer_api.db.manager.get_db_driver")
    def test_db_show1(self, mock_get_db_driver):
        db_driver = mock_get_db_driver("elasticsearch", backend="")
        db_driver.db_show.return_value = {}
        sys.argv = ["freezer-manage", "db", "show"]
        freezer_manage.main()
        self.assertTrue(db_driver.db_show.called)

    @mock.patch("freezer_api.db.manager.get_db_driver")
    def test_db_show2(self, mock_get_db_driver):
        db_driver = mock_get_db_driver("elasticsearch", backend="")
        db_driver.db_show.return_value = {"databaase": "freezer"}
        sys.argv = ["freezer-manage", "db", "show"]
        freezer_manage.main()
        self.assertTrue(db_driver.db_show.called)
