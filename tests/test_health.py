"""
Test calculation of health metrics.
"""

import logging

from GitHubHealth.utils import (
    get_health,
    get_repo_details,
)


def test_perfect_repo_health(test_perfect_repo):
    """
    test the health of known repo.
    """
    repo_health = get_health(test_perfect_repo)
    assert repo_health == 10.0


def test_bad_repo_health(test_bad_repo):
    """
    test the health of known repo.
    """
    repo_health = get_health(test_bad_repo)
    assert repo_health == 0.0


def test_median_repo_health(test_median_repo):
    """
    test the health of known repo.
    """
    repo_health = get_health(test_median_repo)
    assert repo_health == 5.0


def test_perfect_user_health(test_perfect_user):
    """
    test the health of known user.
    """
    user_health = get_health(test_perfect_user)
    assert user_health == 10.0


def test_bad_user_health(test_bad_user):
    """
    test the health of known user.
    """
    user_health = get_health(test_bad_user)
    assert user_health == 0.0


def test_median_user_health(test_median_user):
    """
    test the health of known repo.
    """
    user_health = get_health(test_median_user)
    assert user_health == 5.0


def test_a_repo(ghh):
    """
    test the health of repo from ghh object.
    """
    this_repo = ghh.user.get_repo("github")
    this_repo_dict = get_repo_details(this_repo, output="dict")
    user_health = get_health(this_repo_dict)
    logging.debug("this_repo_df: %s", this_repo_dict)
    logging.debug("user_health: %s", user_health)


def test_multiple_repos(ghh):
    """
    test the health of repo from ghh object.
    """
    ghh.user.get_repo_df()
    user_health = get_health(ghh.user.repo_dict)
    logging.debug("this_repo_dict: %s", ghh.user.repo_dict)
    logging.debug("user_health: %s", user_health)
