# (c) Copyright 2018 ZTE Corporation.
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

"""Freezer-api DB test base class."""

import fixtures
from oslo_config import cfg
from oslo_db import options as db_options

from freezer_api.db.sqlalchemy import api as sqla_api
from freezer_api.db.sqlalchemy import models

from freezer_api.db import manager

from freezer_api.tests.unit import common

CONF = cfg.CONF

_DB_CACHE = None

IN_MEM_DB_CONN_STRING = 'sqlite://'


class Database(fixtures.Fixture):

    def __init__(self, db_api):
        self.initialize_sql_session(IN_MEM_DB_CONN_STRING)
        self.engine = sqla_api.get_engine()
        self.engine.dispose()
        conn = self.engine.connect()
        self.setup_sqlite()

        self._DB = "".join(line for line in conn.connection.iterdump())
        self.engine.dispose()

    def initialize_sql_session(self, connection_str):
        db_options.set_defaults(
            CONF,
            connection=connection_str)
        CONF.set_override('connection', IN_MEM_DB_CONN_STRING,
                          group='database')

    def setup_sqlite(self):
        models.register_models(self.engine)

    def setUp(self):
        super().setUp()

        conn = self.engine.connect()
        conn.connection.executescript(self._DB)
        self.addCleanup(self.engine.dispose)


class DbTestCase(common.FreezerBaseTestCase):

    def setUp(self):
        super().setUp()
        dbbackend = "sqlalchemy"
        dbdriver = "sqlalchemy"
        db_driver = manager.get_db_driver(dbdriver,
                                          backend=dbbackend)
        self.dbapi = db_driver.IMPL
        global _DB_CACHE
        if not _DB_CACHE:
            _DB_CACHE = Database(sqla_api)
        self.useFixture(_DB_CACHE)
