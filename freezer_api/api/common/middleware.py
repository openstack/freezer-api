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

from freezer_api.common import exceptions as freezer_api_exc
import json
from webob.dec import wsgify


@wsgify.middleware
def json_translator(req, app):
    resp = req.get_response(app)
    if resp.body:
        if isinstance(resp.body, dict):
            try:
                resp.body = json.dumps(resp.body)
            except Exception:
                raise freezer_api_exc.FreezerAPIException(
                    'Internal server error: malformed json reply')
    return resp


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
