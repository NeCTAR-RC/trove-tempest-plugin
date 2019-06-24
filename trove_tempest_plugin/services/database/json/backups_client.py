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


class DatabaseBackupsClient(rest_client.RestClient):

    def list_backups(self, params=None):
        """List all available backups."""
        url = 'backups'
        if params:
            url += '?%s' % urllib.urlencode(params)
        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def create_backup(self, instance_id, name, description=None, parent=None,
                      incremental=False):
        """Create a backup."""
        url = 'backups'
        data = {'instance': instance_id,
                'name': name,
                'incremental': int(incremental)}
        post_body = json.dumps({"backup": data})
        resp, body = self.post(url, body=post_body)
        self.expected_success(202, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def delete_backup(self, backup_id):
        """Delete the backup"""
        url = 'backups/%s' % backup_id
        resp, body = self.delete(url)
        self.expected_success(202, resp.status)
        return rest_client.ResponseBody(resp, body)

    def show_backup(self, backup_id):
        """Show backups."""
        url = 'backups/%s' % backup_id
        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)
