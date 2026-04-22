# (c) Copyright 2026, Cleura AB.
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

from keystoneauth1 import exceptions as ks_exceptions
from oslo_config import cfg
from unittest import mock

from freezer_api.common import exceptions
from freezer_api import context
from freezer_api.keystone_client import KeystoneClient
from freezer_api.tests.unit import common

CONF = cfg.CONF


class TestKeystoneClient(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestKeystoneClient, self).setUp()
        self.mock_context = mock.Mock(spec=context.FreezerContext)
        self.mock_context.auth_token = 'fake_token'
        self.mock_context.auth_token_info = {
            'token': {
                'roles': [
                    {'id': 'role1', 'name': 'admin'},
                    {'id': 'role2', 'name': 'member'}
                ]
            }
        }
        self.mock_context.roles = ['admin', 'member']
        CONF.set_override('service_user', 'service_user_val',
                          'centralized_scheduler')
        self.client = KeystoneClient(self.mock_context)

    @mock.patch('freezer_api.common.config.get_keystone_endpoint')
    @mock.patch('openstack.connection.Connection')
    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('keystoneauth1.identity.v3.Token')
    def test_create_client(self,
                           mock_token,
                           mock_session,
                           mock_conn, mock_get_endpoint):
        mock_get_endpoint.return_value = 'http://keystone:5000/v3'
        trustor_project_id = 'test_project'
        c = self.client.create_client(trustor_project_id)

        mock_get_endpoint.assert_called_once()
        mock_token.assert_called_once_with(
            auth_url='http://keystone:5000/v3',
            token='fake_token',
            project_id=trustor_project_id
        )
        mock_conn.assert_called_once()
        self.assertEqual(mock_conn.return_value, c)

    @mock.patch('openstack.connection.Connection')
    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('keystoneauth1.loading.load_auth_from_conf_options')
    def test_create_service_client(self,
                                   mock_load_auth,
                                   mock_session,
                                   mock_conn):
        c = self.client.create_service_client()

        mock_load_auth.assert_called_once_with(
            CONF, 'keystone_authtoken'
        )
        mock_conn.assert_called_once()
        self.assertEqual(mock_conn.return_value, c)

    @mock.patch.object(KeystoneClient, 'create_service_client')
    @mock.patch.object(KeystoneClient, 'create_client')
    def test_create_trust_reuses_existing(self, mock_create_client,
                                          mock_create_service_client):
        mock_conn = mock_create_client.return_value
        mock_admin_conn = mock_create_service_client.return_value
        mock_admin_conn.session.get_user_id.return_value = 'trustee_id'
        mock_trust = mock.Mock()
        mock_trust.id = 'existing_trust_id'
        mock_conn.identity.trusts.return_value = [mock_trust]

        trust = self.client.create_trust('user1', 'project1')

        self.assertEqual(mock_trust, trust)
        mock_conn.identity.trusts.assert_called_once_with(
            trustor_user_id='user1',
            trustee_user_id='trustee_id',
            project_id='project1'
        )
        mock_conn.identity.create_trust.assert_not_called()

    @mock.patch.object(KeystoneClient, 'create_service_client')
    @mock.patch.object(KeystoneClient, 'create_client')
    def test_create_trust_uses_default_member_role(self, mock_create_client,
                                                   mock_create_service_client):
        mock_conn = mock_create_client.return_value
        mock_admin_conn = mock_create_service_client.return_value
        mock_admin_conn.session.get_user_id.return_value = 'trustee_id'
        mock_conn.identity.trusts.return_value = []
        mock_new_trust = mock.Mock()
        mock_conn.identity.create_trust.return_value = mock_new_trust

        # Default trusts_delegated_roles is ['member']
        self.client.create_trust('user1', 'project1')

        mock_conn.identity.create_trust.assert_called_once_with(
            trustee_user_id='trustee_id',
            trustor_user_id='user1',
            project_id='project1',
            impersonation=False,
            allow_redelegation=False,
            roles=[{'name': 'member'}]
        )

    @mock.patch.object(KeystoneClient, 'create_service_client')
    @mock.patch.object(KeystoneClient, 'create_client')
    def test_create_trust_inherits_all_token_roles_when_config_is_empty(
            self, mock_create_client, mock_create_service_client):
        mock_conn = mock_create_client.return_value
        mock_admin_conn = mock_create_service_client.return_value
        mock_admin_conn.session.get_user_id.return_value = 'trustee_id'
        mock_conn.identity.trusts.return_value = []
        mock_new_trust = mock.Mock()
        mock_conn.identity.create_trust.return_value = mock_new_trust

        # Explicitly clear the delegated roles to trigger inheritance
        CONF.set_override('trusts_delegated_roles', [],
                          'centralized_scheduler')

        self.client.create_trust('user1', 'project1')

        # Should pick up all roles by ID from token_info
        mock_conn.identity.create_trust.assert_called_once_with(
            trustee_user_id='trustee_id',
            trustor_user_id='user1',
            project_id='project1',
            impersonation=False,
            allow_redelegation=False,
            roles=[{'id': 'role1'}, {'id': 'role2'}]
        )

    @mock.patch.object(KeystoneClient, 'create_service_client')
    @mock.patch.object(KeystoneClient, 'create_client')
    def test_create_trust_respects_delegated_roles_config(
        self,
        mock_create_client,
        mock_create_service_client
    ):
        mock_conn = mock_create_client.return_value
        mock_admin_conn = mock_create_service_client.return_value
        mock_admin_conn.session.get_user_id.return_value = 'trustee_id'
        mock_conn.identity.trusts.return_value = []

        # Override config to delegate a custom role
        CONF.set_override('trusts_delegated_roles', ['backup-operator'],
                          'centralized_scheduler')

        self.client.create_trust('user1', 'project1')

        mock_conn.identity.create_trust.assert_called_once_with(
            trustee_user_id='trustee_id',
            trustor_user_id='user1',
            project_id='project1',
            impersonation=False,
            allow_redelegation=False,
            roles=[{'name': 'backup-operator'}]
        )

    @mock.patch.object(KeystoneClient, 'create_service_client')
    @mock.patch.object(KeystoneClient, 'create_client')
    def test_create_trust_handles_not_found_roles(self, mock_create_client,
                                                  mock_create_service_client):
        mock_conn = mock_create_client.return_value
        mock_admin_conn = mock_create_service_client.return_value
        mock_admin_conn.session.get_user_id.return_value = 'trustee_id'
        mock_conn.identity.trusts.return_value = []
        mock_conn.identity.create_trust.side_effect = ks_exceptions.NotFound()

        self.assertRaises(exceptions.MissingCredentialError,
                          self.client.create_trust, 'user1', 'project1')

    @mock.patch.object(KeystoneClient, 'create_client')
    def test_delete_trust(self, mock_create_client):
        mock_conn = mock_create_client.return_value
        self.client.delete_trust('trust1', 'project1')
        mock_conn.identity.delete_trust.assert_called_once_with('trust1')
