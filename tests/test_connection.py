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
