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

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib
from tempest.lib.common import rest_client
from tempest.lib import exceptions as lib_exc

import re
import time


class DatabaseInstancesClient(rest_client.RestClient):

    def list_db_instances(self, params=None):
        """List all available instances."""
        url = 'instances'
        if params:
            url += '?%s' % urllib.urlencode(params)
        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def create_db_instance(self, params):
        """Create an instance."""
        url = 'instances'
        headers = self.get_headers()
        resp, body = self.post(url, headers=headers, body=params)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def show_db_instance(self, instance_id):
        """Show the db instance"""
        url = 'instances/%s' % instance_id
        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def delete_db_instance(self, instance_id):
        """Delete the db instance"""
        url = 'instances/%s' % instance_id
        resp, body = self.delete(url)
        self.expected_success(202, resp.status)
        return rest_client.ResponseBody(resp, body)

    def wait_for_db_instance_status(self, instance_id, status,
                                    failure_pattern='^.*_ERROR$'):
        """Wait for a db instance to reach a given status"""
        start = int(time.time())
        fail_regexp = re.compile(failure_pattern)

        while True:
            try:
                body = self.show_db_instance(instance_id)['instance']
            except lib_exc.NotFound:
                if status == 'DELETE_COMPLETE':
                    return
            instance_name = body['name']
            instance_status = body['status']
            if instance_status == status:
                return body
            if fail_regexp.search(instance_status):
                raise KeyError
            if int(time.time()) - start >= self.build_timeout:
                message = ('DB Instance %s failed to reach %s status'
                           '(current: %s) within the required time (%s s).' %
                           (instance_name, status, instance_status,
                            self.build_timeout))
                raise lib_exc.TimeoutException(message)

            time.sleep(self.build_interval)

    def wait_for_db_instance_decommission(self, instance_id):
        """Wait for a db instance decomission"""
        start = int(time.time())
        while True:
            try:
                self.show_db_instance(instance_id)['instance']
            except lib_exc.NotFound:
                return
            if int(time.time()) - start >= self.build_timeout:
                message = ('DB Instance %s deletion failed '
                           'within the required time (%s s).' %
                           (instance_id, self.build_timeout))
                raise lib_exc.TimeoutException(message)

            time.sleep(self.build_interval)
