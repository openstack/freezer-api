# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
from oslo_db import api as db_api
from oslo_log import log

from freezer_api.db import base as db_base
from freezer_api.db.sqlalchemy import api as db_session
from freezer_api.db.sqlalchemy import models


CONF = cfg.CONF
LOG = log.getLogger(__name__)

_BACKEND_MAPPING = {'sqlalchemy': 'freezer_api.db.sqlalchemy.api'}


class SQLDriver(db_base.DBDriver):

    def __init__(self, backend):
        super(SQLDriver, self).__init__(backend)
        self.IMPL = db_api.DBAPI.from_config(CONF, _BACKEND_MAPPING)
        self._engine = None

    def get_engine(self):
        if not self._engine:
            self._engine = db_session.get_engine()
        return self._engine

    def get_api(self):
        return self.get_engine()

    def db_sync(self):
        if not self._engine:
            self._engine = self.get_engine()
        models.register_models(self._engine)

    def db_show(self):
        if not self._engine:
            self._engine = self.get_engine()
        return models.get_tables(self._engine)

    def db_remove(self):
        if not self._engine:
            self._engine = self.get_engine()
        models.unregister_models(self._engine)

    def name(self):
        return "sqlalchemy"
