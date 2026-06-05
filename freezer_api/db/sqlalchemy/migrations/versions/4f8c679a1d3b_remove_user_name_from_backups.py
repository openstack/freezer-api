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

"""remove user_name from backups

Revision ID: 4f8c679a1d3b
Revises: 30a3fd20ec97
Create Date: 2026-06-01 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4f8c679a1d3b'
down_revision = '30a3fd20ec97'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('backups', 'user_name')


def downgrade() -> None:
    op.add_column('backups', sa.Column('user_name', sa.String(length=64),
                                       nullable=True))
