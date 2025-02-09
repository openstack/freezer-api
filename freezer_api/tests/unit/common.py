"""Freezer swift.py related tests

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

import copy
import io
import os
import uuid

import fixtures
from oslo_config import cfg
from oslo_config import fixture as cfg_fixture
import testtools

from freezer_api.common import config
from freezer_api import policy
from freezer_api.tests.unit import fixtures as freezer_fixtures

CONF = cfg.CONF

fake_data_0_backup_id = 'b740ed9ad2b646aba304ef54c21c6774'
fake_data_0_user_id = 'qwerty1234'
fake_data_0_user_name = 'asdffdsa'
fake_data_0_project_id = "tecs"

fake_data_0_wrapped_backup_metadata = {
    'backup_id': 'b740ed9ad2b646aba304ef54c21c6774',
    'project_id': 'tecs',
    'user_id': 'qwerty1234',
    'user_name': 'asdffdsa',
    'backup_metadata': {
        "container": "freezer_container",
        "hostname": "alpha",
        "backup_name": "important_data_backup",
        "time_stamp": 8475903425,
        "curr_backup_level": 0,
        "backup_session": 8475903425,
        "max_level": 5,
        "mode": "fs",
        "fs_real_path": "/blabla",
        "vol_snap_path": "/blablasnap",
        "total_broken_links": 0,
        "total_fs_files": 11,
        "total_directories": 2,
        "backup_size_uncompressed": 4567,
        "backup_size_compressed": 1212,
        "total_backup_session_size": 6789,
        "compression_alg": "None",
        "encrypted": "false",
        "client_os": "linux",
        "broken_links": ["link_01", "link_02"],
        "excluded_files": ["excluded_file_01", "excluded_file_02"],
        "cli": ""
    }
}


fake_data_0_backup_metadata = {
    "container": "freezer_container",
    "hostname": "alpha",
    "backup_name": "important_data_backup",
    "time_stamp": 8475903425,
    "curr_backup_level": 0,
    "backup_session": 8475903425,
    "max_level": 5,
    "mode": "fs",
    "fs_real_path": "/blabla",
    "vol_snap_path": "/blablasnap",
    "total_broken_links": 0,
    "total_fs_files": 11,
    "total_directories": 2,
    "backup_size_uncompressed": 4567,
    "backup_size_compressed": 1212,
    "total_backup_session_size": 6789,
    "compression_alg": "None",
    "encrypted": "false",
    "client_os": "linux",
    "broken_links": ["link_01", "link_02"],
    "excluded_files": ["excluded_file_01", "excluded_file_02"],
    "cli": ""
}


def get_fake_backup_metadata():
    return copy.deepcopy(fake_data_0_backup_metadata)


fake_malformed_data_0_backup_metadata = {
    "hostname": "alpha",
    "backup_name": "important_data_backup",
    "time_stamp": 8475903425,
    "curr_backup_level": 0,
    "backup_session": 8475903425,
    "max_level": 5,
    "mode": "fs",
    "fs_real_path": "/blabla",
    "vol_snap_path": "/blablasnap",
    "total_broken_links": 0,
    "total_fs_files": 11,
    "total_directories": 2,
    "backup_size_uncompressed": 4567,
    "backup_size_compressed": 1212,
    "total_backup_session_size": 6789,
    "compression_alg": "None",
    "encrypted": "false",
    "client_os": "linux",
    "broken_links": ["link_01", "link_02"],
    "excluded_files": ["excluded_file_01", "excluded_file_02"],
    "cli": ""
}

fake_data_0_elasticsearch_hit = {
    "_shards": {
        "failed": 0,
        "successful": 5,
        "total": 5
    },
    "hits": {
        "hits": [
            {
                "_id": "AUx_iu-ewlhuOVELWtH0",
                "_index": "freezer",
                "_score": 1.0,
                "_type": "backups",
                "_source": {
                    "container": "freezer_container",
                    "hostname": "alpha",
                    "backup_name": "important_data_backup",
                    "time_stamp": 8475903425,
                    "curr_backup_level": 0,
                    "backup_session": 8475903425,
                    "max_level": 5,
                    "mode": "fs",
                    "fs_real_path": "/blabla",
                    "vol_snap_path": "/blablasnap",
                    "total_broken_links": 0,
                    "total_fs_files": 11,
                    "total_directories": 2,
                    "backup_size_uncompressed": 4567,
                    "backup_size_compressed": 1212,
                    "total_backup_session_size": 6789,
                    "compression_alg": "None",
                    "encrypted": "false",
                    "client_os": "linux",
                    "broken_links": ["link_01", "link_02"],
                    "excluded_files": ["excluded_file_01", "excluded_file_02"],
                    "cli": ""
                }
            }
        ],
        "max_score": 1.0,
        "total": 1
    },
    "timed_out": False,
    "took": 3
}

fake_data_0_elasticsearch_miss = {
    "_shards": {
        "failed": 0,
        "successful": 5,
        "total": 5
    },
    "hits": {
        "hits": [],
        "max_score": None,
        "total": 0
    },
    "timed_out": False,
    "took": 1
}

fake_job_0_project_id = "tecs"
fake_job_0_user_id = "f4db4da085f043059441565720b217c7"
fake_job_0_job_id = "e7181e5e-2c75-43f8-92c0-c037ae5f11e4"

fake_job_0_elasticsearch_not_found = {
    "_id": "e7181e5e-2c75-43f8-92c0-c037ae5f11e43",
    "_index": "freezer",
    "_type": "job",
    "found": False
}

fake_job_0 = {
    "job_actions": [
        {
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "path_to_backup": "/home/tylerdurden/project_mayhem",
                "backup_name": "project_mayhem_backup",
                "container": "my_backup_container"
            },
            "max_retries": 3,
            "max_retries_interval": 60,
            "mandatory": False
        },
        {
            "freezer_action": {
                "action": "restore",
                "mode": "fs",
                "restore_abs_path": "/home/tylerdurden/project_mayhem",
                "restore_from_host": "node_on_which_backup_was_made",
                "backup_name": "project_mayhem_backup",
                "container": "my_backup_container"
            },
            "max_retries": 3,
            "max_retries_interval": 60,
            "mandatory": True
        }
    ],
    "job_schedule": {
        "time_created": 1234,
        "time_started": 1234,
        "time_ended": 1234,
        "status": "stop",
        "result": "success",
        "schedule_date": "2015-06-02T16:20:00",
        "schedule_interval": "2 days"
    },
    "job_id": "e7181e5e-2c75-43f8-92c0-c037ae5f11e4",
    "client_id": "mytenantid_myhostname",
    "user_id": "f4db4da085f043059441565720b217c7",
    "project_id": "tecs",
    "description": "test action 4"
}


fake_job_2 = {
    "job_actions": [
        {
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "path_to_backup": "/home/tylerdurden/project_mayhem",
                "backup_name": "project_mayhem_backup",
                "container": "my_backup_container1"
            },
            "max_retries": 6,
            "max_retries_interval": 100,
            "mandatory": False
        },
        {
            "freezer_action": {
                "action": "restore",
                "mode": "fs",
                "restore_abs_path": "/home/tylerdurden/project_mayhem",
                "restore_from_host": "node_on_which_backup_was_made",
                "backup_name": "project_mayhem_backup",
                "container": "my_backup_container1"
            },
            "max_retries": 4,
            "max_retries_interval": 60,
            "mandatory": True
        }
    ],
    "job_schedule": {
        "time_created": 1234,
        "time_started": 1234,
        "time_ended": 1234,
        "status": "stop",
        "result": "success",
        "schedule_date": "2015-06-02T16:20:00",
        "schedule_interval": "7 days"
    },
    "job_id": "e7181e5e-2c75-43f8-92c0-c037ae5f11e4",
    "client_id": "mytenantid_myhostname1",
    "user_id": "f4db4da085f043059441565720b217c7",
    "project_id": "tecs",
    "description": "test action 5"
}

fake_job_3 = {
    "job_actions": [
        {
            "freezer_action": {
                "action": "backup",
                "mode": "fs",
                "path_to_backup": "/home/tylerdurden/project_mayhem",
                "backup_name": "project_mayhem_backup",
                "container": "my_backup_container1"
            },
            "max_retries": 3,
            "max_retries_interval": 150,
            "mandatory": False
        },
        {
            "freezer_action": {
                "action": "restore",
                "mode": "fs",
                "restore_abs_path": "/home/tylerdurden/project_mayhem",
                "restore_from_host": "node_on_which_backup_was_made",
                "backup_name": "project_mayhem_backup",
                "container": "my_backup_container1"
            },
            "max_retries": 4,
            "max_retries_interval": 60,
            "mandatory": True
        }
    ],
    "job_schedule": {
        "time_created": 1234,
        "time_started": 1234,
        "time_ended": 1234,
        "status": "stop",
        "result": "success",
        "schedule_date": "2015-06-02T16:20:00",
        "schedule_interval": "14 days"
    },
    "job_id": "e7181e5e-2c75-43f8-92c0-c037ae5f11e5",
    "client_id": "mytenantid_myhostname2",
    "user_id": "f4db4da085f043059441565720b217c7",
    "project_id": "tecs",
    "description": "test action 6"
}


def get_fake_job_0():
    return copy.deepcopy(fake_job_0)


def get_fake_job_1():
    job = copy.deepcopy(fake_job_0)
    job["job_id"] = 'pqoqurioew'
    return job


def get_fake_job_2():
    return copy.deepcopy(fake_job_2)


def get_fake_job_3():
    return copy.deepcopy(fake_job_3)


def get_fake_job_id():
    return uuid.uuid4().hex


fake_job_0_elasticsearch_found = {
    "_id": "e7181e5e-2c75-43f8-92c0-c037ae5f11e4",
    "_index": "freezer",
    "_source": fake_job_0,
    "_type": "actions",
    "_version": 1,
    "found": True
}

fake_data_1_wrapped_backup_metadata = {
    'backup_id': 'b740ed9ad2b646aba304ef54c21c6774',
    'user_id': 'qwerty1234',
    'user_name': 'asdffdsa',
    'backup_metadata': {
        "container": "freezer_container",
        "hostname": "alpha",
        "backup_name": "important_data_backup",
        "time_stamp": 125235431,
        "curr_backup_level": 1,
        "backup_session": 8475903425,
        "max_level": 5,
        "mode": "fs",
        "fs_real_path": "/blabla",
        "vol_snap_path": "/blablasnap",
        "total_broken_links": 0,
        "total_fs_files": 11,
        "total_directories": 2,
        "backup_size_uncompressed": 4567,
        "backup_size_compressed": 1212,
        "total_backup_session_size": 6789,
        "compression_alg": "None",
        "encrypted": "false",
        "client_os": "linux",
        "broken_links": ["link_01", "link_02"],
        "excluded_files": ["excluded_file_01", "excluded_file_02"],
        "cli": ""
    }
}

fake_client_info_0 = {
    "project_id": "tecs",
    "client_id": "test-tenant_5253_test-hostname_09544",
    "description": "some usefule text here",
    "config_id": "config_id_contains_uuid_of_config",
    "supported_actions": ["backup"],
    "supported_modes": ["cindernative"],
    "supported_storages": ["swift"],
    "supported_engines": [],
}

fake_client_info_1 = {
    "project_id": "tecs",
    "client_id": "test-tenant_5253_test-hostname_6543",
    "description": "also some useful text here",
    "config_id": "config_id_blablawhatever",
}

fake_client_entry_0 = {
    "client": fake_client_info_0,
    "user_id": "user_id-is-provided-keystone"
}

fake_client_entry_1 = {
    "client": fake_client_info_0,
    "user_id": "user_id-is-provided-keystone"
}


def get_fake_client_0():
    return copy.deepcopy(fake_client_entry_0)


def get_fake_client_1():
    return copy.deepcopy(fake_client_entry_1)


def get_fake_client_id():
    return uuid.uuid4().hex


fake_action_0 = {
    "freezer_action":
        {
            "action": "backup",
            "mode": "fs",
            "path_to_backup": "/home/tylerdurden/project_mayhem",
            "backup_name": "project_mayhem_backup",
            "container": "my_backup_container",
        },
    "exit_status": "success",
    "max_retries": 3,
    "max_retries_interval": 60,
    "mandatory": True,

    "action_id": "qwerqwerqwerrewq",
    "user_id": "user_id-is-provided-by-keystone",
    "project_id": "project_id-is-tecs"
}

fake_action_1 = {
    "freezer_action":
        {
            "action": "backup",
            "mode": "fs",
            "path_to_backup": "/home/tylerdurden/project_mayhem",
            "backup_name": "project_mayhem_backup",
            "container": "my_backup_container",
        },
    "exit_status": "success",
    "max_retries": 3,
    "max_retries_interval": 60,
    "mandatory": True,

    "action_id": "jk4lkjbn4r3k",
    "user_id": "user_id-is-provided-by-keystone",
    "project_id": "project_id-is-tecs"
}

fake_action_2 = {
    "freezer_action":
        {
            "action": "restore",
            "mode": "fs",
            "path_to_backup": "/home/tecs/project_tecs",
            "backup_name": "project_tecs_restore",
            "container": "my_restore_container",
        },
    "exit_status": "success",
    "max_retries": 5,
    "max_retries_interval": 70,
    "mandatory": False,
    "action_id": "qwerqwerqwerrewq",
    "user_id": "user_id-is-provided-by-keystone",
    "project_id": "project_id-is-tecs"
}

fake_action_3 = {
    "freezer_action":
        {
            "action": "restore",
            "mode": "fs",
            "path_to_backup": "/home/tecs/project_tecs",
            "backup_name": "project_tecs_restore",
            "container": "my_restore_container",
        },
    "exit_status": "success",
    "max_retries": 5,
    "max_retries_interval": 70,
    "mandatory": False,
    "user_id": "user_id-is-provided-by-keystone",
    "project_id": "project_id-is-tecs"
}


def get_fake_action_0():
    return copy.deepcopy(fake_action_0)


def get_fake_action_1():
    return copy.deepcopy(fake_action_1)


def get_fake_action_2():
    return copy.deepcopy(fake_action_2)


def get_fake_action_id():
    return uuid.uuid4().hex


def get_fake_action_3():
    return copy.deepcopy(fake_action_3)


fake_session_0 = {
    "session_id": 'turistidellademocrazia',
    "session_tag": 5,
    "description": 'some text here',
    "hold_off": 60,
    "schedule": {
        "time_created": 1234,
        "time_started": 1234,
        "time_ended": 0,
        "status": "stop",
        "schedule_date": "2015-06-02T16:20:00"
    },
    "jobs": {
        'venerescollataincorpodalolita': {
            "client_id": 'bruco',
            "status": 'running',
            "start_time": 12344321,
        },
        'job_id_2': {
            "client_id": "cocktail",
            "status": 'completed',
            "result": 'success',
            "start_time": 123321,
            "end_time": 123325,
        }
    },
    "time_start": 123412344,
    "time_end": 432234432,
    "status": "running",
    "user_id": "califfo",
    "project_id": "tecs"
}

fake_session_1 = {
    "session_id": 'turistidellademocrazia',
    "session_tag": 5,
    "description": 'some text here',
    "hold_off": 60,
    "schedule": {
        "time_created": 1234,
        "time_started": 1234,
        "time_ended": 0,
        "status": "stop",
        "schedule_date": "2015-06-02T16:20:00"
    },
    "jobs": {
        'venerescollataincorpodalolita': {
            "client_id": 'bruco',
            "status": 'running',
            "start_time": 12344321,
        }
    },
    "time_start": 123412344,
    "time_end": 432234432,
    "status": "running",
    "user_id": "califfo",
    "project_id": "tecs"
}

fake_session_2 = {
    "session_id": 'turistidellademocrazia',
    "session_tag": 5,
    "description": 'This is a session about test',
    "hold_off": 100,
    "schedule": {
        "time_created": 1234,
        "time_started": 1234,
        "time_ended": 0,
        "status": "stop",
        "schedule_date": "2018-11-14T16:20:00"
    },
    "jobs": {
        'venerescollataincorpodalolita': {
            "client_id": 'bruco',
            "status": 'running',
            "start_time": 12344321,
        },
        'job_id_2': {
            "client_id": "cocktail",
            "status": 'completed',
            "result": 'success',
            "start_time": 123321,
            "end_time": 123325,
        }
    },
    "time_start": 123412344,
    "time_end": 432234432,
    "status": "running",
    "user_id": "califfo",
    "project_id": "tecs"
}

fake_session_3 = {
    "session_id": 'turistidellademocrazia',
    "session_tag": 6,
    "description": 'This is a session about test',
    "hold_off": 150,
    "schedule": {
        "time_created": 1234,
        "time_started": 1234,
        "time_ended": 0,
        "status": "stop",
        "schedule_date": "2018-11-14T16:20:00"
    },
    "jobs": {
        'venerescollataincorpodalolita': {
            "client_id": 'bruco',
            "status": 'running',
            "start_time": 12344321,
        },
        'job_id_2': {
            "client_id": "cocktail",
            "status": 'completed',
            "result": 'success',
            "start_time": 123321,
            "end_time": 123325,
        }
    },
    "time_start": 123412344,
    "time_end": 432234432,
    "status": "running",
    "user_id": "califfo",
    "project_id": "tecs"
}


def get_fake_session_0():
    return copy.deepcopy(fake_session_0)


def get_fake_session_1():
    return copy.deepcopy(fake_session_1)


def get_fake_session_2():
    return copy.deepcopy(fake_session_2)


def get_fake_session_3():
    return copy.deepcopy(fake_session_3)


def get_fake_session_id():
    return uuid.uuid4().hex


class FakeReqResp(object):
    def __init__(self, method='GET', body=''):
        self.method = method
        self.body = body
        self.stream = io.BytesIO(body)
        self.content_length = len(body)
        self.context = {}
        self.header = {}

    def get_header(self, key):
        return self.header.get(key, None)


class FreezerBaseTestCase(testtools.TestCase):
    REGISTER_CONFIG = True
    REGISTER_POLICY = True

    def setUp(self):
        super().setUp()

        if self.REGISTER_CONFIG:
            self._config_fixture = self.useFixture(cfg_fixture.Config())
            config.parse_args(args=[])
            self.addCleanup(CONF.reset)

            if self.REGISTER_POLICY:
                policy.ENFORCER = None
                policy.setup_policy(CONF)
        elif self.REGISTER_POLICY:
            raise Exception('You need to register config to register policy')

        self.useFixture(freezer_fixtures.WarningsFixture())

        self.test_dir = self.useFixture(fixtures.TempDir()).path
        self.conf_dir = os.path.join(self.test_dir, 'etc')
        os.makedirs(self.conf_dir)


class FakeContext(object):
    def __init__(self, *args, **kwargs):
        self.context = {}

    def to_dict(self):
        return self.context


def get_req_items(name):
    req_info = {'freezer.context': FakeContext()}
    return req_info[name]
