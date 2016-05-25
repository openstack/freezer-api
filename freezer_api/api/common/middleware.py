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

import falcon
import json

from oslo_log import log

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

    def process_response(self, resp):
        """
        Implement this to modify your response
        """
        return None

    @classmethod
    def factory(cls, global_conf, **local_conf):
        def filter(app):
            return cls(app)
        return filter

    def __call__(self, req, resp):
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self.app)
        response.req = req
        try:
            self.process_response(response)
        except falcon.HTTPError as e:
            LOG.error(e)


# @todo this should be removed and oslo.middleware should be used instead
class HealthApp(Middleware):
    """
    Simple WSGI app to support HAProxy polling.
    If the requested url matches the configured path it replies
    with a 200 otherwise passes the request to the inner app
    """
    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO') == '/v1/health':
            start_response('200 OK', [])
            return []
        return self.app(environ, start_response)


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'Freezer-api only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')


class JSONTranslator(object):

    def process_response(self, req, resp, resource):
        if not hasattr(resp, 'body'):
            return
        if isinstance(resp.data, dict):
            resp.data = json.dumps(resp.data)

        if isinstance(resp.body, dict):
            resp.body = json.dumps(resp.body)
