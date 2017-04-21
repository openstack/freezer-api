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
from oslo_config import cfg
from oslo_log import log


from freezer_api.api.common import middleware
from freezer_api.api import v1
from freezer_api.api import v2

CONF = cfg.CONF
LOG = log.getLogger(__name__)

VERSIONS = {
    'versions': [
        v2.VERSION,
        v1.VERSION
    ]
}


def api_versions(conf=None):
    """API version negotiation app
    :return: Falcon WSGI app
    """
    middleware_list = list()
    middleware_list.append(middleware.RequireJSON())
    middleware_list.append(middleware.JSONTranslator())
    app = falcon.API(middleware=middleware_list)
    app.add_route('/', Resource())
    return app


class Resource(object):

    def _build_versions(self, host_url):
        allowed_versions = {'v1': CONF.enable_v1_api, 'v2': CONF.enable_v2_api}

        updated_versions = {'versions': []}
        for version in VERSIONS['versions']:
            if allowed_versions[version['id']]:
                version['links'][0]['href'] = \
                    version['links'][0]['href'].format(host_url)
                updated_versions['versions'].append(version)
        return json.dumps(updated_versions, ensure_ascii=False)

    def on_get(self, req, resp):
        resp.data = self._build_versions(req.url)

        resp.status = falcon.HTTP_300


class VersionNegotiator(middleware.Middleware):

    def process_request(self, req):
        if req.path == '/':
            app = api_versions()
            return req.get_response(app)

        return None
