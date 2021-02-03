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
from freezer_api.common import elasticv2_utils as utilsv2
from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.common import utils as utilsv1
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


def delete_tuple(tablename, user_id, tuple_id, project_id=None):
    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, tablename, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=tuple_id)
            result = query.all()
            if 1 == len(result):
                result[0].delete(session=session)
                LOG.info('Tuple delete, Tuple_id: '
                         '{0} deleted in Table {1}'.
                         format(tuple_id, tablename))
            else:
                LOG.info('Tuple delete, Tuple_id: '
                         '{0} not found in Table {1}'.
                         format(tuple_id, tablename))
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Mysql operation failed {0}'.format(e))
    return tuple_id


def get_tuple(tablename, user_id, tuple_id, project_id=None):
    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, tablename, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=tuple_id)
            result = query.all()
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Mysql operation failed {0}'.format(e))
    session.close()
    return result


def add_tuple(tuple):
    session = get_db_session()
    with session.begin():
        try:
            tuple.save(session=session)
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Mysql operation failed {0}'.format(e))


def update_tuple(tablename, user_id, tuple_id, tuple_values, project_id=None):

    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, tablename, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=tuple_id)
            result = query.update(tuple_values)
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='sql operation failed {0}'.format(e))

    if not result:
        raise freezer_api_exc.DocumentNotFound(
            message='Tuple not registered with ID'
                    ' {0} in Table{1} '.format(tuple_id, tablename))

    else:
        LOG.info('Tuple updated, tuple_id: {0}'.format(tuple_id))
        return tuple_id


def replace_tuple(tablename, user_id, tuple_id, tuple_values, project_id=None):

    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, tablename, project_id=project_id)
            query = query.filter_by(user_id=user_id).filter_by(id=tuple_id)
            result = query.update(tuple_values)
            if not result:
                tuplet = tablename()
                tuplet.update(tuple_values)
                tuplet.save(session=session)
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Mysql operation failed {0}'.format(e))
    return tuple_id


def search_tuple(tablename, user_id, project_id=None, offset=0,
                 limit=100, search=None):
    search = valid_and_get_search_option(search=search)
    session = get_db_session()
    with session.begin():
        try:
            # TODO(gecong) search will be implemented in the future
            query = model_query(session, tablename, project_id=project_id)
            query = query.filter_by(user_id=user_id)
            #  If search option isn't valid or set, we use limit and offset
            #  in sqlalchemy level
            if len(search) == 0:
                query = query.offset(offset)
                query = query.limit(limit)
            result = query.all()
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Mysql operation failed {0}'.format(e))
    session.close()
    return result, search


def get_recursively(source_dict, search_keys):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the search_keys
    provided.
    """
    search_keys_found = {}
    for key, value in source_dict.items():
        if key in search_keys.keys():
            search_keys_found[key] = value
        elif isinstance(value, dict):
            results = get_recursively(value, search_keys)
            for keytmp in results.keys():
                search_keys_found[keytmp] = results.get(keytmp)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, search_keys)
                    for key_another in more_results.keys():
                        search_keys_found[key_another] = \
                            more_results.get(key_another)

    return search_keys_found


def valid_and_get_search_option(search=None):
    if not search:
        return {}
    match_opt = search.get('match', {})
    match_not_opt = search.get('match_not', {})

    if not match_opt and not match_not_opt:
        return {}
    if len(match_opt) and '_all' in match_opt[0].keys():
        error_msg = '''
        Freezer-api supported by sqlalchemy:
        The option --search in freezer cmd needs a list about {key, value},
        such as:
        '[{"client_id": "node1_2"}]'
        '[{"client_id": "node1_2"}, {"status": "completed"}]'
        '''
        search = match_opt[0].get('_all')
        try:
            search = json_utils.json_decode(search)
        except Exception as e:
            msg = "{0} \n json_decode error: {1}".\
                format(error_msg, e)
            LOG.error(msg)
            return {}
        if not isinstance(search, list):
            LOG.error(error_msg)
            return {}
        search = {'match': search}
    if not isinstance(search, dict):
        return {}
    return search


def filter_tuple_by_search_opt(tuples, offset=0, limit=100, search=None):
    search = search or {}
    search_key = {}
    result_last = []
    # search opt is null, all tuples will be filtered in.
    if len(search) == 0:
        return tuples
    for m in search.get('match', []):
        for key, value in m.items():
            search_key[key] = value
    for m in search.get('match_not', []):
        for key, value in m.items():
            search_key[key] = value

    jobs_search_offset = 0
    jobs_search_count = 0
    for tuple in tuples:
        if jobs_search_count >= limit:
            return result_last
        filter_out = False
        search_keys_found = get_recursively(tuple, search_key)
        # If all keys and values are in search_keys_found, this tuple will be
        # filtered in, otherwise filtered out
        for m in search.get('match', []):
            for key, value in m.items():
                if value != search_keys_found.get(key):
                    filter_out = True
                    break
        # If one keys and values are in search_keys_found, this tuple will be
        # filtered out, otherwise filtered in.
        for m in search.get('match_not', []):
            for key, value in m.items():
                if value == search_keys_found.get(key):
                    filter_out = True
                    break
        if not filter_out:
            jobs_search_offset += 1
            if jobs_search_offset > offset:
                jobs_search_count += 1
                result_last.append(tuple)
    return result_last


def get_client_byid(user_id, client_id, project_id=None):

    session = get_db_session()
    with session.begin():
        try:
            query = model_query(session, models.Client, project_id=project_id)
            if client_id:
                query = query.filter_by(user_id=user_id).filter_by(
                    client_id=client_id)
                result = query.all()
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Mysql operation failed {0}'.format(e))
    session.close()
    return result


def get_client(user_id, project_id=None, client_id=None, offset=0,
               limit=100, search=None):

    clients = []
    search_key = {}
    if client_id:
        result = get_client_byid(user_id, client_id, project_id=project_id)
    else:
        result, search_key = search_tuple(tablename=models.Client,
                                          user_id=user_id,
                                          project_id=project_id, offset=offset,
                                          limit=limit, search=search)

    for client in result:
        clientmap = {}
        clientmap['project_id'] = client.project_id
        clientmap['user_id'] = client.user_id
        clientmap['client'] = {'uuid': client.uuid,
                               'hostname': client.hostname,
                               'client_id': client.client_id,
                               'description': client.description}
        clients.append(clientmap)

    # If search opt is wrong, filter will not work,
    # return all tuples.
    if not client_id:
        clients = filter_tuple_by_search_opt(clients, offset=offset,
                                             limit=limit, search=search_key)
    return clients


def add_client(user_id, doc, project_id=None):
    if CONF.enable_v1_api:
        client_doc = utilsv1.ClientDoc.create(doc, user_id)
    else:
        client_doc = utilsv2.ClientDoc.create(doc, project_id, user_id)
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

    add_tuple(tuple=client)

    LOG.info('Client registered, client_id: {0}'.format(client_id))
    return client_id


def delete_client(user_id, client_id, project_id=None):

    existing = get_client(project_id=project_id, user_id=user_id,
                          client_id=client_id)

    if existing:
        clientt = existing[0].get('client')
        clientid = clientt.get('uuid')
        delete_tuple(tablename=models.Client, user_id=user_id,
                     tuple_id=clientid, project_id=project_id)
        LOG.info('Client delete, client_id: {0} deleted'.
                 format(client_id))
    else:
        LOG.info('Client delete, client_id: {0} not found'.
                 format(client_id))
    return client_id


def delete_action(user_id, action_id, project_id=None):

    tupleid = delete_tuple(tablename=models.Action, user_id=user_id,
                           tuple_id=action_id, project_id=project_id)

    tupleid = delete_tuple(tablename=models.ActionReport, user_id=user_id,
                           tuple_id=action_id, project_id=project_id)
    return tupleid


def add_action(user_id, doc, project_id=None):
    if CONF.enable_v1_api:
        action_doc = utilsv1.ActionDoc.create(doc, user_id)
    else:
        action_doc = utilsv2.ActionDoc.create(doc, user_id, project_id)

    keyt = ['action', 'backup_name',
            'container', 'path_to_backup', 'timeout',
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
    actionvalue['actionmode'] = freezer_action.get('mode', None)

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

    add_tuple(tuple=action)

    LOG.info('Action registered, action_id: {0}'.format(action_id))

    actionReport = models.ActionReport()

    actionreportvalue['project_id'] = project_id
    actionreportvalue['id'] = action_id
    actionreportvalue['user_id'] = user_id

    actionReport.update(actionreportvalue)

    add_tuple(tuple=actionReport)
    LOG.info('Action Reports registered, action_id: {0}'.
             format(action_id))
    return action_id


def get_action(user_id, action_id, project_id=None):

    result = get_tuple(tablename=models.Action, user_id=user_id,
                       tuple_id=action_id, project_id=project_id)

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
        values['freezer_action']['mode'] = result[0].get('actionmode')
        values['freezer_action']['container'] = result[0].\
            get('container')
        values['freezer_action']['timeout'] = result[0].get('timeout')
        values['freezer_action']['priority'] = result[0].get('priority')
        values['freezer_action']['path_to_backup'] = result[0].\
            get('path_to_backup')
        values['freezer_action']['log_file'] = result[0].get('log_file')
    return values


def search_action(user_id, project_id=None, offset=0,
                  limit=100, search=None):

    actions = []

    result, search_key = search_tuple(tablename=models.Action, user_id=user_id,
                                      project_id=project_id, offset=offset,
                                      limit=limit, search=search)
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
        actionmap['freezer_action']['mode'] = action.get('actionmode')
        actionmap['freezer_action']['action'] = action.get('action')
        actionmap['freezer_action']['container'] = action.\
            get('container')
        actionmap['freezer_action']['timeout'] = action.get('timeout')
        actionmap['freezer_action']['priority'] = action.get('priority')
        actionmap['freezer_action']['path_to_backup'] = action.\
            get('path_to_backup')
        actionmap['freezer_action']['log_file'] = action.get('log_file')

        actions.append(actionmap)
    # If search opt is wrong, filter will not work,
    # return all tuples.
    actions = filter_tuple_by_search_opt(actions, offset=offset, limit=limit,
                                         search=search_key)
    return actions


def update_action(user_id, action_id, patch_doc, project_id=None):
    # changes in user_id or action_id are not allowed
    if CONF.enable_v1_api:
        valid_patch = utilsv1.ActionDoc.create_patch(patch_doc)
    else:
        valid_patch = utilsv2.ActionDoc.create_patch(patch_doc)

    keyt = ['action', 'backup_name', 'container',
            'path_to_backup', 'timeout', 'priority', 'mandatory', 'log_file']

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

    values['actionmode'] = freezer_action.get('mode', None)
    values['backup_metadata'] = json_utils.json_encode(freezer_action)

    update_tuple(tablename=models.Action, user_id=user_id, tuple_id=action_id,
                 tuple_values=values, project_id=project_id)

    return action_id


def replace_action(user_id, action_id, doc, project_id=None):
    if CONF.enable_v1_api:
        valid_doc = utilsv1.ActionDoc.update(doc, user_id, action_id)
    else:
        valid_doc = utilsv2.ActionDoc.update(doc, user_id, action_id,
                                             project_id)
    values = {}
    keyt = ['action', 'backup_name', 'container',
            'path_to_backup', 'timeout', 'priority', 'mandatory', 'log_file']

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
    values['actionmode'] = freezer_action.get('mode', None)
    values['backup_metadata'] = json_utils.json_encode(freezer_action)
    replace_tuple(tablename=models.Action, user_id=user_id,
                  tuple_id=action_id, tuple_values=values,
                  project_id=project_id)

    LOG.info('action replaced, action_id: {0}'.format(action_id))
    return action_id


def delete_job(user_id, job_id, project_id=None):

    tupleid = delete_tuple(tablename=models.Job, user_id=user_id,
                           tuple_id=job_id, project_id=project_id)
    return tupleid


def add_job(user_id, doc, project_id=None):
    if CONF.enable_v1_api:
        job_doc = utilsv1.JobDoc.create(doc, user_id)
    else:
        job_doc = utilsv2.JobDoc.create(doc, project_id, user_id)

    job_id = job_doc.get('job_id')
    existing = get_job(project_id=project_id, user_id=user_id,
                       job_id=job_id)
    if existing:
        raise freezer_api_exc.\
            DocumentExists(message='Job already registered with ID {0}'.
                           format(job_id))

    job = models.Job()
    jobvalue = {}
    jobvalue['id'] = job_id
    jobvalue['project_id'] = project_id
    jobvalue['user_id'] = user_id
    jobvalue['schedule'] = json_utils.\
        json_encode(job_doc.pop('job_schedule', ''))
    jobvalue['client_id'] = job_doc.get('client_id', '')
    jobvalue['session_id'] = job_doc.pop('session_id', '')
    jobvalue['session_tag'] = job_doc.pop('session_tag', 0)
    jobvalue['description'] = job_doc.pop('description', '')
    jobvalue['job_actions'] = json_utils.\
        json_encode(job_doc.pop('job_actions', ''))
    job.update(jobvalue)

    add_tuple(tuple=job)

    LOG.info('Job registered, job_id: {0}'.format(job_id))

    return job_id


def get_job(user_id, job_id, project_id=None):

    result = get_tuple(tablename=models.Job, user_id=user_id,
                       tuple_id=job_id, project_id=project_id)
    values = {}
    if 1 == len(result):
        values['job_id'] = result[0].get('id')
        values['project_id'] = result[0].get('project_id')
        values['user_id'] = result[0].get('user_id')
        values['job_schedule'] = json_utils.\
            json_decode(result[0].get('schedule'))
        values['client_id'] = result[0].get('client_id')
        values['session_id'] = result[0].get('session_id')
        values['session_tag'] = result[0].get('session_tag')
        values['description'] = result[0].get('description')
        values['job_actions'] = json_utils.\
            json_decode(result[0].get('job_actions'))
    return values


def search_job(user_id, project_id=None, offset=0,
               limit=100, search=None):
    jobs = []
    result, search_key = search_tuple(tablename=models.Job, user_id=user_id,
                                      project_id=project_id, offset=offset,
                                      limit=limit, search=search)
    for job in result:
        jobmap = {}
        jobmap['job_id'] = job.get('id')
        jobmap['project_id'] = job.get('project_id')
        jobmap['user_id'] = job.get('user_id')
        jobmap['job_schedule'] = json_utils.json_decode(job.get('schedule'))
        jobmap['client_id'] = job.get('client_id')
        jobmap['session_id'] = job.get('session_id')
        jobmap['session_tag'] = job.get('session_tag')
        jobmap['description'] = job.get('description')
        jobmap['job_actions'] = json_utils.json_decode(
            job.get('job_actions'))

        jobs.append(jobmap)
    # If search opt is wrong, filter will not work,
    # return all tuples.
    jobs = filter_tuple_by_search_opt(jobs, offset=offset, limit=limit,
                                      search=search_key)
    return jobs


def update_job(user_id, job_id, patch_doc, project_id=None):
    if CONF.enable_v1_api:
        valid_patch = utilsv1.JobDoc.create_patch(patch_doc)
    else:
        valid_patch = utilsv2.JobDoc.create_patch(patch_doc)

    values = {}
    for key in valid_patch.keys():
        if key == 'job_schedule':
            values['schedule'] = json_utils.\
                json_encode(valid_patch.get(key, None))
        elif key == 'job_actions':
            values[key] = json_utils.json_encode(valid_patch.get(key, None))
        else:
            values[key] = valid_patch.get(key, None)

    update_tuple(tablename=models.Job, user_id=user_id, tuple_id=job_id,
                 tuple_values=values, project_id=project_id)

    return 0


def replace_job(user_id, job_id, doc, project_id=None):
    if CONF.enable_v1_api:
        valid_doc = utilsv1.JobDoc.update(doc, user_id, job_id)
    else:
        valid_doc = utilsv2.JobDoc.update(doc, user_id, job_id, project_id)

    values = {}
    valuesnew = {}

    values['id'] = job_id
    values['project_id'] = project_id
    values['user_id'] = user_id
    values['schedule'] = json_utils.\
        json_encode(valid_doc.pop('job_schedule', ''))
    values['client_id'] = valid_doc.get('client_id', '')
    values['session_id'] = valid_doc.pop('session_id', '')
    values['session_tag'] = valid_doc.pop('session_tag', 0)
    values['description'] = valid_doc.pop('description', '')
    values['job_actions'] = json_utils.\
        json_encode(valid_doc.pop('job_actions', ''))

    for key in values:
        if values[key] is not None:
            valuesnew[key] = values[key]

    replace_tuple(tablename=models.Job, user_id=user_id,
                  tuple_id=job_id, tuple_values=valuesnew,
                  project_id=project_id)
    LOG.info('job replaced, job_id: {0}'.format(job_id))
    return job_id


def get_backup(user_id, backup_id, project_id=None):
    result = get_tuple(tablename=models.Backup, user_id=user_id,
                       tuple_id=backup_id, project_id=project_id)
    values = {}
    if 1 == len(result):
        values['project_id'] = result[0].get('project_id')
        values['backup_id'] = result[0].get('id')
        values['user_id'] = result[0].get('user_id')
        values['user_name'] = result[0].get('user_name')
        values['backup_metadata'] = json_utils.\
            json_decode(result[0].get('backup_metadata'))
    return values


def add_backup(user_id, user_name, doc, project_id=None):
    if CONF.enable_v1_api:
        metadatadoc = utilsv1.BackupMetadataDoc(user_id, user_name,
                                                doc)
    else:
        metadatadoc = utilsv2.BackupMetadataDoc(project_id, user_id, user_name,
                                                doc)
    if not metadatadoc.is_valid():
        raise freezer_api_exc.BadDataFormat(
            message='Bad Data Format')
    backup_id = metadatadoc.backup_id
    backupjson = metadatadoc.serialize()
    backup_metadata = backupjson.get('backup_metadata')

    existing = get_backup(project_id=project_id, user_id=user_id,
                          backup_id=backup_id)
    if existing:
        raise freezer_api_exc.DocumentExists(
            message='Backup already registered with ID'
                    ' {0}'.format(backup_id))

    backup = models.Backup()
    backupvalue = {}
    backupvalue['project_id'] = project_id
    backupvalue['id'] = backup_id
    backupvalue['user_id'] = user_id
    backupvalue['user_name'] = user_name
    backupvalue['job_id'] = backup_metadata.get('job_id')
    # The field backup_metadata is json, including :
    # hostname , backup_name , container etc
    backupvalue['backup_metadata'] = json_utils.json_encode(backup_metadata)
    backup.update(backupvalue)

    add_tuple(tuple=backup)
    LOG.info('Backup registered, backup_id: {0}'.format(backup_id))
    return backup_id


def delete_backup(user_id, backup_id, project_id=None):

    tupleid = delete_tuple(tablename=models.Backup, user_id=user_id,
                           tuple_id=backup_id, project_id=project_id)
    return tupleid


def search_backup(user_id, project_id=None, offset=0,
                  limit=100, search=None):
    backups = []

    result, search_key = search_tuple(tablename=models.Backup, user_id=user_id,
                                      project_id=project_id, offset=offset,
                                      limit=limit, search=search)
    for backup in result:
        backupmap = {}
        backupmap['project_id'] = project_id
        backupmap['user_id'] = user_id
        backupmap['backup_id'] = backup.id
        backupmap['user_name'] = backup.user_name
        backupmap['backup_metadata'] = json_utils.\
            json_decode(backup.get('backup_metadata'))
        backups.append(backupmap)
    # If search opt is wrong, filter will not work,
    # return all tuples.
    backups = filter_tuple_by_search_opt(backups, offset=offset, limit=limit,
                                         search=search_key)
    return backups


def get_session(user_id, session_id, project_id=None):
    jobt = {}
    values = {}
    result = get_tuple(tablename=models.Session, user_id=user_id,
                       tuple_id=session_id, project_id=project_id)
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


def delete_session(user_id, session_id, project_id=None):

    tupleid = delete_tuple(tablename=models.Session, user_id=user_id,
                           tuple_id=session_id, project_id=project_id)
    return tupleid


def add_session(user_id, doc, project_id=None):
    if CONF.enable_v1_api:
        session_doc = utilsv1.SessionDoc.create(doc=doc,
                                                user_id=user_id)
    else:
        session_doc = utilsv2.SessionDoc.create(doc=doc,
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

    add_tuple(tuple=sessiont)
    LOG.info('Session registered, session_id: {0}'.format(session_id))

    return session_id


def update_session(user_id, session_id, patch_doc, project_id=None):
    if CONF.enable_v1_api:
        valid_patch = utilsv1.SessionDoc.create_patch(patch_doc)
    else:
        valid_patch = utilsv2.SessionDoc.create_patch(patch_doc)

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

    update_tuple(tablename=models.Session, user_id=user_id,
                 tuple_id=session_id, tuple_values=values,
                 project_id=project_id)

    return 0


def replace_session(user_id, session_id, doc, project_id=None):
    if CONF.enable_v1_api:
        valid_doc = utilsv1.SessionDoc.update(doc, user_id, session_id)

    else:
        valid_doc = utilsv2.SessionDoc.update(doc, user_id, session_id,
                                              project_id)
    values = {}
    valuesnew = {}

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

    replace_tuple(tablename=models.Session, user_id=user_id,
                  tuple_id=session_id,
                  tuple_values=valuesnew,
                  project_id=project_id)
    LOG.info('session replaced, session_id: {0}'.format(session_id))
    return session_id


def search_session(user_id, project_id=None, offset=0,
                   limit=100, search=None):
    sessions = []
    jobt = {}

    result, search_key = search_tuple(tablename=models.Session,
                                      user_id=user_id,
                                      project_id=project_id, offset=offset,
                                      limit=limit, search=search)
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
    # If search opt is wrong, filter will not work,
    # return all tuples.
    sessions = filter_tuple_by_search_opt(sessions, offset=offset,
                                          limit=limit, search=search_key)

    return sessions
