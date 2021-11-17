"""
Test pandas DataFrame object of GitHubHealth class.
"""

import os

from GitHubHealth import (
    GitHubHealth,
    ACCESS_TOKEN_VAR_NAME,
)


def test_df_columns():
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_repos(user="ckear1989")
    ghh.get_repo_dfs()
    assert "private" in ghh.repo_dfs["user"].columns
    assert "branch_count" in ghh.repo_dfs["user"].columns
    assert "max_branch_age_days" in ghh.repo_dfs["user"].columns
    assert "primary_language" in ghh.repo_dfs["user"].columns
