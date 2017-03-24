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

"""

import time

import falcon
import six

from freezer_api.api.common import resource
from freezer_api.common import exceptions as freezer_api_exc
from freezer_api import policy


class SessionsCollectionResource(resource.BaseResource):
    """
    Handler for endpoint: /v1/sessions
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('sessions:get_all')
    def on_get(self, req, resp, project_id):
        # GET /v1/sessions(?limit,offset)     Lists sessions
        user_id = req.get_header('X-User-ID')
        offset = req.get_param_as_int('offset', min=0) or 0
        limit = req.get_param_as_int('limit', min=1) or 10
        search = self.json_body(req)
        obj_list = self.db.search_session(project_id=project_id,
                                          user_id=user_id, offset=offset,
                                          limit=limit, search=search)
        resp.body = {'sessions': obj_list}

    @policy.enforce('sessions:create')
    def on_post(self, req, resp, project_id):
        # POST /v1/sessions    Creates session entry
        doc = self.json_body(req)
        if not doc:
            raise freezer_api_exc.BadDataFormat(
                message='Missing request body')
        user_id = req.get_header('X-User-ID')
        session_id = self.db.add_session(project_id=project_id,
                                         user_id=user_id, doc=doc)
        resp.status = falcon.HTTP_201
        resp.body = {'session_id': session_id}


class SessionsResource(resource.BaseResource):
    """
    Handler for endpoint: /v1/sessions/{session_id}
    """

    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('sessions:get')
    def on_get(self, req, resp, project_id, session_id):
        # GET /v1/sessions/{session_id}     retrieves the specified session
        # search in body
        user_id = req.get_header('X-User-ID') or ''
        obj = self.db.get_session(project_id=project_id,
                                  user_id=user_id, session_id=session_id)
        if obj:
            resp.body = obj
        else:
            resp.status = falcon.HTTP_404

    @policy.enforce('sessions:delete')
    def on_delete(self, req, resp, project_id, session_id):
        # DELETE /v1/sessions/{session_id}     Deletes the specified session
        user_id = req.get_header('X-User-ID')
        self.db.delete_session(project_id=project_id,
                               user_id=user_id, session_id=session_id)
        resp.body = {'session_id': session_id}
        resp.status = falcon.HTTP_204

    @policy.enforce('sessions:update')
    def on_patch(self, req, resp, project_id, session_id):
        # PATCH /v1/sessions/{session_id}     updates the specified session
        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)
        new_version = self.db.update_session(project_id=project_id,
                                             user_id=user_id,
                                             session_id=session_id,
                                             patch_doc=doc)
        resp.body = {'session_id': session_id, 'version': new_version}

    @policy.enforce('sessions:replace')
    def on_post(self, req, resp, project_id, session_id):
        # PUT /v1/sessions/{session_id} creates/replaces the specified session
        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)
        if not doc:
            raise freezer_api_exc.BadDataFormat(
                message='Missing request body')
        new_version = self.db.replace_session(project_id=project_id,
                                              user_id=user_id,
                                              session_id=session_id,
                                              doc=doc)
        resp.status = falcon.HTTP_201
        resp.body = {'session_id': session_id, 'version': new_version}


class SessionsAction(resource.BaseResource):
    """
    Handler for endpoint: /v1/sessions/{session_id}/action
    """

    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('sessions:action:create')
    def on_post(self, req, resp, project_id, session_id):
        # POST /v1/sessions/{session_id}/action
        # executes an action on the specified session

        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)

        try:
            action, params = next(six.iteritems(doc))
        except Exception:
            raise freezer_api_exc.BadDataFormat("Bad action request format")

        session_doc = self.db.get_session(project_id=project_id,
                                          user_id=user_id,
                                          session_id=session_id)
        session = Session(session_doc)
        session.execute_action(action, params)

        if session.need_update:
            self.db.update_session(project_id=project_id,
                                   user_id=user_id,
                                   session_id=session_id,
                                   patch_doc=session.doc)
        resp.status = falcon.HTTP_202
        resp.body = {'result': session.action_result,
                     'session_tag': session.session_tag}


class Session(resource.BaseResource):
    """
    A class to manage the actions that can be taken upon a
    Session data structure.
    It modifies information contained in its document
    in accordance to the requested action
    """
    def __init__(self, doc):
        self.doc = doc
        self.action_result = ''
        self.need_update = False

    @property
    def session_tag(self):
        return int(self.doc.get('session_tag', 0))

    @session_tag.setter
    def session_tag(self, value):
        self.doc['session_tag'] = int(value)

    def execute_action(self, action, params):
        if action == 'start':
            try:
                self.start(params['job_id'], params['current_tag'])
            except freezer_api_exc.BadDataFormat:
                raise
            except Exception as e:
                raise freezer_api_exc.FreezerAPIException(e)
        elif action == 'end':
            try:
                self.end(params['job_id'], params['result'])
            except freezer_api_exc.BadDataFormat:
                raise
            except Exception as e:
                raise freezer_api_exc.FreezerAPIException(e)
        else:
            raise freezer_api_exc.MethodNotImplemented("Bad Action Method")

    def end(self, job_id, result):
        """
        Apply the 'end' action to the session object
        If the request can be accepted it modifies the relevant fields
        and sets the need_update member to notify that the stored
        document needs to be updated
        """
        now = int(time.time())
        self.set_job_end(job_id, result, now)
        new_result = self.get_job_overall_result()
        if self.doc.get('status', '') != 'completed':
            if new_result in ['fail', 'success']:
                self.doc['time_end'] = now
                self.doc['result'] = new_result
                self.doc['status'] = 'completed'
        self.action_result = 'success'
        self.need_update = True

    def start(self, job_id, job_tag):
        """
        Apply the 'start' action to the session object
        If the request can be accepted it modifies the relevant fields
        and sets the need_update member to notify that the stored
        document needs to be updated
        """
        job_tag = int(job_tag)
        self.session_tag = int(self.session_tag)
        now = int(time.time())
        time_since_last_start = now - self.doc.get('time_start', 0)

        if job_tag > self.session_tag:
            raise freezer_api_exc.BadDataFormat(
                'requested tag value too high. Session Tag: {0} '
                'Job Tag: {1}'.format(self.session_tag, job_tag))

        if time_since_last_start <= self.doc.get('hold_off', 60):
            # session has been started not so long ago
            # tag increments are not allowed during hold_off
            if job_tag < self.session_tag:
                self.action_result = 'success'
                self.set_job_start(job_id, now)
                self.need_update = True
            else:
                self.action_result = 'hold-off'
                self.need_update = False
        elif time_since_last_start > self.doc.get('hold_off', 60):
            # out of hold_off window:
            #  - ok to trigger new action start (job_tag == session_tag)
            # if job_tag < session_tag client is probably out-of-sync
            if self.session_tag == job_tag:
                self.session_tag += 1
                self.doc['time_start'] = now
                self.doc['status'] = 'running'
                self.doc['result'] = ''
                self.action_result = 'success'
                self.set_job_start(job_id, now)
                self.need_update = True
            else:
                self.action_result = 'out-of-sync'
                self.need_update = False

    def get_job_overall_result(self):
        """
        check the status of all the jobs and return the overall session result
        """
        for job in self.doc['jobs'].values():
            if job['status'] != 'completed':
                return 'running'
            if job['result'] != 'success':
                return 'fail'
        return 'success'

    def set_job_end(self, job_id, result, timestamp):
        try:
            job = self.doc['jobs'][job_id]
        except Exception:
            raise freezer_api_exc.BadDataFormat('job_id not found in session')
        job['status'] = 'completed'
        job['result'] = result
        job['time_ended'] = timestamp

    def set_job_start(self, job_id, timestamp):
        try:
            job = self.doc['jobs'][job_id]
        except Exception:
            raise freezer_api_exc.BadDataFormat('job_id not found in session')
        job['status'] = 'running'
        job['result'] = ''
        job['time_started'] = timestamp


class SessionsJob(resource.BaseResource):
    """
    Handler for endpoint: /v1/sessions/{session_id}/jobs/{job_id}
    """

    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('sessions:job:add')
    def on_put(self, req, resp, project_id, session_id, job_id):
        """
        add a job to a session

        :param req:
        :param resp:
        :param session_id:
        :param job_id:
        :return:
        """

        user_id = req.get_header('X-User-ID', '')

        # --- update session object
        job_doc = self.db.get_job(project_id=project_id,
                                  user_id=user_id, job_id=job_id)

        job_schedule = job_doc.get('job_schedule', {})
        session_update_doc = {
            'jobs': {
                job_id: {
                    'client_id': job_doc['client_id'],
                    'status': job_schedule.get('status', ''),
                    'result': job_schedule.get('result', ''),
                    'time_started': job_schedule.get('time_started', ''),
                    'time_ended': job_schedule.get('time_ended', '')
                }
            }
        }

        self.db.update_session(project_id=project_id,
                               user_id=user_id,
                               session_id=session_id,
                               patch_doc=session_update_doc)
        # --- update job object
        session_doc = self.db.get_session(user_id=user_id,
                                          session_id=session_id)
        job_update_doc = {
            'session_id': session_id,
            'session_tag': session_doc['session_tag'],
            'job_schedule': session_doc['schedule']
        }
        self.db.update_job(project_id=project_id,
                           user_id=user_id,
                           job_id=job_id,
                           patch_doc=job_update_doc)
        resp.status = falcon.HTTP_204

    @policy.enforce('sessions:job:remove')
    def on_delete(self, req, resp, project_id, session_id, job_id):
        """
        remove a job from the session

        :param req:
        :param resp:
        :param session_id:
        :param job_id:
        :return:
        """

        user_id = req.get_header('X-User-ID') or ''

        session_doc = self.db.get_session(project_id=project_id,
                                          user_id=user_id,
                                          session_id=session_id)
        session_doc['jobs'].pop(job_id, None)

        # when replacing, db might raise a VersionConflictEngineException
        self.db.replace_session(project_id=project_id,
                                user_id=user_id,
                                session_id=session_id,
                                doc=session_doc)
        job_update_doc = {
            'session_id': '',
            'session_tag': 0,
            'job_schedule': {
                'event': 'stop'
            }
        }
        self.db.update_job(project_id=project_id,
                           user_id=user_id,
                           job_id=job_id,
                           patch_doc=job_update_doc)
        resp.status = falcon.HTTP_204
