"""
Test functions for app object.
"""

import unittest

import flask

from conftest import app


# pylint: disable=redefined-outer-name
def test_app_creation(app):
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
