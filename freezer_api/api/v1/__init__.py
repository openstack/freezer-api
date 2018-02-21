"""
(c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.

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

from freezer_api.api.v1 import actions
from freezer_api.api.v1 import backups
from freezer_api.api.v1 import clients
from freezer_api.api.v1 import homedoc
from freezer_api.api.v1 import jobs
from freezer_api.api.v1 import sessions


VERSION = {
    'id': 'v1',
    'status': 'DEPRECATED',
    'updated': '2018-02-21T13:30:00',
    'links': [
        {
            'href': '{0}v1/',
            'rel': 'self'
        }
    ]
}


def public_endpoints(storage_driver):
    return [
        ('/',
         homedoc.Resource()),

        ('/backups',
         backups.BackupsCollectionResource(storage_driver)),

        ('/backups/{backup_id}',
         backups.BackupsResource(storage_driver)),

        ('/clients',
         clients.ClientsCollectionResource(storage_driver)),

        ('/clients/{client_id}',
         clients.ClientsResource(storage_driver)),

        ('/jobs',
         jobs.JobsCollectionResource(storage_driver)),

        ('/jobs/{job_id}',
         jobs.JobsResource(storage_driver)),

        ('/jobs/{job_id}/event',
         jobs.JobsEvent(storage_driver)),

        ('/actions',
         actions.ActionsCollectionResource(storage_driver)),

        ('/actions/{action_id}',
         actions.ActionsResource(storage_driver)),

        ('/sessions',
         sessions.SessionsCollectionResource(storage_driver)),

        ('/sessions/{session_id}',
         sessions.SessionsResource(storage_driver)),

        ('/sessions/{session_id}/action',
         sessions.SessionsAction(storage_driver)),

        ('/sessions/{session_id}/jobs/{job_id}',
         sessions.SessionsJob(storage_driver)),

    ]
