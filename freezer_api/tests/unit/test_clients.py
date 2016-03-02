# (c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from mock import Mock, patch

import falcon


from .common import *
from freezer_api.common.exceptions import *

from freezer_api.api.v1 import clients as v1_clients


class TestClientsCollectionResource(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.mock_req = Mock()
        self.mock_req.get_header.return_value = fake_data_0_user_id
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_clients.ClientsCollectionResource(self.mock_db)
        self.mock_json_body = Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_on_get_return_empty_list(self):
        self.mock_db.get_client.return_value = []
        expected_result = {'clients': []}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_get_return_correct_list(self):
        self.mock_db.get_client.return_value = [fake_client_entry_0, fake_client_entry_1]
        expected_result = {'clients': [fake_client_entry_0, fake_client_entry_1]}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_post_raises_when_missing_body(self):
        self.mock_db.add_client.return_value = fake_client_info_0['client_id']
        self.assertRaises(BadDataFormat, self.resource.on_post, self.mock_req, self.mock_req)

    def test_on_post_inserts_correct_data(self):
        self.mock_json_body.return_value = fake_client_info_0
        self.mock_db.add_client.return_value = fake_client_info_0['client_id']
        expected_result = {'client_id': fake_client_info_0['client_id']}
        self.resource.on_post(self.mock_req, self.mock_req)
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)
        self.assertEqual(self.mock_req.body, expected_result)


class TestClientsResource(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.mock_req = Mock()
        self.mock_req.get_header.return_value = fake_data_0_user_id
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_clients.ClientsResource(self.mock_db)
        self.mock_json_body = Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_create_resource(self):
        self.assertIsInstance(self.resource, v1_clients.ClientsResource)

    def test_on_get_return_no_result_and_404_when_not_found(self):
        self.mock_db.get_client.return_value = []
        self.mock_req.body = None
        self.resource.on_get(self.mock_req, self.mock_req, fake_client_info_0['client_id'])
        self.assertIsNone(self.mock_req.body)
        self.assertEqual(self.mock_req.status, falcon.HTTP_404)

    def test_on_get_return_correct_data(self):
        self.mock_db.get_client.return_value = [fake_client_entry_0]
        expected_result = fake_client_entry_0
        self.resource.on_get(self.mock_req, self.mock_req, fake_client_info_0['client_id'])
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_delete_removes_proper_data(self):
        self.resource.on_delete(self.mock_req, self.mock_req, fake_client_info_0['client_id'])
        result = self.mock_req.body
        expected_result = {'client_id': fake_client_info_0['client_id']}
        self.assertEquals(self.mock_req.status, falcon.HTTP_204)
        self.assertEqual(result, expected_result)
