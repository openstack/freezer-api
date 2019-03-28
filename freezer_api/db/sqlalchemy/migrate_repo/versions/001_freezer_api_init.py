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
from sqlalchemy import Integer, MetaData, String, Table, Text
from sqlalchemy import BLOB, TIMESTAMP

CLASS_NAME = 'default'


def define_tables(meta, sqlite):
    clients = Table(
        'clients', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('user_id', String(36), nullable=False),
        Column('id', String(255), primary_key=True, nullable=False),
        Column('project_id', String(36)),
        Column('client_id', String(255), nullable=False),
        Column('hostname', String(255), nullable=False),
        Column('description', String(255)),
        Column('uuid', String(36), nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    # scheduling field info is json, same as job table
    sessions = Table(
        'sessions', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('id', String(36), primary_key=True, nullable=False),
        Column('session_tag', Integer, default=0),
        Column('description', String(255)),
        Column('hold_off', Integer, default=30),
        Column('schedule', Text),
        Column('job', Text),
        Column('project_id', String(36)),
        Column('user_id', String(36), nullable=False),
        Column('time_start', Integer, default=-1),
        Column('time_end', Integer, default=-1),
        Column('time_started', Integer, default=-1),
        Column('time_ended', Integer, default=-1),
        Column('status', String(255)),
        Column('result', String(255)),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    # scheduling field info is json, including: {
    #  "time_ended" : 1538122522,
    #  "schedule_hour" : "16",
    #  "time_started" : 1538122500,
    #  "schedule_start_date" : "2018-09-25T15:50:03",
    # "schedule_minute" : "15",
    #  "time_created" : 1537861978,
    #  "event" : "",
    #  "status" : "scheduled",
    #  "result" : "success",
    #  "current_pid" : 14520
    # }, etc
    jobs = Table(
        'jobs', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('id', String(36), primary_key=True, nullable=False),
        Column('project_id', String(36)),
        Column('user_id', String(36), nullable=False),
        Column('schedule', Text),
        Column('client_id', String(255), nullable=False),
        Column('session_id', String(36), default=''),
        Column('session_tag', Integer, default=0),
        Column('description', String(255)),
        Column('job_actions', Text),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    # The field metadata is json, including :
    # nova_inst_id, engine_name, storage, remove_older_than, restore_from_date,
    # command, incremental, restore_abs_path, etc
    if sqlite:
        column_name = 'actionmode'
    else:
        column_name = 'mode'

    actions = Table(
        'actions', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('id', String(36), primary_key=True, nullable=False),
        Column('action', String(255), nullable=False),
        Column('project_id', String(36)),
        Column('user_id', String(36), nullable=False),
        Column(column_name, String(255)),
        Column('src_file', String(255)),
        Column('backup_name', String(255)),
        Column('container', String(255)),
        Column('timeout', Integer),
        Column('priority', Integer),
        Column('max_retries_interval', Integer, default=6),
        Column('max_retries', Integer, default=5),
        Column('mandatory', Boolean, default=False),
        Column('log_file', String(255)),
        Column('backup_metadata', Text),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    action_reports = Table(
        'action_reports', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('id', String(36), primary_key=True, nullable=False),
        Column('project_id', String(36)),
        Column('user_id', String(36), nullable=False),
        Column('result', String(255)),
        Column('time_elapsed', String(255)),
        Column('report_date', TIMESTAMP),
        Column('log', BLOB),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    # The field metadata is json, including :
    # nova_inst_id, engine_name, storage, remove_older_than, restore_from_date,
    # command, incremental, restore_abs_path, etc
    backups = Table(
        'backups', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('id', String(36), primary_key=True, nullable=False),
        Column('job_id', String(36)),
        Column('project_id', String(36)),
        Column('user_id', String(64), nullable=False),
        Column('user_name', String(64)),
        Column('backup_metadata', Text),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )
    return [clients, sessions, jobs, actions, action_reports, backups]


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # create all tables
    # Take care on create order for those with FK dependencies
    if migrate_engine.name == 'sqlite':
        sqlite = True
    else:
        sqlite = False

    tables = define_tables(meta, sqlite)
    for table in tables:
        table.create()
