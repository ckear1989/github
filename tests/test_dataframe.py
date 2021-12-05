"""
Test pandas DataFrame object of GitHubHealth class.
"""

import os

from GitHubHealth import (
    GitHubHealth,
    ACCESS_TOKEN_VAR_NAME,
)


def test_search_df_columns():
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_requested_object("ckear1989")
    ghh.requested_object.get_repos()
    ghh.requested_object.get_repo_df()
    assert "private" in ghh.requested_object.repo_df.columns
    assert "branch_count" in ghh.requested_object.repo_df.columns
    assert "max_branch_age_days" in ghh.requested_object.repo_df.columns
    assert "primary_language" in ghh.requested_object.repo_df.columns


def test_metadata_df_columns():
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.user.get_metadata_df()
    assert "resource" in ghh.user.metadata_df.columns
    assert "name" in ghh.user.metadata_df.columns
    assert "url" in ghh.user.metadata_df.columns
