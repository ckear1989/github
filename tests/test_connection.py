"""
Test connection functionality.
"""

import pytest

from github.GithubException import BadCredentialsException

from GitHubHealth.main import get_connection


def test_get_connection(connection_with_token):
    """
    Test that connection object can be obtained.
    """
    assert connection_with_token[0] is not None


def test_invalid_gat():
    """
    Test that trying an incorrect gat still gets a connection but warns user.
    """
    with pytest.raises(BadCredentialsException):
        assert get_connection(gat="invalid-access-token") is not None
