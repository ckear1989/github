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
    return get_connection(gat=os.environ[ACCESS_TOKEN_VAR_NAME])


def test_get_connection(connection_with_token):
    """
    Test that connection object can be obtained.
    """
    assert connection_with_token[0] is not None


def test_invalid_gat():
    """
    Test that trying an incorrect gat still gets a connection but warns user.
    """
    with pytest.warns(UserWarning):
        assert get_connection(gat="invalid-access-token") is not None
    assert get_connection(gat=os.environ[ACCESS_TOKEN_VAR_NAME]) is not None
