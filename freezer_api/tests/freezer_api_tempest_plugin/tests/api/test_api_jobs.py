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

fake_job = {
    "job_actions":
        [
            {
                "freezer_action":
                    {
                        "action": "backup",
                        "mode": "fs",
                        "src_file": "/home/tylerdurden/project_mayhem",
                        "backup_name": "project_mayhem_backup",
                        "container": "my_backup_container",
                    },
                "exit_status": "success",
                "max_retries": 1,
                "max_retries_interval": 1,
                "mandatory": True
            }
        ],
    "job_schedule":
        {
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
    "job_id": "blabla",
    "client_id": "01b0f00a-4ce2-11e6-beb8-9e71128cae77_myhost.mydomain.mytld",
    "user_id": "blabla",
    "description": "scheduled one shot"
}


class TestFreezerApiJobs(base.BaseFreezerApiTest):
    @classmethod
    def resource_setup(cls):
        super(TestFreezerApiJobs, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(TestFreezerApiJobs, cls).resource_cleanup()

    @decorators.attr(type="gate")
    def test_api_jobs(self):

        resp, response_body = self.freezer_api_client.get_jobs()
        self.assertEqual(200, resp.status)

        response_body_json = json.loads(response_body)
        self.assertIn('jobs', response_body_json)
        jobs = response_body_json['jobs']
        self.assertEmpty(jobs)

    @decorators.attr(type="gate")
    def test_api_jobs_get_limit(self):
        # limits > 0 should return successfully
        for valid_limit in [2, 1]:
            resp, body = self.freezer_api_client.get_jobs(limit=valid_limit)
            self.assertEqual(200, resp.status)

        # limits <= 0 should raise a bad request error
        for bad_limit in [0, -1, -2]:
            self.assertRaises(exceptions.BadRequest,
                              self.freezer_api_client.get_jobs,
                              limit=bad_limit)

    @decorators.attr(type="gate")
    def test_api_jobs_get_offset(self):
        # offsets >= 0 should return 200
        for valid_offset in [1, 0]:
            resp, body = self.freezer_api_client.get_jobs(offset=valid_offset)
            self.assertEqual(200, resp.status)

        # offsets < 0 should return 400
        for bad_offset in [-1, -2]:
            self.assertRaises(exceptions.BadRequest,
                              self.freezer_api_client.get_jobs,
                              offset=bad_offset)

    @decorators.attr(type="gate")
    def test_api_jobs_post(self):

        # Create the job with POST
        resp, response_body = self.freezer_api_client.post_jobs(fake_job)
        self.assertEqual(201, resp.status)

        self.assertIn('job_id', response_body)
        job_id = response_body['job_id']

        # Check that the job has the correct values
        resp, response_body = self.freezer_api_client.get_jobs(job_id)
        self.assertEqual(200, resp.status)

        # Delete the job
        resp, response_body = self.freezer_api_client.delete_jobs(
            job_id)
        self.assertEqual(204, resp.status)

    @decorators.attr(type="gate")
    def test_api_jobs_with_invalid_client_project_id_fail(self):
        """Ensure that a job submitted with a bad client_id project id fails"""
        fake_bad_job = fake_job
        fake_bad_job['client_id'] = 'bad%project$id_host.domain.tld'

        # Create the job with POST
        self.assertRaises(exceptions.BadRequest,
                          lambda: self.freezer_api_client.post_jobs(
                              fake_bad_job))

    @decorators.attr(type="gate")
    def test_api_jobs_with_invalid_client_host_fail(self):
        """Ensure that a job submitted with a bad client_id hostname fails"""
        fake_bad_job = fake_job
        fake_bad_job['client_id'] = ("01b0f00a-4ce2-11e6-beb8-9e71128cae77"
                                     "_bad_hostname.bad/domain.b")

        # Create the job with POST
        self.assertRaises(exceptions.BadRequest,
                          lambda: self.freezer_api_client.post_jobs(
                              fake_bad_job))

    def test_api_jobs_with_only_fqdn_succeeds(self):
        """Ensure that a job submitted with only an FQDN succeeds"""
        fqdn_only_job = fake_job
        fqdn_only_job['client_id'] = 'padawan-ccp-c1-m1-mgmt'

        # Attempt to post the job, should succeed
        resp, response_body = self.freezer_api_client.post_jobs(fqdn_only_job)
        self.assertEqual(201, resp.status)
