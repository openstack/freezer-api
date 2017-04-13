"""
Copyright 2015 Hewlett-Packard

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import elasticsearch
import logging
import os

from freezer_api.common import elasticv2_utils as utils
from freezer_api.common import exceptions as freezer_api_exc

from oslo_config import cfg
from oslo_log import log

CONF = cfg.CONF
LOG = log.getLogger(__name__)


class TypeManagerV2(object):
    def __init__(self, es, doc_type, index):
        self.es = es
        self.index = index
        self.doc_type = doc_type

    @staticmethod
    def get_base_search_filter(project_id, user_id=None, search=None):
        search = search or {}
        project_id_filter = {"term": {"project_id": project_id}}
        base_filter = [project_id_filter]
        if user_id:
            user_id_filter = {"term": {"user_id": user_id}}
            base_filter.append(user_id_filter)

        match_list = [{"match": m} for m in search.get('match', [])]
        match_not_list = [{"match": m} for m in search.get('match_not', [])]
        base_filter.append({"query": {"bool": {"must": match_list,
                                               "must_not": match_not_list}}})
        return base_filter

    @staticmethod
    def get_search_query(project_id, doc_id, user_id=None, search=None):
        search = search or {}
        try:
            base_filter = TypeManagerV2.get_base_search_filter(
                project_id=project_id,
                user_id=user_id,
                search=search
            )
            query_filter = {"filter": {"bool": {"must": base_filter}}}
            return {'query': {'filtered': query_filter}}
        except Exception:
            raise freezer_api_exc.StorageEngineError(
                message='search operation failed: query not valid')

    def get(self, project_id, doc_id, user_id=None):
        try:
            res = self.es.get(index=self.index,
                              doc_type=self.doc_type,
                              id=doc_id)
            doc = res['_source']
        except elasticsearch.TransportError:
            raise freezer_api_exc.DocumentNotFound(
                message='No document found with ID:{0}'.format(doc_id))
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Get operation failed: {}'.format(e))
        if doc['project_id'] != project_id:
            raise freezer_api_exc.AccessForbidden("You are not allowed to"
                                                  " access")
        if user_id:
            if doc['user_id'] != user_id:
                raise freezer_api_exc.AccessForbidden(
                    "Document access forbidden"
                )
        if '_version' in res:
            doc['_version'] = res['_version']
        return doc

    def search(self, project_id, user_id=None, doc_id=None, search=None,
               offset=0, limit=10):
        search = search or {}
        query_dsl = self.get_search_query(
            project_id=project_id,
            user_id=user_id,
            doc_id=doc_id,
            search=search
        )
        try:
            res = self.es.search(index=self.index, doc_type=self.doc_type,
                                 size=limit, from_=offset, body=query_dsl)
        except elasticsearch.ConnectionError:
            raise freezer_api_exc.StorageEngineError(
                message='unable to connect to db server')
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='search operation failed: {0}'.format(e))
        hit_list = res['hits']['hits']
        return [x['_source'] for x in hit_list]

    def insert(self, doc, doc_id=None):
        try:
            # remove _version from the document
            doc.pop('_version', None)
            res = self.es.index(index=self.index, doc_type=self.doc_type,
                                body=doc, id=doc_id)
            created = res['created']
            version = res['_version']
            self.es.indices.refresh(index=self.index)
        except elasticsearch.TransportError as e:
            if e.status_code == 409:
                raise freezer_api_exc.DocumentExists(message=e.error)
            raise freezer_api_exc.StorageEngineError(
                message='index operation failed {0}'.format(e))
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='index operation failed {0}'.format(e))
        return created, version

    def delete(self, project_id, doc_id, user_id=None):
        query_dsl = self.get_search_query(
            project_id=project_id,
            user_id=user_id,
            doc_id=doc_id
        )
        try:
            results = self.es.search(index=self.index,
                                     doc_type=self.doc_type,
                                     body=query_dsl)
            results = results['hits']['hits']
        except Exception as e:
            raise freezer_api_exc.StorageEngineError(
                message='Scan operation failed: {0}'.format(e))
        id = None
        for res in results:
            id = res.get('_id')
            try:
                self.es.delete(index=self.index, doc_type=self.doc_type, id=id)
                self.es.indices.refresh(index=self.index)
            except Exception as e:
                raise freezer_api_exc.StorageEngineError(
                    message='Delete operation failed: {0}'.format(e))
        return id


class BackupTypeManagerV2(TypeManagerV2):
    def __init__(self, es, doc_type, index='freezer'):
        TypeManagerV2.__init__(self, es, doc_type, index=index)

    @staticmethod
    def get_search_query(project_id, doc_id, user_id=None, search=None):
        search = search or {}
        base_filter = TypeManagerV2.get_base_search_filter(
            project_id=project_id,
            user_id=user_id,
            search=search
        )
        if doc_id is not None:
            base_filter.append({"term": {"backup_id": doc_id}})

        if 'time_after' in search:
            base_filter.append(
                {"range": {"timestamp": {"gte": int(search['time_after'])}}}
            )

        if 'time_before' in search:
            base_filter.append(
                {"range": {"timestamp": {"lte": int(search['time_before'])}}}
            )
        query_filter = {"filter": {"bool": {"must": base_filter}}}
        return {'query': {'filtered': query_filter}}


class ClientTypeManagerV2(TypeManagerV2):
    def __init__(self, es, doc_type, index='freezer'):
        TypeManagerV2.__init__(self, es, doc_type, index=index)

    @staticmethod
    def get_search_query(project_id, doc_id, user_id=None, search=None):
        search = search or {}
        base_filter = TypeManagerV2.get_base_search_filter(
            project_id=project_id,
            user_id=user_id,
            search=search
        )
        if doc_id is not None:
            base_filter.append({"term": {"client.client_id": doc_id}})
        query_filter = {"filter": {"bool": {"must": base_filter}}}
        return {'query': {'filtered': query_filter}}


class JobTypeManagerV2(TypeManagerV2):
    def __init__(self, es, doc_type, index='freezer'):
        TypeManagerV2.__init__(self, es, doc_type, index=index)

    @staticmethod
    def get_search_query(project_id, doc_id, user_id=None, search=None):
        search = search or {}
        base_filter = TypeManagerV2.get_base_search_filter(
            project_id=project_id,
            user_id=user_id,
            search=search
        )
        if doc_id is not None:
            base_filter.append({"term": {"job_id": doc_id}})
        query_filter = {"filter": {"bool": {"must": base_filter}}}
        return {'query': {'filtered': query_filter}}

    def update(self, job_id, job_update_doc):
        # remove _version from the document
        job_update_doc.pop('_version', 0)
        update_doc = {"doc": job_update_doc}
        try:
            res = self.es.update(index=self.index, doc_type=self.doc_type,
                                 id=job_id, body=update_doc)
            version = res['_version']
            self.es.indices.refresh(index=self.index)
        except elasticsearch.TransportError as e:
            if e.status_code == 409:
                raise freezer_api_exc.DocumentExists(message=e.error)
            raise freezer_api_exc.DocumentNotFound(
                message='Unable to find job to update with id'
                        ' {0} {1}'.format(job_id, e))
        except Exception:
            raise freezer_api_exc.StorageEngineError(
                message='Unable to update job with id {0}'.format(job_id))
        return version


class ActionTypeManagerV2(TypeManagerV2):
    def __init__(self, es, doc_type, index='freezer'):
        TypeManagerV2.__init__(self, es, doc_type, index=index)

    @staticmethod
    def get_search_query(project_id, doc_id, user_id=None, search=None):
        search = search or {}
        base_filter = TypeManagerV2.get_base_search_filter(
            project_id=project_id,
            user_id=user_id,
            search=search
        )
        if doc_id is not None:
            base_filter.append({"term": {"action_id": doc_id}})
        query_filter = {"filter": {"bool": {"must": base_filter}}}
        return {'query': {'filtered': query_filter}}

    def update(self, action_id, action_update_doc):
        # remove _version from the document
        action_update_doc.pop('_version', 0)
        update_doc = {"doc": action_update_doc}
        try:
            res = self.es.update(index=self.index, doc_type=self.doc_type,
                                 id=action_id, body=update_doc)
            version = res['_version']
            self.es.indices.refresh(index=self.index)
        except elasticsearch.TransportError as e:
            if e.status_code == 409:
                raise freezer_api_exc.DocumentExists(message=e.error)
            raise freezer_api_exc.DocumentNotFound(
                message='Unable to find action to update with id'
                        ' {0}'.format(action_id))
        except Exception:
            raise freezer_api_exc.StorageEngineError(
                message='Unable to update action with id'
                        ' {0}'.format(action_id))
        return version


class SessionTypeManagerV2(TypeManagerV2):
    def __init__(self, es, doc_type, index='freezer'):
        TypeManagerV2.__init__(self, es, doc_type, index=index)

    @staticmethod
    def get_search_query(project_id, doc_id, user_id=None, search=None):
        search = search or {}
        base_filter = TypeManagerV2.get_base_search_filter(
            project_id=project_id,
            user_id=user_id,
            search=search
        )
        if doc_id is not None:
            base_filter.append({"term": {"session_id": doc_id}})
        query_filter = {"filter": {"bool": {"must": base_filter}}}
        return {'query': {'filtered': query_filter}}

    def update(self, session_id, session_update_doc):
        # remove _version from the document
        session_update_doc.pop('_version', 0)
        update_doc = {"doc": session_update_doc}
        try:
            res = self.es.update(index=self.index, doc_type=self.doc_type,
                                 id=session_id, body=update_doc)
            version = res['_version']
            self.es.indices.refresh(index=self.index)
        except elasticsearch.TransportError as e:
            if e.status_code == 409:
                raise freezer_api_exc.DocumentExists(message=e.error)
            raise freezer_api_exc.DocumentNotFound(
                message='Unable to update session ID: {0}, '
                        'Error: {1}'.format(session_id, e))
        except Exception:
            raise freezer_api_exc.StorageEngineError(
                message='Unable to update session with id'
                        ' {0}'.format(session_id))
        return version


class ElasticSearchEngineV2(object):

    _OPTS = [
        cfg.ListOpt('hosts',
                    default=['http://127.0.0.1:9200'],
                    help='specify the storage hosts'),
        cfg.StrOpt('index',
                   default='freezer',
                   help='specify the name of the elasticsearch index'),
        cfg.IntOpt('timeout',
                   default=60,
                   help='specify the connection timeout'),
        cfg.IntOpt('retries',
                   default=20,
                   help='number of retries to allow before raising and error'),
        cfg.BoolOpt('use_ssl',
                    default=False,
                    help='explicitly turn on SSL'),
        cfg.BoolOpt('verify_certs',
                    default=False,
                    help='turn on SSL certs verification'),
        cfg.StrOpt('ca_certs',
                   help='path to CA certs on disk'),
        cfg.IntOpt('number_of_replicas',
                   default=0,
                   help='Number of replicas for elk cluster. Default is 0. '
                        'Use 0 for no replicas. This should be set to (number '
                        'of node in the ES cluter -1).')
    ]

    def __init__(self, backend):
        """backend: name of the section in the config file to load
        elasticsearch opts
        """
        self.index = None
        self.es = None
        self.backup_manager = None
        self.client_manager = None
        self.job_manager = None
        self.action_manager = None
        self.session_manager = None
        # register elasticsearch opts
        CONF.register_opts(self._OPTS, group=backend)
        self.conf = dict(CONF.get(backend))
        self.backend = backend
        self._validate_opts()
        self.init(**self.conf)

    def _validate_opts(self):
        if not 'hosts' or 'endpoint' in self.conf.keys():
            raise ValueError("Couldn't find hosts in {0} section".format(
                self.backend)
            )
        if self.conf.get('ca_certs'):
            if not os.path.isfile(self.conf.get('ca_certs')):
                raise Exception("File not found: ca_certs file ({0}) not "
                                "found".format(self.conf.get('ca_certs')))

    def get_opts(self):
        return self._OPTS

    def init(self, index='freezer', **kwargs):
        self.index = index
        self.es = elasticsearch.Elasticsearch(**kwargs)
        logging.info('Storage backend: Elasticsearch at'
                     ' {0}'.format(kwargs['hosts']))
        self.backup_manager = BackupTypeManagerV2(self.es, 'backups')
        self.client_manager = ClientTypeManagerV2(self.es, 'clients')
        self.job_manager = JobTypeManagerV2(self.es, 'jobs')
        self.action_manager = ActionTypeManagerV2(self.es, 'actions')
        self.session_manager = SessionTypeManagerV2(self.es, 'sessions')

    def get_backup(self, user_id, backup_id, project_id=None):
        return self.backup_manager.get(
            project_id=project_id,
            user_id=user_id,
            doc_id=backup_id
        )

    def search_backup(self, user_id, offset=0, limit=10, search=None,
                      project_id=None):
        search = search or {}
        return self.backup_manager.search(project_id=project_id,
                                          user_id=user_id,
                                          search=search,
                                          offset=offset,
                                          limit=limit)

    def add_backup(self, project_id, user_id, user_name, doc):
        # raises if data is malformed (HTTP_400) or already present (HTTP_409)
        backup_metadata_doc = utils.BackupMetadataDoc(
            project_id,
            user_id,
            user_name,
            doc
        )
        if not backup_metadata_doc.is_valid():
            raise freezer_api_exc.BadDataFormat(
                message='Bad Data Format')
        backup_id = backup_metadata_doc.backup_id
        self.backup_manager.insert(backup_metadata_doc.serialize(), backup_id)
        return backup_id

    def delete_backup(self, project_id, user_id, backup_id):
        return self.backup_manager.delete(project_id, user_id, backup_id)

    def get_client(self, project_id, user_id, client_id=None,
                   offset=0, limit=10, search=None):
        search = search or {}
        return self.client_manager.search(project_id=project_id,
                                          user_id=user_id,
                                          doc_id=client_id,
                                          search=search,
                                          offset=offset,
                                          limit=limit)

    def add_client(self, project_id, user_id, doc):
        client_doc = utils.ClientDoc.create(doc, project_id, user_id)
        client_id = client_doc['client']['client_id']
        existing = self.client_manager.search(
            project_id=project_id,
            user_id=user_id,
            doc_id=client_id
        )
        if existing:
            raise freezer_api_exc.DocumentExists(
                message='Client already registered with ID'
                        ' {0}'.format(client_id))
        self.client_manager.insert(client_doc)
        logging.info('Client registered, client_id: {0}'.format(client_id))
        return client_id

    def delete_client(self, project_id, user_id, client_id):
        return self.client_manager.delete(
            project_id=project_id,
            user_id=user_id,
            doc_id=client_id)

    def get_job(self, project_id, user_id, job_id):
        return self.job_manager.get(
            project_id=project_id,
            user_id=user_id,
            doc_id=job_id
        )

    def search_job(self, project_id, user_id, offset=0, limit=10, search=None):
        search = search or {}
        return self.job_manager.search(project_id=project_id,
                                       user_id=user_id,
                                       search=search,
                                       offset=offset,
                                       limit=limit)

    def add_job(self, user_id, doc, project_id):
        jobdoc = utils.JobDoc.create(doc, project_id, user_id)
        job_id = jobdoc['job_id']
        self.job_manager.insert(jobdoc, job_id)
        logging.info('Job registered, job id: {0}'.format(job_id))
        return job_id

    def delete_job(self, user_id, job_id, project_id):
        return self.job_manager.delete(user_id=user_id,
                                       doc_id=job_id,
                                       project_id=project_id)

    def update_job(self, user_id, job_id, patch_doc, project_id):
        valid_patch = utils.JobDoc.create_patch(patch_doc)

        # check that document exists
        assert (self.job_manager.get(user_id=user_id,
                                     doc_id=job_id,
                                     project_id=project_id
                                     )
                )

        version = self.job_manager.update(job_id, valid_patch)
        logging.info('Job id {0} updated to version'
                     ' {1}'.format(job_id, version))
        return version

    def replace_job(self, user_id, job_id, doc, project_id):
        # check that no document exists with
        # same job_id and different user_id
        try:
            self.job_manager.get(user_id=user_id,
                                 doc_id=job_id,
                                 project_id=project_id)
        except freezer_api_exc.DocumentNotFound:
            pass

        valid_doc = utils.JobDoc.update(doc, project_id, user_id, job_id)

        (created, version) = self.job_manager.insert(valid_doc, job_id)
        if created:
            logging.info('Job {0} created'.format(job_id))
        else:
            logging.info('Job {0} replaced with version'
                         ' {1}'.format(job_id, version))
        return version

    def get_action(self, user_id, action_id, project_id):
        return self.action_manager.get(user_id=user_id,
                                       doc_id=action_id,
                                       project_id=project_id
                                       )

    def search_action(self, user_id, offset=0, limit=10, search=None,
                      project_id=None):
        search = search or {}
        return self.action_manager.search(project_id=project_id,
                                          user_id=user_id,
                                          search=search,
                                          offset=offset,
                                          limit=limit)

    def add_action(self, user_id, doc, project_id):
        actiondoc = utils.ActionDoc.create(doc, user_id, project_id)
        action_id = actiondoc['action_id']
        self.action_manager.insert(actiondoc, action_id)
        logging.info('Action registered, action id: {0}'.format(action_id))
        return action_id

    def delete_action(self, user_id, action_id, project_id):
        return self.action_manager.delete(user_id=user_id,
                                          doc_id=action_id,
                                          project_id=project_id
                                          )

    def update_action(self, user_id, action_id, patch_doc, project_id):
        valid_patch = utils.ActionDoc.create_patch(patch_doc)

        # check that document exists
        assert (self.action_manager.get(project_id=project_id,
                                        user_id=user_id,
                                        doc_id=action_id))

        version = self.action_manager.update(action_id, valid_patch)
        logging.info('Action {0} updated to version'
                     ' {1}'.format(action_id, version))
        return version

    def replace_action(self, user_id, action_id, doc, project_id):
        # check that no document exists with
        # same action_id and different user_id
        try:
            self.action_manager.get(user_id=user_id,
                                    doc_id=action_id,
                                    project_id=project_id
                                    )
        except freezer_api_exc.DocumentNotFound:
            pass

        valid_doc = utils.ActionDoc.update(doc, user_id, action_id, project_id)

        (created, version) = self.action_manager.insert(valid_doc, action_id)
        if created:
            logging.info('Action {0} created'.format(action_id))
        else:
            logging.info('Action {0} replaced with version'
                         ' {1}'.format(action_id, version))
        return version

    def get_session(self, user_id, session_id, project_id):
        return self.session_manager.get(user_id=user_id,
                                        doc_id=session_id,
                                        project_id=project_id)

    def search_session(self, user_id, offset=0, limit=10, search=None,
                       project_id=None):
        search = search or {}
        return self.session_manager.search(user_id=user_id,
                                           project_id=project_id,
                                           search=search,
                                           offset=offset,
                                           limit=limit)

    def add_session(self, user_id, doc, project_id):
        session_doc = utils.SessionDoc.create(doc, user_id, project_id)
        session_id = session_doc['session_id']
        self.session_manager.insert(session_doc, session_id)
        logging.info('Session registered, session id: {0}'.format(session_id))
        return session_id

    def delete_session(self, user_id, session_id, project_id):
        return self.session_manager.delete(user_id=user_id,
                                           doc_id=session_id,
                                           project_id=project_id)

    def update_session(self, user_id, session_id, patch_doc, project_id):
        valid_patch = utils.SessionDoc.create_patch(patch_doc)

        # check that document exists
        assert (self.session_manager.get(user_id=user_id, doc_id=session_id,
                                         project_id=project_id))

        version = self.session_manager.update(session_id, valid_patch)
        logging.info('Session {0} updated to version'
                     ' {1}'.format(session_id, version))
        return version

    def replace_session(self, user_id, session_id, doc, project_id):
        # check that no document exists with
        # same session_id and different user_id
        try:
            self.session_manager.get(user_id=user_id, doc_id=session_id,
                                     project_id=project_id)
        except freezer_api_exc.DocumentNotFound:
            pass

        valid_doc = utils.SessionDoc.update(doc, user_id, session_id,
                                            project_id)

        (created, version) = self.session_manager.insert(valid_doc, session_id)
        if created:
            logging.info('Session {0} created'.format(session_id))
        else:
            logging.info('Session {0} replaced with version'
                         ' {1}'.format(session_id, version))
        return version
