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

from freezer_api.api.v2 import actions
from freezer_api.api.v2 import backups
from freezer_api.api.v2 import clients
from freezer_api.api.v2 import homedoc
from freezer_api.api.v2 import jobs
from freezer_api.api.v2 import sessions


VERSION = {
    'id': 'v2',
    'status': 'EXPERIMENTAL',
    'updated': '2017-04-21T17:00:00',
    'links': [
        {
            'href': '{0}v2/',
            'rel': 'self'
        }
    ]
}


def public_endpoints(storage_driver):
    return [
        ('/',
         homedoc.Resource()),

        ('/{project_id}/backups',
         backups.BackupsCollectionResource(storage_driver)),

        ('/{project_id}/backups/{backup_id}',
         backups.BackupsResource(storage_driver)),

        ('/{project_id}/clients',
         clients.ClientsCollectionResource(storage_driver)),

        ('/{project_id}/clients/{client_id}',
         clients.ClientsResource(storage_driver)),

        ('/{project_id}/jobs',
         jobs.JobsCollectionResource(storage_driver)),

        ('/{project_id}/jobs/{job_id}',
         jobs.JobsResource(storage_driver)),

        ('/{project_id}/jobs/{job_id}/event',
         jobs.JobsEvent(storage_driver)),

        ('/{project_id}/actions',
         actions.ActionsCollectionResource(storage_driver)),

        ('/{project_id}/actions/{action_id}',
         actions.ActionsResource(storage_driver)),

        ('/{project_id}/sessions',
         sessions.SessionsCollectionResource(storage_driver)),

        ('/{project_id}/sessions/{session_id}',
         sessions.SessionsResource(storage_driver)),

        ('/{project_id}/sessions/{session_id}/action',
         sessions.SessionsAction(storage_driver)),

        ('/{project_id}/sessions/{session_id}/jobs/{job_id}',
         sessions.SessionsJob(storage_driver)),

    ]
