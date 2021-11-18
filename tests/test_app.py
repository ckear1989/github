"""
Test functions for app object.
"""

import unittest

import flask
import pytest

from GitHubHealth import app

# pylint: disable=redefined-outer-name


@pytest.fixture
def client():
    """
    Flask client for testing.
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            # no db yet
            # app.init_db()
            pass
        yield client


def test_app_creation():
    """
    App can be created from importing module.
    """
    assert isinstance(app, flask.app.Flask)


class MyAppTestCase(unittest.TestCase):
    """
    Class for testing app routing and functionality.
    """

    def setUp(self):
        """
        get test client for app.
        """
        self.app = app.test_client()

    def test_greeting(self):
        """
        Header of index.
        """
        ret_val = self.app.get("/")
        assert ret_val.data[:15] == b"<!DOCTYPE html>"
