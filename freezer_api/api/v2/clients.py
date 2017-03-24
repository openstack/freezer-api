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


class ClientsCollectionResource(resource.BaseResource):
    """
    Handler for endpoint: /v1/clients
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('clients:get_all')
    def on_get(self, req, resp, project_id):
        # GET /v1/clients(?limit,offset)     Lists clients
        user_id = req.get_header('X-User-ID')
        offset = req.get_param_as_int('offset', min=0) or 0
        limit = req.get_param_as_int('limit', min=1) or 10
        search = self.json_body(req)
        obj_list = self.db.get_client(project_id=project_id,
                                      user_id=user_id,
                                      offset=offset,
                                      limit=limit,
                                      search=search)
        resp.body = {'clients': obj_list}

    @policy.enforce('clients:create')
    def on_post(self, req, resp, project_id):
        # POST /v1/clients    Creates client entry
        doc = self.json_body(req)
        if not doc:
            raise freezer_api_exc.BadDataFormat(
                message='Missing request body')
        user_id = req.get_header('X-User-ID')
        client_id = self.db.add_client(
            project_id=project_id, user_id=user_id, doc=doc)
        resp.status = falcon.HTTP_201
        resp.body = {'client_id': client_id}


class ClientsResource(resource.BaseResource):
    """
    Handler for endpoint: /v1/clients/{client_id}
    """
    def __init__(self, storage_driver):
        self.db = storage_driver

    @policy.enforce('clients:get')
    def on_get(self, req, resp, project_id, client_id):
        # GET /v1/clients(?limit,offset)
        # search in body
        user_id = req.get_header('X-User-ID') or ''
        obj = self.db.get_client(project_id=project_id,
                                 user_id=user_id,
                                 client_id=client_id)
        if obj:
            resp.body = obj[0]
        else:
            resp.status = falcon.HTTP_404

    @policy.enforce('clients:delete')
    def on_delete(self, req, resp, project_id, client_id):
        # DELETE /v1/clients/{client_id}     Deletes the specified backup
        user_id = req.get_header('X-User-ID')
        self.db.delete_client(project_id=project_id,
                              user_id=user_id,
                              client_id=client_id)
        resp.body = {'client_id': client_id}
        resp.status = falcon.HTTP_204
