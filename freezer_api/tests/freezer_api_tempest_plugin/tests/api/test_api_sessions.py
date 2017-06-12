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
from tempest.lib import exceptions

from freezer_api.tests.freezer_api_tempest_plugin.tests.api import base


class TestFreezerApiSessions(base.BaseFreezerApiTest):
    @classmethod
    def resource_setup(cls):
        super(TestFreezerApiSessions, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(TestFreezerApiSessions, cls).resource_cleanup()

    @decorators.attr(type="gate")
    def test_api_sessions(self):

        resp, response_body = self.freezer_api_client.get_sessions()
        self.assertEqual(200, resp.status)

        response_body_json = json.loads(response_body)
        self.assertIn('sessions', response_body_json)
        sessions = response_body_json['sessions']
        self.assertEmpty(sessions)

    @decorators.attr(type="gate")
    def test_api_sessions_get_limit(self):
        # limits > 0 should return successfully
        for valid_limit in [2, 1]:
            resp, body = self.freezer_api_client.get_sessions(
                limit=valid_limit)
            self.assertEqual(200, resp.status)

        # limits <= 0 should raise a bad request error
        for bad_limit in [0, -1, -2]:
            self.assertRaises(exceptions.BadRequest,
                              self.freezer_api_client.get_sessions,
                              limit=bad_limit)

    @decorators.attr(type="gate")
    def test_api_sessions_get_offset(self):
        # offsets >= 0 should return 200
        for valid_offset in [1, 0]:
            resp, body = self.freezer_api_client.get_sessions(
                offset=valid_offset)
            self.assertEqual(200, resp.status)

        # offsets < 0 should return 400
        for bad_offset in [-1, -2]:
            self.assertRaises(exceptions.BadRequest,
                              self.freezer_api_client.get_sessions,
                              offset=bad_offset)

    @decorators.attr(type="gate")
    def test_api_sessions_post(self):

        session = {
            "session_id": "test-session",
            "session_tag": 1,
            "description": "a test session",
            "hold_off": 5,
            "schedule": {
                "time_created": 1234,
                "time_started": 1234,
                "time_ended": 0,
                "status": "stop",
                "schedule_date": "2015-06-02T16:20:00",
                "schedule_month": "1-6, 9-12",
                "schedule_day": "mon, wed, fri",
                "schedule_hour": "03",
                "schedule_minute": "25",
            },
            "jobs": [
                {
                    'job_id_1': {
                        "client_id": "client-id-1",
                        "status": "stop",
                        "result": "success",
                        "time_started": 1234,
                        "time_ended": 1234
                    },
                    'job_id_2': {
                        "client_id": "client-id-1",
                        "status": "stop",
                        "result": "success",
                        "time_started": 1234,
                        "time_ended": 1234,
                    }
                }
            ],
            "time_start": 1234,
            "time_end": 1234,
            "time_started": 1234,
            "time_ended": 1234,
            "status": "completed",
            "result": "success",
            "user_id": "user-id-1"
        }

        # Create the session with POST
        resp, response_body = self.freezer_api_client.post_sessions(session)
        self.assertEqual(201, resp.status)

        self.assertIn('session_id', response_body)
        session_id = response_body['session_id']

        # Check that the session has the correct values
        resp, response_body = self.freezer_api_client.get_sessions(session_id)
        self.assertEqual(200, resp.status)

        # Delete the session
        resp, response_body = self.freezer_api_client.delete_sessions(
            session_id)
        self.assertEqual(204, resp.status)
