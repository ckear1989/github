"""
Module for flask app.
"""

import os

from flask import (
    Flask,
    render_template,
    request,
    session,
)
from flask.logging import create_logger
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
from requests.exceptions import ReadTimeout

from github.GithubException import (
    UnknownObjectException,
    BadCredentialsException,
)

from GitHubHealth import GitHubHealth
from GitHubHealth.app.forms import (
    LoginForm,
    SearchForm,
)


def get_ghh(login_user, gat):
    """
    Get ghh object.
    Useful for quickly verifying if credentials can be used to login.
    """
    ghh = GitHubHealth(login=login_user, gat=gat)
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
            try:
                ghh = get_ghh(session["login_user"], session["gat"])
            except BadCredentialsException as bce_error:
                del session["gat"]
                return render_template(
                    "home.html",
                    error=bce_error,
                )
            return render_template("index.html", ghh=ghh)
    return render_template(
        "index.html",
    )


@app.route("/about", methods=["POST", "GET"])
def about():
    """
    Get about page.
    """
    return render_template("about.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    Get login page with form.
    """
    login_form = LoginForm()
    if "login_user" in session:
        if "gat" in session:
            try:
                ghh = get_ghh(session["login_user"], session["gat"])
            except BadCredentialsException:
                del session["gat"]
                return render_template(
                    "login.html",
                    login_form=login_form,
                )
            return user(ghh)
    if request.method == "POST" and login_form.validate():
        login_user = login_form.login_user.data
        gat = login_form.gat.data
        try:
            ghh = get_ghh(login_user, gat)
        except BadCredentialsException as bce_error:
            return render_template(
                "login.html",
                login_form=login_form,
                error=bce_error,
            )
        session["login_user"] = login_user
        session["gat"] = gat
        return user(ghh)
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
    search_user = search_form.search_user.data
    search_org = search_form.search_org.data
    search_ignore_repos = search_form.search_ignore_repos.data
    if search_ignore_repos is None:
        search_ignore_repos = ""
    search_ignore_repos = [x.strip() for x in search_ignore_repos.strip().split(",")]
    if "login_user" in session:
        if "gat" in session:
            ghh = get_ghh(session["login_user"], session["gat"])
            # pylint: disable=no-else-return
            if request.method == "POST" and search_form.validate():
                try:
                    ghh.get_repos(
                        user=search_user,
                        org=search_org,
                        ignore_repos=search_ignore_repos,
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
                    ignore_repos_forms=search_ignore_repos,
                )
    return render_template(
        "search.html",
        search_form=search_form,
        ignore_repos_forms=search_ignore_repos,
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
