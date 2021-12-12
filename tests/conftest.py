"""
Config for tests.
"""

import os

import pytest

from GitHubHealth import (
    app,
    GitHubHealth,
    ACCESS_TOKEN_VAR_NAME,
)
from GitHubHealth.main import get_connection


@pytest.fixture(name="app")
def fixture_app():
    """
    reusable app object.
    """
    return app


@pytest.fixture(name="ghh")
def fixture_ghh():
    """
    reusable ghh object.
    """
    return GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])


@pytest.fixture(name="client")
def fixture_client():
    """
    Flask client for testing.
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            # no db yet
            # app.init_db()
            pass
        yield client


@pytest.fixture(name="connection_with_token")
def fixture_connection_with_token():
    """
    Set these fixtures up front so we can test both connections with and without token.
    """
    assert ACCESS_TOKEN_VAR_NAME in os.environ
    return get_connection(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
