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
    ghh.get_requested_object("ckear1989")
    ghh.requested_object.get_repos()
    assert "github" in [repo.name for repo in ghh.requested_object.repos]


def test_ignore():
    """
    Get repos with ignore option.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_requested_object("ckear1989")
    ghh.requested_object.get_repos(ignore="github")
    assert "github" not in [repo.name for repo in ghh.requested_object.repos]


def test_get_org_repos():
    """
    Test get repos from known org.
    PyGitHub org has a repo called PyGithub
    (note the lowercase "h")
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
    ghh.get_requested_object("PyGitHub")
    ghh.requested_object.get_repos()
    assert "PyGithub" in [repo.name for repo in ghh.requested_object.repos]


def test_results_limit():
    """
    Test get repos from known user with limiting of results.
    """
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME], results_limit=2)
    ghh.user.get_metadata()
    assert len(ghh.user.metadata.metadata_df) <= 2
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME], results_limit=4)
    ghh.user.get_metadata()
    assert len(ghh.user.metadata.metadata_df) <= 4
    ghh = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME], results_limit=10)
    ghh.user.get_metadata()
    assert len(ghh.user.metadata.metadata_df) <= 10
