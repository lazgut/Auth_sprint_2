import uuid
from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


async def test_roles_read(make_request, role_fixture):
    response = await make_request('get')('roles')
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert response.body[0]['id'] == role_fixture['id']


async def test_role_update_idchange(make_request, role_fixture):
    """Don't allow to change role id. Try to change role id with zero id."""
    put_resp = await make_request('put')(
        'roles/{0}'.format(role_fixture['id']),
        {**role_fixture, 'id': str(uuid.UUID(int=0))},
    )
    assert put_resp.status == HTTPStatus.BAD_REQUEST


async def test_role_update(make_request, role_fixture):
    updated_value = 'new_test_client_id'
    put_resp = await make_request('put')(
        'roles/{0}'.format(role_fixture['id']),
        {**role_fixture, 'client_service_id': updated_value},
    )
    assert put_resp.status == HTTPStatus.NO_CONTENT

    # ensure the db data was updated
    get_resp = await make_request('get')('roles/{0}'.format(role_fixture['id']))
    assert get_resp.status == HTTPStatus.OK
    assert get_resp.body['client_service_id'] == updated_value
