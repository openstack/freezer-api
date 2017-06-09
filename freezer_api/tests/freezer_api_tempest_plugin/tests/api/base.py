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
from tempest import test

from freezer_api.tests.freezer_api_tempest_plugin import clients

CONF = config.CONF


class BaseFreezerApiTest(test.BaseTestCase):
    """Base test case class for all Freezer API tests."""

    credentials = ['primary']

    client_manager = clients.Manager

    @classmethod
    def setup_clients(cls):
        super(BaseFreezerApiTest, cls).setup_clients()
        cls.freezer_api_client = cls.os_primary.freezer_api_client
