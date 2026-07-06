# Copyright 2026, Cleura AB
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

"""normalize job actions

Replace the ``jobs.job_actions`` JSON blob (which duplicated the whole action
definition for every assignment) with a dedicated ``job_actions`` child table
that links a job to its actions by foreign key, preserving order via
``position``. The action definition itself keeps living in the ``actions``
table.

Revision ID: a1b2c3d4e5f6
Revises: 4f8c679a1d3b
Create Date: 2026-07-03 10:00:00.000000

"""
from typing import Sequence
import uuid

from alembic import op
from oslo_log import log
from oslo_serialization import jsonutils as json
import sqlalchemy as sa

LOG = log.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: str = '4f8c679a1d3b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _loads(value):
    if not value:
        return None
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        LOG.warning('Failed to load JSON value: %s', value)
        return None


def upgrade() -> None:
    op.create_table(
        'job_actions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('action_id', sa.String(length=36), nullable=False),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id']),
        sa.ForeignKeyConstraint(['action_id'], ['actions.id']),
        mysql_engine='InnoDB',
    )
    op.create_index('ix_job_actions_job_id', 'job_actions', ['job_id'])
    op.create_index('ix_job_actions_action_id', 'job_actions', ['action_id'])

    _migrate_data_up()

    op.drop_column('jobs', 'job_actions')


def _action_values(action_entry, action_id, job_row):
    """
    Build action values from a job actions entry.
    """

    # freezer_action keys that map onto dedicated Action columns (mirrors
    # freezer_api.db.sqlalchemy.api.add_action).
    freezer_action_keys = ('action', 'backup_name', 'container',
                           'path_to_backup', 'timeout', 'priority',
                           'mandatory', 'log_file')
    freezer_action = action_entry.get('freezer_action') or {}
    values = {
        'id': action_id,
        'project_id': action_entry.get('project_id') or job_row.project_id,
        'user_id': action_entry.get('user_id') or job_row.user_id,
        'actionmode': freezer_action.get('mode'),
        'max_retries': action_entry.get('max_retries', 5),
        'max_retries_interval': action_entry.get('max_retries_interval', 6),
        'backup_metadata': json.dumps(freezer_action),
        'deleted': False,
        'created_at': job_row.created_at,
        'updated_at': job_row.updated_at,
    }
    for key in freezer_action_keys:
        values[key] = freezer_action.get(key)
    # ``action`` is NOT NULL; make sure it is always populated.
    values['action'] = freezer_action.get('action')
    return values


def _migrate_data_up() -> None:
    """
    Migrate job actions from the old JSON blob column to the new table.
    WARNING: If job actions are invalid, the migration is irreversible
    and the down migration will not restore invalid data.
    """
    conn = op.get_bind()
    meta = sa.MetaData()
    jobs = sa.Table('jobs', meta, autoload_with=conn)
    actions = sa.Table('actions', meta, autoload_with=conn)
    job_actions = sa.Table('job_actions', meta, autoload_with=conn)

    known_actions = {
        row.id for row in conn.execute(sa.select(actions.c.id)).fetchall()
    }

    job_rows = conn.execute(sa.select(jobs)).fetchall()

    for job_row in job_rows:
        job_actions_entries = _loads(job_row.job_actions) or []
        if not isinstance(job_actions_entries, list):
            LOG.warning('Skipping job %s: job_actions is of type %s',
                        job_row.id, type(job_actions_entries))
            continue
        for position, job_action_entry in enumerate(job_actions_entries):
            if not isinstance(job_action_entry, dict):
                LOG.warning('Skipping job_action %s of job %s: not a '
                            'dictionary', position, job_row.id)
                continue
            action_id = job_action_entry.get('action_id')
            if not action_id or action_id not in known_actions:
                # The referenced action is missing (inline action that was
                # never registered): create a new action row for it.
                freezer_action = job_action_entry.get('freezer_action') or {}
                if not freezer_action.get('action'):
                    # actions.action is NOT NULL; without an action name we
                    # cannot create a valid row, so skip this entry instead
                    # of aborting the whole migration.
                    LOG.warning('Skipping job_action %s of job %s: no action '
                                'name to create an action from',
                                position, job_row.id)
                    continue
                action_id = action_id or uuid.uuid4().hex
                LOG.info('Creating missing action %s referenced by job %s',
                         action_id, job_row.id)
                conn.execute(actions.insert().values(
                    **_action_values(job_action_entry, action_id, job_row)))
                known_actions.add(action_id)
            conn.execute(job_actions.insert().values(
                id=uuid.uuid4().hex,
                job_id=job_row.id,
                action_id=action_id,
                position=position,
                deleted=False,
            ))


def downgrade() -> None:
    op.add_column('jobs', sa.Column('job_actions', sa.Text(), nullable=True))

    _migrate_data_down()

    op.drop_index('ix_job_actions_action_id', table_name='job_actions')
    op.drop_index('ix_job_actions_job_id', table_name='job_actions')
    op.drop_table('job_actions')


def _action_entry(action_row):
    """Rebuild a legacy job_actions entry from an actions row."""
    freezer_action = _loads(action_row.backup_metadata) or {}
    freezer_action['backup_name'] = action_row.backup_name
    freezer_action['action'] = action_row.action
    freezer_action['mode'] = action_row.actionmode
    freezer_action['container'] = action_row.container
    freezer_action['timeout'] = action_row.timeout
    freezer_action['priority'] = action_row.priority
    freezer_action['path_to_backup'] = action_row.path_to_backup
    freezer_action['log_file'] = action_row.log_file
    return {
        'action_id': action_row.id,
        'user_id': action_row.user_id,
        'project_id': action_row.project_id,
        'max_retries': action_row.max_retries,
        'max_retries_interval': action_row.max_retries_interval,
        'freezer_action': freezer_action,
    }


def _migrate_data_down() -> None:
    """
    Migrate job actions from the new table to the old JSON blob column.
    WARNING: If migrated job actions were invalid, this migration will not
    restore them.
    """
    conn = op.get_bind()
    meta = sa.MetaData()
    jobs = sa.Table('jobs', meta, autoload_with=conn)
    actions = sa.Table('actions', meta, autoload_with=conn)
    job_actions = sa.Table('job_actions', meta, autoload_with=conn)

    for job in conn.execute(sa.select(jobs.c.id)).fetchall():
        job_actions_links = conn.execute(
            sa.select(job_actions).where(
                job_actions.c.job_id == job.id
            ).order_by(job_actions.c.position)
        ).fetchall()

        action_entries = []
        for job_actions_link in job_actions_links:
            if job_actions_link.deleted:
                continue
            action_row = conn.execute(
                sa.select(actions).where(
                    actions.c.id == job_actions_link.action_id)
            ).first()
            if action_row is not None:
                action_entries.append(_action_entry(action_row))

        conn.execute(jobs.update().where(jobs.c.id == job.id).values(
            job_actions=json.dumps(action_entries),
        ))
