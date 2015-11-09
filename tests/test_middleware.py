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


import unittest
from mock import Mock

from freezer_api.api.common import middleware

class TestHealthApp(unittest.TestCase):

    def test_call_nested_app(self):
        mock_app = Mock()
        mock_app.return_value = ['app_body']
        health_app = middleware.HealthApp(mock_app, 'test_path_78908')
        environ = {}
        start_response = Mock()
        result = health_app(environ, start_response)
        self.assertEqual(result, ['app_body'])

    def test_return_200_when_paths_match(self):
        mock_app = Mock()
        mock_app.return_value = ['app_body']
        health_app = middleware.HealthApp(mock_app, 'test_path_6789')
        environ = {'PATH_INFO': 'test_path_6789'}
        start_response = Mock()
        result = health_app(environ, start_response)
        start_response.assert_called_once_with('200 OK', [])
        self.assertEqual(result, [])
