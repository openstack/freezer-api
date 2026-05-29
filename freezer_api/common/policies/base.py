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


from oslo_policy import policy

ADMIN_OR_SERVICE = 'rule:admin_or_service'
ADMIN_OR_OWNER = 'rule:admin_or_owner'
PROJECT_MEMBER = 'rule:project_member'
PROJECT_READER = 'rule:project_reader'
ADMIN_OR_READER_OR_SERVICE = 'rule:admin_or_reader_or_service'

rules = [
    policy.RuleDefault(
        "context_is_admin",
        "role:admin",
        scope_types=['project']),
    policy.RuleDefault(
        "admin_or_owner",
        "is_admin:True or project_id:%(project_id)s",
        scope_types=['project']),
    policy.RuleDefault(
        "admin_or_service",
        "role:admin or role:service",
        scope_types=['project']),
    policy.RuleDefault(
        "project_member",
        "role:member and project_id:%(project_id)s",
        scope_types=['project']),
    policy.RuleDefault(
        "project_reader",
        "role:reader and project_id:%(project_id)s",
        scope_types=['project']),
    policy.RuleDefault(
        "admin_or_reader_or_service",
        "rule:admin_or_owner or rule:project_reader or role:service",
        scope_types=['project']),
]


def list_rules():
    return rules
