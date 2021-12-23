"""
Test getting repo functions.
"""


# pylint: disable=invalid-sequence-index
def test_get_repos(ghh):
    """
    Default get repos.
    """
    ghh.get_requested_object("ckear1989")
    ghh.requested_object.get_repos()
    assert "github" in [repo.name for repo in ghh.requested_object.repos]


def test_ignore(ghh):
    """
    Get repos with ignore option.
    """
    ghh.get_requested_object("ckear1989")
    ghh.requested_object.get_repos(ignore="github")
    assert "github" not in [repo.name for repo in ghh.requested_object.repos]


def test_get_org_repos(ghh):
    """
    Test get repos from known org.
    PyGitHub org has a repo called PyGithub
    (note the lowercase "h")
    """
    ghh.get_requested_object("PyGitHub")
    ghh.requested_object.get_repos()
    assert "PyGithub" in [repo.name for repo in ghh.requested_object.repos]


def test_results_limit(ghh):
    """
    Test get repos from known user with limiting of results.
    """
    ghh.user.get_metadata()
    ghh.user.metadata.set_input_limits(input_from=1, input_to=2)
    ghh.user.metadata.get_metadata()
    assert len(ghh.user.metadata.metadata_df) <= 2
    ghh.user.metadata.set_input_limits(input_from=1, input_to=4)
    ghh.user.metadata.get_metadata()
    assert len(ghh.user.metadata.metadata_df) <= 4
    ghh.user.metadata.set_input_limits(input_from=1, input_to=10)
    ghh.user.metadata.get_metadata()
    assert len(ghh.user.metadata.metadata_df) <= 10
