"""
Test metadata for requested object.
"""

import pytest

from GitHubHealth.requested_object import Metadata


def test_create_class_object(ghh):
    """
    create class object from ghh user.
    """
    Metadata(ghh.user)


def test_get_metadata_default(ghh):
    """
    create class object from ghh user.
    """
    metadata = Metadata(ghh.user)
    metadata.get_metadata()
    assert len(metadata.metadata_df) <= 10


def test_get_metadata_increased_limit(ghh):
    """
    create class object from ghh user.
    """
    metadata = Metadata(ghh.user, input_to=12)
    metadata.get_metadata()
    assert len(metadata.metadata_df) <= 12


def test_get_metadata_decreased_limit(ghh):
    """
    create class object from ghh user.
    """
    metadata = Metadata(ghh.user, input_to=8)
    metadata.get_metadata()
    assert len(metadata.metadata_df) <= 8


def test_change_metadata_limit(ghh):
    """
    create class object from ghh user.
    """
    metadata = Metadata(ghh.user)
    assert metadata.input_from == 1
    assert metadata.input_to == 10
    with pytest.raises(ValueError):
        metadata.set_input_limits(10, 1)
    metadata.set_input_limits(2, 10)
    assert metadata.input_from == 2
    assert metadata.input_to == 10
