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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import falcon
from unittest import mock

from freezer_api.api.v2 import clients as v2_clients
from freezer_api.common import exceptions
from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base as db_base


class TestClientsCollectionResource(common.FreezerBaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.env.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = common.fake_data_0_user_id
        self.mock_req.status = falcon.HTTP_200
        self.resource = v2_clients.ClientsCollectionResource(self.mock_db)
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_on_get_return_empty_list(self):
        self.mock_db.get_client.return_value = []
        expected_result = {'clients': []}
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_client_info_0['project_id'])
        result = self.mock_req.media
        self.assertEqual(expected_result, result)
        self.assertEqual(falcon.HTTP_200, self.mock_req.status)

    def test_on_get_return_correct_list(self):
        self.mock_db.get_client.return_value = [common.fake_client_entry_0,
                                                common.fake_client_entry_1]
        expected_result = {'clients': [common.fake_client_entry_0,
                                       common.fake_client_entry_1]}
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_client_info_0['project_id'])
        result = self.mock_req.media
        self.assertEqual(expected_result, result)
        self.assertEqual(falcon.HTTP_200, self.mock_req.status)

    def test_on_post_raises_when_missing_body(self):
        self.mock_db.add_client.return_value = common.fake_client_info_0[
            'client_id']
        self.assertRaises(exceptions.BadDataFormat, self.resource.on_post,
                          self.mock_req, self.mock_req,
                          common.fake_client_info_0['project_id'])

    def test_on_post_inserts_correct_data(self):
        self.mock_json_body.return_value = common.fake_client_info_0
        self.mock_db.add_client.return_value = common.fake_client_info_0[
            'client_id']
        expected_result = {'client_id': common.fake_client_info_0['client_id']}
        self.resource.on_post(self.mock_req, self.mock_req,
                              common.fake_client_info_0['project_id'])
        self.assertEqual(falcon.HTTP_201, self.mock_req.status)
        self.assertEqual(expected_result, self.mock_req.media)

    @mock.patch('freezer_api.policy.can')
    def test_on_post_central_client(self, mock_policy_can):
        doc = {'is_central': True, 'client': {'client_id': 'node_1'}}
        self.mock_json_body.return_value = doc
        self.mock_db.add_client.return_value = 'node_1'
        fake_context = mock.Mock()
        self.mock_req.env.__getitem__.side_effect = (
            lambda k: fake_context if k == 'freezer.context'
            else common.get_req_items(k)
        )

        self.resource.on_post(self.mock_req, self.mock_req,
                              common.fake_client_info_0['project_id'])

        expected_calls = [
            mock.call('clients:create', fake_context),
            mock.call('clients:create_central', fake_context)
        ]
        mock_policy_can.assert_has_calls(expected_calls)

        self.mock_db.add_client.assert_called_once_with(
            project_id=common.fake_client_info_0['project_id'],
            user_id=common.fake_data_0_user_id, doc=doc
        )
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)

    @mock.patch('freezer_api.policy.can')
    def test_on_post_central_client_policy_denied(self, mock_policy_can):
        doc = {'is_central': True}
        self.mock_json_body.return_value = doc
        mock_policy_can.side_effect = Exception("Policy Denied")
        self.mock_req.env.__getitem__.side_effect = (
            lambda k: mock.Mock() if k == 'freezer.context'
            else common.get_req_items(k)
        )

        self.assertRaises(Exception, self.resource.on_post,
                          self.mock_req, self.mock_req,
                          common.fake_client_info_0['project_id'])
        self.mock_db.add_client.assert_not_called()


class TestClientsResource(common.FreezerBaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.env.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = common.fake_data_0_user_id
        self.mock_req.status = falcon.HTTP_200
        self.resource = v2_clients.ClientsResource(self.mock_db)
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_create_resource(self):
        self.assertIsInstance(self.resource, v2_clients.ClientsResource)

    def test_on_get_return_no_result_and_404_when_not_found(self):
        self.mock_db.get_client.return_value = []
        self.mock_req.media = None
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_client_info_0['project_id'],
                             common.fake_client_info_0['client_id'])
        self.assertIsNone(self.mock_req.media)
        self.assertEqual(falcon.HTTP_404, self.mock_req.status)

    def test_on_get_return_correct_data(self):
        self.mock_db.get_client.return_value = [common.fake_client_entry_0]
        expected_result = common.fake_client_entry_0
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_client_info_0['project_id'],
                             common.fake_client_info_0['client_id'])
        result = self.mock_req.media
        self.assertEqual(expected_result, result)
        self.assertEqual(falcon.HTTP_200, self.mock_req.status)

    def test_on_delete_removes_proper_data(self):
        self.resource.on_delete(self.mock_req, self.mock_req,
                                common.fake_client_info_0['project_id'],
                                common.fake_client_info_0['client_id'])
        result = self.mock_req.media
        expected_result = {'client_id': common.fake_client_info_0['client_id']}
        self.assertEqual(falcon.HTTP_204, self.mock_req.status)
        self.assertEqual(expected_result, result)

    @mock.patch('freezer_api.policy.can')
    def test_on_delete_policy_denied(self, mock_policy_can):
        mock_policy_can.side_effect = exceptions.AccessForbidden("Forbidden")

        self.assertRaises(exceptions.AccessForbidden, self.resource.on_delete,
                          self.mock_req, self.mock_req,
                          common.fake_client_info_0['project_id'],
                          common.fake_client_info_0['client_id'])

        self.mock_db.delete_client.assert_not_called()


class TestClientsDb(db_base.DbTestCase):

    def test_get_client_list_central_visibility(self):
        doc_central = {
            'is_central': True,
            'client_id': 'central_node',
            'hostname': 'central-host',
            'description': 'global visibility node'
        }
        self.dbapi.add_client(user_id='user_a', project_id='project_A',
                              doc=doc_central)

        doc_private = {
            'is_central': False,
            'client_id': 'private_node',
            'hostname': 'private-host',
            'description': 'private visibility node'
        }
        self.dbapi.add_client(user_id='user_a', project_id='project_A',
                              doc=doc_private)

        # Project B should see the central client but NOT Project A's
        # private client.
        clients_list = self.dbapi.get_client(user_id='user_b',
                                             project_id='project_B')
        client_ids = [c['client']['client_id'] for c in clients_list]

        self.assertIn('central_node', client_ids)
        self.assertNotIn('private_node', client_ids)
        self.assertEqual(1, len(clients_list))
        self.assertTrue(clients_list[0]['client'].get('is_central'))

        # Project A should see both, and private_node should have
        # is_central=False
        clients_list_a = self.dbapi.get_client(user_id='user_a',
                                               project_id='project_A')
        self.assertEqual(2, len(clients_list_a))
        private = next(c for c in clients_list_a
                       if c['client']['client_id'] == 'private_node')
        self.assertFalse(private['client'].get('is_central'))

    def test_get_client_by_id_central_visibility(self):
        doc_central = {
            'is_central': True,
            'client_id': 'central_node',
            'hostname': 'central-host',
            'description': 'global visibility node'
        }
        self.dbapi.add_client(user_id='user_a', project_id='project_A',
                              doc=doc_central)

        # Project B requests the central client specifically by ID.
        client = self.dbapi.get_client(user_id='user_b',
                                       project_id='project_B',
                                       client_id='central_node')
        self.assertEqual(1, len(client))
        self.assertEqual('central_node', client[0]['client']['client_id'])
        self.assertTrue(client[0]['client'].get('is_central'))

    def test_add_client_default_is_central(self):
        doc = {
            'client_id': 'default_node',
            'hostname': 'default-host'
        }
        self.dbapi.add_client(user_id='user_a', project_id='project_A',
                              doc=doc)

        clients_list = self.dbapi.get_client(user_id='user_a',
                                             project_id='project_A')
        self.assertFalse(clients_list[0]['client'].get('is_central'),
                         "is_central should default to False if not provided")

    def test_get_client_by_id_private_isolation(self):
        doc_private = {
            'is_central': False,
            'client_id': 'private_node',
            'hostname': 'private-host',
            'description': 'private visibility node'
        }
        self.dbapi.add_client(user_id='user_a', project_id='project_A',
                              doc=doc_private)

        # Project B requests the private client specifically by ID.
        # It should NOT be found.
        client = self.dbapi.get_client(user_id='user_b',
                                       project_id='project_B',
                                       client_id='private_node')
        self.assertEqual(0, len(client))

    def test_delete_client_central_isolation(self):
        doc_central = {
            'is_central': True,
            'client_id': 'central_node',
            'hostname': 'central-host'
        }
        self.dbapi.add_client(user_id='user_a', project_id='project_A',
                              doc=doc_central)

        self.assertRaises(exceptions.AccessForbidden,
                          self.dbapi.delete_client,
                          user_id='user_b', project_id='project_B',
                          client_id='central_node')

        clients = self.dbapi.get_client(user_id='user_a',
                                        project_id='project_A',
                                        client_id='central_node')
        self.assertEqual(
            1, len(clients),
            "Central client should not be deletable by non-owner"
        )

    def test_add_client_central_global_uniqueness(self):
        # Register a central client in Project A
        doc1 = {
            'is_central': True,
            'client_id': 'unique-node',
            'hostname': 'host-a',
            'description': 'Central client'
        }
        self.dbapi.add_client(user_id='user-a', doc=doc1,
                              project_id='project-a')

        # Attempt to register another central client with the same ID/Hostname
        # in Project B. This should fail with DocumentExists.
        doc2 = {
            'is_central': True,
            'client_id': 'unique-node',
            'hostname': 'host-a',
            'description': 'Clashing central client'
        }
        self.assertRaises(
            exceptions.DocumentExists,
            self.dbapi.add_client,
            user_id='user-b', doc=doc2, project_id='project-b'
        )

    def test_add_central_client_clash_with_private(self):
        # Register a private client in Project A
        doc1 = {
            'is_central': False,
            'client_id': 'private-node',
            'hostname': 'host-p'
        }
        self.dbapi.add_client(user_id='user-a', doc=doc1,
                              project_id='project-a')

        # Attempt to register a central client in Project B using the same
        # identity (client_id + hostname).
        doc2 = {
            'is_central': True,
            'client_id': 'private-node',
            'hostname': 'host-p'
        }
        self.assertRaises(
            exceptions.DocumentExists,
            self.dbapi.add_client,
            user_id='user-b', doc=doc2, project_id='project-b'
        )
