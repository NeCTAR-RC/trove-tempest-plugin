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

import testtools

from tempest import config
from tempest.lib import decorators

from trove_tempest_plugin.common import utils
from trove_tempest_plugin.common import waiters
from trove_tempest_plugin.tests.api.database.instances import base

CONF = config.CONF


class UpgradeInstanceScenarioTest(base.WithInstanceBaseTest):

    @classmethod
    def resource_setup(cls):
        super().resource_setup(
            datastore_version=CONF.database.previous_datastore_version)
        cls.client = cls.database_instances_client

    @testtools.skipUnless(CONF.database.previous_datastore_version,
                          'The previous_datastore_version must be specified.')
    @decorators.idempotent_id('7950255c-ddcb-4af0-936f-523e0ee31041')
    def test_upgrade_instance(self):
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

        self.client.upgrade_db_instance(self.instance_id,
                                        self.datastore_version)
        waiters.wait_for_db_instance_status(self.client, self.instance_id,
                                            'ACTIVE')

        databases_upgrade = self.client.list_databases(
            self.instance_id)['databases']
        users_upgrade = self.client.list_users(self.instance_id)['users']

        # Ensure users and databases match
        self.assertEqual(databases, databases_upgrade)
        self.assertEqual(users, users_upgrade)
