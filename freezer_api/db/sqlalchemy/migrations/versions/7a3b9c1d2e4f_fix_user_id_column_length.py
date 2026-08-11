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

"""fix user_id column length in jobs and sessions tables

The user_id columns in the jobs and sessions tables were defined as
VARCHAR(36), matching standard UUID length. However some Keystone
deployments produce user IDs longer than 36 characters (up to 64),
which causes a DataError on job and session creation.

The clients, actions, backups and action_reports tables already use
VARCHAR(64) for user_id consistently. This migration aligns jobs and
sessions to the same length.

Revision ID: 7a3b9c1d2e4f
Revises: 5c9d21e87f34
Create Date: 2026-08-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '7a3b9c1d2e4f'
down_revision = '5c9d21e87f34'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('jobs') as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.String(36),
            type_=sa.String(64),
            existing_nullable=False,
            nullable=False,
        )
    with op.batch_alter_table('sessions') as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.String(36),
            type_=sa.String(64),
            existing_nullable=False,
            nullable=False,
        )


def downgrade():
    with op.batch_alter_table('jobs') as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.String(64),
            type_=sa.String(36),
            existing_nullable=False,
            nullable=False,
        )
    with op.batch_alter_table('sessions') as batch_op:
        batch_op.alter_column(
            'user_id',
            existing_type=sa.String(64),
            type_=sa.String(36),
            existing_nullable=False,
            nullable=False,
        )
