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

"""add is_central to clients

Revision ID: 30a3fd20ec97
Revises: 29a2fd19eb86
Create Date: 2026-03-26 20:41:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '30a3fd20ec97'
down_revision = '29a2fd19eb86'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('clients', sa.Column('is_central', sa.Boolean(),
                                       server_default=sa.sql.false(),
                                       nullable=False))


def downgrade() -> None:
    op.drop_column('clients', 'is_central')
