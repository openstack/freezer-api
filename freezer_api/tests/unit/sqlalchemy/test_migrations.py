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

"""Tests for database migrations."""

from alembic import command as alembic_api
from alembic import script as alembic_script
from freezer_api.db import manager
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import test_fixtures
from oslotest import base as test_base
import sqlalchemy


class DatabaseSanityChecks(
    test_fixtures.OpportunisticDBTestMixin,
    test_base.BaseTestCase,
):
    def setUp(self):
        super().setUp()
        self.engine = enginefacade.writer.get_engine()
        self.db_driver = manager.get_db_driver('sqlalchemy',
                                               backend='sqlalchemy')
        self.config = self.db_driver._find_alembic_conf()

    def test_single_base_revision(self):
        """Ensure we only have a single base revision.

        There's no good reason for us to have diverging history, so validate
        that only one base revision exists. This will prevent simple errors
        where people forget to specify the base revision. If this fail for your
        change, look for migrations that do not have a 'revises' line in them.
        """
        script = alembic_script.ScriptDirectory.from_config(self.config)
        self.assertEqual(1, len(script.get_bases()))

    def test_single_head_revision(self):
        """Ensure we only have a single head revision.

        There's no good reason for us to have diverging history, so validate
        that only one head revision exists. This will prevent merge conflicts
        adding additional head revision points. If this fail for your change,
        look for migrations with the same 'revises' line in them.
        """
        script = alembic_script.ScriptDirectory.from_config(self.config)
        self.assertEqual(1, len(script.get_heads()))


class MigrationsWalk(
    test_fixtures.OpportunisticDBTestMixin,
    test_base.BaseTestCase,
):
    # Migrations can take a long time, particularly on underpowered CI nodes.
    # Give them some breathing room.
    TIMEOUT_SCALING_FACTOR = 4

    def setUp(self):
        super().setUp()
        self.db_driver = manager.get_db_driver('sqlalchemy',
                                               backend='sqlalchemy')
        self.config = self.db_driver._find_alembic_conf()
        # Currently, alembic uses 'sqlite:///freezer.db'
        # ignoring self.config.attributes['connection'] = connection
        # (which connected to sqlite://)
        # Use the same database as alembic until we can fix this.
        self.engine = sqlalchemy.create_engine(
            self.config.get_main_option('sqlalchemy.url'))
        self.init_versions = {'1333cef214d9', 'e74c32f034c5'}

    def _migrate_up(self, revision, connection):
        check_method = getattr(self, f'_check_{revision}', None)
        # no tests for the initial revisions
        if revision not in self.init_versions:
            self.assertIsNotNone(
                check_method,
                f"DB Migration {revision} doesn't have a test; add one"
            )

        pre_upgrade = getattr(self, f'_pre_upgrade_{revision}', None)
        if pre_upgrade:
            pre_upgrade(connection)

        alembic_api.upgrade(self.config, revision)

        if check_method:
            check_method(connection)

    _23c8ad2655a6_added_columns = (
        'supported_actions',
        'supported_modes',
        'supported_storages',
        'supported_engines',
    )

    def _check_23c8ad2655a6(self, connection):
        inspector = sqlalchemy.inspect(connection)
        columns = [x['name'] for x in inspector.get_columns('clients')]
        for added_column in self._23c8ad2655a6_added_columns:
            self.assertIn(added_column, columns)

    def test_walk_versions(self):
        with self.engine.begin() as connection:
            self.config.attributes['connection'] = connection
            script = alembic_script.ScriptDirectory.from_config(self.config)
            revisions = list(script.walk_revisions())
            # Need revisions from older to newer so the walk works as intended
            revisions.reverse()
            for revision_script in revisions:
                self._migrate_up(revision_script.revision, connection)


class TestMigrationsWalkMySQL(
    MigrationsWalk,
    test_fixtures.OpportunisticDBTestMixin,
    test_base.BaseTestCase,
):
    FIXTURE = test_fixtures.MySQLOpportunisticFixture


class TestMigrationsWalkPostgreSQL(
    MigrationsWalk,
    test_fixtures.OpportunisticDBTestMixin,
    test_base.BaseTestCase,
):
    FIXTURE = test_fixtures.PostgresqlOpportunisticFixture
