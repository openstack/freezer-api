"""
(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.

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


class BackupsCollectionResource(resource.BaseResource):
    """
    Handler for endpoint: /v2/{project_id}/backups
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('backups:get_all')
    def on_get(self, req, resp, project_id):
        # GET /v2/{project_id}/backups(?limit,offset)     Lists backups
        user_id = req.get_header('X-User-ID')
        offset = req.get_param_as_int('offset') or 0
        limit = req.get_param_as_int('limit') or 10
        search = self.json_body(req)
        obj_list = self.db.search_backup(project_id=project_id,
                                         user_id=user_id, offset=offset,
                                         limit=limit, search=search)
        resp.media = {'backups': obj_list}

    @policy.enforce('backups:create')
    def on_post(self, req, resp, project_id):
        # POST /v2/{project_id}/backups    Creates backup entry
        doc = self.json_body(req)
        if not doc:
            raise freezer_api_exc.BadDataFormat(
                message='Missing request body')
        user_name = req.get_header('X-User-Name')
        user_id = req.get_header('X-User-ID')
        backup_id = self.db.add_backup(project_id=project_id,
                                       user_id=user_id,
                                       user_name=user_name,
                                       doc=doc)
        resp.status = falcon.HTTP_201
        resp.media = {'backup_id': backup_id}


class BackupsResource(resource.BaseResource):
    """
    Handler for endpoint: /v2/{project_id}/backups/{backup_id}
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('backups:get')
    def on_get(self, req, resp, project_id, backup_id):
        # GET /v2/{project_id}/backups/{backup_id}     Get backup details
        user_id = req.get_header('X-User-ID')
        obj = self.db.get_backup(project_id=project_id,
                                 user_id=user_id,
                                 backup_id=backup_id)
        if obj:
            resp.media = obj
        else:
            resp.status = falcon.HTTP_404

    @policy.enforce('backups:delete')
    def on_delete(self, req, resp, project_id, backup_id):
        # DELETE /v2/{project_id}/backups/{backup_id}
        # Deletes the specified backup
        user_id = req.get_header('X-User-ID')
        self.db.delete_backup(project_id=project_id,
                              user_id=user_id,
                              backup_id=backup_id)
        resp.media = {'backup_id': backup_id}
        resp.status = falcon.HTTP_204
