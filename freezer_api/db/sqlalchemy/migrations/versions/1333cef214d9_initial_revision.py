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

"""Initial revision

Revision ID: 1333cef214d9
Revises:
Create Date: 2024-03-29 18:40:39.728144

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1333cef214d9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'action_reports',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('result', sa.String(length=255), nullable=True),
        sa.Column('time_elapsed', sa.String(length=255), nullable=True),
        sa.Column('report_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('log', sa.BLOB(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'actions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('actionmode', sa.String(length=255), nullable=True),
        sa.Column('src_file', sa.String(length=255), nullable=True),
        sa.Column('backup_name', sa.String(length=255), nullable=True),
        sa.Column('container', sa.String(length=255), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('max_retries_interval', sa.Integer(), default=6),
        sa.Column('max_retries', sa.Integer(), default=5),
        sa.Column('mandatory', sa.Boolean(), default=False),
        sa.Column('log_file', sa.String(length=255), nullable=True),
        sa.Column('backup_metadata', sa.Text(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'backups',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('user_name', sa.String(length=64), nullable=False),
        sa.Column('backup_metadata', sa.Text(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'clients',
        sa.Column(
            'id', sa.String(255), nullable=False,
        ),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('client_id', sa.String(length=255), nullable=False),
        sa.Column('hostname', sa.String(length=128), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('session_tag', sa.Integer(), nullable=True, default=0),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('hold_off', sa.Integer(), nullable=True, default=30),
        sa.Column('schedule', sa.Text(), nullable=True),
        sa.Column('job', sa.Text(), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('time_start', sa.Integer(), default=-1),
        sa.Column('time_end', sa.Integer(), default=-1),
        sa.Column('time_started', sa.Integer(), default=-1),
        sa.Column('time_ended', sa.Integer(), default=-1),
        sa.Column('status', sa.String(length=255), nullable=True),
        sa.Column('result', sa.String(length=255), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('schedule', sa.Text(), nullable=True),
        sa.Column('client_id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=36), default=''),
        sa.Column('session_tag', sa.Integer(), default=0),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('job_actions', sa.Text(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
