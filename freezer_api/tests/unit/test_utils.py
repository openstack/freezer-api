# (c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import patch

from freezer_api.common import exceptions
from freezer_api.common import utils
from freezer_api.tests.unit import common

DATA_backup_metadata = {
    "container": "freezer_container",
    "hostname": "alpha",
    "backup_name": "important_data_backup",
    "time_stamp": 12341234,
    "curr_backup_level": 0,
    "backup_session": 12341234,
    "max_level": 5,
    "mode": "fs",
    "fs_real_path": "/blabla",
    "vol_snap_path": "/blablasnap",
    "total_broken_links": 0,
    "total_fs_files": 11,
    "total_directories": 2,
    "backup_size_uncompressed": 12112342,
    "backup_size_compressed": 1214322,
    "total_backup_session_size": 1212,
    "compression_alg": "None",
    "encrypted": "false",
    "client_os": "linux",
    "broken_links": ["link_01", "link_02"],
    "excluded_files": ["excluded_file_01", "excluded_file_02"],
    'cli': 'whatever'
}

DATA_user_id = 'AUx6F07NwlhuOVELWtHx'

DATA_user_name = 'gegrex55NPlwlhuOVELWtHv'

DATA_backup_id = 'd78f820089d64b7b9096d3133ca3162d'

DATA_wrapped_backup_metadata = {
    'user_id': DATA_user_id,
    'user_name': DATA_user_name,
    'backup_id': DATA_backup_id,
    'backup_medatada': {
        "container": "freezer_container",
        "hostname": "alpha",
        "backup_name": "important_data_backup",
        "time_stamp": 12341234,
        "curr_backup_level": 0,
        "backup_session": 12341234,
        "max_level": 5,
        "mode": "fs",
        "fs_real_path": "/blabla",
        "vol_snap_path": "/blablasnap",
        "total_broken_links": 0,
        "total_fs_files": 11,
        "total_directories": 2,
        "backup_size_uncompressed": 12112342,
        "backup_size_compressed": 1214322,
        "total_backup_session_size": 1212,
        "compression_alg": "None",
        "encrypted": "false",
        "client_os": "linux",
        "broken_links": ["link_01", "link_02"],
        "excluded_files": ["excluded_file_01", "excluded_file_02"],
        'cli': 'whatever'
    }
}


class TestBackupMetadataDoc(common.FreezerBaseTestCase):
    def setUp(self):
        super().setUp()
        self.backup_metadata = utils.BackupMetadataDoc(
            user_id=DATA_user_id,
            user_name=DATA_user_name,
            data=DATA_backup_metadata)

    def test_is_valid_return_True_when_valid(self):
        self.assertTrue(self.backup_metadata.is_valid())

    def test_is_valid_returns_False_when_user_id_empty(self):
        self.backup_metadata.user_id = ''
        self.assertFalse(self.backup_metadata.is_valid())


class TestJobDoc(common.FreezerBaseTestCase):
    def test_validate_ok_when_data_ok(self):
        job_doc = common.get_fake_job_0()
        self.assertIsNone(utils.JobDoc.validate(job_doc))

    def test_validate_raises_BadDataFormat_when_doc_has_no_jobid(self):
        job_doc = common.get_fake_job_0()
        job_doc.pop('job_id')
        self.assertRaises(exceptions.BadDataFormat, utils.JobDoc.validate,
                          job_doc)

    def test_validate_raises_BadDataFormat_when_doc_has_no_userid(self):
        job_doc = common.get_fake_job_0()
        job_doc.pop('job_id')
        self.assertRaises(exceptions.BadDataFormat, utils.JobDoc.validate,
                          job_doc)

    def test_validate_raises_BadDataFormat_when_doc_has_invalid_state(self):
        job_doc = common.get_fake_job_0()
        job_doc['job_schedule']['status'] = 'not_valid'
        self.assertRaises(exceptions.BadDataFormat, utils.JobDoc.validate,
                          job_doc)

    def test_validate_patch_raises_when_doc_has_invalid_state(self):
        job_doc = common.get_fake_job_0()
        job_doc['job_schedule']['status'] = 'value_no_allowed'
        self.assertRaises(exceptions.BadDataFormat,
                          utils.JobDoc.validate_patch, job_doc)

    def test_createpatch_pops_jobid_and_userid(self):
        job_doc = common.get_fake_job_0()
        res_doc = utils.JobDoc.create_patch(job_doc)
        self.assertNotIn('job_id', res_doc)
        self.assertNotIn('user_id', res_doc)

    def test_createpatch_raises_BadDataFormat_when_patch_has_invalid_state(
            self):
        job_doc = common.get_fake_job_0()
        job_doc['job_schedule']['status'] = 'value_no_allowed'
        self.assertRaises(exceptions.BadDataFormat, utils.JobDoc.create_patch,
                          job_doc)

    def test_createpatch_raises_BadDataFormat_when_patch_has_invalid_event(
            self):
        job_doc = common.get_fake_job_0()
        job_doc['job_schedule']['event'] = 'value_no_allowed'
        self.assertRaises(exceptions.BadDataFormat, utils.JobDoc.create_patch,
                          job_doc)

    @patch('freezer_api.common.utils.uuid')
    @patch('freezer_api.common.utils.time')
    def test_create_inserts_correct_uuid_timecreated_status(self, mock_time,
                                                            mock_uuid):
        mock_time.time.return_value = 1433611337
        mock_uuid.uuid4.return_value = mock_uuid
        mock_uuid.hex = 'hotforteacher'
        job_doc = common.get_fake_job_0()
        job_doc['job_schedule']['status'] = 'stop'
        res_doc = utils.JobDoc.create(job_doc, 'dude')
        self.assertEqual(1433611337, res_doc['job_schedule']['time_created'])
        self.assertEqual(-1, res_doc['job_schedule']['time_started'])
        self.assertEqual(-1, res_doc['job_schedule']['time_ended'])
        self.assertEqual('stop', res_doc['job_schedule']['status'])
        self.assertEqual('dude', res_doc['user_id'])
        self.assertEqual('hotforteacher', res_doc['job_id'])

    @patch('freezer_api.common.utils.uuid')
    @patch('freezer_api.common.utils.time')
    def test_create_raises_BadDataFormat_when_isvalid_fails(self, mock_time,
                                                            mock_uuid):
        mock_time.time.return_value = 1433611337
        mock_uuid.uuid4.return_value = mock_uuid
        mock_uuid.hex = 'hotforteacher'
        job_doc = common.get_fake_job_0()
        job_doc['job_schedule']['event'] = 'not_valid'
        self.assertRaises(exceptions.BadDataFormat, utils.JobDoc.create,
                          job_doc, 'dude')


class TestActionDoc(common.FreezerBaseTestCase):
    def test_validate_ok_when_data_ok(self):
        action_doc = common.get_fake_action_0()
        self.assertIsNone(utils.ActionDoc.validate(action_doc))

    def test_validate_raises_BadDataFormat_when_doc_has_no_actionid(self):
        action_doc = common.get_fake_action_0()
        action_doc.pop('action_id')
        self.assertRaises(exceptions.BadDataFormat, utils.ActionDoc.validate,
                          action_doc)

    def test_validate_raises_BadDataFormat_when_doc_has_no_userid(self):
        action_doc = common.get_fake_action_0()
        action_doc.pop('user_id')
        self.assertRaises(exceptions.BadDataFormat, utils.ActionDoc.validate,
                          action_doc)

    def test_validate_raises_BadDataFormat_when_doc_has_invalid_field(self):
        action_doc = common.get_fake_action_0()
        action_doc['action_id'] = 44
        self.assertRaises(exceptions.BadDataFormat, utils.ActionDoc.validate,
                          action_doc)

    def test_validate_patch_raises_when_doc_has_invalid_field(self):
        action_doc = common.get_fake_action_0()
        action_doc['action_id'] = 44
        self.assertRaises(exceptions.BadDataFormat,
                          utils.ActionDoc.validate_patch, action_doc)

    def test_createpatch_pops_actionid_and_userid(self):
        action_doc = common.get_fake_action_0()
        res_doc = utils.ActionDoc.create_patch(action_doc)
        self.assertNotIn('action_id', res_doc)
        self.assertNotIn('user_id', res_doc)

    def test_createpatch_raises_BadDataFormat_when_patch_has_invalid_field(
            self):
        action_doc = common.get_fake_action_0()
        action_doc['action'] = 44
        self.assertRaises(exceptions.BadDataFormat,
                          utils.ActionDoc.create_patch, action_doc)

    @patch('freezer_api.common.utils.uuid')
    def test_create_inserts_correct_uuid(self, mock_uuid):
        mock_uuid.uuid4.return_value = mock_uuid
        mock_uuid.hex = 'hotforteacher'
        action_doc = common.get_fake_action_0()
        action_doc.pop('action_id')
        res_doc = utils.ActionDoc.create(action_doc, 'dude')
        self.assertEqual('dude', res_doc['user_id'])
        self.assertEqual('hotforteacher', res_doc['action_id'])

    @patch('freezer_api.common.utils.uuid')
    def test_create_raises_BadDataFormat_when_isvalid_fails(self, mock_uuid):
        mock_uuid.uuid4.return_value = mock_uuid
        mock_uuid.hex = 'hotforteacher'
        action_doc = common.get_fake_action_0()
        action_doc['action'] = 44
        self.assertRaises(exceptions.BadDataFormat, utils.ActionDoc.create,
                          action_doc, 'dude')


class TestSessionDoc(common.FreezerBaseTestCase):
    def test_validate_ok_when_data_ok(self):
        session_doc = common.get_fake_session_0()
        self.assertIsNone(utils.SessionDoc.validate(session_doc))

    def test_validate_raises_BadDataFormat_when_doc_has_no_sessionid(self):
        session_doc = common.get_fake_session_0()
        session_doc.pop('session_id')
        self.assertRaises(exceptions.BadDataFormat, utils.SessionDoc.validate,
                          session_doc)

    def test_validate_raises_BadDataFormat_when_doc_has_no_userid(self):
        session_doc = common.get_fake_session_0()
        session_doc.pop('user_id')
        self.assertRaises(exceptions.BadDataFormat, utils.SessionDoc.validate,
                          session_doc)

    def test_validate_raises_BadDataFormat_when_doc_has_invalid_field(self):
        session_doc = common.get_fake_session_0()
        session_doc['session_id'] = 44
        self.assertRaises(exceptions.BadDataFormat, utils.SessionDoc.validate,
                          session_doc)

    def test_validate_patch_raises_when_doc_has_invalid_field(self):
        session_doc = common.get_fake_session_0()
        session_doc['session_id'] = 44
        self.assertRaises(exceptions.BadDataFormat,
                          utils.SessionDoc.validate_patch, session_doc)

    def test_createpatch_pops_sessionid_and_userid(self):
        session_doc = common.get_fake_session_0()
        res_doc = utils.SessionDoc.create_patch(session_doc)
        self.assertNotIn('session_id', res_doc)
        self.assertNotIn('user_id', res_doc)

    def test_createpatch_raises_BadDataFormat_when_patch_has_invalid_field(
            self):
        session_doc = common.get_fake_session_0()
        session_doc['session_tag'] = 'ouch'
        self.assertRaises(exceptions.BadDataFormat,
                          utils.SessionDoc.create_patch, session_doc)

    @patch('freezer_api.common.utils.uuid')
    def test_create_inserts_correct_uuid(self, mock_uuid):
        mock_uuid.uuid4.return_value = mock_uuid
        mock_uuid.hex = 'hotforteacher'
        session_doc = common.get_fake_session_0()
        res_doc = utils.SessionDoc.create(session_doc, 'dude')
        self.assertEqual('dude', res_doc['user_id'])
        self.assertEqual('hotforteacher', res_doc['session_id'])

    @patch('freezer_api.common.utils.uuid')
    def test_create_raises_BadDataFormat_when_isvalid_fails(self, mock_uuid):
        mock_uuid.uuid4.return_value = mock_uuid
        mock_uuid.hex = 'hotforteacher'
        session_doc = common.get_fake_session_0()
        session_doc['time_started'] = 'ouch'
        self.assertRaises(exceptions.BadDataFormat, utils.SessionDoc.create,
                          session_doc, 'dude')
