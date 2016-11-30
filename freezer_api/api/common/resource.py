# Copyright 2015 Hewlett-Packard
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Base resource with utility functions

"""

import json

import falcon

from freezer_api.common import exceptions as freezer_api_exc


class BaseResource(object):

    @staticmethod
    def json_body(req):
        if not req.content_length:
            return {}

        try:
            raw_json = req.stream.read()
        except Exception:
            raise freezer_api_exc.BadDataFormat('Empty request body. A valid '
                                                'JSON document is required.')
        try:
            json_data = json.loads(raw_json, 'utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON')
        return json_data
