# All Rights Reserved.
#
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

from freezer_api.common.check import check_client_capabilities
from freezer_api.common import exceptions
from freezer_api.tests.unit import common


SUPPORTED_JOB_ACTIONS = [
    {
        "freezer_action": {
            "action": "backup",
            "mode": "cindernative",
            "storage": "",
            "engine": "",
        },
    },
]

UNSUPPORTED_JOB_ACTIONS = [
    {
        "freezer_action": {
            "action": "exec",
            "mode": "fs",
            "storage": "local",
            "engine": "tar",
        },
    },
]

TEST_CLIENT = {
    "client": {
        "supported_actions": ["backup"],
        "supported_modes": ["cindernative"],
        "supported_storages": [],
        "supported_engines": [],
    },
}


class TestCheck(common.FreezerBaseTestCase):
    def test_client_capabilities_supported(self):
        # Check passes when no exception is raised
        check_client_capabilities(SUPPORTED_JOB_ACTIONS, TEST_CLIENT)

    def test_client_capabilities_unsupported(self):
        self.assertRaises(
            exceptions.UnprocessableEntity,
            check_client_capabilities,
            UNSUPPORTED_JOB_ACTIONS,
            TEST_CLIENT,
        )
