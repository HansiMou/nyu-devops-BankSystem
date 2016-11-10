from behave import *
import server
import json

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

@given(u'the server is started')
def step_impl(context):
    context.app = server.app.test_client()
    context.server = server
    server.connect_to_redis()

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@when(u'I post a new account to \'{url}\'')
def step_impl(context, url):
    new_account = {'name': context.table[0]['name'], 'balance': context.table[0]['balance'], 'active': context.table[0]['active']}
    context.resp = context.app.post(url, data=json.dumps(new_account), content_type='application/json')

@then(u'I should see \'{name}\' with balance \'{balance}\' and active: \'{active}\'')
def step_impl(context, name, balance, active):
    new_json = json.loads(context.resp.data)
    # check the return message and return code
    assert context.resp.status_code == HTTP_201_CREATED
    assert new_json['name'] == name
    assert new_json['balance'] == balance
    assert new_json['active'] == active

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data

# Need to fix
@given(u'the following accounts')
def step_impl(context):
    accounts = {}
    for row in context.table:
        accounts[row['id']] = {'id': row['id'], 'name': row['name'], 'balance': row['balance'], 'active': row['active']}
    context.server.accounts = accounts

@when(u'I visit \'{url}\'')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200

@then(u'I should see \'{id}\'')
def step_impl(context, id):
    assert id in context.resp.data

@when(u'I search for \'{name}\'')
def step_impl(context, name):
    context.resp = context.app.get('/accounts?name=%s' % name)
    assert context.resp.status_code == 200
    for data in json.loads(context.resp.data):
        assert data['name'] == name


