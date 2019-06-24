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

from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils import test_utils
from tempest.lib import decorators

from trove_tempest_plugin.common import waiters
from trove_tempest_plugin.tests.api.database.instances import base


class InstanceBackupsTest(base.WithInstanceBaseTest):

    @classmethod
    def setup_clients(cls):
        super(InstanceBackupsTest, cls).setup_clients()
        cls.backup_client = cls.database_backups_client

    def _add_cleanup(self, backup_id):
        self.addClassResourceCleanup(
            waiters.wait_for_backup_delete,
            self.backup_client, backup_id)

        self.addClassResourceCleanup(
            test_utils.call_and_ignore_notfound_exc,
            self.backup_client.delete_backup, backup_id)

    @decorators.idempotent_id('e4c2bf6d-e619-4d9b-a79b-67f5463a8705')
    def test_list_create_delete_backup(self):
        name = data_utils.rand_name()
        backup = self.backup_client.create_backup(self.instance_id, name)
        backup_id = backup['backup']['id']
        waiters.wait_for_backup_status(self.backup_client, backup_id,
                                       'COMPLETED')
        backups = self.backup_client.list_backups()
        backup_ids = [x['id'] for x in backups['backups']]
        self.assertIn(backup_id, backup_ids)

        self.backup_client.delete_backup(backup_id)
        waiters.wait_for_backup_delete(self.backup_client, backup_id)

        backups = self.backup_client.list_backups()
        backup_ids = [x['id'] for x in backups['backups']]
        self.assertNotIn(backup_id, backup_ids)

    @decorators.idempotent_id('2ddab860-b487-481f-b89e-9ad06d5f6286')
    def test_backup_incremental(self):
        name = data_utils.rand_name()
        backup = self.backup_client.create_backup(self.instance_id, name)
        parent_id = backup['backup']['id']
        self._add_cleanup(parent_id)
        waiters.wait_for_backup_status(self.backup_client, parent_id,
                                       'COMPLETED')
        backup = self.backup_client.create_backup(self.instance_id, name,
                                                  incremental=True,
                                                  parent=parent_id)
        backup_id = backup['backup']['id']
        self._add_cleanup(backup_id)
        waiters.wait_for_backup_status(self.backup_client, backup_id,
                                       'COMPLETED')
        backup = self.backup_client.show_backup(backup_id)
        self.assertEqual(parent_id, backup['backup']['parent_id'])
