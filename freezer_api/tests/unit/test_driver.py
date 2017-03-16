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

import mock
from mock import patch

from freezer_api.storage import driver
from freezer_api.tests.unit import common


class TestStorageDriver(common.FreezerBaseTestCase):
    @patch('freezer_api.storage.driver.LOG')
    def test_get_db_raises_when_db_not_supported(self, mock_LOG):
        mock_CONF = mock.Mock()
        mock_CONF.storage.db = 'nodb'
        driver.CONF = mock_CONF
        self.assertRaises(Exception, driver.get_db)

    @patch('freezer_api.storage.driver.elastic')
    @patch('freezer_api.storage.driver.LOG')
    @patch('freezer_api.storage.driver.get_db')
    def test_get_db_elastic(self, mock_LOG, mock_elastic, mock_get_db):
        mock_get_db.return_value = object()
        driver.register_storage_opts()
        driver.get_db()
        self.assertTrue(mock_elastic.ElasticSearchEngine)

    @patch('freezer_api.storage.driver.elastic')
    @patch('freezer_api.storage.driver.LOG')
    def test_get_db_elastic_raises_Exception_when_cert_file_not_found(
            self, mock_LOG, mock_elastic):
        mock_CONF = mock.Mock()
        mock_CONF.storage.backend = 'elasticsearch'
        mock_CONF.storage.driver = 'freezer_api.storage.elastic.' \
                                   'ElasticSearchEngine'
        mock_CONF.elasticsearch.hosts = 'es_server'
        mock_CONF.elasticsearch.verify_certs = 'False'
        mock_CONF.elasticsearch.ca_certs = 'not_existant'
        mock_CONF.elasticsearch.use_ssl = False
        mock_CONF.elasticsearch.timeout = 43
        mock_CONF.elasticsearch.retries = 37
        driver.CONF = mock_CONF
        self.assertRaises(Exception, driver.get_db)

    @patch('freezer_api.storage.driver.elastic')
    @patch('freezer_api.storage.driver.LOG')
    def test_get_db_elastic_raises_Exception_when_hosts_not_defined(
            self, mock_LOG, mock_elastic):
        mock_CONF = mock.Mock()
        mock_CONF.storage.backend = 'elasticsearch'
        mock_CONF.elasticsearch.hosts = ''
        mock_CONF.elasticsearch.endpoint = ''
        mock_CONF.elasticsearch.verify_certs = 'False'
        mock_CONF.elasticsearch.ca_certs = ''
        mock_CONF.elasticsearch.use_ssl = False
        mock_CONF.elasticsearch.timeout = 43
        mock_CONF.elasticsearch.retries = 37
        driver.CONF = mock_CONF
        self.assertRaises(Exception, driver.get_db)
