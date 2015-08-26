"""
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

import falcon
from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.api.common import resource


class JobsCollectionResource(resource.BaseResource):
    """
    Handler for endpoint: /v1/jobs
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    def on_get(self, req, resp):
        # GET /v1/jobs(?limit,offset)     Lists jobs
        user_id = req.get_header('X-User-ID')
        offset = req.get_param_as_int('offset') or 0
        limit = req.get_param_as_int('limit') or 10
        search = self.json_body(req)
        obj_list = self.db.search_job(user_id=user_id, offset=offset,
                                      limit=limit, search=search)
        resp.body = {'jobs': obj_list}

    def on_post(self, req, resp):
        # POST /v1/jobs    Creates job entry
        try:
            doc = self.json_body(req)
        except KeyError:
            raise freezer_api_exc.BadDataFormat(
                message='Missing request body')

        user_id = req.get_header('X-User-ID')
        job_id = self.db.add_job(user_id=user_id, doc=doc)
        resp.status = falcon.HTTP_201
        resp.body = {'job_id': job_id}


class JobsResource(resource.BaseResource):
    """
    Handler for endpoint: /v1/jobs/{job_id}
    """

    def __init__(self, storage_driver):
        self.db = storage_driver

    def on_get(self, req, resp, job_id):
        # GET /v1/jobs/{job_id}     retrieves the specified job
        # search in body
        user_id = req.get_header('X-User-ID') or ''
        obj = self.db.get_job(user_id=user_id, job_id=job_id)
        if obj:
            resp.body = obj
        else:
            resp.status = falcon.HTTP_404

    def on_delete(self, req, resp, job_id):
        # DELETE /v1/jobs/{job_id}     Deletes the specified job
        user_id = req.get_header('X-User-ID')
        self.db.delete_job(user_id=user_id, job_id=job_id)
        resp.body = {'job_id': job_id}
        resp.status = falcon.HTTP_204

    def on_patch(self, req, resp, job_id):
        # PATCH /v1/jobs/{job_id}     updates the specified job
        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)
        new_version = self.db.update_job(user_id=user_id,
                                         job_id=job_id,
                                         patch_doc=doc)
        resp.body = {'job_id': job_id, 'version': new_version}

    def on_post(self, req, resp, job_id):
        # PUT /v1/jobs/{job_id}     creates/replaces the specified job
        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)
        new_version = self.db.replace_job(user_id=user_id,
                                          job_id=job_id,
                                          doc=doc)
        resp.status = falcon.HTTP_201
        resp.body = {'job_id': job_id, 'version': new_version}


class JobsEvent(resource.BaseResource):
    """
    Handler for endpoint: /v1/jobs/{job_id}/event

    Actions are passed in the body, for example:
    {
        "start": null
    }
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    def on_post(self, req, resp, job_id):
        # POST /v1/jobs/{job_id}/event
        # requests an event on the specified job

        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)

        try:
            event, params = next(doc.iteritems())
        except:
            raise freezer_api_exc.BadDataFormat("Bad event request format")

        job_doc = self.db.get_job(user_id=user_id,
                                  job_id=job_id)
        job = Job(job_doc)
        result = job.execute_event(event, params)

        if job.need_update:
            self.db.replace_job(user_id=user_id,
                                job_id=job_id,
                                doc=job.doc)
        resp.status = falcon.HTTP_202
        resp.body = {'result': result}


class Job(resource.BaseResource):
    """
    A class to manage the events that can be sent upon a
    Job data structure.
    It modifies information contained in its document
    in accordance to the requested event
    """
    def __init__(self, doc):
        self.doc = doc
        self.event_result = ''
        self.need_update = False
        if 'job_schedule' not in doc:
            doc['job_schedule'] = {}
        self.job_schedule = doc['job_schedule']
        self.event_handlers = {'start': self.start,
                               'stop': self.stop,
                               'abort': self.abort}

    def execute_event(self, event, params):
        handler = self.event_handlers.get(event, None)
        if not handler:
            raise freezer_api_exc.BadDataFormat("Bad Action Method")
        try:
            self.event_result = handler(params)
        except freezer_api_exc.BadDataFormat:
            raise
        except Exception as e:
            raise freezer_api_exc.FreezerAPIException(e)
        return self.event_result

    @property
    def job_status(self):
        return self.job_schedule.get('status', '')

    @job_status.setter
    def job_status(self, value):
        self.job_schedule['status'] = value

    def start(self, params=None):
        if self.job_status in ["scheduled", "running"]:
            return 'already active'
        if self.job_status in ["completed", "stop", ""]:
            # completed jobs are not acquired by the scheduler
            self.job_status = 'stop'
            self.job_schedule['event'] = 'start'
            self.job_schedule['result'] = ''
            self.need_update = True
            return 'success'
        else:
            raise freezer_api_exc.BadDataFormat("unable to start a {0} job"
                                                .format(self.job_status))

    def stop(self, params=None):
        if self.job_status in ["scheduled", "running", ""]:
            self.job_schedule['event'] = 'stop'
            self.need_update = True
            return 'success'
        else:
            return 'already stopped'

    def abort(self, params=None):
        if self.job_status in ["scheduled", "running", ""]:
            self.job_schedule['event'] = 'abort'
            self.need_update = True
            return 'success'
        else:
            return 'already stopped'
