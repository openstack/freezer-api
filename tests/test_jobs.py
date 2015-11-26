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

"""

import unittest
from mock import Mock, patch

import random
import json

from common import *
from freezer_api.common.exceptions import *

from freezer_api.api.v1 import jobs as v1_jobs


class TestJobsBaseResource(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.resource = v1_jobs.JobsBaseResource(self.mock_db)

    def test_get_action_returns_found_action(self):
        self.mock_db.get_action.return_value = 'awesome_result'
        result = self.resource.get_action('user-id', 'action-id')
        self.assertEquals(result, 'awesome_result')

    def test_get_action_returns_none_when_action_not_found(self):
        self.mock_db.get_action.side_effect = DocumentNotFound('regular test failure')
        result = self.resource.get_action('user-id', 'action-id')
        self.assertIsNone(result)

    def test_update_actions_in_job_no_action_id(self):
        self.resource.get_action = Mock()
        self.resource.get_action.return_value = None
        action_doc = {
                #"action_id": "ottonero",
                "freezer_action": {
                                "mode" : "mysql",
                                "container": "freezer_backup_test"
                },
                "max_retries": 3
            }
        job_doc = {"job_actions": [action_doc.copy()],
                   "description": "three actions backup"
                   }
        self.resource.update_actions_in_job('duder', job_doc=job_doc)
        self.mock_db.add_action.assert_called_with(user_id='duder',
                                                   doc=action_doc)

    def test_update_actions_in_job_action_id_not_found(self):
        self.resource.get_action = Mock()
        self.resource.get_action.return_value = None
        action_doc = {
                "action_id": "ottonero",
                "freezer_action": {
                                "mode" : "mysql",
                                "container": "freezer_backup_test"
                },
                "max_retries": 3
            }
        job_doc = {"job_actions": [action_doc.copy()],
                   "description": "three actions backup"
                   }
        self.resource.update_actions_in_job('duder', job_doc=job_doc)
        self.mock_db.add_action.assert_called_with(user_id='duder',
                                                   doc=action_doc)

    def test_update_actions_in_job_action_id_found_and_same_action(self):
        self.resource.get_action = Mock()
        action_doc = {
                "action_id": "ottonero",
                "freezer_action": {
                                "mode" : "mysql",
                                "container": "freezer_backup_test"
                },
                "max_retries": 3
            }
        job_doc = {"job_actions": [action_doc.copy()],
                   "description": "three actions backup"
                   }
        self.resource.get_action.return_value = action_doc.copy()
        self.resource.update_actions_in_job('duder', job_doc=job_doc)
        self.mock_db.add_action.assert_not_called()

    def test_update_actions_in_job_action_id_found_and_different_action(self):
        self.resource.get_action = Mock()
        action_doc = {
                "action_id": "ottonero",
                "freezer_action": {
                                "mode" : "mysql",
                                "container": "freezer_backup_test"
                },
                "max_retries": 3
            }
        job_doc = {"job_actions": [action_doc.copy()],
                   "description": "three actions backup"
                   }

        found_action = {
                "action_id": "ottonero",
                "freezer_action": {
                                "mode" : "mysql",
                                "container": "different_drum"
                },
                "max_retries": 4
            }

        new_doc = action_doc.copy()
        new_doc['action_id'] = ''
        self.resource.get_action.return_value = found_action
        self.resource.update_actions_in_job('duder', job_doc=job_doc)
        self.mock_db.add_action.assert_called_with(user_id='duder',
                                                   doc=new_doc)


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
                     'because': 'size_matters',
                     'job_schedule': {}}
        self.mock_req.stream.read.return_value = json.dumps(patch_doc)
        expected_result = {'job_id': fake_job_0_job_id,
                           'version': new_version}
        self.resource.update_actions_in_job = Mock()
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


class TestJobsEvent(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.mock_req = Mock()
        self.mock_req.get_header.return_value = fake_session_0['user_id']
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_jobs.JobsEvent(self.mock_db)
        self.mock_json_body = Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_create_resource(self):
        self.assertIsInstance(self.resource, v1_jobs.JobsEvent)

    def test_on_post_raises_when_unable_to_read_event_from_body(self):
        self.mock_json_body.return_value = {}
        self.assertRaises(BadDataFormat, self.resource.on_post,
                          self.mock_req,
                          self.mock_req,
                          'my_job_id')

    def test_on_post_start_event_ok(self):
        new_version = random.randint(0, 99)
        self.mock_db.get_job.return_value = {
            'job_schedule': {
                'status': 'stop'
            }
        }
        self.mock_db.replace_job.return_value = new_version
        event = {"start": None}
        self.mock_json_body.return_value = event
        expected_result = {'result': 'success'}
        self.resource.on_post(self.mock_req, self.mock_req, 'my_job_id')
        self.assertEqual(self.mock_req.status, falcon.HTTP_202)
        self.assertEqual(self.mock_req.body, expected_result)


class TestJobs(unittest.TestCase):

    def test_start_raises_BadDataFormat_when_jobstatus_unexpected(self):
        job_doc = {'job_schedule':
            {
                'status': 'complicated',
                'event': 'boost'
            }
        }
        job = v1_jobs.Job(job_doc)
        self.assertRaises(BadDataFormat, job.start)

    def test_start_scheduled_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'scheduled'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.start()
        self.assertEquals(res, 'already active')
        self.assertFalse(job.need_update)

    def test_start_running_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'running'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.start()
        self.assertEquals(res, 'already active')
        self.assertFalse(job.need_update)

    def test_start_stopped_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'stop'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.start()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], 'stop')
        self.assertEqual(job.doc['job_schedule']['event'], 'start')
        self.assertTrue(job.need_update)

    def test_start_completed_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'completed'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.start()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], 'stop')
        self.assertEqual(job.doc['job_schedule']['event'], 'start')
        self.assertTrue(job.need_update)

    def test_start_job_with_no_status(self):
        job_doc = {'job_schedule':
            {
                'status': ''
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.start()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], 'stop')
        self.assertEqual(job.doc['job_schedule']['event'], 'start')
        self.assertTrue(job.need_update)

    def test_stop_scheduled_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'scheduled'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.stop()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], 'scheduled')
        self.assertEqual(job.doc['job_schedule']['event'], 'stop')
        self.assertTrue(job.need_update)

    def test_stop_running_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'running'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.stop()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], 'running')
        self.assertEqual(job.doc['job_schedule']['event'], 'stop')
        self.assertTrue(job.need_update)

    def test_stop_job_with_no_status(self):
        job_doc = {'job_schedule':
            {
                'status': ''
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.stop()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], '')
        self.assertEqual(job.doc['job_schedule']['event'], 'stop')
        self.assertTrue(job.need_update)

    def test_stop_not_active_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'whatever'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.stop()
        self.assertEquals(res, 'already stopped')
        self.assertFalse(job.need_update)

    def test_abort_scheduled_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'scheduled'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.abort()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], 'scheduled')
        self.assertEqual(job.doc['job_schedule']['event'], 'abort')
        self.assertTrue(job.need_update)

    def test_abort_running_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'running'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.abort()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], 'running')
        self.assertEqual(job.doc['job_schedule']['event'], 'abort')
        self.assertTrue(job.need_update)

    def test_abort_job_with_no_status(self):
        job_doc = {'job_schedule':
            {
                'status': ''
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.abort()
        self.assertEquals(res, 'success')
        self.assertEqual(job.doc['job_schedule']['status'], '')
        self.assertEqual(job.doc['job_schedule']['event'], 'abort')
        self.assertTrue(job.need_update)

    def test_abort_not_active_job(self):
        job_doc = {'job_schedule':
            {
                'status': 'whatever'
            }
        }
        job = v1_jobs.Job(job_doc)
        res = job.abort()
        self.assertEquals(res, 'already stopped')
        self.assertFalse(job.need_update)

    @patch.object(v1_jobs.Job, 'start')
    def test_execute_start_event(self, mock_start):
        job = v1_jobs.Job({})
        res = job.execute_event('start', 'my_params')
        mock_start.assert_called_once_with('my_params')

    @patch.object(v1_jobs.Job, 'stop')
    def test_execute_start_event(self, mock_stop):
        job = v1_jobs.Job({})
        res = job.execute_event('stop', 'my_params')
        mock_stop.assert_called_once_with('my_params')

    @patch.object(v1_jobs.Job, 'abort')
    def test_execute_start_event(self, mock_abort):
        job = v1_jobs.Job({})
        res = job.execute_event('abort', 'my_params')
        mock_abort.assert_called_once_with('my_params')

    def test_execute_raises_BadDataFormat_when_event_not_implemented(self):
        job = v1_jobs.Job({})
        self.assertRaises(BadDataFormat, job.execute_event, 'smile', 'my_params')

    def test_expand_action_defaults(self):
        job_doc = {
            'action_defaults': {'that_field': 'that_value'},
            'job_actions': [
                {'freezer_action': {'not_that_field': 'some_value'}},
                {'freezer_action': {'that_field': 'another_value'}}
            ]
        }
        expected_job_doc = {
            'job_actions': [
                {'freezer_action': {'not_that_field': 'some_value',
                                    'that_field': 'that_value'}},
                {'freezer_action': {'that_field': 'another_value'}}
            ],
            'job_schedule': {}
        }
        job = v1_jobs.Job(job_doc)
        self.assertEqual(job.doc, expected_job_doc)
