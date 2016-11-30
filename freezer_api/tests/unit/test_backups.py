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

import falcon
import mock

from freezer_api.api.v1 import backups
from freezer_api.common import exceptions
from freezer_api.tests.unit import common


class TestBackupsCollectionResource(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestBackupsCollectionResource, self).setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = {
            'X-User-ID': common.fake_data_0_user_id}
        self.mock_req.status = falcon.HTTP_200
        self.resource = backups.BackupsCollectionResource(self.mock_db)
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_on_get_return_empty_list(self):
        self.mock_db.search_backup.return_value = []
        expected_result = {'backups': []}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_get_return_correct_list(self):
        self.mock_db.search_backup.return_value = [
            common.fake_data_0_backup_metadata]
        expected_result = {'backups': [common.fake_data_0_backup_metadata]}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_post_raises_when_missing_body(self):
        self.mock_db.add_backup.return_value = [
            common.fake_data_0_wrapped_backup_metadata['backup_id']]
        self.assertRaises(exceptions.BadDataFormat, self.resource.on_post,
                          self.mock_req, self.mock_req)

    def test_on_post_inserts_correct_data(self):
        self.mock_json_body.return_value = common.fake_data_0_backup_metadata
        self.mock_db.add_backup.return_value = (
            common.fake_data_0_wrapped_backup_metadata['backup_id']
        )
        self.resource.on_post(self.mock_req, self.mock_req)
        expected_result = {
            'backup_id': common.fake_data_0_wrapped_backup_metadata[
                'backup_id']}
        self.assertEqual(self.mock_req.body, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)


class TestBackupsResource(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestBackupsResource, self).setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = {
            'X-User-ID': common.fake_data_0_user_id}
        self.mock_req.status = falcon.HTTP_200
        self.resource = backups.BackupsResource(self.mock_db)
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_on_get_return_no_result_and_404_when_not_found(self):
        self.mock_db.get_backup.return_value = []
        self.mock_req.body = None
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_data_0_wrapped_backup_metadata[
                                 'backup_id'])
        self.assertIsNone(self.mock_req.body)
        self.assertEqual(self.mock_req.status, falcon.HTTP_404)

    def test_on_get_return_correct_data(self):
        self.mock_db.get_backup.return_value = [
            common.fake_data_0_wrapped_backup_metadata]
        expected_result = [common.fake_data_0_wrapped_backup_metadata]
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_data_0_wrapped_backup_metadata[
                                 'backup_id'])
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_delete_removes_proper_data(self):
        self.resource.on_delete(self.mock_req, self.mock_req,
                                common.fake_data_0_backup_id)
        result = self.mock_req.body
        expected_result = {'backup_id': common.fake_data_0_backup_id}
        self.assertEqual(self.mock_req.status, falcon.HTTP_204)
        self.assertEqual(result, expected_result)
