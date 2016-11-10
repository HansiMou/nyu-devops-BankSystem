# run with:
# python -m unittest discover

import unittest
import json
import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestBankServer(unittest.TestCase):
    idRef = -1
    # contains one account
    def setUp(self):
        server.app.debug = True
        self.app = server.app.test_client()
        server.connect_to_redis()
        new_account = {'name': 'Gina', 'balance': 1000, 'active': 0}
        data = json.dumps(new_account)
        resp = self.app.post('/accounts', data=data, content_type='application/json')
        self.idRef = json.loads(resp.data)['id']

    def test_index(self):
        resp = self.app.get('/')
        self.assertTrue('Banking System REST API Service' in resp.data)
        self.assertTrue(resp.status_code == HTTP_200_OK)

    def test_create_account_successfully(self):
        new_account = {'name': 'john', 'balance': 100, 'active': 1}
        data = json.dumps(new_account)
        resp = self.app.post('/accounts', data=data, content_type='application/json')
        new_json = json.loads(resp.data)
        # check the return message and return code
        self.assertTrue(resp.status_code == HTTP_201_CREATED )
        self.assertTrue(new_json['name'] == 'john')
        self.assertTrue(new_json['balance'] == '100')
        self.assertTrue(new_json['active'] == '1')

        # check that id has gone up and includes john
        resp = self.app.get('/accounts/%s' %new_json['id'])
        data = json.loads(resp.data)
        self.assertTrue(resp.status_code == HTTP_200_OK)
        self.assertTrue(new_json == data)

    def test_create_account_missing_attributes(self):
        new_account = {'name': 'john', 'balance': 100}
        data = json.dumps(new_account)
        resp = self.app.post('/accounts', data=data, content_type='application/json')
        # check the return message and return code
        self.assertTrue(resp.status_code == HTTP_400_BAD_REQUEST)

    def test_get_account_list(self):
        resp = self.app.get('/accounts')
        #print 'resp_data: ' + resp.data
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue( len(data) ==  self.get_account_count())
        self.assertFalse( 'nextId' in resp.data)

    def test_get_account_list_with_existing_name(self):
        resp = self.app.get('/accounts?name=Gina')
        #print 'resp_data: ' + resp.data
        self.assertTrue( resp.status_code == HTTP_200_OK )
        for data in json.loads(resp.data):
            self.assertTrue (data['name'] == 'Gina')
        self.assertFalse( 'nextId' in resp.data)

    def test_get_account_list_with_nonexisting_name(self):
        resp = self.app.get('/accounts?name=Xi')
        #print 'resp_data: ' + resp.data
        self.assertTrue(resp.status_code == HTTP_404_NOT_FOUND)

    def test_get_account_list_with_empty_name(self):
        resp = self.app.get('/accounts?name=')
        #print 'resp_data: ' + resp.data
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue( len(data) ==  self.get_account_count())
        self.assertFalse( 'nextId' in resp.data)

######################################################################
# Utility functions
######################################################################

    def get_account_count(self):
        # save the current number of accounts
        resp = self.app.get('/accounts')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        # print 'resp_data: ' + resp.data
        data = json.loads(resp.data)
        return len(data)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
