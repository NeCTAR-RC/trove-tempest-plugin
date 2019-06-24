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

import json

from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils import test_utils
import tempest.test

from trove_tempest_plugin.common import waiters
from trove_tempest_plugin.services.database.json import backups_client
from trove_tempest_plugin.services.database.json import datastores_client
from trove_tempest_plugin.services.database.json import flavors_client
from trove_tempest_plugin.services.database.json import instances_client
from trove_tempest_plugin.services.database.json import limits_client
from trove_tempest_plugin.services.database.json import versions_client

CONF = config.CONF


class BaseDatabaseTest(tempest.test.BaseTestCase):
    """Base test case class for all Database API tests."""

    credentials = ['primary']

    @classmethod
    def skip_checks(cls):
        super(BaseDatabaseTest, cls).skip_checks()
        if not CONF.service_available.trove:
            skip_msg = ("%s skipped as trove is not available" % cls.__name__)
            raise cls.skipException(skip_msg)

    @classmethod
    def setup_clients(cls):
        super(BaseDatabaseTest, cls).setup_clients()
        default_params = config.service_client_config()

        # NOTE: Tempest uses timeout values of compute API if project specific
        # timeout values don't exist.
        default_params_with_timeout_values = {
            'build_interval': CONF.compute.build_interval,
            'build_timeout': CONF.compute.build_timeout
        }
        default_params_with_timeout_values.update(default_params)
        cls.database_flavors_client = flavors_client.DatabaseFlavorsClient(
            cls.os_primary.auth_provider,
            CONF.database.catalog_type,
            CONF.identity.region,
            **default_params_with_timeout_values)
        cls.os_flavors_client = cls.os_primary.flavors_client
        cls.database_limits_client = limits_client.DatabaseLimitsClient(
            cls.os_primary.auth_provider,
            CONF.database.catalog_type,
            CONF.identity.region,
            **default_params_with_timeout_values)
        cls.database_versions_client = versions_client.DatabaseVersionsClient(
            cls.os_primary.auth_provider,
            CONF.database.catalog_type,
            CONF.identity.region,
            **default_params_with_timeout_values)
        cls.database_datastores_client =\
            datastores_client.DatabaseDatastoresClient(
                cls.os_primary.auth_provider,
                CONF.database.catalog_type,
                CONF.identity.region,
                **default_params_with_timeout_values)
        cls.database_instances_client =\
            instances_client.DatabaseInstancesClient(
                cls.os_primary.auth_provider,
                CONF.database.catalog_type,
                CONF.identity.region,
                **default_params_with_timeout_values)
        cls.database_backups_client =\
            backups_client.DatabaseBackupsClient(
                cls.os_primary.auth_provider,
                CONF.database.catalog_type,
                CONF.identity.region,
                **default_params_with_timeout_values)

    @classmethod
    def resource_setup(cls):
        super(BaseDatabaseTest, cls).resource_setup()

        cls.catalog_type = CONF.database.catalog_type
        cls.db_flavor_ref = CONF.database.db_flavor_ref
        cls.db_current_version = CONF.database.db_current_version
        cls.datastore_type = CONF.database.datastore_type
        cls.availability_zone = CONF.database.availability_zone
        cls.volume_size = CONF.database.volume_size
        cls.dns_name_server = CONF.database.dns_name_server

    @classmethod
    def create_test_instance(cls, backup_id=None):
        """Wrapper utility that returns a test serinstancever.

        This wrapper utility calls the common create test instance and
        returns a test instance. The purpose of this wrapper is to minimize
        the impact on the code of the tests already using this
        function.

        :param validatable: Whether the server will connectable via db protocol
        :param validation_resources: Dictionary of validation resources as
            returned by `get_class_validation_resources`.
        :param kwargs: Extra arguments are passed down to the
            `create_test_instance` call.
        """
        name = data_utils.rand_name(cls.__name__ + "-instance")
        instance_dict = {
            "users": [],
            "availability_zone": CONF.database.availability_zone,
            "flavorRef": CONF.database.db_flavor_ref,
            "volume": {"size": CONF.database.volume_size},
            "databases": [],
            "datastore": {"type": CONF.database.datastore_type},
            "name": name
        }
        if backup_id:
            instance_dict["restorePoint"] = {"backupRef": backup_id}

        post_body = json.dumps({'instance': instance_dict})
        instance = cls.client.create_db_instance(post_body)['instance']

        waiters.wait_for_db_instance_status(cls.client, instance['id'],
                                            'ACTIVE')

        # For each instance schedule wait and delete, so we first delete all
        # and then wait for all
        cls.addClassResourceCleanup(
            waiters.wait_for_db_instance_decommission,
            cls.database_instances_client, instance['id'])

        cls.addClassResourceCleanup(
            test_utils.call_and_ignore_notfound_exc,
            cls.database_instances_client.delete_db_instance, instance['id'])

        return instance
