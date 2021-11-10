"""
Test pandas DataFrame object of GitHubHealth class.
"""


from GitHubHealth.main import GitHubHealth


def test_df_columns():
    """
    Get a GithubHealth instance and check that expected columns are in DataFrame.
    """
    ghh = GitHubHealth()
    assert "private" in ghh.repo_df.columns
    assert "branch_count" in ghh.repo_df.columns
    assert "max_branch_age_days" in ghh.repo_df.columns
    assert "primary_language" in ghh.repo_df.columns
