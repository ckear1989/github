"""
Test connection functionality.
"""

import os
import pytest

from GitHubHealth.main import (
    ACCESS_TOKEN_VAR_NAME,
    get_connection,
)


# pylint: disable=redefined-outer-name
@pytest.fixture
def connection_with_token():
    """
    Set these fixtures up front so we can test both connections with and without token.
    """
    assert ACCESS_TOKEN_VAR_NAME in os.environ
    return get_connection(user="ckear1989")


@pytest.fixture
def connection_no_token():
    """
    Set these fixtures up front so we can test both connections with and without token.
    """
    if ACCESS_TOKEN_VAR_NAME in os.environ:
        gat = os.getenv(ACCESS_TOKEN_VAR_NAME)
        del os.environ[ACCESS_TOKEN_VAR_NAME]
        with pytest.warns(UserWarning):
            ret_val = get_connection(user="ckear1989")
        os.environ[ACCESS_TOKEN_VAR_NAME] = gat
    else:
        ret_val = get_connection(user="ckear1989")
    assert ret_val[0] is not None
    return ret_val


def test_get_connection(connection_with_token):
    """
    Test that connection object can be obtained.
    """
    assert connection_with_token[0] is not None


def test_get_connection_no_access_token(connection_no_token):
    """
    Test that connection object can be obtained.
    """
    assert connection_no_token is not None
    gat = os.getenv(ACCESS_TOKEN_VAR_NAME)
    del os.environ[ACCESS_TOKEN_VAR_NAME]
    with pytest.warns(UserWarning):
        assert get_connection(user="ckear1989") is not None
    os.environ[ACCESS_TOKEN_VAR_NAME] = gat
    assert get_connection() is not None


def test_get_connection_no_org(connection_with_token):
    """
    Test that no org is returned if not requested.
    Non existent org should return None with warning.
    """
    assert connection_with_token[0] is not None
    assert connection_with_token[1] is not None
    assert connection_with_token[2] is None
    with pytest.warns(UserWarning):
        github_con, user, org = get_connection(org="noorgcanbecallthisright")
    assert github_con is not None
    assert user is not None
    assert org is None
