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

"""
Tests for database migrations. This test case reads the configuration
file test_migrations.conf for database connection settings
to use in the tests. For each connection found in the config file,
the test case runs a series of test cases to ensure that migrations work
properly both upgrading and downgrading, and that no data loss occurs
if possible.
"""

import os

import fixtures
from migrate.versioning import api as migration_api
from migrate.versioning import repository
from oslo_db.sqlalchemy import test_migrations
from oslo_db.sqlalchemy import utils as db_utils
# from oslo_db.tests.sqlalchemy import base as test_base
import sqlalchemy
from sqlalchemy.engine import reflection

from freezer_api.db.sqlalchemy import driver
import freezer_api.db.sqlalchemy.migrate_repo


class MigrationsMixin(test_migrations.WalkVersionsMixin):
    """Test sqlalchemy-migrate migrations."""

    BOOL_TYPE = sqlalchemy.types.BOOLEAN
    TIME_TYPE = sqlalchemy.types.DATETIME
    INTEGER_TYPE = sqlalchemy.types.INTEGER
    VARCHAR_TYPE = sqlalchemy.types.VARCHAR
    TEXT_TYPE = sqlalchemy.types.Text

    @property
    def INIT_VERSION(self):
        return driver.INIT_VERSION

    @property
    def REPOSITORY(self):
        migrate_file = freezer_api.db.sqlalchemy.migrate_repo.__file__
        return repository.Repository(
            os.path.abspath(os.path.dirname(migrate_file)))

    @property
    def migration_api(self):
        return migration_api

    @property
    def migrate_engine(self):
        return self.engine

    def get_table_ref(self, engine, name, metadata):
        metadata.bind = engine
        return sqlalchemy.Table(name, metadata, autoload=True)

    class BannedDBSchemaOperations(fixtures.Fixture):
        """Ban some operations for migrations"""
        def __init__(self, banned_resources=None):
            super(MigrationsMixin.BannedDBSchemaOperations, self).__init__()
            self._banned_resources = banned_resources or []

        @staticmethod
        def _explode(resource, op):
            print('%s.%s()' % (resource, op))  # noqa
            raise Exception(
                'Operation %s.%s() is not allowed in a database migration' % (
                    resource, op))

        def setUp(self):
            super(MigrationsMixin.BannedDBSchemaOperations, self).setUp()
            for thing in self._banned_resources:
                self.useFixture(fixtures.MonkeyPatch(
                    'sqlalchemy.%s.drop' % thing,
                    lambda *a, **k: self._explode(thing, 'drop')))
                self.useFixture(fixtures.MonkeyPatch(
                    'sqlalchemy.%s.alter' % thing,
                    lambda *a, **k: self._explode(thing, 'alter')))

    def migrate_up(self, version, with_data=False):
        # NOTE(dulek): This is a list of migrations where we allow dropping
        # things. The rules for adding things here are very very specific.
        # Insight on how to drop things from the DB in a backward-compatible
        # manner is provided in Cinder's developer documentation.
        # Reviewers: DO NOT ALLOW THINGS TO BE ADDED HERE WITHOUT CARE
        exceptions = [3]

        if version not in exceptions:
            banned = ['Table', 'Column']
        else:
            banned = None
        with MigrationsMixin.BannedDBSchemaOperations(banned):
            super(MigrationsMixin, self).migrate_up(version, with_data)

    def assertColumnExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertIn(column, t.c)

    def assertColumnsExist(self, engine, table, columns):
        for column in columns:
            self.assertColumnExists(engine, table, column)

    def assertColumnType(self, engine, table, column, column_type):
        t = db_utils.get_table(engine, table)
        column_ref_type = str(t.c[column].type)
        self.assertEqual(column_ref_type, column_type)

    def assertColumnCount(self, engine, table, columns):
        t = db_utils.get_table(engine, table)
        self.assertEqual(len(columns), len(t.columns))

    def assertColumnNotExists(self, engine, table, column):
        t = db_utils.get_table(engine, table)
        self.assertNotIn(column, t.c)

    def assertIndexExists(self, engine, table, index):
        t = db_utils.get_table(engine, table)
        index_names = [idx.name for idx in t.indexes]
        self.assertIn(index, index_names)

    def __check_cinderbase_fields(self, columns):
        """Check fields inherited from CinderBase ORM class."""
        self.assertIsInstance(columns.created_at.type, self.TIME_TYPE)
        self.assertIsInstance(columns.updated_at.type, self.TIME_TYPE)
        self.assertIsInstance(columns.deleted_at.type, self.TIME_TYPE)
        self.assertIsInstance(columns.deleted.type, self.BOOL_TYPE)

    def _check_001(self, engine, data):
        clients_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'user_id',
            'id',
            'project_id',
            'client_id',
            'hostname',
            'description',
            'uuid',
        ]
        self.assertColumnsExist(
            engine, 'clients', clients_columns)
        self.assertColumnCount(
            engine, 'clients', clients_columns)

        sessions_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'id',
            'session_tag',
            'description',
            'hold_off',
            'schedule',
            'job',
            'project_id',
            'user_id',
            'time_start',
            'time_end',
            'time_started',
            'time_ended',
            'status',
            'result',
        ]
        self.assertColumnsExist(
            engine, 'sessions', sessions_columns)
        self.assertColumnCount(
            engine, 'sessions', sessions_columns)

        jobs_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'id',
            'project_id',
            'user_id',
            'schedule',
            'client_id',
            'session_id',
            'session_tag',
            'description',
            'job_actions',
        ]
        self.assertColumnsExist(
            engine, 'jobs', jobs_columns)
        self.assertColumnCount(
            engine, 'jobs', jobs_columns)

        actions_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'id',
            'action',
            'project_id',
            'user_id',
            'actionmode',
            'src_file',
            'backup_name',
            'container',
            'timeout',
            'priority',
            'max_retries_interval',
            'max_retries',
            'mandatory',
            'log_file',
            'backup_metadata',
        ]
        self.assertColumnsExist(
            engine, 'actions', actions_columns)
        self.assertColumnCount(
            engine, 'actions', actions_columns)

        action_reports_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'id',
            'project_id',
            'user_id',
            'result',
            'time_elapsed',
            'report_date',
            'log',
        ]
        self.assertColumnsExist(
            engine, 'action_reports', action_reports_columns)
        self.assertColumnCount(
            engine, 'action_reports', action_reports_columns)

        backups_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'id',
            'job_id',
            'project_id',
            'user_id',
            'user_name',
            'backup_metadata',
        ]
        self.assertColumnsExist(
            engine, 'backups', backups_columns)
        self.assertColumnCount(
            engine, 'backups', backups_columns)

    def _check_002(self, engine, data):
        actions_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'id',
            'action',
            'project_id',
            'user_id',
            'actionmode',
            'src_file',
            'backup_name',
            'container',
            'timeout',
            'priority',
            'max_retries_interval',
            'max_retries',
            'mandatory',
            'log_file',
            'backup_metadata',
        ]
        self.assertColumnsExist(
            engine, 'actions', actions_columns)
        self.assertColumnCount(
            engine, 'actions', actions_columns)

    def _check_003(self, engine, data):
        actions_columns = [
            'created_at',
            'updated_at',
            'deleted_at',
            'deleted',
            'id',
            'action',
            'project_id',
            'user_id',
            'actionmode',
            'path_to_backup',
            'backup_name',
            'container',
            'timeout',
            'priority',
            'max_retries_interval',
            'max_retries',
            'mandatory',
            'log_file',
            'backup_metadata',
        ]
        self.assertColumnsExist(
            engine, 'actions', actions_columns)
        self.assertColumnCount(
            engine, 'actions', actions_columns)

    def get_table_names(self, engine):
        inspector = reflection.Inspector.from_engine(engine)
        return inspector.get_table_names()

    def get_foreign_key_columns(self, engine, table_name):
        foreign_keys = set()
        table = db_utils.get_table(engine, table_name)
        inspector = reflection.Inspector.from_engine(engine)
        for column_dict in inspector.get_columns(table_name):
            column_name = column_dict['name']
            column = getattr(table.c, column_name)
            if column.foreign_keys:
                foreign_keys.add(column_name)
        return foreign_keys

    def get_indexed_columns(self, engine, table_name):
        indexed_columns = set()
        for index in db_utils.get_indexes(engine, table_name):
            for column_name in index['column_names']:
                indexed_columns.add(column_name)
        return indexed_columns

    def assert_each_foreign_key_is_part_of_an_index(self):
        engine = self.migrate_engine

        non_indexed_foreign_keys = set()

        for table_name in self.get_table_names(engine):
            indexed_columns = self.get_indexed_columns(engine, table_name)
            foreign_key_columns = self.get_foreign_key_columns(
                engine, table_name
            )
            for column_name in foreign_key_columns - indexed_columns:
                non_indexed_foreign_keys.add(table_name + '.' + column_name)

        self.assertSetEqual(set(), non_indexed_foreign_keys)

    def test_walk_versions(self):
        self.walk_versions(False, False)
        self.assert_each_foreign_key_is_part_of_an_index()


# class TestSqliteMigrations(test_base.DbTestCase,
#                            MigrationsMixin):
#     def assert_each_foreign_key_is_part_of_an_index(self):
        # Skip the test for SQLite because SQLite does not list
        # UniqueConstraints as indexes, which makes this test fail.
        # Given that SQLite is only for testing purposes, it is safe to skip
    # pass
