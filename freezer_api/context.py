"""
(c) Copyright 2016 Hewlett-Packard Enterprise Development Company, L.P.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import copy

from oslo_context import context
from oslo_log import log

LOG = log.getLogger(__name__)


class FreezerContext(context.RequestContext):

    def __init__(self, auth_token=None, user=None, tenant=None, domain=None,
                 user_domain=None, project_domain=None, is_admin=False,
                 read_only=False, show_deleted=False, request_id=None,
                 resource_uuid=None, overwrite=True, roles=None):
        super(FreezerContext, self).__init__(
            auth_token=auth_token,
            user=user,
            tenant=tenant,
            domain=domain,
            user_domain=user_domain,
            project_domain=project_domain,
            is_admin=is_admin,
            read_only=read_only,
            show_deleted=show_deleted,
            request_id=request_id,
            resource_uuid=resource_uuid,
            overwrite=overwrite,
            roles=roles)

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def elevated(self, show_deleted=False):
        _context = copy.deepcopy(self)
        _context.is_admin = True
        if 'admin' not in _context.roles:
            _context.roles.append('admin')

        if show_deleted is not None:
            _context.show_deleted = show_deleted

        return _context

    @property
    def view_deleted(self):
        return self.show_deleted or self.is_admin


def get_admin_context(show_deleted="no"):
    return FreezerContext(is_admin=True, show_deleted=show_deleted)


def get_current():
    return context.get_current()
