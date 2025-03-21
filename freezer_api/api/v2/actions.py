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

import falcon

from freezer_api.api.common import resource
from freezer_api.common import exceptions as freezer_api_exc
from freezer_api import policy


class ActionsCollectionResource(resource.BaseResource):
    """
    Handler for endpoint: /v2/{project_id}/actions
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('actions:get_all')
    def on_get(self, req, resp, project_id):
        # GET /v2/{project_id}/actions(?limit,offset)     Lists actions
        user_id = req.get_header('X-User-ID')
        offset = req.get_param_as_int('offset') or 0
        limit = req.get_param_as_int('limit') or 10
        search = self.json_body(req)
        obj_list = self.db.search_action(project_id=project_id,
                                         user_id=user_id, offset=offset,
                                         limit=limit, search=search)
        resp.media = {'actions': obj_list}

    @policy.enforce('actions:create')
    def on_post(self, req, resp, project_id):
        # POST /v2/{project_id}/actions    Creates action entry
        doc = self.json_body(req)
        if not doc:
            raise freezer_api_exc.BadDataFormat(
                message='Missing request body')
        user_id = req.get_header('X-User-ID')
        action_id = self.db.add_action(project_id=project_id,
                                       user_id=user_id,
                                       doc=doc)
        resp.status = falcon.HTTP_201
        resp.media = {'action_id': action_id}


class ActionsResource(resource.BaseResource):
    """
    Handler for endpoint: /v2/{project_id}/actions/{action_id}
    """

    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('actions:get')
    def on_get(self, req, resp, project_id, action_id):
        # GET /v2/{project_id}/actions/{action_id}
        # retrieves the specified action
        # search in body
        user_id = req.get_header('X-User-ID') or ''
        obj = self.db.get_action(project_id=project_id,
                                 user_id=user_id,
                                 action_id=action_id)
        if obj:
            resp.media = obj
        else:
            resp.status = falcon.HTTP_404

    @policy.enforce('actions:delete')
    def on_delete(self, req, resp, project_id, action_id):
        # DELETE /v2/{project_id}/actions/{action_id}
        # Deletes the specified action
        user_id = req.get_header('X-User-ID')
        self.db.delete_action(project_id=project_id,
                              user_id=user_id,
                              action_id=action_id)
        resp.media = {'action_id': action_id}
        resp.status = falcon.HTTP_204

    @policy.enforce('actions:update')
    def on_patch(self, req, resp, project_id, action_id):
        # PATCH /v2/{project_id}/actions/{action_id}
        # updates the specified action
        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)
        new_version = self.db.update_action(project_id=project_id,
                                            user_id=user_id,
                                            action_id=action_id,
                                            patch_doc=doc)
        resp.media = {'action_id': action_id, 'version': new_version}

    @policy.enforce('actions:replace')
    def on_post(self, req, resp, project_id, action_id):
        # PUT /v2/{project_id}/actions/{action_id}
        # Creates/Replaces the specified action
        user_id = req.get_header('X-User-ID') or ''
        doc = self.json_body(req)
        new_version = self.db.replace_action(project_id=project_id,
                                             user_id=user_id,
                                             action_id=action_id,
                                             doc=doc)
        resp.status = falcon.HTTP_201
        resp.media = {'action_id': action_id, 'version': new_version}
