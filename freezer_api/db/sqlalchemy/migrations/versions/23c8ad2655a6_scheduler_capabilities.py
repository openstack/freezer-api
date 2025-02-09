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

"""Add scheduler capabilities to clients table

Revision ID: 23c8ad2655a6
Revises: e74c32f034c5
Create Date: 2025-01-23 16:56:41.991073

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '23c8ad2655a6'
down_revision: Union[str, None] = 'e74c32f034c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'clients',
        sa.Column(
            'supported_actions',
            sa.String(length=255),
            nullable=True,
        )
    )
    default_supported_actions = (
        '["backup", "restore", "info", "admin", "exec"]')
    # backward compatibility: existing clients supports all actions
    op.execute("UPDATE clients SET "
               f"supported_actions = '{default_supported_actions}'")
    op.add_column(
        'clients',
        sa.Column(
            'supported_modes',
            sa.String(length=255),
            nullable=True,
        )
    )
    default_supported_modes = (
        '["fs", "mongo", "mysql", "sqlserver", "cinder", "glance", '
        '"cindernative", "nova"]')
    op.execute("UPDATE clients SET "
               f"supported_modes = '{default_supported_modes}'")
    op.add_column(
        'clients',
        sa.Column(
            'supported_storages',
            sa.String(length=255),
            nullable=True,
        )
    )
    default_supported_storages = (
        '["local", "swift", "ssh", "s3", "ftp", "ftps"]')
    op.execute("UPDATE clients SET "
               f"supported_storages = '{default_supported_storages}'")
    op.add_column(
        'clients',
        sa.Column(
            'supported_engines',
            sa.String(length=255),
            nullable=True,
        )
    )
    default_supported_engines = (
        '["tar", "rsync", "rsyncv2", "nova", "osbrick", "glance"]')
    op.execute("UPDATE clients SET "
               f"supported_engines = '{default_supported_engines}'")
