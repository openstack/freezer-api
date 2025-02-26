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

JOBS = 'jobs:%s'

rules = [
    policy.DocumentedRuleDefault(
        name=JOBS % 'create',
        check_str=base.UNPROTECTED,
        description='Creates job.',
        operations=[
            {
                'path': '/v1/jobs',
                'method': 'POST'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=JOBS % 'delete',
        check_str=base.UNPROTECTED,
        description='Delete jobs.',
        operations=[
            {
                'path': '/v1/jobs/{job_id}',
                'method': 'DELETE'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=JOBS % 'get',
        check_str=base.UNPROTECTED,
        description='Show jobs.',
        operations=[
            {
                'path': '/v1/jobs/{job_id}',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=JOBS % 'get_all',
        check_str=base.UNPROTECTED,
        description='Lists jobs.',
        operations=[
            {
                'path': '/v1/jobs',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=JOBS % 'get_all_projects',
        check_str=base.ADMIN_OR_SERVICE,
        description='Lists all projects jobs.',
        operations=[
            {
                'path': '/v1/jobs',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=JOBS % 'update',
        check_str=base.UNPROTECTED,
        description='Updates jobs.',
        operations=[
            {
                'path': '/v1/jobs/{job_id}',
                'method': 'PATCH'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name=JOBS % 'event:create',
        check_str=base.UNPROTECTED,
        description='Create an event on the specified job',
        operations=[
            {
                'path': '/v1/jobs/{job_id}/event',
                'method': 'POST'
            }
        ]
    )
]


def list_rules():
    return rules
