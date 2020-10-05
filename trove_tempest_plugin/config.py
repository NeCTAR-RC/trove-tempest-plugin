# Copyright (c) 2016 Hewlett-Packard Development Company, L.P.
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

from oslo_config import cfg

service_option = cfg.BoolOpt('trove',
                             default=True,
                             help="Whether or not Trove is expected to be "
                                  "available")

database_group = cfg.OptGroup(name='database',
                              title='Database Service Options')

DatabaseGroup = [
    cfg.StrOpt('catalog_type',
               default='database',
               help="Catalog type of the Database service."),
    cfg.StrOpt('db_flavor_ref',
               default="1",
               help="Valid primary flavor to use in database tests."),
    cfg.StrOpt('db_current_version',
               default="v1.0",
               help="Current database version to use in database tests."),
    cfg.StrOpt('datastore_type',
               default="MySQL",
               help="Type of the Database"),
    cfg.StrOpt('datastore_version',
               default=None,
               help="Specific datastore version to use (optional)"),
    cfg.StrOpt('previous_datastore_version',
               default=None,
               help="Specific datastore version to use for upgrading from"),
    cfg.StrOpt('availability_zone',
               default='nova',
               help="Availability zone of the db instance to use"),
    cfg.IntOpt('volume_size',
               default=1,
               help="Volume size for the db instances"),
    cfg.StrOpt('dns_name_server',
               default=None,
               help="The DNS server used to query trove instance domain name")
]
