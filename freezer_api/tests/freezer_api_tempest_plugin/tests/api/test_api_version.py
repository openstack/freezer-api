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

from tempest.lib import decorators

from freezer_api.tests.freezer_api_tempest_plugin.tests.api import base


class TestFreezerApiVersion(base.BaseFreezerApiTest):
    @classmethod
    def resource_setup(cls):
        super(TestFreezerApiVersion, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(TestFreezerApiVersion, cls).resource_cleanup()

    @decorators.attr(type="gate")
    def test_api_version(self):
        resp, response_body = self.freezer_api_client.get_version()
        self.assertEqual(300, resp.status)

        resp_body_json = json.loads(response_body)
        self.assertIn('versions', resp_body_json)
        current_version = resp_body_json['versions'][1]
        self.assertEqual(len(current_version), 4)
        self.assertIn('id', current_version)
        self.assertEqual(current_version['id'], 'v1')
        self.assertIn('links', current_version)
        links = current_version['links'][0]
        self.assertIn('href', links)
        href = links['href']
        self.assertIn('/v1/', href)
        self.assertIn('rel', links)
        rel = links['rel']
        self.assertEqual('self', rel)
        self.assertIn('status', current_version)
        status = current_version['status']
        self.assertEqual('CURRENT', status)
        self.assertIn('updated', current_version)

    @decorators.attr(type="gate")
    def test_api_version_v1(self):
        resp, response_body = self.freezer_api_client.get_version_v1()
        self.assertEqual(200, resp.status)

        response_body_jason = json.loads(response_body)
        self.assertIn('resources', response_body_jason)
        resource = response_body_jason['resources']
        self.assertIn('rel/backups', resource)
        rel_backups = resource['rel/backups']
        self.assertIn('href-template', rel_backups)
        href_template = rel_backups['href-template']
        self.assertEqual('/v1/backups/{backup_id}', href_template)
        self.assertIn('href-vars', rel_backups)
        href_vars = rel_backups['href-vars']
        self.assertIn('backup_id', href_vars)
        backup_id = href_vars['backup_id']
        self.assertEqual('param/backup_id', backup_id)
        self.assertIn('hints', rel_backups)
        hints = rel_backups['hints']
        self.assertIn('allow', hints)
        allow = hints['allow']
        self.assertEqual('GET', allow[0])
        self.assertIn('formats', hints)
        formats = hints['formats']
        self.assertIn('application/json', formats)

    @decorators.attr(type="gate")
    def test_api_version_v2(self):
        resp, response_body = self.freezer_api_client.get_version_v2()
        self.assertEqual(200, resp.status)

        response_body_jason = json.loads(response_body)
        self.assertIn('resources', response_body_jason)
        resource = response_body_jason['resources']
        self.assertIn('rel/backups', resource)
        rel_backups = resource['rel/backups']
        self.assertIn('href-template', rel_backups)
        href_template = rel_backups['href-template']
        self.assertEqual('/v2/{project_id}/backups/{backup_id}', href_template)
        self.assertIn('href-vars', rel_backups)
        href_vars = rel_backups['href-vars']
        self.assertIn('backup_id', href_vars)
        self.assertIn('project_id', href_vars)
        backup_id = href_vars['backup_id']
        self.assertEqual('param/backup_id', backup_id)
        project_id = href_vars['project_id']
        self.assertEqual('param/project_id', project_id)
        self.assertIn('hints', rel_backups)
        hints = rel_backups['hints']
        self.assertIn('allow', hints)
        allow = hints['allow']
        self.assertEqual('GET', allow[0])
        self.assertIn('formats', hints)
        formats = hints['formats']
        self.assertIn('application/json', formats)
