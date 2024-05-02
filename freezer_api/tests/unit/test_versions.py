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

import falcon
from unittest import mock

from oslo_serialization import jsonutils as json

from freezer_api.api import v2
from freezer_api.api import versions
from freezer_api.tests.unit import common


class TestVersionResource(common.FreezerBaseTestCase):

    def setUp(self):
        super().setUp()
        self.resource = versions.Resource()
        self.req = mock.Mock()
        self.req.url = "{0}"

    def test_on_get_return_versions(self):
        self.resource.on_get(self.req, self.req)
        self.assertEqual(falcon.HTTP_300, self.req.status)
        expected_result = json.dumps({'versions': [v2.VERSION]})
        self.assertEqual(expected_result, self.req.data)
