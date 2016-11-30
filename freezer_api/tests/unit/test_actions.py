"""
Copyright 2015 Hewlett-Packard

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

import random

import falcon
import mock

from freezer_api.api.v1 import actions as v1_actions
from freezer_api.common import exceptions
from freezer_api.tests.unit import common


class TestActionsCollectionResource(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestActionsCollectionResource, self).setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = common.fake_action_0['user_id']
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_actions.ActionsCollectionResource(self.mock_db)
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_on_get_return_empty_list(self):
        self.mock_db.search_action.return_value = []
        expected_result = {'actions': []}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_get_return_correct_list(self):
        self.mock_db.search_action.return_value = [common.get_fake_action_0(),
                                                   common.get_fake_action_1()]
        expected_result = {'actions': [common.get_fake_action_0(),
                                       common.get_fake_action_1()]}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_post_raises_when_missing_body(self):
        self.mock_db.add_action.return_value = common.fake_action_0[
            'action_id']
        self.assertRaises(exceptions.BadDataFormat, self.resource.on_post,
                          self.mock_req, self.mock_req)

    def test_on_post_inserts_correct_data(self):
        action = common.get_fake_action_0()
        self.mock_json_body.return_value = action
        self.mock_db.add_action.return_value = 'pjiofrdslaikfunr'
        expected_result = {'action_id': 'pjiofrdslaikfunr'}
        self.resource.on_post(self.mock_req, self.mock_req)
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)
        self.assertEqual(self.mock_req.body, expected_result)


class TestActionsResource(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestActionsResource, self).setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = common.fake_action_0['user_id']
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_actions.ActionsResource(self.mock_db)
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_create_resource(self):
        self.assertIsInstance(self.resource, v1_actions.ActionsResource)

    def test_on_get_return_no_result_and_404_when_not_found(self):
        self.mock_db.get_action.return_value = None
        self.mock_req.body = None
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_action_0['action_id'])
        self.assertIsNone(self.mock_req.body)
        self.assertEqual(self.mock_req.status, falcon.HTTP_404)

    def test_on_get_return_correct_data(self):
        self.mock_db.get_action.return_value = common.get_fake_action_0()
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_action_0['action_id'])
        result = self.mock_req.body
        self.assertEqual(result, common.get_fake_action_0())
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_delete_removes_proper_data(self):
        self.resource.on_delete(self.mock_req, self.mock_req,
                                common.fake_action_0['action_id'])
        result = self.mock_req.body
        expected_result = {'action_id': common.fake_action_0['action_id']}
        self.assertEqual(self.mock_req.status, falcon.HTTP_204)
        self.assertEqual(result, expected_result)

    def test_on_patch_ok_with_some_fields(self):
        new_version = random.randint(0, 99)
        self.mock_db.update_action.return_value = new_version
        patch_doc = {'some_field': 'some_value',
                     'because': 'size_matters'}
        self.mock_json_body.return_value = patch_doc

        patch_doc.copy()

        expected_result = {'action_id': common.fake_action_0['action_id'],
                           'version': new_version}

        self.resource.on_patch(self.mock_req, self.mock_req,
                               common.fake_action_0['action_id'])
        self.mock_db.update_action.assert_called_with(
            user_id=common.fake_action_0['user_id'],
            action_id=common.fake_action_0['action_id'],
            patch_doc=patch_doc)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)

    def test_on_post_ok(self):
        new_version = random.randint(0, 99)
        self.mock_db.replace_action.return_value = new_version
        action = common.get_fake_action_0()
        self.mock_json_body.return_value = action
        expected_result = {'action_id': common.fake_action_0['action_id'],
                           'version': new_version}

        self.resource.on_post(self.mock_req, self.mock_req,
                              common.fake_action_0['action_id'])
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)
        self.assertEqual(self.mock_req.body, expected_result)

    def test_on_post_raises_when_db_replace_action_raises(self):
        self.mock_db.replace_action.side_effect = exceptions.AccessForbidden(
            'regular test failure')
        action = common.get_fake_action_0()
        self.mock_json_body.return_value = action
        self.assertRaises(exceptions.AccessForbidden, self.resource.on_post,
                          self.mock_req,
                          self.mock_req,
                          common.fake_action_0['action_id'])
