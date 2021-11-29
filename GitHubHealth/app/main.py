"""
Module for flask app.
"""

import os

from flask import (
    Flask,
    flash,
    render_template,
    request,
    session,
)
from flask.logging import create_logger
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
import pkg_resources
import setuptools_scm
from requests.exceptions import (
    ReadTimeout,
    ConnectionError as RequestsConnectionError,
)

from github.GithubException import (
    UnknownObjectException,
    BadCredentialsException,
    GithubException,
)

from GitHubHealth import GitHubHealth
from GitHubHealth.app.forms import (
    LoginForm,
    SearchForm,
)

version_scm = setuptools_scm.get_version()
REQUIREMENTS = str(
    pkg_resources.resource_stream("GitHubHealth", "app/requirements.txt").read()
)
version_requirements = [
    x.strip().split("GitHubHealth==")[1]
    for x in REQUIREMENTS.split("\\n")
    if "GitHubHealth" in x
][0]
VERSION = "|".join(list(set([version_scm, version_requirements])))


def try_ghh(this_session):
    """
    Try ghh object.
    Useful for quickly verifying if credentials can be used to login.
    """
    required = ["login_user", "gat", "hostname", "timeout"]
    if all(x in this_session for x in required):
        try:
            ghh = get_ghh(
                this_session["login_user"],
                this_session["gat"],
                this_session["hostname"],
                this_session["timeout"],
            )
        except (
            BadCredentialsException,
            GithubException,
            RequestsConnectionError,
            ReadTimeout,
        ) as bce_gh_error:
            return None, bce_gh_error
        return ghh, None
    error_msg = f"please fill in {','.join([x for x in required if x not in session])}"
    return None, error_msg


def get_ghh(login_user, gat, hostname, timeout):
    """
    Get ghh object.
    Useful for quickly verifying if credentials can be used to login.
    """
    ghh = GitHubHealth(login=login_user, gat=gat, hostname=hostname, timeout=timeout)
    return ghh


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
csrf = CSRFProtect()
csrf.init_app(app)
LOG = create_logger(app)
Bootstrap(app)


@app.errorhandler(400)
def page_not_found(error_message):
    """
    Handle a 400 error.
    """
    LOG.debug("debug400: %s", error_message)
    login_form = LoginForm()
    return (
        render_template(
            "index.html",
            login_form=login_form,
            error=error_message,
        ),
        400,
    )


@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def home():
    """
    Get home page.
    """
    login_form = LoginForm()
    if "login_user" in request.form.keys():
        if request.method == "POST" and login_form.validate():
            session["login_user"] = login_form.login_user.data
            session["gat"] = login_form.gat.data
            session["hostname"] = login_form.hostname.data
            session["timeout"] = login_form.timeout.data
            ghh, error_message = try_ghh(session)
            if ghh is not None:
                return user(ghh.user.name, ghh)
            return render_template(
                "index.html",
                login_form=login_form,
                error=error_message,
            )
    if "search_request" in request.form.keys():
        if request.method == "POST":
            ghh, error_message = try_ghh(session)
            if ghh is not None:
                return user(ghh.user.name, ghh)
    if request.method == "GET":
        ghh, _ = try_ghh(session)
        if ghh is not None:
            return user(ghh.user.name, ghh)
    return render_template(
        "index.html",
        login_form=login_form,
    )


@app.route("/about", methods=["POST", "GET"])
def about():
    """
    Get about page.
    """
    ghh, _ = try_ghh(session)
    if ghh is not None:
        return render_template(
            "about.html",
            ghh=ghh,
            version=VERSION,
        )
    return render_template(
        "about.html",
        version=VERSION,
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    Get login page with form.
    """
    if "search" in request.form.keys():
        ghh, error_message = try_ghh(session)
        if ghh is not None:
            return user(ghh.user.name, ghh)
    if request.method == "GET":
        ghh, error_message = try_ghh(session)
        if ghh is not None:
            return user(ghh.user.name, ghh)
    login_form = LoginForm()
    if request.method == "POST" and login_form.validate():
        session["login_user"] = login_form.login_user.data
        session["gat"] = login_form.gat.data
        session["hostname"] = login_form.hostname.data
        session["timeout"] = login_form.timeout.data
        ghh, error_message = try_ghh(session)
        if ghh is not None:
            return user(ghh.user.name, ghh)
        return render_template(
            "index.html",
            login_form=login_form,
            error=error_message,
        )
    return render_template(
        "index.html",
        login_form=login_form,
    )


@app.route("/logout", methods=["POST", "GET"])
def logout():
    """
    Logout and return to login.
    """
    if "login_user" in session:
        del session["login_user"]
    if "gat" in session:
        del session["gat"]
    flash("logged out")
    return login()


# is this the right way of handling view routes?
# pylint: disable=unused-argument
@app.route("/user/<username>", methods=["POST", "GET"])
def user(username, ghh):
    """
    Get user page.
    """
    ghh.user.get_metadata_html()
    search_form = SearchForm()
    if request.method == "POST" and search_form.validate():
        try:
            ghh.get_repos(
                search_request=search_form.search_request.data,
                users=search_form.search_users.data,
                orgs=search_form.search_orgs.data,
                ignore_repos=search_form.search_ignore_repos.data,
            )
        except UnknownObjectException as uoe_error:
            return render_template(
                "user.html",
                ghh=ghh,
                search_form=search_form,
                error=uoe_error,
            )
        except ReadTimeout as timeout_error:
            return render_template(
                "user.html",
                ghh=ghh,
                search_form=search_form,
                error=timeout_error,
            )
        ghh.get_repo_dfs()
        ghh.render_repo_html_tables()
        ghh.get_plots()
        return status(ghh)
    if request.method == "POST" and search_form.validate() is False:
        warning = search_form.search_request.errors[0]
        return render_template(
            "user.html",
            ghh=ghh,
            search_form=search_form,
            warning=warning,
        )
    if all(
        x in request.form.keys() for x in ["login_user", "gat", "hostname", "login"]
    ):
        return render_template(
            "user.html",
            ghh=ghh,
            search_form=search_form,
        )
    return render_template(
        "user.html",
        ghh=ghh,
        search_form=search_form,
    )


@app.route("/status")
def status(ghh):
    """
    Print status of app.
    """
    return render_template(
        "status.html",
        ghh=ghh,
    )


if __name__ == "__main__":
    app.run(debug=True)
