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

"""add heartbeat columns to clients

Adds the column freezer-api stamps when a scheduler reports that it is
alive, the interval the scheduler says it will report at, and the index
the lookup for one scheduler within one client uses.

The index is deliberately not unique: rows are soft-deleted, so a unique
index would stop a deleted scheduler from registering again under the
same identity.

Revision ID: b4e7f1a90c26
Revises: 7a3b9c1d2e4f
Create Date: 2026-08-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b4e7f1a90c26'
down_revision = '7a3b9c1d2e4f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clients', sa.Column('last_heartbeat', sa.DateTime(),
                                       nullable=True))
    op.add_column('clients', sa.Column('poll_interval', sa.Integer(),
                                       nullable=True))
    op.create_index('ix_clients_project_client_hostname', 'clients',
                    ['project_id', 'client_id', 'hostname'])


def downgrade():
    op.drop_index('ix_clients_project_client_hostname', 'clients')
    op.drop_column('clients', 'poll_interval')
    op.drop_column('clients', 'last_heartbeat')
