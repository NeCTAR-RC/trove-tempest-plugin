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

from tempest.lib import decorators
from testtools import testcase as testtools

from trove_tempest_plugin.tests.api.database import base


class DatabaseDatastoresTest(base.BaseDatabaseTest):

    @classmethod
    def resource_setup(cls):
        super(DatabaseDatastoresTest, cls).resource_setup()
        cls.client = cls.database_datastores_client

    @testtools.attr('smoke')
    @decorators.idempotent_id('e4cdcadf-51bc-41ec-8cc6-530a3da08d10')
    def test_datastores(self):
        datastores = self.client.list_db_datastores()['datastores']
        self.assertTrue(len(datastores) > 0, "No available datastores found")
