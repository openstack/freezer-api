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

import json
import random

import falcon
import mock
from mock import patch

from freezer_api.api.v1 import jobs as v1_jobs
from freezer_api.common import exceptions
from freezer_api.tests.unit import common


class TestJobsBaseResource(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestJobsBaseResource, self).setUp()
        self.mock_db = mock.Mock()
        self.resource = v1_jobs.JobsBaseResource(self.mock_db)

    def test_get_action_returns_found_action(self):
        self.mock_db.get_action.return_value = 'awesome_result'
        result = self.resource.get_action('user-id', 'action-id')
        self.assertEqual(result, 'awesome_result')

    def test_get_action_returns_none_when_action_not_found(self):
        self.mock_db.get_action.side_effect = exceptions.DocumentNotFound(
            'regular test failure')
        result = self.resource.get_action('user-id', 'action-id')
        self.assertIsNone(result)

    def test_update_actions_in_job_no_action_id(self):
        self.resource.get_action = mock.Mock()
        self.resource.get_action.return_value = None
        action_doc = {
            # "action_id": "ottonero",
            "freezer_action": {
                "mode": "mysql",
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
        self.resource.get_action = mock.Mock()
        self.resource.get_action.return_value = None
        action_doc = {
            "action_id": "ottonero",
            "freezer_action": {
                "mode": "mysql",
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
        self.resource.get_action = mock.Mock()
        action_doc = {
            "action_id": "ottonero",
            "freezer_action": {
                "mode": "mysql",
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
        self.resource.get_action = mock.Mock()
        action_doc = {
            "action_id": "ottonero",
            "freezer_action": {
                "mode": "mysql",
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
                "mode": "mysql",
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


class TestJobsCollectionResource(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestJobsCollectionResource, self).setUp()
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = common.fake_job_0_user_id
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
        self.mock_db.search_job.return_value = [common.get_fake_job_0(),
                                                common.get_fake_job_1()]
        expected_result = {
            'jobs': [common.get_fake_job_0(), common.get_fake_job_1()]}
        self.resource.on_get(self.mock_req, self.mock_req)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_post_inserts_correct_data(self):
        job = common.get_fake_job_0()
        self.mock_json_body.return_value = job
        self.mock_db.add_job.return_value = 'pjiofrdslaikfunr'
        expected_result = {'job_id': 'pjiofrdslaikfunr'}
        self.resource.on_post(self.mock_req, self.mock_req)
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)
        self.assertEqual(self.mock_req.body, expected_result)


class TestJobsResource(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestJobsResource, self).setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.stream.read.return_value = {}
        self.mock_req.get_header.return_value = common.fake_job_0_user_id
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_jobs.JobsResource(self.mock_db)

    def test_create_resource(self):
        self.assertIsInstance(self.resource, v1_jobs.JobsResource)

    def test_on_get_return_no_result_and_404_when_not_found(self):
        self.mock_req.body = None
        self.mock_db.get_job.return_value = None
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_job_0_job_id)
        self.assertIsNone(self.mock_req.body)
        self.assertEqual(self.mock_req.status, falcon.HTTP_404)

    def test_on_get_return_correct_data(self):
        self.mock_db.get_job.return_value = common.get_fake_job_0()
        self.resource.on_get(self.mock_req, self.mock_req,
                             common.fake_job_0_job_id)
        result = self.mock_req.body
        self.assertEqual(result, common.get_fake_job_0())
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)

    def test_on_delete_removes_proper_data(self):
        self.resource.on_delete(self.mock_req, self.mock_req,
                                common.fake_job_0_job_id)
        result = self.mock_req.body
        expected_result = {'job_id': common.fake_job_0_job_id}
        self.assertEqual(self.mock_req.status, falcon.HTTP_204)
        self.assertEqual(result, expected_result)

    def test_on_patch_ok_with_some_fields(self):
        new_version = random.randint(0, 99)
        self.mock_db.update_job.return_value = new_version
        patch_doc = {'some_field': 'some_value',
                     'because': 'size_matters',
                     'job_schedule': {}}
        self.mock_req.stream.read.return_value = json.dumps(patch_doc)
        expected_result = {'job_id': common.fake_job_0_job_id,
                           'version': new_version}
        self.resource.update_actions_in_job = mock.Mock()
        self.resource.on_patch(self.mock_req, self.mock_req,
                               common.fake_job_0_job_id)
        self.mock_db.update_job.assert_called_with(
            user_id=common.fake_job_0_user_id,
            job_id=common.fake_job_0_job_id,
            patch_doc=patch_doc)
        self.assertEqual(self.mock_req.status, falcon.HTTP_200)
        result = self.mock_req.body
        self.assertEqual(result, expected_result)

    def test_on_post_ok(self):
        new_version = random.randint(0, 99)
        self.mock_db.replace_job.return_value = new_version
        job = common.get_fake_job_0()
        self.mock_req.stream.read.return_value = json.dumps(job)
        expected_result = {'job_id': common.fake_job_0_job_id,
                           'version': new_version}

        self.resource.on_post(self.mock_req, self.mock_req,
                              common.fake_job_0_job_id)
        self.assertEqual(self.mock_req.status, falcon.HTTP_201)
        self.assertEqual(self.mock_req.body, expected_result)

    def test_on_post_raises_when_db_replace_job_raises(self):
        self.mock_db.replace_job.side_effect = exceptions.AccessForbidden(
            'regular test failure')
        job = common.get_fake_job_0()
        self.mock_req.stream.read.return_value = json.dumps(job)
        self.assertRaises(exceptions.AccessForbidden, self.resource.on_post,
                          self.mock_req,
                          self.mock_req,
                          common.fake_job_0_job_id)


class TestJobsEvent(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestJobsEvent, self).setUp()
        self.mock_db = mock.Mock()
        self.mock_req = mock.MagicMock()
        self.mock_req.__getitem__.side_effect = common.get_req_items
        self.mock_req.get_header.return_value = common.fake_session_0[
            'user_id']
        self.mock_req.status = falcon.HTTP_200
        self.resource = v1_jobs.JobsEvent(self.mock_db)
        self.mock_json_body = mock.Mock()
        self.mock_json_body.return_value = {}
        self.resource.json_body = self.mock_json_body

    def test_create_resource(self):
        self.assertIsInstance(self.resource, v1_jobs.JobsEvent)

    def test_on_post_raises_when_unable_to_read_event_from_body(self):
        self.mock_json_body.return_value = {}
        self.assertRaises(exceptions.BadDataFormat, self.resource.on_post,
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


class TestJobs(common.FreezerBaseTestCase):
    def setUp(self):
        super(TestJobs, self).setUp()

    def _test_job_start(self, status, event, response, need_update):
        job_schedule = {}
        if status is not None:
            job_schedule['status'] = status
        if event is not None:
            job_schedule['event'] = event
        job = v1_jobs.Job({'job_schedule': job_schedule})
        res = job.start()
        self.assertEqual(res, response)
        self.assertEqual(job.need_update, need_update)

    def _test_job_stop(self, status, event, response, need_update):
        job_schedule = {}
        if status is not None:
            job_schedule['status'] = status
        if event is not None:
            job_schedule['event'] = event
        job = v1_jobs.Job({'job_schedule': job_schedule})
        res = job.stop()
        self.assertEqual(res, response)
        self.assertEqual(job.need_update, need_update)

    def _test_job_abort(self, status, event, response, need_update):
        job_schedule = {}
        if status is not None:
            job_schedule['status'] = status
        if event is not None:
            job_schedule['event'] = event
        job = v1_jobs.Job({'job_schedule': job_schedule})
        res = job.abort()
        self.assertEqual(res, response)
        self.assertEqual(job.need_update, need_update)

    def test_start_scheduled_unstarted_job(self):
        self._test_job_start(status='scheduled',
                             event=None,
                             response='success',
                             need_update=True)

    def test_start_scheduled_started_job(self):
        self._test_job_start(status='scheduled',
                             event='start',
                             response='start already requested',
                             need_update=False)

    def test_start_running_unstarted_job(self):
        self._test_job_start(status='running',
                             event=None,
                             response='success',
                             need_update=True)

    def test_start_running_started_job(self):
        self._test_job_start(status='running',
                             event='start',
                             response='start already requested',
                             need_update=False)

    def test_start_stopped_unstarted_job(self):
        self._test_job_start(status='stop',
                             event=None,
                             response='success',
                             need_update=True)

    def test_start_stopped_started_job(self):
        self._test_job_start(status='stop',
                             event='start',
                             response='start already requested',
                             need_update=False)

    def test_start_completed_unstarted_job(self):
        self._test_job_start(status='completed',
                             event=None,
                             response='success',
                             need_update=True)

    def test_start_completed_started_job(self):
        self._test_job_start(status='completed',
                             event='start',
                             response='start already requested',
                             need_update=False)

    def test_start_emptystatus_unstarted_job(self):
        self._test_job_start(status='',
                             event=None,
                             response='success',
                             need_update=True)

    def test_start_emptystatus_started_job(self):
        self._test_job_start(status=None,
                             event='start',
                             response='start already requested',
                             need_update=False)

    def test_start_nostatus_unstarted_job(self):
        self._test_job_start(status=None,
                             event=None,
                             response='success',
                             need_update=True)

    def test_stop_scheduled_unstopped_job(self):
        self._test_job_stop(status='scheduled',
                            event=None,
                            response='success',
                            need_update=True)

    def test_stop_scheduled_stopped_job(self):
        self._test_job_stop(status='scheduled',
                            event='stop',
                            response='stop already requested',
                            need_update=False)

    def test_stop_running_unstopped_job(self):
        self._test_job_stop(status='running',
                            event=None,
                            response='success',
                            need_update=True)

    def test_stop_running_stopped_job(self):
        self._test_job_stop(status='running',
                            event='stop',
                            response='stop already requested',
                            need_update=False)

    def test_stop_stopped_unstopped_job(self):
        self._test_job_stop(status='stop',
                            event=None,
                            response='success',
                            need_update=True)

    def test_stop_stopped_stopped_job(self):
        self._test_job_stop(status='stop',
                            event='stop',
                            response='stop already requested',
                            need_update=False)

    def test_stop_completed_unstopped_job(self):
        self._test_job_stop(status='completed',
                            event=None,
                            response='success',
                            need_update=True)

    def test_stop_completed_stopped_job(self):
        self._test_job_stop(status='completed',
                            event='stop',
                            response='stop already requested',
                            need_update=False)

    def test_stop_emptystatus_unstopped_job(self):
        self._test_job_stop(status='',
                            event=None,
                            response='success',
                            need_update=True)

    def test_stop_emptystatus_stopped_job(self):
        self._test_job_stop(status=None,
                            event='stop',
                            response='stop already requested',
                            need_update=False)

    def test_stop_nostatus_unstopped_job(self):
        self._test_job_stop(status=None,
                            event=None,
                            response='success',
                            need_update=True)

    def test_abort_scheduled_unaborted_job(self):
        self._test_job_abort(status='scheduled',
                             event=None,
                             response='success',
                             need_update=True)

    def test_abort_scheduled_abortped_job(self):
        self._test_job_abort(status='scheduled',
                             event='abort',
                             response='abort already requested',
                             need_update=False)

    def test_abort_running_unaborted_job(self):
        self._test_job_abort(status='running',
                             event=None,
                             response='success',
                             need_update=True)

    def test_abort_running_abortped_job(self):
        self._test_job_abort(status='running',
                             event='abort',
                             response='abort already requested',
                             need_update=False)

    def test_abort_abortped_unaborted_job(self):
        self._test_job_abort(status='abort',
                             event=None,
                             response='success',
                             need_update=True)

    def test_abort_abortped_abortped_job(self):
        self._test_job_abort(status='abort',
                             event='abort',
                             response='abort already requested',
                             need_update=False)

    def test_abort_completed_unaborted_job(self):
        self._test_job_abort(status='completed',
                             event=None,
                             response='success',
                             need_update=True)

    def test_abort_completed_abortped_job(self):
        self._test_job_abort(status='completed',
                             event='abort',
                             response='abort already requested',
                             need_update=False)

    def test_abort_emptystatus_unaborted_job(self):
        self._test_job_abort(status='',
                             event=None,
                             response='success',
                             need_update=True)

    def test_abort_emptystatus_abortped_job(self):
        self._test_job_abort(status=None,
                             event='abort',
                             response='abort already requested',
                             need_update=False)

    def test_abort_nostatus_unaborted_job(self):
        self._test_job_abort(status=None,
                             event=None,
                             response='success',
                             need_update=True)

    @patch.object(v1_jobs.Job, 'start')
    def test_execute_start_event(self, mock_start):
        job = v1_jobs.Job({})
        job.execute_event('start', 'my_params')
        mock_start.assert_called_once_with('my_params')

    @patch.object(v1_jobs.Job, 'stop')
    def test_execute_stop_event(self, mock_stop):
        job = v1_jobs.Job({})
        job.execute_event('stop', 'my_params')
        mock_stop.assert_called_once_with('my_params')

    @patch.object(v1_jobs.Job, 'abort')
    def test_execute_abort_event(self, mock_abort):
        job = v1_jobs.Job({})
        job.execute_event('abort', 'my_params')
        mock_abort.assert_called_once_with('my_params')

    def test_execute_raises_BadDataFormat_when_event_not_implemented(self):
        job = v1_jobs.Job({})
        self.assertRaises(exceptions.BadDataFormat, job.execute_event, 'smile',
                          'my_params')

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
