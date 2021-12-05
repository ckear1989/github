"""
Test pandas DataFrame object of GitHubHealth class.
"""

import os

import pytest

from GitHubHealth import (
    GitHubHealth,
    ACCESS_TOKEN_VAR_NAME,
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
    assert "private" in ghh.requested_object.repo_df.columns
    assert "branch_count" in ghh.requested_object.repo_df.columns
    assert "max_branch_age_days" in ghh.requested_object.repo_df.columns
    assert "primary_language" in ghh.requested_object.repo_df.columns
    assert "issues" in ghh.requested_object.repo_df.columns
    assert "pull_requests" in ghh.requested_object.repo_df.columns


def test_metadata_df_columns(ghh):
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh.user.get_metadata_df()
    assert "resource" in ghh.user.metadata_df.columns
    assert "name" in ghh.user.metadata_df.columns
    assert "url" in ghh.user.metadata_df.columns
    assert "health" in ghh.user.metadata_df.columns


def test_search_df_columns(ghh):
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    search_results = SearchResults(ghh, "ckear1989")
    search_results.search()
    assert "resource" in search_results.table_df.columns
    assert "name" in search_results.table_df.columns
    assert "url" in search_results.table_df.columns
    assert "health" in search_results.table_df.columns
