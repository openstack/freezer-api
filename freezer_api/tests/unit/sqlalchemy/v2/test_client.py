# (c) Copyright 2018 ZTE Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Tests for manipulating  Client via the DB API"""


import copy
from unittest import mock

from freezer_api.common import exceptions
from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbClientTestCase(base.DbTestCase):

    def setUp(self):
        super().setUp()
        self.fake_client_0 = common.get_fake_client_0()
        self.fake_client_doc = self.fake_client_0.get('client')
        self.fake_user_id = self.fake_client_0.get('user_id')
        self.fake_project_id = self.fake_client_doc.get('project_id')

    def test_decode_capability_none(self):
        result = self.dbapi.decode_capability(None)
        self.assertEqual([], result)

    def test_decode_capability_value(self):
        result = self.dbapi.decode_capability('["backup"]')
        self.assertEqual(['backup'], result)

    def test_add_and_get_client(self):
        client_doc = copy.deepcopy(self.fake_client_doc)
        client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                          doc=client_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(client_id)

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       client_id=client_id)

        self.assertIsNotNone(result)

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0].get('user_id'),
                         self.fake_user_id)

        client = result[0].get('client')

        self.assertEqual(client.get('client_id'),
                         self.fake_client_doc.get('client_id'))

        self.assertEqual(client.get('description'),
                         self.fake_client_doc.get('description'))
        self.assertEqual(client.get('supported_actions'),
                         self.fake_client_doc.get('supported_actions'))
        self.assertEqual(client.get('supported_modes'),
                         self.fake_client_doc.get('supported_modes'))
        self.assertEqual(client.get('supported_storages'),
                         self.fake_client_doc.get('supported_storages'))
        self.assertEqual(client.get('supported_engines'),
                         self.fake_client_doc.get('supported_engines'))

    def test_add_and_delete_client(self):
        client_doc = copy.deepcopy(self.fake_client_doc)
        client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                          doc=client_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(client_id)

        result = self.dbapi.delete_client(project_id=self.fake_project_id,
                                          user_id=self.fake_user_id,
                                          client_id=client_id)

        self.assertIsNotNone(result)

        self.assertEqual(result, client_id)

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       client_id=client_id)

        self.assertEqual(len(result), 0)

    def test_add_and_search_client(self):
        count = 0
        clientids = []
        while (count < 20):
            client_doc = copy.deepcopy(self.fake_client_doc)
            clientid = common.get_fake_client_id()
            client_doc['client_id'] = clientid
            client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                              doc=client_doc,
                                              project_id=self.fake_project_id)
            self.assertIsNotNone(client_id)
            self.assertEqual(clientid, client_id)
            clientids.append(client_id)
            count += 1

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=10,
                                       offset=0)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 10)

        for index in range(len(result)):
            clientmap = result[index]
            clientid = clientmap['client'].get('client_id')
            self.assertEqual(clientids[index], clientid)

    def test_add_and_search_client_with_search_match_and_match_not(self):
        count = 0
        clientids = []
        while (count < 20):
            client_doc = copy.deepcopy(self.fake_client_doc)
            clientid = common.get_fake_client_id()
            client_doc['client_id'] = clientid
            client_doc['hostname'] = "node1"
            if count in [0, 4, 8, 12, 16]:
                client_doc['description'] = "tecs"
                if count in [4, 12]:
                    client_doc['hostname'] = 'node2'

            client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                              doc=client_doc,
                                              project_id=self.fake_project_id)
            self.assertIsNotNone(client_id)
            self.assertEqual(clientid, client_id)
            clientids.append(client_id)
            count += 1

        search_opt = {'match_not': [{'hostname': 'node2'}],
                      'match': [{'description': 'tecs'}]}

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=20,
                                       offset=0,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)

        for index in range(len(result)):
            clientmap = result[index]
            hostname = clientmap['client'].get('hostname')
            description = clientmap['client'].get('description')
            self.assertEqual('node1', hostname)
            self.assertEqual('tecs', description)

    def test_add_and_search_client_with_search_match_list(self):
        count = 0
        clientids = []
        while (count < 20):
            client_doc = copy.deepcopy(self.fake_client_doc)
            clientid = common.get_fake_client_id()
            client_doc['client_id'] = clientid
            client_doc['hostname'] = "node1"
            if count in [0, 4, 8, 12, 16]:
                client_doc['description'] = "tecs"
                if count in [4, 12]:
                    client_doc['hostname'] = 'node2'

            client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                              doc=client_doc,
                                              project_id=self.fake_project_id)
            self.assertIsNotNone(client_id)
            self.assertEqual(clientid, client_id)
            clientids.append(client_id)
            count += 1

        search_opt = {'match': [{'hostname': 'node2'},
                                {'description': 'tecs'}]}

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=20,
                                       offset=0,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

        for index in range(len(result)):
            clientmap = result[index]
            hostname = clientmap['client'].get('hostname')
            description = clientmap['client'].get('description')
            self.assertEqual('node2', hostname)
            self.assertEqual('tecs', description)

    def test_add_and_search_client_with_search_match_not_list(self):
        count = 0
        clientids = []
        while (count < 20):
            client_doc = copy.deepcopy(self.fake_client_doc)
            clientid = common.get_fake_client_id()
            client_doc['client_id'] = clientid
            client_doc['hostname'] = "node1"
            if count in [0, 4, 8, 12, 16]:
                client_doc['description'] = "tecs"
                if count in [4, 12]:
                    client_doc['hostname'] = 'node2'

            client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                              doc=client_doc,
                                              project_id=self.fake_project_id)
            self.assertIsNotNone(client_id)
            self.assertEqual(clientid, client_id)
            clientids.append(client_id)
            count += 1

        search_opt = {'match_not': [{'hostname': 'node2'},
                                    {'description': 'some usefule text here'}]}

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=20,
                                       offset=0,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)

        for index in range(len(result)):
            clientmap = result[index]
            hostname = clientmap['client'].get('hostname')
            description = clientmap['client'].get('description')
            self.assertEqual('node1', hostname)
            self.assertEqual('tecs', description)

    def test_add_and_search_client_with_all_opt_one_match(self):
        count = 0
        clientids = []
        while (count < 20):
            client_doc = copy.deepcopy(self.fake_client_doc)
            clientid = common.get_fake_client_id()
            client_doc['client_id'] = clientid
            client_doc['hostname'] = "node1"
            if count in [0, 4, 8, 12, 16]:
                client_doc['description'] = "tecs"

            client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                              doc=client_doc,
                                              project_id=self.fake_project_id)
            self.assertIsNotNone(client_id)
            self.assertEqual(clientid, client_id)
            clientids.append(client_id)
            count += 1

        search_opt = {'match': [{'_all': '[{"description": "tecs"}]'}]}

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=20,
                                       offset=0,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)

        for index in range(len(result)):
            clientmap = result[index]
            description = clientmap['client'].get('description')
            self.assertEqual('tecs', description)

    def test_add_and_search_client_with_all_opt_two_match(self):
        count = 0
        clientids = []
        while (count < 20):
            client_doc = copy.deepcopy(self.fake_client_doc)
            clientid = common.get_fake_client_id()
            client_doc['client_id'] = clientid
            client_doc['hostname'] = "node1"
            if count in [0, 4, 8, 12, 16]:
                client_doc['hostname'] = "node2"
            if count in [4, 12]:
                client_doc['description'] = "tecs"

            client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                              doc=client_doc,
                                              project_id=self.fake_project_id)
            self.assertIsNotNone(client_id)
            self.assertEqual(clientid, client_id)
            clientids.append(client_id)
            count += 1

        search_opt = {'match':
                      [{'_all':
                        '[{"description": "tecs"}, '
                        '{"hostname": "node2"}]'}]}

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=20,
                                       offset=0,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

        for index in range(len(result)):
            clientmap = result[index]
            description = clientmap['client'].get('description')
            hostname = clientmap['client'].get('hostname')
            self.assertEqual('tecs', description)
            self.assertEqual('node2', hostname)

    def test_add_and_search_client_with_error_all_opt_return_alltuples(self):
        count = 0
        clientids = []
        while (count < 20):
            client_doc = copy.deepcopy(self.fake_client_doc)
            clientid = common.get_fake_client_id()
            client_doc['client_id'] = clientid
            client_doc['hostname'] = "node1"
            if count in [0, 4, 8, 12, 16]:
                client_doc['hostname'] = "node2"

            client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                              doc=client_doc,
                                              project_id=self.fake_project_id)
            self.assertIsNotNone(client_id)
            self.assertEqual(clientid, client_id)
            clientids.append(client_id)
            count += 1

        search_opt = {'match': [{'_all': '{"hostname": "node2"}'}]}
        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=20,
                                       offset=0,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)

        search_opt = {'match': [{'_all': 'hostname=node2'}]}
        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       limit=20,
                                       offset=0,
                                       search=search_opt)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 20)

    def test_add_client_update(self):
        client_doc = copy.deepcopy(self.fake_client_doc)
        client_id = self.dbapi.add_client(user_id=self.fake_user_id,
                                          doc=client_doc,
                                          project_id=self.fake_project_id)
        self.assertIsNotNone(client_id)

        # Update description
        client_doc['description'] = 'Updated description'
        updated_client_id = self.dbapi.add_client(
            user_id=self.fake_user_id,
            doc=client_doc,
            project_id=self.fake_project_id)

        self.assertEqual(client_id, updated_client_id)

        result = self.dbapi.get_client(project_id=self.fake_project_id,
                                       user_id=self.fake_user_id,
                                       client_id=client_id)

        self.assertEqual(
            result[0]['client'].get('description'),
            'Updated description'
        )

    def test_add_client_update_forbidden(self):
        client_doc = copy.deepcopy(self.fake_client_doc)
        client_doc['is_central'] = True
        # Register in project 1
        self.dbapi.add_client(user_id=self.fake_user_id,
                              doc=client_doc,
                              project_id='project_1')

        # Try to update in project 2 (hijack)
        self.assertRaises(exceptions.DocumentExists, self.dbapi.add_client,
                          user_id=self.fake_user_id,
                          doc=client_doc,
                          project_id='project_2')

    def test_add_client_update_ignores_owner_change(self):
        client_doc = copy.deepcopy(self.fake_client_doc)
        client_id = self.dbapi.add_client(user_id='original_user',
                                          doc=client_doc,
                                          project_id='original_project')

        # Try to update, but provide different owner info in doc
        # (The API should ignore these and use the authenticated project/user)
        update_doc = copy.deepcopy(client_doc)
        update_doc['project_id'] = 'malicious_project'
        update_doc['user_id'] = 'malicious_user'
        update_doc['description'] = 'Updated description'

        self.dbapi.add_client(user_id='original_user',
                              doc=update_doc,
                              project_id='original_project')

        # Verify record still belongs to original project/user
        res = self.dbapi.get_client_byid(user_id='original_user',
                                         client_id=client_id,
                                         project_id='original_project')
        self.assertEqual(1, len(res))
        self.assertEqual('original_project', res[0].project_id)
        self.assertEqual('original_user', res[0].user_id)
        self.assertEqual('Updated description', res[0].description)

    def test_add_client_different_projects_same_id(self):
        client_id = self.fake_client_doc['client_id']

        # Register in project 1 (using unique copy)
        self.dbapi.add_client(user_id='user_1',
                              doc=copy.deepcopy(self.fake_client_doc),
                              project_id='project_1')

        # Register same client_id in project 2 (using unique copy)
        self.dbapi.add_client(user_id='user_2',
                              doc=copy.deepcopy(self.fake_client_doc),
                              project_id='project_2')

        # Verify they are separate records
        res1 = self.dbapi.get_client_byid(user_id='user_1',
                                          client_id=client_id,
                                          project_id='project_1')
        res2 = self.dbapi.get_client_byid(user_id='user_2',
                                          client_id=client_id,
                                          project_id='project_2')

        self.assertEqual(1, len(res1))
        self.assertEqual(1, len(res2))
        self.assertEqual('project_1', res1[0].project_id)
        self.assertEqual('project_2', res2[0].project_id)
        self.assertNotEqual(res1[0].uuid, res2[0].uuid)

    def test_add_client_no_change_no_update(self):
        client_doc = copy.deepcopy(self.fake_client_doc)
        # Ensure description is present
        client_doc['description'] = 'same description'

        # First registration
        self.dbapi.add_client(user_id=self.fake_user_id,
                              doc=client_doc,
                              project_id=self.fake_project_id)

        # Second registration with same data
        # We patch the low-level update_tuple to verify it's skipped
        with mock.patch('freezer_api.db.sqlalchemy.api.update_tuple') as \
                mock_upd:
            self.dbapi.add_client(user_id=self.fake_user_id,
                                  doc=client_doc,
                                  project_id=self.fake_project_id)
            mock_upd.assert_not_called()
