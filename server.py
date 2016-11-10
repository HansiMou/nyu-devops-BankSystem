# Copyright 2016 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import redis
from flask import Flask, Response, jsonify, request, json

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_403_ACCESS_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return jsonify(name='Banking System REST API Service', version='1.0', url='/accounts'), HTTP_200_OK

######################################################################
# LIST ALL ACCOUNTS WITHOUT A CERTAIN NAME :/accounts
# LIST ALL ACCOUNTS WITH A CERTAIN NAME: /accounts?name=john
######################################################################
@app.route('/accounts', methods=['GET'])
def list_accounts():
    name = request.args.get('name')
    if name:
        message = []
        for key in redis_server.keys():
            account = redis_server.hgetall(key)
            if account.has_key('name'):
                if account.get('name')==name:
                    message.append(account)
                    rc = HTTP_200_OK
        if not message:
            message = { 'error' : 'Account under name: %s is not found' % name }
            rc = HTTP_404_NOT_FOUND
    else :
        message = []
        rc = HTTP_200_OK
        for key in redis_server.keys():
            if (key == 'nextId'):
                continue
            account = redis_server.hgetall(key)
            message.append(account)
    return reply(message, rc)

######################################################################
# RETRIEVE AN ACCOUNT WITH ID
######################################################################
@app.route('/accounts/<id>', methods=['GET'])
def get_account_by_id(id):
    message = []
    if id == 'nextId':
        message = {'error' : 'Account id: %s is not found' % id }
        rc = HTTP_404_NOT_FOUND
    elif redis_server.exists(id):
        message = redis_server.hgetall(id)
        rc = HTTP_200_OK
    if not message:
        message = { 'error' : 'Account id: %s is not found' % id }
        rc = HTTP_404_NOT_FOUND
    return reply(message, rc)

######################################################################
# DEACTIVATE AN ACCOUNT WITH ID
######################################################################
# the link used to be /accounts/<id>/deactive, which should be /accounts/<id>/deactivate
# /accounts/<id>/deactive is still used in the bluemix link
# It will be corrected in the hw2
@app.route('/accounts/<id>/deactivate', methods=['PUT'])
def deactivate_account_by_id(id):
    message = []
    for account in redis_server.keys():
        if account == id:
            redis_server.hset(id, 'active', 0)
            message = redis_server.hgetall(account)
            rc = HTTP_200_OK

    if not message:
        message = { 'error' : 'Account id: %s is not found' % id }
        rc = HTTP_404_NOT_FOUND
    return reply(message, rc)

######################################################################
# CREATE AN ACCOUNT
######################################################################
@app.route('/accounts', methods=['POST'])
def create_account():
    payload = json.loads(request.data)
    missing_params = find_missing_params(payload)
    if not missing_params:
        id = redis_server.hget('nextId', 'nextId')
        redis_server.hset('nextId','nextId',int(id) + 1)
        redis_server.hset(id, 'id', id)

        redis_server.hset(id, 'name',  payload['name'])
        redis_server.hset(id, 'balance', payload['balance'])
        redis_server.hset(id, 'active', payload['active'])

        message = redis_server.hgetall(id)
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Missing %s' % missing_params }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route('/accounts/<id>', methods=['PUT'])
def update_account(id):
    payload = json.loads(request.data)
    if id == 'nextId':
        message = {'error' : 'Account %s is not found' % id}
        rc = HTTP_404_NOT_FOUND
    elif find_missing_params(payload):
        message = { 'error' : 'Missing %s' % find_missing_params(payload) }
        rc = HTTP_400_BAD_REQUEST
    elif redis_server.exists(id):
        redis_server.hset(id, 'name', payload['name'])
        redis_server.hset(id, 'active', payload['active'])
        redis_server.hset(id, 'balance', payload['balance'])
        message = redis_server.hgetall(id)
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Account id: %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route('/accounts/<id>', methods=['DELETE'])
def delete_account(id):
    if (id == 'nextId'):
        message = {'error' : 'Account id: %s was not found' % id }
        rc = HTTP_404_NOT_FOUND
        return reply(message, rc)
    if redis_server.exists(id):
        redis_server.delete(id)

    return '', HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

# NEED THREE FIELDS TO BE NOT NULL: name, balance, active
def find_missing_params(data):
    missing_params = []
    if not data.has_key('active'):
        missing_params.append('active')
    if not data.has_key('balance'):
        missing_params.append('balance')
    if not data.has_key('name'):
        missing_params.append('name')
    return missing_params

def connect_to_redis():
    # Get the crdentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        VCAP_SERVICES = os.environ['VCAP_SERVICES']
        services = json.loads(VCAP_SERVICES)
        redis_creds = services['rediscloud'][0]['credentials']
        # pull out the fields we need
        redis_hostname = redis_creds['hostname']
        redis_port = int(redis_creds['port'])
        redis_password = redis_creds['password']
    else:
    #     response = os.system("ping -c 1 redis")
    # if response == 0:
    #     redis_hostname = 'redis'
    # else:
        redis_hostname = '127.0.0.1'
        redis_port = 6379
        redis_password = None

    init_redis(redis_hostname, redis_port, redis_password)

# Initialize Redis
def init_redis(hostname, port, password):
    # Connect to Redis Server
    global redis_server
    redis_server = redis.Redis(host=hostname, port=port, password=password)
    try:
        response = redis_server.client_list()
    except redis.ConnectionError:
        # if you end up here, redis instance is down.
        print '*** FATAL ERROR: Could not conect to the Redis Service'
    if not redis_server.exists('nextId'):
        redis_server.hset('nextId','nextId',len(redis_server.keys()) + 1)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    connect_to_redis()
    # redis_server.flushdb()
    # Get bindings from the environment
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=True)
