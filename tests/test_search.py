"""
Test search functionality of ghh object.
There is an issue with this module.
The api only allows 30 searches per hour and this suite hits that limit.
So the solution is to somehow extend that limit, or (for now) comment out
some tests :(
"""

import pytest


def test_invalid_search(ghh):
    """
    Test searching for known repo.
    """
    with pytest.raises(ValueError):
        # results from, to should be 1 indexed
        ghh.search("pyGitHub", orgs=True, input_from=0, input_to=0)
    with pytest.raises(ValueError):
        # results to should be >= input_from
        ghh.search("pyGitHub", orgs=True, input_from=2, input_to=1)
    with pytest.raises(ValueError):
        # results should be >0
        ghh.search("pyGitHub", users=True, input_from=-10, input_to=-9)


def test_search_default_result(ghh):
    """
    Test searching for known repo.
    """
    ghh.search("pyGitHub", users=True)


def test_search_1_result(ghh):
    """
    Test searching for known repo.
    """
    # got to break and then fix this
    ghh.search("pyGitHub", users=True, input_from=1, input_to=1)
    assert len(ghh.search_results.table_df) == 1


def test_search_2_result(ghh_2_search_results):
    """
    Test searching for known repo.
    """
    assert len(ghh_2_search_results.search_results.table_df) == 2


def test_search_update_result(ghh_2_search_results):
    """
    Test searching for known repo.
    """
    assert len(ghh_2_search_results.search_results.table_df) == 2
    ghh_2_search_results.search_results.set_input_limits(1, 4)
    ghh_2_search_results.search_results.get_output_results()
    assert len(ghh_2_search_results.search_results.table_df) == 4


def test_search_update_error_result(ghh_2_search_results):
    """
    Test searching for known repo.
    """
    assert len(ghh_2_search_results.search_results.table_df) == 2
    with pytest.raises(ValueError):
        ghh_2_search_results.search_results.set_input_limits(4, 1)


def test_search_too_many_results(ghh):
    """
    Test searching for known repo.
    """
    with pytest.warns(UserWarning):
        ghh.search("pyGitHub", users=True, input_from=1, input_to=52)


# def test_search_result_out_of_range(ghh):
#     """
#     Test searching for known repo.
#     """
#     with pytest.warns(UserWarning):
#         ghh.search("pyGitHub", users=True, input_from=1001, input_to=1002)
