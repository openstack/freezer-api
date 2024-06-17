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

from alembic import command as alembic_api
from alembic import config as alembic_config
from alembic import migration as alembic_migration

import sqlalchemy as sa

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

    def _find_alembic_conf(self):
        """Get the project's alembic configuration

        :returns: An instance of ``alembic.config.Config``
        """
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'alembic.ini',
        )
        config = alembic_config.Config(os.path.abspath(path))
        return config

    def _migrate_legacy_database(self, engine, connection, config):
        """Check if database is a legacy sqlalchemy-migrate-managed database.

        If it is, migrate it by "stamping" the initial alembic schema.
        """
        # If the database doesn't have the sqlalchemy-migrate legacy migration
        # table, we don't have anything to do
        if not sa.inspect(engine).has_table('migrate_version'):
            return

        # Likewise, if we've already migrated to alembic, we don't have
        # anything to do
        context = alembic_migration.MigrationContext.configure(
            connection
        )
        if context.get_current_revision():
            return

        alembic_init_version = '1333cef214d9'

        LOG.info(
            'The database is still under sqlalchemy-migrate control; '
            'fake applying the initial alembic migration'
        )
        alembic_api.stamp(config, alembic_init_version)

    def _upgrade_alembic(self, engine, config, version):
        # re-use the connection rather than creating a new one
        with engine.begin() as connection:
            config.attributes['connection'] = connection
            self._migrate_legacy_database(engine, connection, config)
            alembic_api.upgrade(config, version or 'head')

    def get_engine(self):
        if not self._engine:
            self._engine = db_session.get_engine()
        return self._engine

    def get_api(self):
        self.get_engine()
        return self.IMPL

    def db_sync(self, version=None, engine=None):
        """Migrate the database to `version` or the most recent version."""
        # If the user requested a specific version, check if it's an integer:
        # if so, we're almost certainly in sqlalchemy-migrate land and won't
        # support that
        if version is not None and version.isdigit():
            raise ValueError(
                'You requested an sqlalchemy-migrate database version;'
                'this is no longer supported'
            )

        if engine is None:
            engine = self.get_engine()

        config = self._find_alembic_conf()

        # Discard the URL encoded in alembic.ini in favour of the URL
        # configured for the engine by the database fixtures, casting from
        # 'sqlalchemy.engine.url.URL' to str in the process. This returns a
        # RFC-1738 quoted URL, which means that a password like "foo@" will be
        # turned into "foo%40". This in turns causes a problem for
        # set_main_option() because that uses ConfigParser.set, which
        # (by design) uses *python* interpolation to write the string out ...
        # where "%" is the special python interpolation character!
        # Avoid this mismatch by quoting all %'s for the set below.
        engine_url = engine.url.render_as_string(
            hide_password=False).replace('%', '%%')
        config.set_main_option('sqlalchemy.url', str(engine_url))
        LOG.info('Applying migration(s)')
        self._upgrade_alembic(engine, config, version)
        LOG.info('Migration(s) applied')

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
