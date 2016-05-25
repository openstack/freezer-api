"""Freezer swift.py related tests

(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""


import unittest
from mock import Mock, patch

from freezer_api.storage import driver
from freezer_api.cmd.api import build_app


class TestStorageDriver(unittest.TestCase):

    @patch('freezer_api.storage.driver.logging')
    def test_get_db_raises_when_db_not_supported(self, mock_logging):
        mock_CONF = Mock()
        mock_CONF.storage.db = 'nodb'
        driver.CONF = mock_CONF
        self.assertRaises(Exception, driver.get_db)

    @patch('freezer_api.storage.driver.elastic')
    @patch('freezer_api.storage.driver.logging')
    def test_get_db_elastic(self, mock_logging, mock_elastic):
        driver.register_elk_opts()
        db = driver.get_db()
        self.assertTrue(mock_elastic.ElasticSearchEngine)

    @patch('freezer_api.storage.driver.elastic')
    @patch('freezer_api.storage.driver.logging')
    def test_get_db_elastic_raises_Exception_when_cert_file_not_found(self, mock_logging, mock_elastic):
        mock_CONF = Mock()
        mock_CONF.storage.db = 'elasticsearch'
        mock_CONF.storage.hosts = 'es_server'
        mock_CONF.storage.verify_certs = 'False'
        mock_CONF.storage.ca_certs = 'not_existant'
        mock_CONF.storage.use_ssl = False
        mock_CONF.storage.timeout = 43
        mock_CONF.storage.retries = 37
        driver.CONF = mock_CONF
        self.assertRaises(Exception, driver.get_db)

    @patch('freezer_api.storage.driver.elastic')
    @patch('freezer_api.storage.driver.logging')
    def test_get_db_elastic_raises_Exception_when_hosts_not_defined(self, mock_logging, mock_elastic):
        mock_CONF = Mock()
        mock_CONF.storage.db = 'elasticsearch'
        mock_CONF.storage.hosts = ''
        mock_CONF.storage.endpoint = ''
        mock_CONF.storage.verify_certs = 'False'
        mock_CONF.storage.ca_certs = ''
        mock_CONF.storage.use_ssl = False
        mock_CONF.storage.timeout = 43
        mock_CONF.storage.retries = 37
        driver.CONF = mock_CONF
        self.assertRaises(Exception, driver.get_db)
