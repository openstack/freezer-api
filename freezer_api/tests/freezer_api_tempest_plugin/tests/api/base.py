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
from tempest import config
from tempest.common import credentials_factory
import tempest.test

from freezer_api.tests.freezer_api_tempest_plugin import clients

CONF = config.CONF

class BaseFreezerApiTest(tempest.test.BaseTestCase):
    """Base test case class for all Freezer API tests."""

    @classmethod
    def skip_checks(cls):
        super(BaseFreezerApiTest, cls).skip_checks()

    @classmethod
    def resource_setup(cls):
        super(BaseFreezerApiTest, cls).resource_setup()
        auth_version = CONF.identity.auth_version
        cls.cred_provider = credentials_factory.get_credentials_provider(
            cls.__name__,
            force_tenant_isolation=True,
            identity_version=auth_version)
        credentials = cls.cred_provider.get_creds_by_roles(
            ['admin', 'service'])
        cls.os = clients.Manager(credentials=credentials)
        cls.freezer_api_client = cls.os.freezer_api_client

    @classmethod
    def resource_cleanup(cls):
        super(BaseFreezerApiTest, cls).resource_cleanup()

