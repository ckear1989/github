"""
Test connection functionality.
"""

import os
import pytest

from GitHubHealth.main import (
    ACCESS_TOKEN_VAR_NAME,
    get_connection,
)


def test_get_connection():
    """
    Test that connection object can be obtained.
    """
    _ = get_connection()


def test_get_connection_no_access_token():
    """
    Test that connection object can be obtained.
    """
    gat = os.getenv(ACCESS_TOKEN_VAR_NAME)
    del os.environ[ACCESS_TOKEN_VAR_NAME]
    with pytest.warns(UserWarning):
        assert get_connection() is None
    os.environ[ACCESS_TOKEN_VAR_NAME] = gat
    assert get_connection() is not None


def test_get_connection_no_org():
    """
    Test that no org is returned if not requested.
    Non existent org should return None with warning.
    """
    github_con, user, org = get_connection()
    assert github_con is not None
    assert user.login is not None
    assert org is None
    with pytest.warns(UserWarning):
        github_con, user, org = get_connection(org="noorgcanbecallthisright")
        assert org is None
