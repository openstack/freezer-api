"""
Copyright 2016 Hewlett-Packard

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

import falcon
from mock import patch

from freezer_api import service


class TestService(unittest.TestCase):
    def setUp(self):
        self.falcon_versions_hooks = ['0.1.6', '0.1.7', '0.1.8', '0.1.9',
                                      '0.1.10']
        self.falcon_versions_middleware = ['0.2.0', '0.3.0', '1.0.0']

    @patch('freezer_api.cmd.api.v1')
    @patch('freezer_api.cmd.api.driver')
    @patch('freezer_api.cmd.api.falcon')
    def test_on_old_falcon_builds_v0(self, mock_falcon, mock_driver, mock_v1):
        """Test that falcon versions that should use old middleware syntax do so

        :param mock_falcon: The falcon import freezer-api will try to
        start up
        :param mock_driver: Database driver
        :param mock_v1: List of endpoints for v1 for the freezer API.
        """
        mock_driver.get_db.return_value = None
        mock_v1.endpoints = []

        # Iterate through all of the versions of falcon that should be using
        # the old before=,after= invocation and ensure that freezer-api isn't
        # trying to invoke it in the old style.
        for version_string in self.falcon_versions_hooks:
            version_attribute = '__version__' if hasattr(
                falcon, '__version__') else 'version'
            with patch('falcon.' + version_attribute, version_string):
                # Attempt to invoke a mocked version of falcon to see what args
                # it was called with
                service.freezer_appv1_factory(None)

                # Check kwargs to see if the correct arguments are being passed
                _, named_args = mock_falcon.API.call_args

                self.assertIn('before', named_args)
                self.assertIn('after', named_args)
                self.assertNotIn('middleware', named_args)

    @patch('freezer_api.cmd.api.v1')
    @patch('freezer_api.cmd.api.driver')
    @patch('freezer_api.cmd.api.falcon')
    def test_on_new_falcon_builds_v1(self, mock_falcon, mock_driver, mock_v1):
        """Test that falcon versions that should use new middleware syntax do so

        :param mock_falcon: The falcon import freezer-api will try to
        start up
        :param mock_driver: Database driver
        :param mock_v1: List of endpoints for v1 for the freezer API.
        """
        mock_driver.get_db.return_value = None
        mock_v1.endpoints = []

        # Iterate through all of the versions of falcon that should be using
        # the old before=,after= invocation and ensure that freezer-api isn't
        # trying to invoke it in the old style.
        for version_string in self.falcon_versions_middleware:
            version_attribute = '__version__' if hasattr(
                falcon, '__version__') else 'version'
            with patch('falcon.' + version_attribute, version_string):
                # Attempt to invoke a mocked version of falcon to see what args
                # it was called with
                service.freezer_appv1_factory(None)

                # Check kwargs to see if the correct arguments are being passed
                _, kwargs = mock_falcon.API.call_args

                named_args = kwargs.keys()

                self.assertNotIn('before', named_args)
                self.assertNotIn('after', named_args)
                self.assertIn('middleware', named_args)

    @patch('freezer_api.cmd.api.v2')
    @patch('freezer_api.cmd.api.driver')
    @patch('freezer_api.cmd.api.falcon')
    def test_on_old_falcon_builds_v2(self, mock_falcon, mock_driver, mock_v2):
        """Test that falcon versions that should use old middleware syntax do so

        :param mock_falcon: The falcon import freezer-api will try to
        start up
        :param mock_driver: Database driver
        :param mock_v1: List of endpoints for v1 for the freezer API.
        """
        mock_driver.get_db.return_value = None
        mock_v2.endpoints = []

        # Iterate through all of the versions of falcon that should be using
        # the old before=,after= invocation and ensure that freezer-api isn't
        # trying to invoke it in the old style.
        for version_string in self.falcon_versions_hooks:
            version_attribute = '__version__' if hasattr(
                falcon, '__version__') else 'version'
            with patch('falcon.' + version_attribute, version_string):
                # Attempt to invoke a mocked version of falcon to see what args
                # it was called with
                service.freezer_appv2_factory(None)

                # Check kwargs to see if the correct arguments are being passed
                _, named_args = mock_falcon.API.call_args

                self.assertNotIn('before', named_args)
                self.assertNotIn('after', named_args)
                self.assertIn('middleware', named_args)
