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

from oslo_log import log

from freezer_api import context

LOG = log.getLogger(__name__)


def inject_context(req, resp, params):
    user_id = req.get_header('X-USER-ID')
    request_id = req.get_header('X-Openstack-Request-ID')
    auth_token = req.get_header('X-AUTH-TOKEN')
    tenant = req.get_header('X-TENANT-ID')

    roles = req.get_header('X-ROLES')
    roles = roles and roles.split(',') or []

    ctxt = context.FreezerContext(auth_token=auth_token,
                                  user=user_id,
                                  tenant=tenant,
                                  request_id=request_id,
                                  roles=roles)

    req.env['freezer.context'] = ctxt
    LOG.info('Request context set')


def before_hooks():
    return [inject_context]


class FuncMiddleware(object):
    """
    Injecting some function as middleware for freezer-api
    """
    def __init__(self, func):
        self.func = func

    def process_resource(self, req, resp, resource, params=None):
        return self.func(req, resp, params)
