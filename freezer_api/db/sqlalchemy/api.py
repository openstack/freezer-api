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
