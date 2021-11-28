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
    ghh.get_repos(search_request="ckear1989", users=True)
    ghh.get_repo_dfs()
    assert "private" in ghh.repo_dfs["users"].columns
    assert "branch_count" in ghh.repo_dfs["users"].columns
    assert "max_branch_age_days" in ghh.repo_dfs["users"].columns
    assert "primary_language" in ghh.repo_dfs["users"].columns


def test_metadata_df_columns():
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.user.get_metadata_df()
    assert "resource" in ghh.user.metadata_df.columns
    assert "name" in ghh.user.metadata_df.columns
    assert "url" in ghh.user.metadata_df.columns
