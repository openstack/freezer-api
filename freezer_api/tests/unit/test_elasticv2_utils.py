# Copyright 2026, Cleura AB.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from freezer_api.common import elasticv2_utils
from freezer_api.tests.unit import common


class TestElasticV2Utils(common.FreezerBaseTestCase):

    def test_action_doc_create_generates_id_if_missing(self):
        doc = {
            'freezer_action': {
                'action': 'backup',
                'mode': 'fs'
            }
        }
        res = elasticv2_utils.ActionDoc.create(doc, 'user1', 'proj1')
        self.assertIn('action_id', res)
        self.assertTrue(len(res['action_id']) > 0)
        self.assertEqual('user1', res['user_id'])
        self.assertEqual('proj1', res['project_id'])

    def test_action_doc_create_generates_id_if_empty(self):
        doc = {
            'freezer_action': {
                'action': 'backup',
                'mode': 'fs'
            },
            'action_id': ''
        }
        res = elasticv2_utils.ActionDoc.create(doc, 'user1', 'proj1')
        self.assertIn('action_id', res)
        self.assertNotEqual('', res['action_id'])
        self.assertTrue(len(res['action_id']) > 0)

    def test_action_doc_create_preserves_existing_id(self):
        doc = {
            'freezer_action': {
                'action': 'backup',
                'mode': 'fs'
            },
            'action_id': 'my-custom-id'
        }
        res = elasticv2_utils.ActionDoc.create(doc, 'user1', 'proj1')
        self.assertEqual('my-custom-id', res['action_id'])

    def test_job_doc_create_generates_id_if_missing(self):
        doc = {
            'client_id': 'c1',
            'job_actions': []
        }
        res = elasticv2_utils.JobDoc.create(doc, 'proj1', 'user1')
        self.assertIn('job_id', res)
        self.assertTrue(len(res['job_id']) > 0)
        self.assertEqual('user1', res['user_id'])
        self.assertEqual('proj1', res['project_id'])

    def test_job_doc_create_preserves_existing_id(self):
        doc = {
            'client_id': 'c1',
            'job_actions': [],
            'job_id': 'custom-job-id'
        }
        res = elasticv2_utils.JobDoc.create(doc, 'proj1', 'user1')
        self.assertEqual('custom-job-id', res['job_id'])

    def test_job_doc_create_generates_id_if_empty(self):
        doc = {
            'client_id': 'c1',
            'job_actions': [],
            'job_id': ''
        }
        res = elasticv2_utils.JobDoc.create(doc, 'proj1', 'user1')
        self.assertIn('job_id', res)
        self.assertNotEqual('', res['job_id'])
        self.assertTrue(len(res['job_id']) > 0)
