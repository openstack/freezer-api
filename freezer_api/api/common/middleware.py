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


class HealthApp(object):
    """
    Simple WSGI app to support HAProxy polling.
    If the requested url matches the configured path it replies
    with a 200 otherwise passes the request to the inner app
    """
    def __init__(self, app, path):
        self.app = app
        self.path = path

    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO') == self.path:
            start_response('200 OK', [])
            return []
        return self.app(environ, start_response)


class SignedHeadersAuth(object):

    def __init__(self, app, auth_app):
        self._app = app
        self._auth_app = auth_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO')
        # NOTE(flwang): The root path of Zaqar service shouldn't require any
        # auth.
        if path == '/':
            return self._app(environ, start_response)

        signature = environ.get('HTTP_URL_SIGNATURE')

        if signature is None or path.startswith('/v1'):
            return self._auth_app(environ, start_response)

        return self._app(environ, start_response)


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
