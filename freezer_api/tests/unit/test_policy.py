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

from oslo_policy import policy
from oslotest import base
from unittest import mock

from freezer_api.common import policies
from freezer_api.context import FreezerContext
from freezer_api import policy as freezer_policy


class TestPolicyEnforcement(base.BaseTestCase):

    def setUp(self):
        super(TestPolicyEnforcement, self).setUp()
        self.rules = list(policies.list_rules())

    def test_no_empty_policies(self):
        """Ensure no policy is left completely unprotected."""
        for rule in self.rules:
            self.assertNotEqual(
                "", rule.check_str,
                f"Policy {rule.name} is unprotected (empty check_str). "
                "Every rule must have a defined role or scope."
            )

    def test_get_operations_allow_reader(self):
        """Ensure all GET operations include the reader role for Secure RBAC"""
        # List of GET operations that are intentionally NOT accessible by a
        # project-scoped reader (e.g., global or administrative GETs).
        global_get_operations = [
            'jobs:get_all_projects',
        ]

        for rule in self.rules:
            if isinstance(rule, policy.DocumentedRuleDefault):
                for op in rule.operations:
                    if op['method'] == 'GET':
                        if rule.name not in global_get_operations:
                            # For project-scoped GET operations,
                            # ensure they allow 'reader'
                            self.assertIn(
                                'reader', rule.check_str,
                                f"GET operation {rule.name} does not appear "
                                "to support the 'reader' role."
                            )

    def test_write_operations_exclude_reader(self):
        """Ensure POST/PUT/PATCH/DELETE operations do not allow reader."""
        write_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        for rule in self.rules:
            if isinstance(rule, policy.DocumentedRuleDefault):
                for op in rule.operations:
                    if op['method'] in write_methods:
                        # We expect write operations to be restricted to
                        # admin or owner/member, excluding simple readers.
                        self.assertNotIn(
                            'reader', rule.check_str,
                            f"Write operation {rule.name} incorrectly allows "
                            "the 'reader' role."
                        )

    @mock.patch('freezer_api.policy.can')
    def test_enforce_decorator_populates_target(self, mock_can):
        """Verify decorator extracts target data from kwargs."""

        @freezer_policy.enforce('test:rule')
        def fake_on_get(resource, req, resp, project_id=None, user_id=None):
            return "success"

        mock_req = mock.MagicMock()
        mock_req.env = {'freezer.context': mock.MagicMock()}

        # Call with keyword arguments
        fake_on_get(None, mock_req, None,
                    project_id='target_proj', user_id='target_user')

        expected_target = {
            'project_id': 'target_proj',
            'user_id': 'target_user'
        }

        mock_can.assert_called_once_with(
            'test:rule', mock_req.env['freezer.context'],
            target=expected_target)


class TestFreezerContext(base.BaseTestCase):

    def test_context_initialization_and_to_dict(self):
        ctx = FreezerContext(
            user='my_user',
            tenant='my_tenant',
            domain='my_domain',
            user_domain='my_user_domain',
            project_domain='my_project_domain',
            is_admin=True,
            roles=['admin']
        )
        ctx_dict = ctx.to_dict()

        self.assertEqual('my_user', ctx.user_id)
        self.assertEqual('my_tenant', ctx.project_id)
        self.assertEqual('my_domain', ctx.domain_id)
        self.assertEqual('my_user_domain', ctx.user_domain_id)
        self.assertEqual('my_project_domain', ctx.project_domain_id)
        self.assertTrue(ctx.is_admin)
        self.assertEqual(['admin'], ctx.roles)

        self.assertEqual('my_user', ctx_dict['user'])
        self.assertEqual('my_tenant', ctx_dict['project_id'])
        self.assertTrue(ctx_dict['is_admin'])
