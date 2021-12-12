"""
Test search functionality of ghh object
"""

import pytest


def test_invalid_search(ghh):
    """
    Test searching for known repo.
    """
    with pytest.raises(ValueError):
        # results from, to should be 1 indexed
        ghh.search("pyGitHub", orgs=True, results_from=0, results_to=0)
    with pytest.raises(ValueError):
        # results to should be >= results_from
        ghh.search("pyGitHub", orgs=True, results_from=2, results_to=1)
    with pytest.raises(ValueError):
        # results should be >0
        ghh.search("pyGitHub", users=True, results_from=-10, results_to=-9)


def test_search_default_result(ghh):
    """
    Test searching for known repo.
    """
    ghh.search("pyGitHub", users=True)
    print(ghh.search_results.table_df)


def test_search_1_result(ghh):
    """
    Test searching for known repo.
    """
    # got to break and then fix this
    ghh.search("pyGitHub", users=True, results_from=1, results_to=1)
    assert len(ghh.search_results.table_df) == 1


def test_search_2_result(ghh):
    """
    Test searching for known repo.
    """
    ghh.search("pyGitHub", users=True, results_from=1, results_to=2)
    assert len(ghh.search_results.table_df) == 2


def test_search_too_many_results(ghh):
    """
    Test searching for known repo.
    """
    with pytest.warns(UserWarning):
        ghh.search("pyGitHub", users=True, results_from=1, results_to=52)


def test_search_result_out_of_range(ghh):
    """
    Test searching for known repo.
    """
    with pytest.warns(UserWarning):
        ghh.search("pyGitHub", users=True, results_from=1000, results_to=1010)
