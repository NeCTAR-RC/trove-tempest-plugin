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

from tempest.lib import exceptions as lib_exc

from trove_tempest_plugin.common import waiters
from trove_tempest_plugin.tests.api.database import base


class WithInstanceBaseTest(base.BaseDatabaseTest):

    def setUp(self):
        # Normally we use the same server with all test cases,
        # but if it has an issue, we build a new one
        super(WithInstanceBaseTest, self).setUp()
        # Check if the server is in a clean state after test
        try:
            waiters.wait_for_db_instance_status(self.client, self.instance_id,
                                                'ACTIVE')
        except lib_exc.NotFound:
            instance = self.create_test_instance()
            self.__class__.instance_id = instance['id']

    @classmethod
    def setup_clients(cls):
        super(WithInstanceBaseTest, cls).setup_clients()
        cls.client = cls.database_instances_client

    @classmethod
    def resource_setup(cls, datastore_version=None):
        super(WithInstanceBaseTest, cls).resource_setup()
        instance = cls.create_test_instance(
            datastore_version=datastore_version)
        cls.instance_id = instance['id']
