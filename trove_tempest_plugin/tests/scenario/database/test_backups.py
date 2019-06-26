# Copyright 2014 OpenStack Foundation
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

from tempest.lib.common.utils import test_utils
from tempest.lib import decorators

from trove_tempest_plugin.common import utils
from trove_tempest_plugin.common import waiters
from trove_tempest_plugin.tests.api.database.instances import base


class BackupRestoreScenarioTest(base.WithInstanceBaseTest):

    @classmethod
    def resource_setup(cls):
        super(BackupRestoreScenarioTest, cls).resource_setup()
        cls.backup_client = cls.database_backups_client

    @decorators.idempotent_id('aec0a59a-1f94-4235-ba8c-5bb2b210bc49')
    def test_restore_from_backup(self):
        # Create a user and a DB as verification restore works
        db_name = utils.rand_name()
        user_name = utils.rand_name()
        user_password = utils.rand_name()
        self.client.create_database(self.instance_id, name=db_name)
        self.client.create_user(self.instance_id, name=user_name,
                                password=user_password)
        self.client.grant_user_access(self.instance_id, user_name, [db_name])

        databases = self.client.list_databases(self.instance_id)['databases']
        users = self.client.list_users(self.instance_id)['users']

        # Create backup
        backup_name = utils.db_rand_name()
        backup = self.backup_client.create_backup(self.instance_id,
                                                  backup_name)
        backup_id = backup['backup']['id']
        waiters.wait_for_backup_status(self.backup_client, backup_id,
                                       'COMPLETED')

        self.addClassResourceCleanup(waiters.wait_for_backup_delete,
                                     self.backup_client, backup_id)
        self.addClassResourceCleanup(test_utils.call_and_ignore_notfound_exc,
                                     self.backup_client.delete_backup,
                                     backup_id)

        # Create new instance from backup
        restored_instance = self.create_test_instance(backup_id=backup_id)

        restored_databases = self.client.list_databases(
            restored_instance['id'])['databases']
        restored_users = self.client.list_users(
            restored_instance['id'])['users']

        # Ensure users and databases match
        self.assertEqual(databases, restored_databases)
        self.assertEqual(users, restored_users)

    @decorators.idempotent_id('ae37347c-9dac-4b4d-bf95-cb64722094dc')
    def test_restore_from_incremental_backup(self):
        # Create a user and a DB as verification restore works
        db_name = utils.rand_name()
        user_name = utils.rand_name()
        user_password = utils.rand_name()
        self.client.create_database(self.instance_id, name=db_name)
        self.client.create_user(self.instance_id, name=user_name,
                                password=user_password)
        self.client.grant_user_access(self.instance_id, user_name, [db_name])

        # Create backup
        backup_name = utils.rand_name()
        backup = self.backup_client.create_backup(self.instance_id,
                                                  backup_name)
        backup_id = backup['backup']['id']
        waiters.wait_for_backup_status(self.backup_client, backup_id,
                                       'COMPLETED')

        self.addClassResourceCleanup(waiters.wait_for_backup_delete,
                                     self.backup_client, backup_id)
        self.addClassResourceCleanup(test_utils.call_and_ignore_notfound_exc,
                                     self.backup_client.delete_backup,
                                     backup_id)

        # Create another user and a DB as verification for incremental works
        db_name = utils.rand_name()
        user_name = utils.rand_name()
        user_password = utils.rand_name()
        self.client.create_database(self.instance_id, name=db_name)
        self.client.create_user(self.instance_id, name=user_name,
                                password=user_password)
        self.client.grant_user_access(self.instance_id, user_name, [db_name])

        databases = self.client.list_databases(self.instance_id)['databases']
        users = self.client.list_users(self.instance_id)['users']

        # Create incremental backup
        backup_name = utils.rand_name()
        backup = self.backup_client.create_backup(
            self.instance_id, backup_name, parent=backup_id, incremental=True)
        backup_id = backup['backup']['id']
        waiters.wait_for_backup_status(self.backup_client, backup_id,
                                       'COMPLETED')

        self.addClassResourceCleanup(waiters.wait_for_backup_delete,
                                     self.backup_client, backup_id)
        self.addClassResourceCleanup(test_utils.call_and_ignore_notfound_exc,
                                     self.backup_client.delete_backup,
                                     backup_id)

        # Create new instance from backup
        restored_instance = self.create_test_instance(backup_id=backup_id)

        restored_databases = self.client.list_databases(
            restored_instance['id'])['databases']
        restored_users = self.client.list_users(
            restored_instance['id'])['users']

        # Ensure users and databases match
        self.assertEqual(databases, restored_databases)
        self.assertEqual(users, restored_users)
