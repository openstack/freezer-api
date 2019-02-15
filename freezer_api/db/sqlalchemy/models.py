# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2014 IBM Corp.
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

from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy import BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship


BASE = declarative_base()


class FreezerBase(models.TimestampMixin,
                  models.ModelBase):
    """Base class for Freezer Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}

    deleted_at = Column(DateTime)
    deleted = Column(Boolean, default=False)
    backup_metadata = None

    @staticmethod
    def delete_values():
        return {'deleted': True,
                'deleted_at': timeutils.utcnow()}

    def delete(self, session):
        """Delete this object."""
        updated_values = self.delete_values()
        self.update(updated_values)
        self.save(session=session)
        return updated_values


class Client(BASE, FreezerBase):
    """Represents a scheduler of the freezer action."""

    __tablename__ = 'clients'
    id = Column(String(255), primary_key=True)
    project_id = Column(String(36))
    user_id = Column(String(64), nullable=False)
    client_id = Column(String(255), nullable=False)
    hostname = Column(String(128))
    description = Column(String(255))
    uuid = Column(String(36), nullable=False)


class Action(BASE, FreezerBase):
    """Represents freezer action."""
    # The field backup_metadata is json, including :
    # hostname ,snapshot ,storage ,dry_run , lvm_auto_snap, lvm_dirmount,
    # lvm_snapname max_level , max_priority, max_segment_size , mode,
    # mysql_conf, path_to_backup,  remove_older_than restore_abs_path
    # restore_from_host, ssh_host , ssh_key , ssh_username, ssh_port , proxy
    # no_incremental, overwrite , nova_inst_id , engine_name
    # restore_from_date , command , incremental

    __tablename__ = 'actions'
    id = Column(String(36), primary_key=True)
    action = Column(String(255), nullable=False)
    project_id = Column(String(36))
    user_id = Column(String(64), nullable=False)
    mode = Column(String(255))
    src_file = Column(String(255))
    backup_name = Column(String(255))
    container = Column(String(255))
    timeout = Column(Integer)
    priority = Column(Integer)
    max_retries_interval = Column(Integer, default=6)
    max_retries = Column(Integer, default=5)
    mandatory = Column(Boolean, default=False)
    log_file = Column(String(255))
    backup_metadata = Column(Text)


class Session(BASE, FreezerBase):
    """Represents freezer session."""

    __tablename__ = 'sessions'
    id = Column(String(36), primary_key=True)
    session_tag = Column(Integer, default=0)
    description = Column(String(255))
    hold_off = Column(Integer, default=30)
    schedule = Column(Text)
    job = Column(Text)
    project_id = Column(String(36))
    user_id = Column(String(36), nullable=False)
    time_start = Column(Integer, default=-1)
    time_end = Column(Integer, default=-1)
    time_started = Column(Integer, default=-1)
    time_ended = Column(Integer, default=-1)
    status = Column(String(255))
    result = Column(String(255))


class Job(BASE, FreezerBase):
    """Represents freezer job."""

    __tablename__ = 'jobs'
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36))
    user_id = Column(String(36), nullable=False)
    schedule = Column(Text)
    client_id = Column(String(255), ForeignKey('clients.id'), nullable=False)
    session_id = Column(String(36), ForeignKey('sessions.id'), nullable=False)
    session_tag = Column(Integer, default=0)
    description = Column(String(255))
    job_actions = Column(Text)
    client = relationship(Client, backref='jobs',
                          foreign_keys=client_id,
                          primaryjoin='and_('
                          'Job.client_id == Client.id,'
                          'Job.deleted == False)')
    session = relationship(Session, backref='jobs',
                           foreign_keys=session_id,
                           primaryjoin='and_('
                           'Job.session_id == Session.id,'
                           'Job.deleted == False)')


class ActionReport(BASE, FreezerBase):
    __tablename__ = 'action_reports'
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36))
    user_id = Column(String(64), nullable=False)
    result = Column(String(255))
    time_elapsed = Column(String(255))
    report_date = Column(TIMESTAMP)
    log = Column(BLOB)


class Backup(BASE, FreezerBase):
    """Represents freezer Backup."""
    # The field backup_metadata is json, including :
    # nova_inst_id, engine_name, storage, remove_older_than, restore_from_date,
    # command, incremental, restore_abs_path, etc

    __tablename__ = 'backups'
    id = Column(String(36), primary_key=True)
    job_id = Column(String(36))
    project_id = Column(String(36))
    user_id = Column(String(64), nullable=False)
    user_name = Column(String(64), nullable=False)
    backup_metadata = Column(Text)


def register_models(engine):
    _models = (Client, Action, Job, Session,
               ActionReport, Backup)
    for _model in _models:
        _model.metadata.create_all(engine)


def unregister_models(engine):
    _models = (Client, Action, Job, Session,
               ActionReport, Backup)
    for _model in _models:
        _model.metadata.drop_all(engine)


def get_tables(engine):
    from sqlalchemy import MetaData
    _meta = MetaData()
    _meta.reflect(engine)
    return _meta.tables.keys()
