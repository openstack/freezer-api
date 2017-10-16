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
from oslo_policy import policy

from freezer_api.common.policies import base

BACKUPS = 'backups:%s'

rules = [
    policy.DocumentedRuleDefault(
        name=BACKUPS % 'create',
        check_str=base.UNPROTECTED,
        description='Creates backup entry.',
        operations=[
            {
                'path': '/v1/backups',
                'method': 'POST'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=BACKUPS % 'delete',
        check_str=base.UNPROTECTED,
        description='Delete backup.',
        operations=[
            {
                'path': '/v1/backups/{backup_id}',
                'method': 'DELETE'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=BACKUPS % 'get',
        check_str=base.UNPROTECTED,
        description='Show backups.',
        operations=[
            {
                'path': '/v1/backups/{backup_id}',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=BACKUPS % 'get_all',
        check_str=base.UNPROTECTED,
        description='Lists backups.',
        operations=[
            {
                'path': '/v1/backups',
                'method': 'GET'
            }
        ]
    )
]


def list_rules():
    return rules
