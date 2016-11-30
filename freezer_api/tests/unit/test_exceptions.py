# (c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import falcon
import mock

from freezer_api.common import exceptions
from freezer_api.tests.unit import common


class TestExceptions(unittest.TestCase):

    def setUp(self):
        self.ex = mock.Mock()
        self.ex.message = 'test exception'
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.context = {}

    def test_FreezerAPIException(self):
        e = exceptions.FreezerAPIException(message='testing')
        self.assertRaises(falcon.HTTPError,
                          e.handle, self.ex, self.mock_req, self.mock_req,
                          None)

    def test_BadDataFormat(self):
        e = exceptions.BadDataFormat(message='testing')
        self.assertRaises(falcon.HTTPBadRequest,
                          e.handle, self.ex, self.mock_req, self.mock_req,
                          None)

    def test_DocumentExists(self):
        e = exceptions.DocumentExists(message='testing')
        self.assertRaises(falcon.HTTPConflict,
                          e.handle, self.ex, self.mock_req, self.mock_req,
                          None)

    def test_StorageEngineError(self):
        e = exceptions.StorageEngineError(message='testing')
        self.assertRaises(falcon.HTTPInternalServerError,
                          e.handle, self.ex, self.mock_req, self.mock_req,
                          None)

    def test_DocumentNotFound(self):
        e = exceptions.DocumentNotFound(message='testing')
        self.assertRaises(falcon.HTTPError,
                          e.handle, self.ex, self.mock_req, self.mock_req,
                          None)

    def test_AccessForbidden(self):
        e = exceptions.AccessForbidden(message='testing')
        self.assertRaises(falcon.HTTPForbidden,
                          e.handle, self.ex, self.mock_req, self.mock_req,
                          None)
