# Copyright 2026, Cleura AB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

import webob.exc

from freezer_api.api.common import middleware
from freezer_api.api.common import utils
from freezer_api.tests.unit import common


class TestContextMiddleware(common.FreezerBaseTestCase):

    def setUp(self):
        super().setUp()
        self.mock_app = mock.Mock()
        self.middleware = middleware.ContextMiddleware(self.mock_app)

    def test_process_request_confirmed(self):
        req = mock.MagicMock()
        req.headers = {
            'X-Identity-Status': 'Confirmed',
            'X-Auth-Token': 'fake-token',
            'X-User-Id': 'fake-user',
            'X-Project-Id': 'fake-project',
            'X-Roles': 'member,admin',
        }
        req.environ = {}

        self.middleware.process_request(req)

        self.assertIsNotNone(req.context)
        self.assertEqual('fake-user', req.context.user_id)
        self.assertEqual('fake-project', req.context.project_id)
        self.assertTrue(req.context.is_admin)
        self.assertEqual(req.context, req.environ['freezer.context'])

    def test_process_request_unauthorized(self):
        req = mock.MagicMock()
        req.headers = {
            'X-Identity-Status': 'Invalid',
        }
        self.assertRaises(webob.exc.HTTPUnauthorized,
                          self.middleware.process_request, req)


class TestInjectContext(common.FreezerBaseTestCase):

    def test_inject_context_creates_new(self):
        req = mock.MagicMock()
        req.env = {}
        req.get_header.side_effect = lambda k: {
            'X-USER-ID': 'user-123',
            'X-TENANT-ID': 'project-123',
            'X-ROLES': 'member',
        }.get(k)

        utils.inject_context(req, None, None)

        self.assertIsNotNone(req.context)
        self.assertEqual('user-123', req.context.user_id)
        self.assertEqual('project-123', req.context.project_id)
        self.assertEqual(req.context, req.env['freezer.context'])

    def test_inject_context_reuses_existing(self):
        req = mock.MagicMock()
        existing_context = mock.Mock()
        req.env = {'freezer.context': existing_context}

        utils.inject_context(req, None, None)

        self.assertEqual(existing_context, req.context)
        self.assertEqual(existing_context, req.env['freezer.context'])
