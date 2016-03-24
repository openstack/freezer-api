# (C) Copyright 2016 Hewlett Packard Enterprise Development Company LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

from freezer_api.tests.freezer_api_tempest_plugin.tests.api import base
from tempest import test


class TestFreezerApiActions(base.BaseFreezerApiTest):
    @classmethod
    def resource_setup(cls):
        super(TestFreezerApiActions, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(TestFreezerApiActions, cls).resource_cleanup()

    @test.attr(type="gate")
    def test_api_actions(self):
        resp, response_body = self.freezer_api_client.get_actions()
        self.assertEqual(200, resp.status)

        resp_body_json = json.loads(response_body)
        self.assertIn('actions', resp_body_json)
        actions = resp_body_json['actions']
        self.assertEqual(actions, [])

    @test.attr(type="gate")
    def test_api_actions_post(self):

        action = {'actions': 'backup',
                  'mode': 'fs',
                  'src_file': '/dev/null',
                  'backup_name': 'test freezer api actions',
                  'container': 'test_freezer_api_actions_container',
                  'max_backup_level': 1,
                  'always_backup_level': 0,
                  'no_incremental': True,
                  'encrypt_pass_file': '/dev/null',
                  'log_file': '/dev/null',
                  'hostname': False,
                  'max_cpu_priority': False}

        # Create the action with POST
        resp, response_body = self.freezer_api_client.post_actions(action)
        self.assertEqual(201, resp.status)

        self.assertIn('action_id', response_body)
        action_id = response_body['action_id']

        # Check that the action has the correct values
        resp, response_body = self.freezer_api_client.get_actions(action_id)
        self.assertEqual(200, resp.status)

        resp_body_json = json.loads(response_body)

        self.assertIn('backup_name', resp_body_json)
        backup_name = resp_body_json['backup_name']
        self.assertEqual('test freezer api actions', backup_name)

        self.assertIn('container', resp_body_json)
        container = resp_body_json['container']
        self.assertEqual('test_freezer_api_actions_container', container)

        self.assertIn('no_incremental', resp_body_json)
        no_incremental = resp_body_json['no_incremental']
        self.assertEqual(True, no_incremental)

        self.assertIn('max_backup_level', resp_body_json)
        max_backup_level = resp_body_json['max_backup_level']
        self.assertEqual(1, max_backup_level)

        self.assertIn('hostname', response_body)
        hostname = resp_body_json['hostname']
        self.assertEqual(False, hostname)

        self.assertIn('_version', resp_body_json)
        _version = resp_body_json['_version']
        self.assertEqual(1, _version)

        self.assertIn('actions', resp_body_json)
        actions = resp_body_json['actions']
        self.assertEqual('backup', actions)

        self.assertIn('src_file', resp_body_json)
        src_file = resp_body_json['src_file']
        self.assertEqual('/dev/null', src_file)

        self.assertIn('always_backup_level', resp_body_json)
        always_backup_level = resp_body_json['always_backup_level']
        self.assertEqual(0, always_backup_level)

        self.assertIn('mode', resp_body_json)
        mode = resp_body_json['mode']
        self.assertEqual('fs', mode)

        self.assertIn('encrypt_pass_file', resp_body_json)
        encrypt_pass_file = resp_body_json['encrypt_pass_file']
        self.assertEqual('/dev/null', encrypt_pass_file)

        self.assertIn('max_cpu_priority', resp_body_json)
        max_cpu_priority = resp_body_json['max_cpu_priority']
        self.assertEqual(False, max_cpu_priority)

        self.assertIn('user_id', resp_body_json)
        user_id = resp_body_json['user_id']

        self.assertIn('log_file', resp_body_json)
        log_file = resp_body_json['log_file']
        self.assertEqual('/dev/null', log_file)

        self.assertIn('action_id', resp_body_json)
        action_id_in_resp_body = resp_body_json['action_id']
        self.assertEqual(action_id, action_id_in_resp_body)

        # Update the action backup_name with POST
        action['backup_name'] = 'test freezer api actions update with post'

        resp, response_body = self.freezer_api_client.post_actions(
            action, action_id)
        self.assertEqual(201, resp.status)

        self.assertIn('version', response_body)
        version = response_body['version']
        self.assertEqual(2, version)

        self.assertIn('action_id', response_body)
        action_id_in_resp_body = response_body['action_id']
        self.assertEqual(action_id, action_id_in_resp_body)

        resp, response_body = self.freezer_api_client.get_actions(action_id)
        self.assertEqual(200, resp.status)

        resp_body_json = json.loads(response_body)

        self.assertIn('backup_name', resp_body_json)
        backup_name = resp_body_json['backup_name']
        self.assertEqual('test freezer api actions update with post',
                         backup_name)

        # Update the action backup_name with PATCH
        action['backup_name'] = 'test freezer api actions update with patch'

        resp, response_body = self.freezer_api_client.patch_actions(
            action, action_id)
        self.assertEqual(200, resp.status)

        self.assertIn('version', response_body)
        version = response_body['version']
        self.assertEqual(3, version)

        self.assertIn('action_id', response_body)
        action_id_in_resp_body = response_body['action_id']
        self.assertEqual(action_id, action_id_in_resp_body)

        resp, response_body = self.freezer_api_client.get_actions(action_id)
        self.assertEqual(200, resp.status)

        resp_body_json = json.loads(response_body)

        self.assertIn('backup_name', resp_body_json)
        backup_name = resp_body_json['backup_name']
        self.assertEqual('test freezer api actions update with patch',
                         backup_name)

        # Delete the action
        resp, response_body = self.freezer_api_client.delete_actions(
            action_id)
        self.assertEqual(204, resp.status)
