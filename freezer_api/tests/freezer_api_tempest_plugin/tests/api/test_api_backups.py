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

import tempest
from tempest.lib import decorators

from freezer_api.tests.freezer_api_tempest_plugin.tests.api import base


class TestFreezerApiBackups(base.BaseFreezerApiTest):
    credentials = ['primary', 'alt']

    @decorators.attr(type="gate")
    def test_api_backups_list(self):
        for i in range(1, 4):
            self._create_temporary_backup(
                self._build_metadata("test_freezer_backups_" + str(i)))

        resp, response_body = self.freezer_api_client.get_backups()
        self.assertEqual(200, resp.status)

        self.assertIn('backups', response_body)
        backups = response_body['backups']

        self.assertEqual(3, len(backups))

        backup_names = [b['backup_metadata']['backup_name'] for b in backups]
        for i in range(1, 4):
            self.assertIn("test_freezer_backups_" + str(i), backup_names)

    @decorators.attr(type="gate")
    def test_api_backups_list_other_users_backups(self):
        # Test if it is not possible to list backups
        # from a different user
        self._create_temporary_backup(
            self._build_metadata("test_freezer_backups"))

        # Switching to alt_user here
        resp, response_body = self.os_alt.freezer_api_client.get_backups()

        self.assertEqual(200, resp.status)
        self.assertEmpty(response_body['backups'])

    @decorators.attr(type="gate")
    def test_api_backups_list_empty(self):
        resp, response_body = self.freezer_api_client.get_backups()
        self.assertEqual(200, resp.status)

        self.assertEmpty(response_body['backups'])

    @decorators.attr(type="gate")
    def test_api_backups_list_limit(self):
        for i in range(1, 9):
            self._create_temporary_backup(
                self._build_metadata("test_freezer_backups_" + str(i)))

        resp, response_body = self.freezer_api_client.get_backups(limit=5)
        self.assertEqual(200, resp.status)

        self.assertIn('backups', response_body)
        backups = response_body['backups']
        self.assertEqual(5, len(backups))

        # limits <= 0 should return an error (bad request)
        for bad_limit in [0, -1, -2]:
            self.assertRaises(tempest.lib.exceptions.BadRequest,
                              self.freezer_api_client.get_actions,
                              limit=bad_limit)

    @decorators.attr(type="gate")
    def test_api_backups_list_offset(self):
        for i in range(1, 9):
            self._create_temporary_backup(
                self._build_metadata("test_freezer_backups_" + str(i)))

        # valid offsets should return the correct number of entries
        resp, response_body = self.freezer_api_client.get_backups(offset=0)
        self.assertEqual(200, resp.status)
        self.assertEqual(8, len(response_body['backups']))

        resp, response_body = self.freezer_api_client.get_backups(offset=5)
        self.assertEqual(200, resp.status)
        self.assertEqual(3, len(response_body['backups']))

        resp, response_body = self.freezer_api_client.get_backups(offset=8)
        self.assertEqual(200, resp.status)
        self.assertEqual(0, len(response_body['backups']))

        # an offset greater than the number of entries should successfully
        # return no entries
        resp, response_body = self.freezer_api_client.get_backups(offset=10)
        self.assertEqual(200, resp.status)
        self.assertEqual(0, len(response_body['backups']))

        # negative offsets should raise an error
        self.assertRaises(tempest.lib.exceptions.BadRequest,
                          self.freezer_api_client.get_backups, offset=-1)

        self.assertRaises(tempest.lib.exceptions.BadRequest,
                          self.freezer_api_client.get_backups, offset=-2)

    @decorators.attr(type="gate")
    def test_api_backups_list_limit_offset(self):
        """ Test pagination by grabbing the backups in two steps and
        comparing to the list of all backups.
        """
        for i in range(1, 9):
            self._create_temporary_backup(
                self._build_metadata("test_freezer_backups_" + str(i)))

        resp, response_body = self.freezer_api_client.get_backups(limit=5)
        self.assertEqual(200, resp.status)

        self.assertIn('backups', response_body)
        first_5_backups = response_body['backups']
        self.assertEqual(5, len(first_5_backups))

        resp, response_body = self.freezer_api_client.get_backups(limit=3,
                                                                  offset=5)
        second_3_backups = response_body['backups']
        self.assertEqual(3, len(second_3_backups))

        resp, response_body = self.freezer_api_client.get_backups()
        all_backups = response_body['backups']

        self.assertEqual(len(all_backups),
                         len(first_5_backups + second_3_backups))
        self.assertEqual(all_backups, first_5_backups + second_3_backups)

    @decorators.attr(type="gate")
    def test_api_backups_post(self):
        metadata = self._build_metadata("test_freezer_backups")
        backup_id = self._create_temporary_backup(metadata)

        resp, response_body = self._workaround_get_backup(backup_id)

        expected = self._build_expected_data(backup_id, metadata)

        # backup_id is generated automatically, we can't know it
        del(response_body['backup_id'])

        self.assertEqual(200, resp.status)
        self.assertEqual(expected, response_body)

    @decorators.attr(type="gate")
    def test_api_backups_post_without_content_type(self):
        """ Test the backup endpoint without content-type=application/json.

        It's expected to work regardless of whether content-type is set or not.
        """
        metadata = self._build_metadata("test_freezer_backups")

        uri = '/v1/backups'
        request_body = json.dumps(metadata)

        # Passing in an empty dict for headers to avoid automatically
        # generating headers
        resp, response_body = self.freezer_api_client.post(uri, request_body,
                                                           headers={})

        self.assertEqual(resp.status, 201)

    @decorators.attr(type="gate")
    def test_api_backups_post_incomplete(self):
        metadata = self._build_metadata("test_freezer_backups")
        del (metadata['container'])

        self.assertRaises(tempest.lib.exceptions.BadRequest,
                          self.freezer_api_client.post_backups, metadata)

    @decorators.attr(type="gate")
    def test_api_backups_post_minimal(self):
        metadata = {
            "curr_backup_level": 0,
            "container": "test_freezer_api_backups_container",
            "hostname": "localhost",
            "backup_name": "test_freezer_backups",
            "time_stamp": 1459349846,
        }

        backup_id = self._create_temporary_backup(metadata)
        resp, response_body = self._workaround_get_backup(backup_id)

        expected = self._build_expected_data(backup_id, metadata)

        # backup_id is generated automatically, we can't know it
        del(response_body['backup_id'])

        self.assertEqual(200, resp.status)
        self.assertEqual(expected, response_body)

    @decorators.attr(type="gate")
    def test_api_backups_delete(self):
        metadata = self._build_metadata("test_freezer_backups")
        backup_id = self._create_temporary_backup(metadata)

        self.freezer_api_client.delete_backups(backup_id)

        resp, response_body = self.freezer_api_client.get_backups()
        self.assertEqual(0, len(response_body['backups']))

    @decorators.attr(type="gate")
    def test_api_backups_delete_other_users_backups(self):
        metadata = self._build_metadata("test_freezer_backups")
        backup_id = self._create_temporary_backup(metadata)

        # Switching user
        resp, response_body = self.os_alt.freezer_api_client.delete_backups(
            backup_id)
        self.assertEqual('204', resp['status'])
        self.assertEmpty(response_body)

        # Switching back to original user
        resp, response_body = self.freezer_api_client.get_backups()
        self.assertEqual(1, len(response_body['backups']))

    def _build_expected_data(self, backup_id, metadata):
        return {
            'user_name': self.os_primary.credentials.username,
            'user_id': self.os_primary.credentials.user_id,
            'backup_metadata': metadata
        }

    def _build_metadata(self, backup_name):
        return {
            "action": "backup",
            "always_level": "",
            "backup_media": "fs",
            "client_id": "freezer",
            "client_version": "1.2.18",
            "container_segments": "",
            "curr_backup_level": 0,
            "dry_run": "",
            "log_file": "",
            "job_id": "76cf6739ca2e4dc58b2215632c2a0b49",
            "os_auth_version": "",
            "path_to_backup": "/dev/null",
            "proxy": "",
            "ssh_host": "",
            "ssh_key": "",
            "ssh_port": 22,
            "ssh_username": "",
            "storage": "swift",
            "container": "test_freezer_api_backups_container",
            "hostname": "localhost",
            "backup_name": backup_name,
            "time_stamp": 1459349846,
            "level": 1,
            "max_level": 14,
            "mode": "fs",
            "fs_real_path": "/dev/null",
            "vol_snap_path": "",
            "total_broken_links": 1,
            "total_fs_files": 100,
            "total_directories": 100,
            "backup_size_uncompressed": 10000,
            "backup_size_compressed": 1000,
            "compression": "gzip",
            "encrypted": False,
            "client_os": "linux2",
            "broken_links": [],
            "excluded_files": [],
            "cli": "freezer",
            "version": "1.0"
        }

    def _create_temporary_backup(self, metadata):
        resp, response_body = self.freezer_api_client.post_backups(metadata)

        self.assertEqual('201', resp['status'])

        self.assertIn('backup_id', response_body)
        backup_id = response_body['backup_id']

        self.addCleanup(self.freezer_api_client.delete_backups, backup_id)

        return backup_id

    def _workaround_get_backup(self, backup_id):
        # TODO(JonasPf): Use the following line, once this bug is fixed:
        # https://bugs.launchpad.net/freezer/+bug/1564649
        # resp, response_body = self.freezer_api_client.get_backups(backup_id)
        resp, response_body = self.freezer_api_client.get_backups()

        result = next((b for b in response_body['backups'] if
                       b['backup_id'] == backup_id))
        return resp, result
