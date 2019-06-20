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

import re
import time

from tempest.lib import exceptions as lib_exc


def wait_for_db_instance_status(client, instance_id, status,
                                failure_pattern='^.*_ERROR$'):
    """Wait for a db instance to reach a given status"""
    start = int(time.time())
    fail_regexp = re.compile(failure_pattern)

    while True:
        try:
            body = client.show_db_instance(instance_id)['instance']
        except lib_exc.NotFound:
            if status == 'DELETE_COMPLETE':
                return
        instance_name = body['name']
        instance_status = body['status']
        if instance_status == status:
            return body
        if fail_regexp.search(instance_status):
            raise KeyError
        if int(time.time()) - start >= client.build_timeout:
            message = ('DB Instance %s failed to reach %s status'
                       '(current: %s) within the required time (%s s).' %
                       (instance_name, status, instance_status,
                        client.build_timeout))
            raise lib_exc.TimeoutException(message)

        time.sleep(client.build_interval)


def wait_for_db_instance_decommission(client, instance_id):
    """Wait for a db instance decomission"""
    start = int(time.time())
    while True:
        try:
            client.show_db_instance(instance_id)['instance']
        except lib_exc.NotFound:
            return
        if int(time.time()) - start >= client.build_timeout:
            message = ('DB Instance %s deletion failed '
                       'within the required time (%s s).' %
                       (instance_id, client.build_timeout))
            raise lib_exc.TimeoutException(message)

        time.sleep(client.build_interval)


def wait_for_backup_status(client, backup_id, status,
                           failure_pattern='^.*_ERROR$'):
    """Wait for a backup to reach a given status"""
    start = int(time.time())
    fail_regexp = re.compile(failure_pattern)

    while True:
        try:
            body = client.show_backup(backup_id)['backup']
        except lib_exc.NotFound:
            if status == 'DELETE_COMPLETE':
                return
        backup_name = body['name']
        backup_status = body['status']
        if backup_status == status:
            return body
        if fail_regexp.search(backup_status):
            raise KeyError
        if int(time.time()) - start >= client.build_timeout:
            message = ('Backup %s failed to reach %s status'
                       '(current: %s) within the required time (%s s).' %
                       (backup_name, status, backup_status,
                        client.build_timeout))
            raise lib_exc.TimeoutException(message)

        time.sleep(client.build_interval)


def wait_for_backup_delete(client, backup_id):
    """Wait for a backup to be deleted"""
    start = int(time.time())
    while True:
        try:
            client.show_backup(backup_id)['backup']
        except lib_exc.NotFound:
            return
        if int(time.time()) - start >= client.build_timeout:
            message = ('Backup %s deletion failed '
                       'within the required time (%s s).' %
                       (backup_id, client.build_timeout))
            raise lib_exc.TimeoutException(message)

        time.sleep(client.build_interval)
