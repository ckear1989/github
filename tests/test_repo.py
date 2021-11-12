"""
Test getting repo functions.
"""
from GitHubHealth import GitHubHealth


def test_get_repos():
    """
    Default get repos.
    """
    ghh = GitHubHealth()
    ghh.get_repos()
    if ghh.username == "ckear1989":
        assert "github" in [repo.name for repo in ghh.repos]


def test_ignore_repos():
    """
    Get repos with ignore option.
    """
    ghh = GitHubHealth(ignore_repos=["github"])
    ghh.get_repos()
    if ghh.username == "ckear1989":
        assert "github" not in [repo.name for repo in ghh.repos]
