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

from oslo_serialization import jsonutils as json

from tempest import config
from tempest_lib.common import rest_client

CONF = config.CONF

class FreezerApiClient(rest_client.RestClient):

    def __init__(self, auth_provider):
        super(FreezerApiClient, self).__init__(
            auth_provider,
            CONF.backup.catalog_type,
            CONF.backup.region or CONF.identity.region,
            endpoint_type=CONF.backup.endpoint_type
        )

    def get_version(self):
        resp, response_body = self.get('/')
        return resp, response_body