# Copyright 2014 Openinstance Foundation
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

from oslo_serialization import jsonutils as json
from subprocess import PIPE
from subprocess import Popen
from tempest.lib import decorators
from testtools import testcase as testtools
from trove_tempest_plugin.tests.api.database import base


class DatabaseScenarioTest(base.BaseDatabaseTest):

    def db_instance(self):
        post_body = {
            "instance": {
                "users": [
                    {
                        "password": "tempest_password",
                        "name": "tempest_username",
                        "databases": [
                            {
                                "name": "tempest_test"
                            }
                        ]
                    }
                ],
                "availability_zone": self.availability_zone,
                "flavorRef": self.db_flavor_ref,
                "volume": {
                    "size": self.volume_size
                },
                "databases": [
                    {
                        "name": "tempest_test"
                    }
                ],
                "datastore": {
                    "type": self.datastore_type
                },
                "name": "tempest-trove-inst"
                }
            }
        return post_body

    def check_db_connectivity(self, instance_ip):
        command = "mysqladmin -utempest_username -ptempest_password\
                   -h%s ping" % instance_ip
        process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print(stdout, stderr)
        if process.returncode:
            raise Exception.message("DB connectivity check failed with %s"
                                    % stderr)

    @classmethod
    def resource_setup(cls):
        super(DatabaseScenarioTest, cls).resource_setup()
        cls.client = cls.database_instances_client

    @decorators.idempotent_id('91d327ca-f982-4fd9-ae1b-191259f4d60b')
    def test_list_instances(self):
        instances = self.client.list_db_instances()['instances']
        self.assertTrue(len(instances) > 0, "No available instances found")

    @testtools.attr('slow')
    @decorators.idempotent_id('970e5cb3-4ea6-46d2-b522-bd64721ef16c')
    def test_create_instances(self):
        post_body = json.dumps(self.db_instance())
        instances = self.client.create_db_instance(post_body)['instance']
        self.assertTrue(len(instances) > 0, "No available instances found")
        self.client.wait_for_db_instance_status(instances['id'], 'ACTIVE')
        instance_ip = self.client.show_db_instance(
            instances['id'])['instance']['ip']
        self.check_db_connectivity(instance_ip[0])
        self.client.delete_db_instance(instances['id'])
        decommission = self.client.wait_for_db_instance_decommission(
            instances['id'])
        self.assertFalse(decommission, "DB instance deletion failed!")
