"""
(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.

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

import json

import falcon
from oslo_log import log
import webob.dec
import webob.exc

from freezer_api.common import exceptions as freezer_api_exc
from freezer_api import context

LOG = log.getLogger(__name__)


class Middleware(object):
    """
    WSGI wrapper for all freezer middlewares. Use this will allow to manage
    middlewares through paste
    """

    def __init__(self, app):
        self.app = app

    def process_request(self, req):
        """
        implement this function in your middleware to change the request
        if the function return None the request will be handled in the next
        level functions
        """
        return None

    def process_response(self, response):
        """
        Implement this to modify your response
        """
        return response

    @classmethod
    def factory(cls, global_conf, **local_conf):
        def filter(app):
            return cls(app)

        return filter

    @webob.dec.wsgify
    def __call__(self, req, params=None):
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self.app)
        response.req = req
        try:
            return self.process_response(response)
        except webob.exc.HTTPException as e:
            LOG.error(e)
            return e


class HookableMiddlewareMixin(object):
    """Provides methods to extract before and after hooks from WSGI Middleware

    Prior to falcon 0.2.0b1, it's necessary to provide falcon with middleware
    as "hook" functions that are either invoked before (to process requests)
    or after (to process responses) the API endpoint code runs.

    This mixin allows the process_request and process_response methods from a
    typical WSGI middleware object to be extracted for use as these hooks, with
    the appropriate method signatures.
    """

    def as_before_hook(self):
        """Extract process_request method as "before" hook

        :return: before hook function
        """

        # Need to wrap this up in a closure because the parameter counts
        # differ
        def before_hook(req, resp, params=None):
            return self.process_request(req, resp)

        try:
            return before_hook
        except AttributeError as ex:
            # No such method, we presume.
            message_template = ("Failed to get before hook from middleware "
                                "{0} - {1}")
            message = message_template.format(self.__name__, ex.message)
            LOG.error(message)
            LOG.exception(ex)
            raise freezer_api_exc.FreezerAPIException(message)

    def as_after_hook(self):
        """Extract process_response method as "after" hook

        :return: after hook function
        """

        # Need to wrap this up in a closure because the parameter counts
        # differ
        def after_hook(req, resp, resource=None):
            return self.process_response(req, resp, resource)

        try:
            return after_hook
        except AttributeError as ex:
            # No such method, we presume.
            message_template = ("Failed to get after hook from middleware "
                                "{0} - {1}")
            message = message_template.format(self.__name__, ex.message)
            LOG.error(message)
            LOG.exception(ex)
            raise freezer_api_exc.FreezerAPIException(message)


class RequireJSON(HookableMiddlewareMixin, object):
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'Freezer-api only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')


class JSONTranslator(HookableMiddlewareMixin, object):
    def process_response(self, req, resp, resource):
        if not hasattr(resp, 'body'):
            return
        if isinstance(resp.data, dict):
            resp.data = json.dumps(resp.data)

        if isinstance(resp.body, dict):
            resp.body = json.dumps(resp.body)


class BaseContextMiddleware(Middleware):
    def process_response(self, response):
        try:
            request_id = response.req.context.request_id
        except AttributeError:
            LOG.warning('Unable to retrieve request id from context')
        else:
            # For python 3 compatibility need to use bytes type
            prefix = b'req-' if isinstance(request_id, bytes) else 'req-'

            if not request_id.startswith(prefix):
                request_id = prefix + request_id

            response.headers['x-openstack-request-id'] = request_id
        return response


class ContextMiddleware(BaseContextMiddleware):
    """
    Simple WSGI app to support HAProxy polling.
    If the requested url matches the configured path it replies
    with a 200 otherwise passes the request to the inner app
    """

    def get_context(self, req):
        token = req.headers.get('X-Auth-Token')
        userid = req.headers.get('X-User-Id')
        domainid = req.headers.get('X-Domain-Id')
        tenantid = req.headers.get('X-Tenant-Id')
        user_domain_id = req.headers.get('X-User-Domain-Id')
        projectid = req.headers.get('X-Project-Id')
        project_domain_id = req.headers.get('X-Project-Domain-Id')
        request_id = req.headers.get('X-Openstack-Request-ID')
        roles_header = req.headers.get('X-Roles', '')
        roles = [r.strip().lower() for r in roles_header.split(',')]
        is_admin = 'admin' in roles

        return context.FreezerContext(auth_token=token,
                                      user=userid,
                                      tenant=tenantid or projectid,
                                      domain=domainid,
                                      user_domain=user_domain_id,
                                      project_domain=project_domain_id,
                                      is_admin=is_admin,
                                      request_id=request_id,
                                      resource_uuid=None,
                                      roles=roles
                                      )

    def process_request(self, req):
        if req.headers.get('X-Identity-Status') == "Confirmed":
            # falcon is overwriting the context variable in the request
            # so we need to set the context in env variable
            req.context = self.get_context(req)
            req.environ['freezer.context'] = req.context
        else:
            raise webob.exc.HTTPUnauthorized()
