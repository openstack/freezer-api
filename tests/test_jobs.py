"""Freezer swift.py related tests

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

This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com). This product includes software written by Tim
Hudson (tjh@cryptsoft.com).
========================================================================
"""

import unittest
from mock import Mock, patch

import random
import falcon
import json

from common import *
from freezer_api.common.exceptions import *

from freezer_api.api.v1 import jobs as v1_jobs


class TestJobsCollectionResource(unittest.TestCase):

    def setUp(self):
        self.mock_json_body = Mock()
        self.mock_json_body.return_value = {}
        self.mock_db = Mock()
        self.mock_req = Mock()
        self.mock_req.get_header.return_value = fake_job_0_user_id
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_jobs.JobsCollectionResource(self.mock_db)
        self.resource.json_body = self.mock_json_body

    def test_on_get_return_empty_list(self):
        self.mock_db.search_job.return_value = []
        expected_result = {'jobs': []}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_get_return_correct_list(self):
        self.mock_db.search_job.return_value = [get_fake_job_0(), get_fake_job_1()]
        expected_result = {'jobs': [get_fake_job_0(), get_fake_job_1()]}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_post_inserts_correct_data(self):
        job = get_fake_job_0()
        self.mock_json_body.return_value = job
        self.mock_db.add_job.return_value = 'pjiofrdslaikfunr'
        expected_result = {'job_id': 'pjiofrdslaikfunr'}
        self.resource.on_post(self.mock_req, self.mock_req)
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)
        self.assertEqual(self.mock_req.body, expected_result)


class TestJobsResource(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.mock_req = Mock()
        self.mock_req.stream.read.return_value = {}
        self.mock_req.get_header.return_value = fake_job_0_user_id
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_jobs.JobsResource(self.mock_db)

    def test_create_resource(self):
        self.assertIsInstance(self.resource, v1_jobs.JobsResource)

    def test_on_get_return_no_result_and_404_when_not_found(self):
        self.mock_req.body = None
        self.mock_db.get_job.return_value = None
        self.resource.on_get(self.mock_req, self.mock_req, fake_job_0_job_id)
        self.assertIsNone(self.mock_req.body)
        self.assertEqual(self.mock_req.status, falcon.HTTP_404)

    def test_on_get_return_correct_data(self):
        self.mock_db.get_job.return_value = get_fake_job_0()
        self.resource.on_get(self.mock_req, self.mock_req, fake_job_0_job_id)
        result = self.mock_req.body
        self.assertEqual(result, get_fake_job_0())
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_delete_removes_proper_data(self):
        self.resource.on_delete(self.mock_req, self.mock_req, fake_job_0_job_id)
        result = self.mock_req.body
        expected_result = {'job_id': fake_job_0_job_id}
        self.assertEquals(self.mock_req.status, falcon.HTTP_204)
        self.assertEqual(result, expected_result)

    def test_on_patch_ok_with_some_fields(self):
        new_version = random.randint(0, 99)
        self.mock_db.update_job.return_value = new_version
        patch_doc = {'some_field': 'some_value',
                     'because': 'size_matters'}
        self.mock_req.stream.read.return_value = json.dumps(patch_doc)
        expected_result = {'job_id': fake_job_0_job_id,
                           'version': new_version}
        self.resource.on_patch(self.mock_req, self.mock_req, fake_job_0_job_id)
        self.mock_db.update_job.assert_called_with(
            user_id=fake_job_0_user_id,
            job_id=fake_job_0_job_id,
            patch_doc=patch_doc)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)

    def test_on_post_ok(self):
        new_version = random.randint(0, 99)
        self.mock_db.replace_job.return_value = new_version
        job = get_fake_job_0()
        self.mock_req.stream.read.return_value = json.dumps(job)
        expected_result = {'job_id': fake_job_0_job_id,
                           'version': new_version}

        self.resource.on_post(self.mock_req, self.mock_req, fake_job_0_job_id)
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)
        self.assertEqual(self.mock_req.body, expected_result)

    def test_on_post_raises_when_db_replace_job_raises(self):
        self.mock_db.replace_job.side_effect = AccessForbidden('regular test failure')
        job = get_fake_job_0()
        self.mock_req.stream.read.return_value = json.dumps(job)
        self.assertRaises(AccessForbidden, self.resource.on_post,
                          self.mock_req,
                          self.mock_req,
                          fake_job_0_job_id)
