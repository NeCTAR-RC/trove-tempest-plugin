# Copyright 2019 OpenStack Foundation
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

from tempest.lib.common.utils import data_utils
from tempest.lib import decorators

from trove_tempest_plugin.common import waiters
from trove_tempest_plugin.tests.api.database.instances import base


class InstanceActionsTest(base.WithInstanceBaseTest):

    @decorators.idempotent_id('ace549b3-eee0-4502-bf20-7594d4bf4856')
    def test_restart_server(self):
        self.client.restart_db_instance(self.instance_id)
        waiters.wait_for_db_instance_status(self.client, self.instance_id,
                                            'ACTIVE')

    @decorators.idempotent_id('215fbcbe-40d3-4a8f-9fe1-55ea9e8fb814')
    def test_update_name(self):
        new_name = 'new-name'
        self.client.update_db_instance(self.instance_id, name=new_name)
        waiters.wait_for_db_instance_status(self.client, self.instance_id,
                                            'ACTIVE')

        # Verify the name of the instance has changed
        instance = self.client.show_db_instance(self.instance_id)['instance']
        self.assertEqual(new_name, instance['name'])

    @decorators.idempotent_id('38b5462a-308e-4cb8-9530-cc6741c95501')
    def test_list_create_delete_database(self):
        name = data_utils.rand_name()
        self.client.create_database(self.instance_id, name=name)
        databases = self.client.list_databases(self.instance_id)['databases']
        databases = [x['name'] for x in databases]
        self.assertIn(name, databases)
        self.client.delete_database(self.instance_id, name=name)
        databases = self.client.list_databases(self.instance_id)['databases']
        databases = [x['name'] for x in databases]
        self.assertNotIn(name, databases)

    @decorators.idempotent_id('bf4840fe-8cf8-46a1-8371-13021e87c690')
    def test_enable_disable_root(self):
        root_show = self.client.root_show(self.instance_id)
        self.assertFalse(root_show['rootEnabled'])
        root_enable = self.client.root_enable(self.instance_id)
        self.assertIn('password', list(root_enable['user'].keys()))
        # TODO(sorrison) Test connection with root user/password
        root_show = self.client.root_show(self.instance_id)
        self.assertTrue(root_show['rootEnabled'])
        self.client.root_disable(self.instance_id)
        root_show = self.client.root_show(self.instance_id)
        # Show root show's if root as ever been enabled so disabling should
        # have no impact
        self.assertTrue(root_show['rootEnabled'])

    @decorators.idempotent_id('9f11d15b-9640-4c33-a7db-c78224763014')
    def test_list_create_delete_user(self):
        name = data_utils.rand_name()[:16]
        self.client.create_user(self.instance_id, name=name, password='secret')
        users = self.client.list_users(self.instance_id)['users']
        users = [x['name'] for x in users]
        self.assertIn(name, users)
        self.client.delete_user(self.instance_id, name=name)
        users = self.client.list_users(self.instance_id)['users']
        users = [x['name'] for x in users]
        self.assertNotIn(name, users)

    @decorators.idempotent_id('6f8b8350-f2a9-47b2-a108-8e3653cb9b57')
    def test_grant_revoke_list_access(self):
        # PostgreSQL has an issue granting to user with a -
        user = data_utils.rand_name()[:16].replace('-', '_')
        db = data_utils.rand_name()
        self.client.create_user(self.instance_id, name=user, password='secret')
        self.client.create_database(self.instance_id, name=db)
        access = self.client.show_user_access(self.instance_id, user)
        self.assertEqual([], access['databases'])
        self.client.grant_user_access(self.instance_id, user, [db])
        access = self.client.show_user_access(self.instance_id, user)
        access = [x['name'] for x in access['databases']]
        self.assertIn(db, access)
        self.client.revoke_user_access(self.instance_id, user, db)
        access = self.client.show_user_access(self.instance_id, user)
        access = [x['name'] for x in access['databases']]
        self.assertNotIn(db, access)

    @decorators.idempotent_id('b13ff6fb-6214-416b-8aea-23dc3c24d00e')
    def test_list_backups(self):
        backups = self.client.list_backups(self.instance_id)
        self.assertEqual([], backups['backups'])
