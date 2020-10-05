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

    def update_db_instance(self, instance_id, **kwargs):
        """Updates the db instance"""
        url = 'instances/%s' % instance_id
        post_body = json.dumps({'instance': kwargs})
        resp, body = self.patch(url, post_body)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def action(self, instance_id, action_name, **kwargs):
        post_body = json.dumps({action_name: kwargs})
        resp, body = self.post('instances/%s/action' % instance_id,
                               post_body)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def restart_db_instance(self, instance_id):
        """Restart the db instance"""
        return self.action(instance_id, "restart")

    def upgrade_db_instance(self, instance_id, datastore_version):
        body = json.dumps({"instance": {
            "datastore_version": datastore_version}})
        resp, body = self.patch('instances/%s' % instance_id,
                                body)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def delete_db_instance(self, instance_id):
        """Delete the db instance"""
        url = 'instances/%s' % instance_id
        resp, body = self.delete(url)
        self.expected_success(202, resp.status)
        return rest_client.ResponseBody(resp, body)

    def list_databases(self, instance_id):
        """List all databases on an instance."""
        resp, body = self.get('instances/%s/databases' % instance_id)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def create_database(self, instance_id, name):
        """Creates a database on an instance"""
        post_body = json.dumps({"databases": [{"name": name}]})
        resp, body = self.post('instances/%s/databases' % instance_id,
                               post_body)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def delete_database(self, instance_id, name):
        """Deletes a database on an instance"""
        resp, body = self.delete('instances/%s/databases/%s' % (instance_id,
                                                                name))
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def root_show(self, instance_id):
        """Shows if root has ever been enabled on an instance"""
        url = 'instances/%s/root' % instance_id
        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def root_enable(self, instance_id):
        """Enables root on an instance"""
        url = 'instances/%s/root' % instance_id
        resp, body = self.post(url, body=json.dumps({}))
        self.expected_success(200, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def root_disable(self, instance_id):
        """Disables root on an instance"""
        url = 'instances/%s/root' % instance_id
        resp, body = self.delete(url)
        self.expected_success(204, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def list_users(self, instance_id):
        """List all users on an instance."""
        resp, body = self.get('instances/%s/users' % instance_id)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def show_user(self, instance_id, name):
        """Get a user on an instance."""
        resp, body = self.get('instances/%s/users/%s' % (instance_id, name))
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def create_user(self, instance_id, name, password, databases=[]):
        """Creates a user on an instance"""
        post_body = json.dumps({"users": [{"name": name,
                                           "password": password,
                                           "databases": databases}]})
        resp, body = self.post('instances/%s/users' % instance_id,
                               post_body)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def update_user(self, instance_id, name, **kwargs):
        """Updates the user"""
        url = 'instances/%s/users/%s' % (instance_id, name)
        post_body = json.dumps({'user': kwargs})
        resp, body = self.put(url, post_body)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def delete_user(self, instance_id, name):
        """Updates the user"""
        url = 'instances/%s/users/%s' % (instance_id, name)
        resp, body = self.delete(url)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def grant_user_access(self, instance_id, name, databases):
        """Grants a user access to a database"""
        url = 'instances/%s/users/%s/databases' % (instance_id, name)
        databases = [{'name': x} for x in databases]
        post_body = json.dumps({'databases': databases})
        resp, body = self.put(url, post_body)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def revoke_user_access(self, instance_id, name, database):
        """Revokes a user access to a database"""
        url = 'instances/%s/users/%s/databases/%s' % (instance_id, name,
                                                      database)
        resp, body = self.delete(url)
        self.expected_success(202, resp.status)
        if body:
            body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def show_user_access(self, instance_id, name):
        """Shows access details of a user of an instanceqq"""
        url = 'instances/%s/users/%s/databases' % (instance_id, name)
        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def list_backups(self, instance_id):
        """List all backups on an instance."""
        resp, body = self.get('instances/%s/backups' % instance_id)
        self.expected_success(200, resp.status)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)
