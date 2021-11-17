"""
Test getting repo functions.
"""
import os

from GitHubHealth import GitHubHealth
from GitHubHealth.main import ACCESS_TOKEN_VAR_NAME


# pylint: disable=invalid-sequence-index
def test_get_repos():
    """
    Default get repos.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_repos(user="ckear1989")
    assert "github" in [repo.name for repo in ghh.repos["user"]]


def test_ignore_repos():
    """
    Get repos with ignore option.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_repos(user="ckear1989", ignore_repos=["github"])
    assert "github" not in [repo.name for repo in ghh.repos["user"]]
