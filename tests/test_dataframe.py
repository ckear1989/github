"""
Test pandas DataFrame object of GitHubHealth class.
"""

import os

import pytest

from GitHubHealth import (
    GitHubHealth,
    ACCESS_TOKEN_VAR_NAME,
)
from GitHubHealth.utils import (
    BRANCH_DF_COLUMNS,
    REPOS_DF_COLUMNS,
    SEARCH_DF_COLUMNS,
    get_branch_df,
)
from GitHubHealth.requested_object import SearchResults


@pytest.fixture(name="ghh")
def fixture_ghh():
    """
    reusable ghh object.
    """
    return GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])


def test_repo_df_columns(ghh):
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh.get_requested_object("ckear1989")
    ghh.requested_object.get_repos()
    ghh.requested_object.get_repo_df()
    for column in REPOS_DF_COLUMNS:
        assert column in ghh.requested_object.repo_df.columns


def test_branch_df_columns(ghh):
    """
    Get a GithubHealth instance and test repo.  Check repo details (branch) df.
    """
    ghh.get_requested_object("ckear1989")
    ghh.requested_object.get_repos()
    ghh.requested_object.get_repo_df()
    test_repo = ghh.requested_object.repos[0]
    test_repo_df = get_branch_df(test_repo)
    for column in BRANCH_DF_COLUMNS:
        assert column in test_repo_df.columns


def test_metadata_df_columns(ghh):
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh.user.get_metadata_df()
    for column in SEARCH_DF_COLUMNS:
        assert column in ghh.user.metadata_df.columns


def test_search_df_columns(ghh):
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    search_results = SearchResults(ghh, "ckear1989")
    search_results.search()
    for column in SEARCH_DF_COLUMNS:
        assert column in search_results.table_df.columns
