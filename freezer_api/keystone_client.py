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

from keystoneauth1 import exceptions as ks_exceptions
from keystoneauth1.identity import v3
from keystoneauth1 import session as ks_session
from openstack import connection as os_connection
from openstack import exceptions as os_exceptions
from oslo_config import cfg
from oslo_log import log

from freezer_api.common import config as common_config
from freezer_api.common.exceptions import MissingCredentialError

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class KeystoneClient:
    def __init__(self, context, region_name=None):
        self.context = context
        self.region_name = region_name
        self._client = None

    def create_client(self, trustor_project_id):
        auth_url = common_config.get_keystone_endpoint()
        auth_token = self.context.auth_token
        auth = v3.Token(
            auth_url=auth_url,
            token=auth_token,
            project_id=trustor_project_id)
        session = ks_session.Session(auth=auth)
        conn = os_connection.Connection(
            session=session,
            region_name=CONF.keystone_authtoken.region_name,
            interface=CONF.keystone_authtoken.interface,
            connect_retries=getattr(
                CONF.keystone_authtoken,
                'http_request_max_retries', 3)
        )
        return conn

    def create_trust(self, trustor_user_id, trustor_project_id):
        try:
            roles = []
            # inherit the roles of the trustor,
            # unless set trusts_delegated_roles
            delegated_roles = (
                CONF.centralized_scheduler.trusts_delegated_roles)
            if delegated_roles:
                roles = [{'name': name} for name in delegated_roles]
            else:
                token_info = self.context.auth_token_info
                if token_info and token_info.get('token', {}).get('roles'):
                    roles = [{'id': r['id']} for r in
                             token_info['token']['roles']]
                else:
                    roles = [{'name': name} for name in self.context.roles]

            client = self.create_client(trustor_project_id)
            trustee_user = CONF.centralized_scheduler.service_user
            trustee_domain = CONF.centralized_scheduler.service_user_domain

            trustee_user_id = self._get_user_id(
                client,
                trustee_user,
                trustee_domain
            )

            # Try to find existing trust
            # We filter by trustor, trustee and project
            try:
                existing_trusts = list(client.identity.trusts(
                    trustor_user_id=trustor_user_id,
                    trustee_user_id=trustee_user_id,
                    project_id=trustor_project_id
                ))
                if existing_trusts:
                    # TODO(noonedeadpunk): verify that roles match if needed,
                    # but usually one trust per user/project/trustee is enough
                    # if it has enough roles.
                    # For now, let's reuse the first one found.
                    LOG.debug(f"Reusing existing trust {existing_trusts[0].id}"
                              f" for user {trustor_user_id}")
                    return existing_trusts[0]
            except Exception as e:
                LOG.warning(f"Failed to list trusts: {e}. "
                            f"Proceeding to create a new one.")

            try:
                trust = client.identity.create_trust(
                    trustee_user_id=trustee_user_id,
                    trustor_user_id=trustor_user_id,
                    project_id=trustor_project_id,
                    impersonation=False,
                    allow_redelegation=False,
                    roles=roles,
                )
            except ks_exceptions.NotFound:
                LOG.debug("Failed to find roles %s for user %s"
                          % (roles, trustor_user_id))
                raise MissingCredentialError(
                    message=f"Failed to find roles {roles}")
        except Exception:
            LOG.exception("Failed to create trust")
            raise

        return trust

    def _get_domain_id(self, conn, domain):
        found_domain = conn.identity.find_domain(domain)
        if not found_domain:
            LOG.warning(f"Domain {domain} not found.")
            return None
        return found_domain.id

    def _get_user_id(self, conn, user, domain):
        try:
            return conn.identity.get_user(user).id
        except os_exceptions.NotFoundException:
            domain_id = self._get_domain_id(conn, domain)
            found_user = conn.identity.find_user(user, domain_id=domain_id)
            if not found_user:
                raise MissingCredentialError(
                    message=f"User {user} not found")
            return found_user.id

    def delete_trust(self, trust_id, trustor_project_id):
        try:
            conn = self.create_client(trustor_project_id)
            conn.identity.delete_trust(trust_id)
            LOG.debug(f"Deleted trust {trust_id}")
        except Exception as e:
            LOG.error(f"Failed to delete trust {trust_id}: {e}")
