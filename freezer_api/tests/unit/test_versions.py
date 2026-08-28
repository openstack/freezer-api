"""Freezer swift.py related tests

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

from unittest import mock

import falcon
from falcon import testing
from oslo_serialization import jsonutils as json

from freezer_api.api import v2
from freezer_api.api import versions
from freezer_api.tests.unit import common


class TestVersionResource(common.FreezerBaseTestCase):

    def setUp(self):
        super().setUp()
        self.resource = versions.Resource()
        self.req = mock.Mock()
        self.req.url = "http://127.0.0.1:9090/"
        self.resp = mock.Mock()

    def test_on_get_return_versions(self):
        self.resource.on_get(self.req, self.resp)
        self.assertEqual(falcon.HTTP_300, self.resp.status)
        self.assertEqual(falcon.MEDIA_JSON, self.resp.content_type)
        expected_version = json.loads(json.dumps(v2.VERSION))
        expected_version['links'][0]['href'] = 'http://127.0.0.1:9090/v2/'
        expected_result = json.dumps({'versions': [expected_version]})
        self.assertEqual(expected_result, self.resp.text)

    def test_api_versions_simulate_get(self):
        app = versions.api_versions()
        client = testing.TestClient(app)
        res = client.simulate_get('/', host='10.202.51.229:9090')
        self.assertEqual(300, res.status_code)
        body = json.loads(res.text)
        self.assertEqual(
            'http://10.202.51.229:9090/v2/',
            body['versions'][0]['links'][0]['href']
        )
        self.assertEqual(v2.VERSION['links'][0]['href'], '{0}v2/')
