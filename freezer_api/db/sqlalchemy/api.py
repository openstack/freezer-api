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


import sys

from oslo_config import cfg
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as sqlalchemyutils
from oslo_log import log

from freezer_api.api.common import utils as json_utils
from freezer_api.common._i18n import _
from freezer_api.common import elasticv2_utils as utils
from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.db.sqlalchemy import models


CONF = cfg.CONF
LOG = log.getLogger(__name__)


main_context_manager = enginefacade.transaction_context()
api_context_manager = enginefacade.transaction_context()


def _get_db_conf(conf_group, connection=None):
    kw = dict(
        connection=connection or conf_group.connection,
        slave_connection=conf_group.slave_connection,
        sqlite_fk=False,
        __autocommit=True,
        expire_on_commit=False,
        mysql_sql_mode=conf_group.mysql_sql_mode,
        connection_recycle_time=conf_group.connection_recycle_time,
        connection_debug=conf_group.connection_debug,
        max_pool_size=conf_group.max_pool_size,
        max_overflow=conf_group.max_overflow,
        pool_timeout=conf_group.pool_timeout,
        sqlite_synchronous=conf_group.sqlite_synchronous,
        connection_trace=conf_group.connection_trace,
        max_retries=conf_group.max_retries,
        retry_interval=conf_group.retry_interval)
    return kw


def get_backend():
    return sys.modules[__name__]


def create_context_manager(connection=None):
    """Create a database context manager object.
    : param connection: The database connection string
    """
    ctxt_mgr = enginefacade.transaction_context()
    ctxt_mgr.configure(**_get_db_conf(CONF.database, connection=connection))
    return ctxt_mgr


def _context_manager_from_context(context):
    if context:
        try:
            return context.db_connection
        except AttributeError:
            pass


def get_context_manager(context):
    """Get a database context manager object.
    :param context: The request context that can contain a context manager
    """
    return _context_manager_from_context(context) or main_context_manager


def get_engine(use_slave=False, context=None):
    """Get a database engine object.
    :param use_slave: Whether to use the slave connection
    :param context: The request context that can contain a context manager
    """
    ctxt_mgr = get_context_manager(context)
    return ctxt_mgr.get_legacy_facade().get_engine(use_slave=use_slave)


def get_db_session(context=None):
    """Get a database session object.
    :param context: The request context that can contain a context manager
    """
    ctxt_mgr = get_context_manager(context)
    return ctxt_mgr.get_legacy_facade().get_session()


def get_api_engine():
    return api_context_manager.get_legacy_facade().get_engine()


def model_query(session, model,
                args=None,
                read_deleted='no',
                project_id=None):
    """Query helper that accounts for context's `read_deleted` field.

    :param session:     The session to use, sqlalchemy.orm.session.Session
    :param model:       Model to query. Must be a subclass of ModelBase.
    :param args:        Arguments to query. If None - model is used.
    :param read_deleted: If not None, overrides context's read_deleted field.
                        Permitted values are 'no', which does not return
                        deleted values; 'only', which only returns deleted
                        values; and 'yes', which does not filter deleted
                        values.
    :param project_id:  tenant id
    """

    query_kwargs = {}
    if 'no' == read_deleted:
        query_kwargs['deleted'] = False
    elif 'only' == read_deleted:
        query_kwargs['deleted'] = True
    elif 'yes' == read_deleted:
        pass
    else:
        raise ValueError(_("Unrecognized read_deleted value '%s'")
                         % read_deleted)

    query = sqlalchemyutils.model_query(
        model, session, args, **query_kwargs)

    if project_id:
        query = query.filter_by(project_id=project_id)

    return query


def get_client(project_id, user_id, client_id=None, offset=0,
               limit=10, search=None):
    search = search or {}
    clients = []
    session = get_db_session()
    query = model_query(session, models.Client, project_id=project_id)

    if client_id:
        query = query.filter_by(user_id=user_id).filter_by(client_id=client_id)
    else:
        query = query.filter_by(user_id=user_id)

    result = query.all()

    for client in result:
        clientmap = {}
        clientmap[u'project_id'] = client.project_id
        clientmap[u'user_id'] = client.user_id
        clientmap[u'client'] = {u'uuid': client.uuid,
                                u'hostname': client.hostname,
                                u'client_id': client.client_id,
                                u'description': client.description}
        clients.append(clientmap)

    session.close()
    return clients


def add_client(project_id, user_id, doc):
    client_doc = utils.ClientDoc.create(doc, project_id, user_id)
    client_id = client_doc['client']['client_id']
    values = {}
    client_json = client_doc.get('client', {})

    existing = get_client(project_id=project_id, user_id=user_id,
                          client_id=client_id)
    if existing:
        raise freezer_api_exc.DocumentExists(
            message='Client already registered with ID'
                    ' {0}'.format(client_id))

    client = models.Client()
    values['project_id'] = project_id
    values['client_id'] = client_id
    values['id'] = client_json.get('uuid', None)
    values['user_id'] = user_id
    values['hostname'] = client_json.get('hostname', None)
    values['uuid'] = client_json.get('uuid', None)
    values['description'] = client_json.get('description', None)
    client.update(values)

    session = get_db_session()
    with session.begin():
        try:
            client.save(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    LOG.info('Client registered, client_id: {0}'.format(client_id))
    session.close()
    return client_id


def delete_client(project_id, user_id, client_id):
    session = get_db_session()
    query = model_query(session, models.Client, project_id=project_id)
    query = query.filter_by(user_id=user_id).filter_by(client_id=client_id)
    result = query.all()
    if 1 == len(result):
        try:
            result[0].delete(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))
        LOG.info('Client delete, client_id: {0} deleted'.
                 format(client_id))
    else:
        LOG.info('Client delete, client_id: {0} not found'.
                 format(client_id))

    session.close()
    return client_id


def delete_action(project_id, user_id, action_id):

    session = get_db_session()
    query = model_query(session, models.Action, project_id=project_id)
    query = query.filter_by(user_id=user_id).filter_by(id=action_id)

    result = query.all()
    if 1 == len(result):
        try:
            result[0].delete(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))
            LOG.info('Action delete, action_id: {0} deleted'.
                     format(action_id))
    else:
            LOG.info('Action delete, action_id: {0} not found'.
                     format(action_id))

    query = model_query(session, models.ActionReport, project_id=project_id)
    query = query.filter_by(user_id=user_id).filter_by(id=action_id)

    result = query.all()
    if 1 == len(result):
        try:
            result[0].delete(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))
            LOG.info('ActionReport delete, action_id: {0} deleted'.
                     format(action_id))
    else:
            LOG.info('ActionReport delete, action_id: {0} not found'.
                     format(action_id))
    session.close()
    return action_id


def add_action(project_id, user_id, doc):
    action_doc = utils.ActionDoc.create(doc, user_id, project_id)
    keyt = ['action', 'mode', 'backup_name',
            'container', 'src_file', 'timeout',
            'priority', 'mandatory', 'log_file']
    freezer_action = action_doc.get('freezer_action', {})

    action_id = action_doc.get('action_id')
    existing = get_action(project_id=project_id, user_id=user_id,
                          action_id=action_id)
    if existing:
        raise freezer_api_exc.DocumentExists(
            message='Action already registered with ID'
                    ' {0}'.format(action_id))

    action = models.Action()

    actionvalue = {}
    actionreportvalue = {}
    actionvalue['project_id'] = project_id
    actionvalue['id'] = action_id
    actionvalue['user_id'] = user_id
    actionvalue['max_retries'] = action_doc.get('max_retries', 5)
    actionvalue['max_retries_interval'] = action_doc.\
        get('max_retries_interval', 6)

    for key in freezer_action.keys():
        if key in keyt:
            actionvalue[key] = freezer_action.get(key)

    actionreportvalue['result'] = freezer_action.get('result', None)
    actionreportvalue['time_elapsed'] = freezer_action.\
        get('time_elapsed', None)
    actionreportvalue['report_date'] = freezer_action.\
        get('report_date', None)
    actionvalue['backup_metadata'] = json_utils.json_encode(freezer_action)

    action.update(actionvalue)

    session = get_db_session()
    with session.begin():
        try:
            action.save(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    LOG.info('Action registered, action_id: {0}'.format(action_id))

    actionReport = models.ActionReport()

    actionreportvalue['project_id'] = project_id
    actionreportvalue['id'] = action_id
    actionreportvalue['user_id'] = user_id

    actionReport.update(actionreportvalue)

    with session.begin():
        try:
            actionReport.save(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    LOG.info('Action Reports registered, action_id: {0}'.
             format(action_id))
    session.close()
    return action_id


def get_action(project_id, user_id, action_id):
    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, models.Action, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=action_id)
            result = query.all()
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    session.close()
    values = {}
    if 1 == len(result):
        values['project_id'] = result[0].get('project_id')
        values['action_id'] = result[0].get('id')
        values['user_id'] = result[0].get('user_id')
        values['max_retries'] = result[0].get('max_retries')
        values['max_retries_interval'] = result[0].\
            get('max_retries_interval')
        values['freezer_action'] = json_utils.\
            json_decode(result[0].get('backup_metadata'))
        values['freezer_action']['backup_name'] = result[0].\
            get('backup_name')
        values['freezer_action']['action'] = result[0].get('action')
        values['freezer_action']['mode'] = result[0].get('mode')
        values['freezer_action']['container'] = result[0].\
            get('container')
        values['freezer_action']['timeout'] = result[0].get('timeout')
        values['freezer_action']['priority'] = result[0].get('priority')
        values['freezer_action']['src_file'] = result[0].get('src_file')
        values['freezer_action']['log_file'] = result[0].get('log_file')
    return values


def search_action(project_id, user_id, offset=0, limit=10, search=None):
    search = search or {}
    actions = []

    session = get_db_session()
    query = model_query(session, models.Action, project_id=project_id)
    query = query.filter_by(user_id=user_id)

    result = query.all()

    for action in result:
        actionmap = {}
        actionmap['project_id'] = project_id
        actionmap['user_id'] = user_id
        actionmap['timeout'] = action.timeout
        actionmap['max_retries_interval'] = action.max_retries_interval
        actionmap['max_retries'] = action.max_retries
        actionmap['action_id'] = action.id
        actionmap['mandatory'] = action.mandatory

        actionmap['freezer_action'] = json_utils.\
            json_decode(action.get('backup_metadata'))
        actionmap['freezer_action']['backup_name'] = action.\
            get('backup_name')
        actionmap['freezer_action']['mode'] = action.get('mode')
        actionmap['freezer_action']['action'] = action.get('action')
        actionmap['freezer_action']['container'] = action.\
            get('container')
        actionmap['freezer_action']['timeout'] = action.get('timeout')
        actionmap['freezer_action']['priority'] = action.get('priority')
        actionmap['freezer_action']['src_file'] = action.get('src_file')
        actionmap['freezer_action']['log_file'] = action.get('log_file')

        actions.append(actionmap)

    session.close()
    return actions


def update_action(user_id, action_id, patch_doc, project_id):
    # changes in user_id or action_id are not allowed
    valid_patch = utils.ActionDoc.create_patch(patch_doc)
    keyt = ['action', 'mode', 'backup_name', 'container',
            'src_file', 'timeout', 'priority', 'mandatory', 'log_file']

    values = {}

    freezer_action = valid_patch.get('freezer_action', {})

    values['project_id'] = project_id
    values['id'] = action_id
    values['user_id'] = user_id

    values['max_retries'] = valid_patch.get('max_retries', None)
    values['max_retries_interval'] = valid_patch.\
        get('max_retries_interval', None)

    for key in freezer_action.keys():
        if key in keyt:
            values[key] = freezer_action.get(key)

    values['backup_metadata'] = json_utils.json_encode(freezer_action)

    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, models.Action, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=action_id)
            result = query.update(values)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    session.close()

    if not result:
        raise freezer_api_exc.DocumentNotFound(
            message='Action not registered with ID'
                    ' {0}'.format(action_id))
    else:
        LOG.info('action updated, action_id: {0}'.format(action_id))
        return action_id


def replace_action(user_id, action_id, doc, project_id):

    valid_doc = utils.ActionDoc.update(doc, user_id, action_id, project_id)
    values = {}
    keyt = ['action', 'mode', 'backup_name', 'container',
            'src_file', 'timeout', 'priority', 'mandatory', 'log_file']
    bCreate = False

    freezer_action = valid_doc.get('freezer_action', {})

    values['project_id'] = project_id
    values['id'] = action_id
    values['user_id'] = user_id

    values['max_retries'] = valid_doc.get('max_retries', None)
    values['max_retries_interval'] = valid_doc.\
        get('max_retries_interval', None)

    for key in freezer_action.keys():
        if key in keyt:
            values[key] = freezer_action.get(key)

    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, models.Action, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=action_id)
            result = query.update(values)
            if not result:
                bCreate = True
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    session.close()

    if bCreate:
        action = models.Action()
        action.update(values)
        session = get_db_session()
        with session.begin():
            try:
                action.save(session=session)
            except Exception as e:
                session.close()
                raise freezer_api_exc.\
                    StorageEngineError(message='mysql operation failed {0}'.
                                       format(e))
        session.close()

    LOG.info('action replaced, action_id: {0}'.format(action_id))
    return action_id


def get_session(project_id, user_id, session_id):
    jobt = {}
    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, models.Session, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=session_id)
            result = query.all()
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    session.close()
    values = {}
    if 1 == len(result):
        values['project_id'] = result[0].get('project_id')
        values['session_id'] = result[0].get('id')
        values['user_id'] = result[0].get('user_id')
        values['description'] = result[0].get('description')
        values['session_tag'] = result[0].get('session_tag')
        values['result'] = result[0].get('result')
        values['hold_off'] = result[0].get('hold_off')
        values['status'] = result[0].get('status')
        values['time_ended'] = result[0].get('time_ended')
        values['time_started'] = result[0].get('time_started')
        values['time_end'] = result[0].get('time_end')
        values['time_start'] = result[0].get('time_start')

        values['schedule'] = json_utils.json_decode(result[0].
                                                    get('schedule'))
        jobt = result[0].get('job')
        if jobt is not None:
            values['jobs'] = json_utils.json_decode(result[0].get('job'))

    return values


def delete_session(project_id, user_id, session_id):
    session = get_db_session()
    query = model_query(session, models.Session, project_id=project_id)
    query = query.filter_by(user_id=user_id).filter_by(id=session_id)

    result = query.all()
    if 1 == len(result):
        try:
            result[0].delete(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))
            LOG.info('Session delete, session_id: {0} deleted'.
                     format(session_id))
    else:
        LOG.info('Session delete, session_id: {0} not found'.
                 format(session_id))

    session.close()
    return session_id


def add_session(project_id, user_id, doc):
    session_doc = utils.SessionDoc.create(doc=doc,
                                          user_id=user_id,
                                          project_id=project_id)
    session_id = session_doc['session_id']
    schedulingjson = session_doc.get('schedule')
    existing = get_session(project_id=project_id, user_id=user_id,
                           session_id=session_id)
    if existing:
        raise freezer_api_exc.DocumentExists(
            message='Session already registered with ID'
                    ' {0}'.format(session_id))

    sessiont = models.Session()
    sessionvalue = {}
    sessionvalue['project_id'] = project_id
    sessionvalue['id'] = session_id
    sessionvalue['user_id'] = user_id
    sessionvalue['description'] = session_doc.get('description', None)
    sessionvalue['hold_off'] = session_doc.get('hold_off', 30)
    sessionvalue['session_tag'] = session_doc.get('session_tag', 0)
    sessionvalue['status'] = session_doc.get('status')
    sessionvalue['time_ended'] = session_doc.get('time_ended', -1)
    sessionvalue['time_started'] = session_doc.get('time_started', -1)
    sessionvalue['time_end'] = session_doc.get('time_end', -1)
    sessionvalue['time_start'] = session_doc.get('time_start', -1)
    sessionvalue['result'] = session_doc.get('result', None)

    # The field scheduling is json
    sessionvalue['schedule'] = json_utils.json_encode(schedulingjson)
    sessiont.update(sessionvalue)

    session = get_db_session()
    with session.begin():
        try:
            sessiont.save(session=session)
        except Exception as e:
            session.close()
            raise freezer_api_exc.\
                StorageEngineError(message='mysql operation failed {0}'.
                                   format(e))

    LOG.info('Session registered, session_id: {0}'.format(session_id))

    session.close()
    return session_id


def update_session(user_id, session_id, patch_doc, project_id):
    valid_patch = utils.SessionDoc.create_patch(patch_doc)

    sessiont = get_session(project_id=project_id, user_id=user_id,
                           session_id=session_id)
    if not sessiont:
        raise freezer_api_exc.DocumentNotFound(
            message='Session not register with ID'
                    ' {0}'.format(session_id))

    values = {}
    for key in valid_patch.keys():
        if key == 'jobs':
            jobintable = sessiont.get('jobs', None)
            jobinpatch = valid_patch.get('jobs', None)
            if jobintable:
                jobintable.update(jobinpatch)
                jobinpatch.update(jobintable)
            values['job'] = json_utils.json_encode(valid_patch.get(key, None))
        elif key == 'schedule':
            values[key] = json_utils.json_encode(valid_patch.get(key, None))
        else:
            values[key] = valid_patch.get(key, None)

    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, models.Session, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=session_id)
            result = query.update(values)
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    session.close()

    if not result:
        raise freezer_api_exc.DocumentNotFound(
            message='session not registered with ID'
                    ' {0}'.format(session_id))
    else:
        LOG.info('session updated, session_id: {0}'.format(session_id))
        return 0


def replace_session(user_id, session_id, doc, project_id):

    valid_doc = utils.SessionDoc.update(doc, user_id, session_id,
                                        project_id)
    values = {}
    valuesnew = {}
    bCreate = False

    values['id'] = session_id
    values['project_id'] = project_id
    values['user_id'] = user_id
    values['schedule'] = json_utils.\
        json_encode(valid_doc.get('schedule', None))
    values['job'] = json_utils.json_encode(valid_doc.get('jobs', None))
    values['session_tag'] = valid_doc.get('session_tag', None)
    values['description'] = valid_doc.get('description', None)
    values['status'] = valid_doc.get('status')
    values['time_ended'] = valid_doc.get('time_ended', None)
    values['time_started'] = valid_doc.get('time_started', None)
    values['time_end'] = valid_doc.get('time_end', None)
    values['time_start'] = valid_doc.get('time_start', None)
    values['result'] = valid_doc.get('result', None)
    values['hold_off'] = valid_doc.get('hold_off', None)

    for key in values:
        if values[key] is not None:
            valuesnew[key] = values[key]

    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, models.Session, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=session_id)
            result = query.update(valuesnew)
            if not result:
                bCreate = True
        except Exception as e:
            session.close()
            raise freezer_api_exc.StorageEngineError(
                message='mysql operation failed {0}'.format(e))

    session.close()

    if bCreate:
        sessiont = models.Session()
        sessiont.update(valuesnew)
        session = get_db_session()
        with session.begin():
            try:
                sessiont.save(session=session)
            except Exception as e:
                session.close()
                raise freezer_api_exc.\
                    StorageEngineError(message='mysql operation failed {0}'.
                                       format(e))
        session.close()

    LOG.info('session replaced, session_id: {0}'.format(session_id))
    return session_id


def search_session(project_id, user_id, offset=0,
                   limit=10, search=None):
    search = search or {}
    sessions = []
    jobt = {}

    session = get_db_session()
    query = model_query(session, models.Session, project_id=project_id)
    query = query.filter_by(user_id=user_id)

    result = query.all()

    for sessiont in result:
        sessionmap = {}
        sessionmap['project_id'] = project_id
        sessionmap['user_id'] = user_id
        sessionmap['session_id'] = sessiont.get('id')
        sessionmap['description'] = sessiont.get('description')
        sessionmap['session_tag'] = sessiont.get('session_tag')
        sessionmap['result'] = sessiont.get('result')
        sessionmap['hold_off'] = sessiont.get('hold_off')
        sessionmap['status'] = sessiont.get('status')
        sessionmap['time_ended'] = sessiont.get('time_ended')
        sessionmap['time_end'] = sessiont.get('time_end')
        sessionmap['time_started'] = sessiont.get('time_started')
        sessionmap['time_start'] = sessiont.get('time_start')
        sessionmap['schedule'] = json_utils.\
            json_decode(sessiont.get('schedule'))
        jobt = sessiont.get('job')
        if jobt is not None:
            sessionmap['jobs'] = json_utils.json_decode(sessiont.get('job'))
        sessions.append(sessionmap)

    session.close()
    return sessions