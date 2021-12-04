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
    ghh.get_repos(search_request="ckear1989", users=True)
    assert "github" in [repo.name for repo in ghh.repos["users"]]


def test_ignore_repos():
    """
    Get repos with ignore option.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_repos(search_request="ckear1989", users=True, ignore_repos="github")
    assert "github" not in [repo.name for repo in ghh.repos["users"]]


def test_get_org_repos():
    """
    Test get repos from known org.
    PyGitHub org has a repo called PyGithub
    (note the lowercase "h")
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_repos(search_request="PyGitHub", orgs=True)
    assert "PyGithub" in [repo.name for repo in ghh.repos["orgs"]]


def test_results_limit():
    """
    Test get repos from known user with limiting of results.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME], results_limit=2)
    ghh.get_repos(search_request="ckear1989", users=True)
    ghh.user.get_metadata_df()
    assert len(ghh.user.metadata_df) <= 2
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME], results_limit=4)
    ghh.get_repos(search_request="ckear1989", users=True)
    ghh.user.get_metadata_df()
    assert len(ghh.user.metadata_df) <= 4
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME], results_limit=10)
    ghh.get_repos(search_request="ckear1989", users=True)
    ghh.user.get_metadata_df()
    assert len(ghh.user.metadata_df) <= 10
