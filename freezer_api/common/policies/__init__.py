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
#
# Borrowed from Zun


import itertools

from freezer_api.common.policies import action
from freezer_api.common.policies import backup
from freezer_api.common.policies import base
from freezer_api.common.policies import client
from freezer_api.common.policies import job
from freezer_api.common.policies import session


def list_rules():
    return itertools.chain(
        action.list_rules(),
        backup.list_rules(),
        base.list_rules(),
        client.list_rules(),
        job.list_rules(),
        session.list_rules()
    )
