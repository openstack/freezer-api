#   Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import MetaData, String, Table

CLASS_NAME = 'default'


def define_tables(meta):
    clients = Table(
        'clients', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('user_id', String(36), nullable=False),
        Column('id', String(255), primary_key=True, nullable=False),
        Column('project_id', String(36), nullable=False),
        Column('config_id', String(255), nullable=False),
        Column('hostname', String(255), nullable=False),
        Column('description', String(255)),
        Column('uuid', String(36), nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    return [clients]


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # create all tables
    # Take care on create order for those with FK dependencies
    tables = define_tables(meta)

    for table in tables:
        table.create()
