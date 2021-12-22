"""
Config for tests.
"""

import logging
import os

import pytest

from GitHubHealth import (
    app,
    GitHubHealth,
    ACCESS_TOKEN_VAR_NAME,
)
from GitHubHealth.main import get_connection

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


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
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    rate_limit = ghh.con.get_rate_limit()
    logger.info("rate limit core: %s", rate_limit.raw_data["core"])
    logger.info("rate limit search: %s", rate_limit.raw_data["search"])
    logger.info("rate limit graphql: %s", rate_limit.raw_data["graphql"])
    logger.info(
        "rate limit integration_manifest: %s",
        rate_limit.raw_data["integration_manifest"],
    )
    logger.info("rate limit source_import: %s", rate_limit.raw_data["source_import"])
    logger.info(
        "rate limit code_scanning_upload: %s",
        rate_limit.raw_data["code_scanning_upload"],
    )
    logger.info(
        "rate limit actions_runner_registration: %s",
        rate_limit.raw_data["actions_runner_registration"],
    )
    logger.info("rate limit scim: %s", rate_limit.raw_data["scim"])
    return ghh


@pytest.fixture(name="ghh_2_search_results")
def fixture_ghh_2_search_results(ghh):
    """
    reusable ghh object with pre-populated search results.
    """
    ghh.search("pyGitHub", users=True, input_from=1, input_to=2)
    return ghh


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
