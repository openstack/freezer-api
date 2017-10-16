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

ACTIONS = 'actions:%s'

rules = [
    policy.DocumentedRuleDefault(
        name=ACTIONS % 'create',
        check_str=base.UNPROTECTED,
        description='Creates action.',
        operations=[
            {
                'path': '/v1/actions',
                'method': 'POST'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=ACTIONS % 'delete',
        check_str=base.UNPROTECTED,
        description='Delete action.',
        operations=[
            {
                'path': '/v1/actions/{action_id}',
                'method': 'DELETE'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=ACTIONS % 'get',
        check_str=base.UNPROTECTED,
        description='Show actions.',
        operations=[
            {
                'path': '/v1/actions/{action_id}',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=ACTIONS % 'get_all',
        check_str=base.UNPROTECTED,
        description='Lists actions.',
        operations=[
            {
                'path': '/v1/actions',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=ACTIONS % 'update',
        check_str=base.UNPROTECTED,
        description='Updates actions.',
        operations=[
            {
                'path': '/v1/actions/{action_id}',
                'method': 'PATCH'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=ACTIONS % 'replace',
        check_str=base.UNPROTECTED,
        description='Creates/replaces the specified action.',
        operations=[
            {
                'path': '/v1/actions/{action_id}',
                'method': 'PUT'
            }
        ]
    )
]


def list_rules():
    return rules
