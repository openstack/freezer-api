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

from freezer_api.tests.unit import common
from freezer_api.tests.unit.sqlalchemy import base


class DbClientTestCase(base.DbTestCase):

    def setUp(self):
        super().setUp()
        self.fake_client_0 = common.get_fake_client_0()
        self.fake_client_doc = self.fake_client_0.get('client')
        self.fake_user_id = self.fake_client_0.get('user_id')
        self.fake_project_id = self.fake_client_doc.get('project_id')

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
