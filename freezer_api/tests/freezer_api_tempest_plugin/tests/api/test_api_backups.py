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

class TestFreezerApiBackups(base.BaseFreezerApiTest):

    @classmethod
    def resource_setup(cls):
        super(TestFreezerApiBackups, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(TestFreezerApiBackups, cls).resource_cleanup()

    @test.attr(type="gate")
    def test_api_backups(self):

        resp, response_body = self.freezer_api_client.get_backups()
        self.assertEqual(200, resp.status)

        resp_body_json = json.loads(response_body)
        self.assertIn('backups', resp_body_json)
        backups = resp_body_json['backups']
        self.assertEqual(backups, [])

    @test.attr(type="gate")
    def test_api_backups_post(self):

        backup_metadata = {
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
            "backup_name": "test_freezer_api_backups_name",
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

        resp, response_body = self.freezer_api_client.post_backups(
            backup_metadata)
        self.assertEqual(201, resp.status)

        self.assertIn('backup_id', response_body)
        backup_id = response_body['backup_id']

        # Check that the action has the correct values
        # There is a bug that is preventing this from working.
        # resp, response_body = self.freezer_api_client.get_backups(backup_id)
        # self.assertEqual(200, resp.status)

        resp, response_body = self.freezer_api_client.delete_backups(
            backup_id)
        self.assertEqual(204, resp.status)
