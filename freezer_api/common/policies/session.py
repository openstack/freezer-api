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

SESSIONS = 'sessions:%s'

rules = [
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'create',
        check_str=base.UNPROTECTED,
        description='Creates session.',
        operations=[
            {
                'path': '/v1/sessions',
                'method': 'POST'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'delete',
        check_str=base.UNPROTECTED,
        description='Delete session.',
        operations=[
            {
                'path': '/v1/sessions/{session_id}',
                'method': 'DELETE'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'get',
        check_str=base.UNPROTECTED,
        description='Show sessions.',
        operations=[
            {
                'path': '/v1/sessions/{session_id}',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'get_all',
        check_str=base.UNPROTECTED,
        description='Lists sessions.',
        operations=[
            {
                'path': '/v1/sessions',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'update',
        check_str=base.UNPROTECTED,
        description='Updates sessions.',
        operations=[
            {
                'path': '/v1/sessions/{session_id}',
                'method': 'PATCH'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'replace',
        check_str=base.UNPROTECTED,
        description='Creates/replaces the specified session.',
        operations=[
            {
                'path': '/v1/sessions/{session_id}',
                'method': 'PUT'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'action:create',
        check_str=base.UNPROTECTED,
        description='Executes an action on the specified session.',
        operations=[
            {
                'path': '/v1/sessions/{session_id}/action',
                'method': 'POST'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'job:add',
        check_str=base.UNPROTECTED,
        description='Adds a certain job to a session.',
        operations=[
            {
                'path': '/v1/sessions/{session_id}/jobs/{job_id}',
                'method': 'PUT'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=SESSIONS % 'job:remove',
        check_str=base.UNPROTECTED,
        description='Remove a job from a session.',
        operations=[
            {
                'path': '/v1/sessions/{session_id}',
                'method': 'DELETE'
            }
        ]
    )
]


def list_rules():
    return rules
