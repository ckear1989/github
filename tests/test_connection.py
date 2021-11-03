"""
Test connection functionality.
"""

from ckear.main import get_connection


def test_get_connection():
    """
    Test that connection object can be obtained.
    """
    _ = get_connection()
