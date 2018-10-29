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

import os
import threading

from stevedore import driver

from oslo_config import cfg
from oslo_db import api as db_api
from oslo_db.sqlalchemy import migration
from oslo_log import log

from freezer_api.db import base as db_base
from freezer_api.db.sqlalchemy import api as db_session
from freezer_api.db.sqlalchemy import models


INIT_VERSION = 0

_IMPL = None
_LOCK = threading.Lock()

CONF = cfg.CONF
LOG = log.getLogger(__name__)


MIGRATE_REPO_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'migrate_repo',
)

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
        self.get_engine()
        return self.IMPL

    def get_backend(self):
        global _IMPL
        if _IMPL is None:
            with _LOCK:
                if _IMPL is None:
                    _IMPL = driver.DriverManager(
                        "freezer.database.migration_backend",
                        cfg.CONF.database.backend).driver
        return _IMPL

    def db_sync(self, version=None, init_version=INIT_VERSION, engine=None):
        """Migrate the database to `version` or the most recent version."""

        if not self._engine:
            self._engine = self.get_engine()
        return migration.db_sync(engine=self._engine,
                                 abs_path=MIGRATE_REPO_PATH,
                                 version=version,
                                 init_version=init_version)

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
