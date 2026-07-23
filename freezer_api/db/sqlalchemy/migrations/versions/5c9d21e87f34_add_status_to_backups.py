# Copyright 2026, Cleura AB.
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

"""add status to backups

Revision ID: 5c9d21e87f34
Revises: a1b2c3d4e5f6
Create Date: 2026-07-23 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '5c9d21e87f34'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('backups', sa.Column('status', sa.String(64),
                                       server_default='available',
                                       nullable=False))


def downgrade() -> None:
    op.drop_column('backups', 'status')
