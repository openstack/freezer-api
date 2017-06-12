# (C) Copyright 2016 Hewlett Packard Enterprise Development Company LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import time

from tempest.lib import decorators
from tempest.lib import exceptions

from freezer_api.tests.freezer_api_tempest_plugin.tests.api import base


class TestFreezerApiClients(base.BaseFreezerApiTest):
    @classmethod
    def resource_setup(cls):
        super(TestFreezerApiClients, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(TestFreezerApiClients, cls).resource_cleanup()

    @decorators.attr(type="gate")
    def test_api_clients(self):

        resp, response_body = self.freezer_api_client.get_clients()
        self.assertEqual(200, resp.status)

        response_body_json = json.loads(response_body)
        self.assertIn('clients', response_body_json)
        clients = response_body_json['clients']
        self.assertEmpty(clients)

    @decorators.attr(type="gate")
    def test_api_clients_get_limit(self):
        # limits > 0 should return successfully
        for valid_limit in [2, 1]:
            resp, body = self.freezer_api_client.get_clients(limit=valid_limit)
            self.assertEqual(200, resp.status)

        # limits <= 0 should raise a bad request error
        for bad_limit in [0, -1, -2]:
            self.assertRaises(exceptions.BadRequest,
                              self.freezer_api_client.get_clients,
                              limit=bad_limit)

    @decorators.attr(type="gate")
    def test_api_clients_get_offset(self):
        # offsets >= 0 should return 200
        for valid_offset in [1, 0]:
            resp, body = self.freezer_api_client.get_clients(
                offset=valid_offset)
            self.assertEqual(200, resp.status)

        # offsets < 0 should return 400
        for bad_offset in [-1, -2]:
            self.assertRaises(exceptions.BadRequest,
                              self.freezer_api_client.get_clients,
                              offset=bad_offset)

    @decorators.attr(type="gate")
    def test_api_clients_post(self):
        client = {'client_id': 'test-client-id',
                  'hostname': 'test-host-name',
                  'description': 'a test client',
                  'uuid': 'test-client-uuid'}

        # Create the client with POST
        resp, response_body = self.freezer_api_client.post_clients(client)
        self.assertEqual(201, resp.status)

        self.assertIn('client_id', response_body)
        client_id = response_body['client_id']

        # Check that the client has the correct values

        # Give the DB some time to catch up
        time.sleep(5)

        resp, response_body = self.freezer_api_client.get_clients(client_id)
        self.assertEqual(200, resp.status)

        # Delete the client
        resp, response_body = self.freezer_api_client.delete_clients(
            client_id)
        self.assertEqual(204, resp.status)
