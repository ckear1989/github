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


def try_ghh(login_user, gat, hostname):
    """
    Try ghh object.
    Useful for quickly verifying if credentials can be used to login.
    """
    try:
        ghh = get_ghh(login_user, gat, hostname)
    except (
        BadCredentialsException,
        GithubException,
        RequestsConnectionError,
    ) as bce_gh_error:
        return None, bce_gh_error
    return ghh, None


def get_ghh(login_user, gat, hostname):
    """
    Get ghh object.
    Useful for quickly verifying if credentials can be used to login.
    """
    ghh = GitHubHealth(login=login_user, gat=gat, hostname=hostname)
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
    LOG.debug("debug400")
    login_form = LoginForm()
    return (
        render_template(
            "login.html",
            login_form=login_form,
            error=error_message,
        ),
        400,
    )


@app.route("/under_construction", methods=["POST", "GET"])
def under_construction():
    """
    Get under construction page.
    """
    return render_template("under_construction.html")


@app.route("/", methods=["POST", "GET"])
def home():
    """
    Get home page.
    """
    if "login_user" in session:
        if "gat" in session:
            ghh, error_message = try_ghh(
                session["login_user"], session["gat"], session["hostname"]
            )
            if ghh is not None:
                return render_template("index.html", ghh=ghh)
            del session["gat"]
            return render_template(
                "home.html",
                error=error_message,
            )
    return render_template(
        "index.html",
    )


@app.route("/about", methods=["POST", "GET"])
def about():
    """
    Get about page.
    """
    if "login_user" in session:
        if "gat" in session:
            ghh, error_message = try_ghh(
                session["login_user"], session["gat"], session["hostname"]
            )
            if ghh is not None:
                return render_template(
                    "about.html",
                    ghh=ghh,
                )
            return render_template("login.html", error=error_message)
    return render_template(
        "about.html",
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    Get login page with form.
    """
    login_form = LoginForm()
    if "login_user" in session:
        if "gat" in session:
            if "hostname" in session:
                ghh, error_message = try_ghh(
                    session["login_user"], session["gat"], session["hostname"]
                )
                if ghh is not None:
                    return user(ghh)
                return render_template(
                    "login.html", login_form=login_form, error=error_message
                )
    if request.method == "POST" and login_form.validate():
        login_user = login_form.login_user.data
        gat = login_form.gat.data
        hostname = login_form.hostname.data
        ghh, error_message = try_ghh(login_user, gat, hostname)
        if ghh is not None:
            session["login_user"] = login_user
            session["gat"] = gat
            session["hostname"] = hostname
            return user(ghh)
        return render_template(
            "login.html",
            login_form=login_form,
            error=error_message,
        )
    return render_template(
        "login.html",
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
    return home()


@app.route("/user", methods=["POST", "GET"])
def user(ghh):
    """
    Get user page.
    """
    # will figure out what to actually do with user page
    # pylint: disable=no-else-return
    # if request.method == "POST":
    #     return search()
    ghh.user.get_metadata_html()
    return render_template(
        "user.html",
        ghh=ghh,
    )


@app.route("/search", methods=["POST", "GET"])
def search():
    """
    Search for a user and org.
    """
    search_form = SearchForm()
    if "login_user" in session:
        if "gat" in session:
            if "hostname" in session:
                ghh = get_ghh(
                    session["login_user"], session["gat"], session["hostname"]
                )
                # pylint: disable=no-else-return
                if request.method == "POST" and search_form.validate():
                    try:
                        ghh.get_repos(
                            search_request=search_form.search_request.data,
                            users=search_form.search_users.data,
                            orgs=search_form.search_teams.data,
                            teams=search_form.search_teams.data,
                            ignore_repos=search_form.search_ignore_repos.data,
                        )
                    except UnknownObjectException as uoe_error:
                        return render_template(
                            "search.html",
                            ghh=ghh,
                            search_form=search_form,
                            error=uoe_error,
                        )
                    except ReadTimeout as timeout_error:
                        return render_template(
                            "search.html",
                            ghh=ghh,
                            search_form=search_form,
                            error=timeout_error,
                        )
                    ghh.get_repo_dfs()
                    ghh.render_repo_html_tables()
                    ghh.get_plots()
                    return status(ghh)
                else:
                    return render_template(
                        "search.html",
                        ghh=ghh,
                        search_form=search_form,
                    )
    return render_template(
        "search.html",
        search_form=search_form,
        error="Please log in before using search functionality.",
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


@app.route("/error")
def error(error_type):
    """
    Report error.
    """
    return render_template(
        "error.html",
        error_type=error_type,
    )


if __name__ == "__main__":
    app.run(debug=True)
