# (c) Copyright 2016 Hewlett-Packard Enterprise Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from freezer_api import context


class TestFreezerContext(unittest.TestCase):

    def setUp(self):
        self.ctxt = context.FreezerContext('token01', 'user01', 'tenant01',
                                           is_admin=False,
                                           roles=['_member', 'backup_admin'])

    def test_not_admin(self):
        ctxt = context.get_current()
        self.assertEqual(ctxt.is_admin, False)

    def test_privileges_elevated(self):
        self.ctxt = self.ctxt.elevated('yes')
        self.assertEqual(self.ctxt.is_admin, True)
        self.assertEqual(self.ctxt.show_deleted, 'yes')

    def test_admin_context(self):
        admin_ctxt = context.get_admin_context(show_deleted='yes')
        self.assertEqual(admin_ctxt.is_admin, True)
        self.assertEqual(admin_ctxt.show_deleted, 'yes')

    def test_from_dict(self):
        ctxt_dict = {'user': 'user02',
                     'tenant': 'tenant03',
                     'roles': ['_member', 'member']}
        ctxt = context.FreezerContext.from_dict(ctxt_dict)
        self.assertEqual(ctxt.is_admin, False)
        self.assertEqual(ctxt.user, 'user02')
        self.assertEqual(ctxt.tenant, ctxt_dict.get('tenant'))
