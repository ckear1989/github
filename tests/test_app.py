"""
Test functions for app object.
"""

import os
import tempfile

import flask
import pkg_resources
import pytest

from GitHubHealth.app import app

# pylint: disable=redefined-outer-name


@pytest.fixture
def client():
    """
    Flask client for testing.
    """
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            # no db yet
            # app.init_db()
            pass
        yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])


def test_app_creation():
    """
    App can be created from importing module.
    """
    assert isinstance(app, flask.app.Flask)


def test_run_app(client):
    """
    Test that app can be run.
    """
    with open(
        pkg_resources.resource_filename("GitHubHealth", "templates/base.html"), "rb"
    ) as index_f:
        base_html_head = index_f.read()[:10]
    expected_content = client.get("/")
    assert expected_content.data[:10] == base_html_head
