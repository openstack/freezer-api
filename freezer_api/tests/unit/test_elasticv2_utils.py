# Copyright 2026, Cleura AB.
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

import copy

from freezer_api.common import elasticv2_utils
from freezer_api.common import exceptions as freezer_api_exc
from freezer_api.tests.unit import common


# ---------------------------------------------------------------------------
# Shared minimal document stubs used across several test classes
# ---------------------------------------------------------------------------

MINIMAL_ACTION_DOC = {
    'freezer_action': {
        'action': 'backup',
        'mode': 'fs',
    }
}

MINIMAL_JOB_DOC = {
    'client_id': 'mytenantid_myhostname',
    'job_actions': [],
}

MINIMAL_SESSION_DOC = {
    'description': 'test session',
    'schedule': {
        'time_created': 1234,
        'time_started': -1,
        'time_ended': -1,
        'status': 'stop',
    },
}

MINIMAL_CLIENT_DOC = {
    'client_id': 'test-tenant_hostname',
    'description': 'test client',
}


class TestBackupMetadataDoc(common.FreezerBaseTestCase):

    def _make_valid_data(self):
        return copy.deepcopy(common.fake_data_0_backup_metadata)

    def test_is_valid_returns_true_for_complete_doc(self):
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=self._make_valid_data(),
        )
        self.assertTrue(doc.is_valid())

    def test_is_valid_returns_false_when_project_id_empty(self):
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='',
            user_id='user1',
            user_name='John',
            data=self._make_valid_data(),
        )
        self.assertFalse(doc.is_valid())

    def test_is_valid_returns_false_when_user_id_empty(self):
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='',
            user_name='John',
            data=self._make_valid_data(),
        )
        self.assertFalse(doc.is_valid())

    def test_is_valid_returns_false_when_container_missing(self):
        data = self._make_valid_data()
        data.pop('container')
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=data,
        )
        self.assertFalse(doc.is_valid())

    def test_is_valid_returns_false_when_container_empty(self):
        data = self._make_valid_data()
        data['container'] = ''
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=data,
        )
        self.assertFalse(doc.is_valid())

    def test_is_valid_returns_false_when_hostname_missing(self):
        data = self._make_valid_data()
        data.pop('hostname')
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=data,
        )
        self.assertFalse(doc.is_valid())

    def test_is_valid_returns_false_when_backup_name_empty(self):
        data = self._make_valid_data()
        data['backup_name'] = ''
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=data,
        )
        self.assertFalse(doc.is_valid())

    def test_serialize_returns_expected_keys(self):
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=self._make_valid_data(),
        )
        result = doc.serialize()
        self.assertIn('backup_id', result)
        self.assertEqual('proj1', result['project_id'])
        self.assertEqual('user1', result['user_id'])
        self.assertEqual('John', result['user_name'])
        self.assertIn('backup_metadata', result)

    def test_serialize_backup_id_is_non_empty_hex(self):
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=self._make_valid_data(),
        )
        result = doc.serialize()
        self.assertTrue(len(result['backup_id']) > 0)

    def test_serialize_backup_metadata_equals_input_data(self):
        data = self._make_valid_data()
        doc = elasticv2_utils.BackupMetadataDoc(
            project_id='proj1',
            user_id='user1',
            user_name='John',
            data=data,
        )
        result = doc.serialize()
        self.assertEqual(data, result['backup_metadata'])


class TestActionDocCreate(common.FreezerBaseTestCase):

    def _doc(self, extra=None):
        d = copy.deepcopy(MINIMAL_ACTION_DOC)
        if extra:
            d.update(extra)
        return d

    def test_create_sets_user_id_and_project_id(self):
        res = elasticv2_utils.ActionDoc.create(
            self._doc(), 'user1', 'proj1')
        self.assertEqual('user1', res['user_id'])
        self.assertEqual('proj1', res['project_id'])

    def test_create_generates_action_id_when_absent(self):
        res = elasticv2_utils.ActionDoc.create(self._doc(), 'u', 'p')
        self.assertIn('action_id', res)
        self.assertTrue(len(res['action_id']) > 0)

    def test_create_generates_action_id_when_empty_string(self):
        doc = self._doc({'action_id': ''})
        res = elasticv2_utils.ActionDoc.create(doc, 'u', 'p')
        self.assertNotEqual('', res['action_id'])

    def test_create_preserves_existing_action_id(self):
        doc = self._doc({'action_id': 'my-action-id'})
        res = elasticv2_utils.ActionDoc.create(doc, 'u', 'p')
        self.assertEqual('my-action-id', res['action_id'])

    def test_create_raises_on_invalid_doc(self):
        # completely empty doc fails schema validation
        self.assertRaises(
            freezer_api_exc.BadDataFormat,
            elasticv2_utils.ActionDoc.create,
            {}, 'u', 'p',
        )


class TestActionDocUpdate(common.FreezerBaseTestCase):

    def _doc(self):
        return copy.deepcopy(common.get_fake_action_0())

    def test_update_overwrites_user_id(self):
        doc = self._doc()
        res = elasticv2_utils.ActionDoc.update(
            doc, 'new-user', 'fixed-action-id', 'new-proj')
        self.assertEqual('new-user', res['user_id'])

    def test_update_overwrites_action_id(self):
        doc = self._doc()
        res = elasticv2_utils.ActionDoc.update(
            doc, 'u', 'forced-id', 'p')
        self.assertEqual('forced-id', res['action_id'])

    def test_update_overwrites_project_id(self):
        doc = self._doc()
        res = elasticv2_utils.ActionDoc.update(
            doc, 'u', 'aid', 'new-project')
        self.assertEqual('new-project', res['project_id'])

    def test_update_raises_on_invalid_doc(self):
        self.assertRaises(
            freezer_api_exc.BadDataFormat,
            elasticv2_utils.ActionDoc.update,
            {}, 'u', 'aid', 'p',
        )


class TestActionDocCreatePatch(common.FreezerBaseTestCase):

    def test_create_patch_removes_user_id(self):
        doc = {'user_id': 'should-be-removed', 'max_retries': 5}
        result = elasticv2_utils.ActionDoc.create_patch(doc)
        self.assertNotIn('user_id', result)

    def test_create_patch_removes_action_id(self):
        doc = {'action_id': 'should-be-removed', 'max_retries': 5}
        result = elasticv2_utils.ActionDoc.create_patch(doc)
        self.assertNotIn('action_id', result)

    def test_create_patch_preserves_other_fields(self):
        doc = {'max_retries': 5, 'mandatory': False}
        result = elasticv2_utils.ActionDoc.create_patch(doc)
        self.assertEqual(5, result['max_retries'])
        self.assertFalse(result['mandatory'])

    def test_create_patch_raises_on_invalid_patch(self):
        # 'action' must match pattern ^[\w-]+$ — a value with spaces fails
        self.assertRaises(
            freezer_api_exc.BadDataFormat,
            elasticv2_utils.ActionDoc.create_patch,
            {'action': 'invalid action with spaces!'},
        )


class TestJobDocCreate(common.FreezerBaseTestCase):

    def _doc(self, extra=None):
        d = copy.deepcopy(MINIMAL_JOB_DOC)
        if extra:
            d.update(extra)
        return d

    def test_create_sets_user_id_and_project_id(self):
        res = elasticv2_utils.JobDoc.create(self._doc(), 'proj1', 'user1')
        self.assertEqual('user1', res['user_id'])
        self.assertEqual('proj1', res['project_id'])

    def test_create_generates_job_id_when_absent(self):
        res = elasticv2_utils.JobDoc.create(self._doc(), 'p', 'u')
        self.assertIn('job_id', res)
        self.assertTrue(len(res['job_id']) > 0)

    def test_create_generates_job_id_when_empty(self):
        doc = self._doc({'job_id': ''})
        res = elasticv2_utils.JobDoc.create(doc, 'p', 'u')
        self.assertNotEqual('', res['job_id'])

    def test_create_preserves_existing_job_id(self):
        doc = self._doc({'job_id': 'custom-job-id'})
        res = elasticv2_utils.JobDoc.create(doc, 'p', 'u')
        self.assertEqual('custom-job-id', res['job_id'])

    def test_create_sets_job_schedule_timestamps(self):
        res = elasticv2_utils.JobDoc.create(self._doc(), 'p', 'u')
        schedule = res.get('job_schedule', {})
        self.assertIn('time_created', schedule)
        self.assertEqual(-1, schedule['time_started'])
        self.assertEqual(-1, schedule['time_ended'])

    def test_create_does_not_overwrite_existing_schedule_fields(self):
        # time_created should be freshly set; other non-colliding keys kept
        doc = self._doc({'job_schedule': {'status': 'stop'}})
        res = elasticv2_utils.JobDoc.create(doc, 'p', 'u')
        self.assertEqual('stop', res['job_schedule']['status'])

    def test_create_raises_on_invalid_doc(self):
        self.assertRaises(
            freezer_api_exc.BadDataFormat,
            elasticv2_utils.JobDoc.create,
            {}, 'p', 'u',
        )


class TestJobDocUpdate(common.FreezerBaseTestCase):

    def _base_doc(self):
        return copy.deepcopy(common.get_fake_job_0())

    def test_update_overwrites_user_id(self):
        doc = self._base_doc()
        res = elasticv2_utils.JobDoc.update(doc, 'proj', 'new-user', 'jid')
        self.assertEqual('new-user', res['user_id'])

    def test_update_overwrites_project_id(self):
        doc = self._base_doc()
        res = elasticv2_utils.JobDoc.update(doc, 'new-proj', 'u', 'jid')
        self.assertEqual('new-proj', res['project_id'])

    def test_update_overwrites_job_id(self):
        doc = self._base_doc()
        res = elasticv2_utils.JobDoc.update(doc, 'p', 'u', 'forced-jid')
        self.assertEqual('forced-jid', res['job_id'])

    def test_update_raises_on_invalid_doc(self):
        self.assertRaises(
            freezer_api_exc.BadDataFormat,
            elasticv2_utils.JobDoc.update,
            {}, 'p', 'u', 'jid',
        )


class TestJobDocCreatePatch(common.FreezerBaseTestCase):

    def test_create_patch_removes_user_id(self):
        doc = {'user_id': 'gone', 'description': 'keep me'}
        result = elasticv2_utils.JobDoc.create_patch(doc)
        self.assertNotIn('user_id', result)

    def test_create_patch_removes_job_id(self):
        doc = {'job_id': 'gone', 'description': 'keep me'}
        result = elasticv2_utils.JobDoc.create_patch(doc)
        self.assertNotIn('job_id', result)

    def test_create_patch_removes_user_credentials(self):
        doc = {'user_credentials': {'trust_id': 'abc'}, 'description': 'x'}
        result = elasticv2_utils.JobDoc.create_patch(doc)
        self.assertNotIn('user_credentials', result)

    def test_create_patch_preserves_other_fields(self):
        doc = {'description': 'my desc'}
        result = elasticv2_utils.JobDoc.create_patch(doc)
        self.assertEqual('my desc', result['description'])


class TestSessionDocCreate(common.FreezerBaseTestCase):

    def _doc(self, extra=None):
        d = copy.deepcopy(MINIMAL_SESSION_DOC)
        if extra:
            d.update(extra)
        return d

    def test_create_sets_user_id_and_project_id(self):
        res = elasticv2_utils.SessionDoc.create(
            self._doc(), 'user1', 'proj1')
        self.assertEqual('user1', res['user_id'])
        self.assertEqual('proj1', res['project_id'])

    def test_create_generates_session_id(self):
        res = elasticv2_utils.SessionDoc.create(self._doc(), 'u', 'p')
        self.assertIn('session_id', res)
        self.assertTrue(len(res['session_id']) > 0)

    def test_create_sets_status_active(self):
        res = elasticv2_utils.SessionDoc.create(self._doc(), 'u', 'p')
        self.assertEqual('active', res['status'])

    def test_create_initialises_jobs_as_empty_list(self):
        res = elasticv2_utils.SessionDoc.create(self._doc(), 'u', 'p')
        self.assertEqual([], res['jobs'])

    def test_create_sets_default_hold_off(self):
        res = elasticv2_utils.SessionDoc.create(self._doc(), 'u', 'p')
        self.assertEqual(30, res['hold_off'])

    def test_create_respects_custom_hold_off(self):
        doc = self._doc({'hold_off': 90})
        res = elasticv2_utils.SessionDoc.create(doc, 'u', 'p')
        self.assertEqual(90, res['hold_off'])

    def test_create_sets_default_session_tag_zero(self):
        res = elasticv2_utils.SessionDoc.create(self._doc(), 'u', 'p')
        self.assertEqual(0, res['session_tag'])

    def test_create_preserves_existing_session_tag(self):
        doc = self._doc({'session_tag': 7})
        res = elasticv2_utils.SessionDoc.create(doc, 'u', 'p')
        self.assertEqual(7, res['session_tag'])


class TestSessionDocUpdate(common.FreezerBaseTestCase):

    def _base_doc(self):
        return copy.deepcopy(common.get_fake_session_0())

    def test_update_overwrites_user_id(self):
        doc = self._base_doc()
        res = elasticv2_utils.SessionDoc.update(
            doc, 'new-user', 'sid', 'proj')
        self.assertEqual('new-user', res['user_id'])

    def test_update_overwrites_session_id(self):
        doc = self._base_doc()
        res = elasticv2_utils.SessionDoc.update(doc, 'u', 'new-sid', 'p')
        self.assertEqual('new-sid', res['session_id'])

    def test_update_overwrites_project_id(self):
        doc = self._base_doc()
        res = elasticv2_utils.SessionDoc.update(doc, 'u', 'sid', 'new-proj')
        self.assertEqual('new-proj', res['project_id'])

    def test_update_raises_on_invalid_doc(self):
        self.assertRaises(
            freezer_api_exc.BadDataFormat,
            elasticv2_utils.SessionDoc.update,
            {}, 'u', 'sid', 'p',
        )


class TestSessionDocCreatePatch(common.FreezerBaseTestCase):

    def test_create_patch_removes_user_id(self):
        doc = {'user_id': 'gone', 'description': 'keep'}
        result = elasticv2_utils.SessionDoc.create_patch(doc)
        self.assertNotIn('user_id', result)

    def test_create_patch_removes_session_id(self):
        doc = {'session_id': 'gone', 'description': 'keep'}
        result = elasticv2_utils.SessionDoc.create_patch(doc)
        self.assertNotIn('session_id', result)

    def test_create_patch_preserves_other_fields(self):
        doc = {'description': 'updated desc', 'hold_off': 45}
        result = elasticv2_utils.SessionDoc.create_patch(doc)
        self.assertEqual('updated desc', result['description'])
        self.assertEqual(45, result['hold_off'])


class TestClientDocCreate(common.FreezerBaseTestCase):

    def _doc(self, extra=None):
        d = copy.deepcopy(MINIMAL_CLIENT_DOC)
        if extra:
            d.update(extra)
        return d

    def test_create_wraps_doc_under_client_key(self):
        res = elasticv2_utils.ClientDoc.create(self._doc(), 'proj1', 'user1')
        self.assertIn('client', res)

    def test_create_sets_user_id(self):
        res = elasticv2_utils.ClientDoc.create(self._doc(), 'proj1', 'user1')
        self.assertEqual('user1', res['user_id'])

    def test_create_sets_project_id(self):
        res = elasticv2_utils.ClientDoc.create(self._doc(), 'proj1', 'user1')
        self.assertEqual('proj1', res['project_id'])

    def test_create_generates_uuid_when_absent(self):
        doc = self._doc()
        doc.pop('uuid', None)
        res = elasticv2_utils.ClientDoc.create(doc, 'proj1', 'user1')
        self.assertIn('uuid', res['client'])
        self.assertTrue(len(res['client']['uuid']) > 0)

    def test_create_preserves_existing_uuid(self):
        doc = self._doc({'uuid': 'my-uuid-value'})
        res = elasticv2_utils.ClientDoc.create(doc, 'proj1', 'user1')
        self.assertEqual('my-uuid-value', res['client']['uuid'])

    def test_create_raises_on_missing_client_id(self):
        doc = {'description': 'no client_id here'}
        self.assertRaises(
            freezer_api_exc.BadDataFormat,
            elasticv2_utils.ClientDoc.create,
            doc, 'proj1', 'user1',
        )

    def test_create_client_info_preserved_inside_client_key(self):
        doc = self._doc()
        res = elasticv2_utils.ClientDoc.create(doc, 'proj1', 'user1')
        self.assertEqual(
            MINIMAL_CLIENT_DOC['client_id'],
            res['client']['client_id'],
        )
