"""
Module for flask app.
"""

import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
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
    MoreForm,
    SearchForm,
)

# pylint: disable=invalid-name
try:
    version_scm = setuptools_scm.get_version()
except LookupError:
    version_scm = "?"
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
    required = ["login_user", "gat", "hostname", "results_limit", "timeout"]
    if all(x in this_session for x in required):
        try:
            ghh = get_ghh(
                this_session["login_user"],
                this_session["gat"],
                this_session["hostname"],
                this_session["results_limit"],
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


def get_ghh(login_user, gat, hostname, results_limit, timeout):
    """
    Get ghh object.
    Useful for quickly verifying if credentials can be used to login.
    """
    ghh = GitHubHealth(
        login=login_user,
        gat=gat,
        hostname=hostname,
        results_limit=results_limit,
        timeout=timeout,
    )
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


# who knows how this works?
# pylint: disable=assigning-non-slot
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
            session["results_limit"] = login_form.results_limit.data
            session["timeout"] = login_form.timeout.data
            ghh, error_message = try_ghh(session)
            if ghh is not None:
                return redirect(url_for("user", username=ghh.user.name))
            return render_template(
                "index.html",
                login_form=login_form,
                error=error_message,
            )
    if "search_request" in request.form.keys():
        if request.method == "POST":
            ghh, error_message = try_ghh(session)
            if ghh is not None:
                return redirect(url_for("user", username=ghh.user.name))
    if request.method == "GET":
        ghh, _ = try_ghh(session)
        if ghh is not None:
            return redirect(url_for("user", username=ghh.user.name))
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
            return redirect(url_for("user", username=ghh.user.name))
    if request.method == "GET":
        ghh, error_message = try_ghh(session)
        if ghh is not None:
            return redirect(url_for("user", username=ghh.user.name))
    login_form = LoginForm()
    if request.method == "POST" and login_form.validate():
        session["login_user"] = login_form.login_user.data
        session["gat"] = login_form.gat.data
        session["hostname"] = login_form.hostname.data
        session["results_limit"] = login_form.results_limit.data
        session["timeout"] = login_form.timeout.data
        ghh, error_message = try_ghh(session)
        if ghh is not None:
            return redirect(url_for("user", username=ghh.user.name))
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
    return redirect(url_for("home"))


# is this the right way of handling view routes?
# pylint: disable=unused-argument
# pylint: disable=too-many-return-statements
@app.route("/user/<username>", methods=["POST", "GET"])
def user(username):
    """
    Get user page.
    """
    ghh, _ = try_ghh(session)
    if ghh is not None:
        ghh.user.get_metadata_html()
        search_form = SearchForm()
        more_form = MoreForm()
        print(request.form.keys())
        if all(x in request.form.keys() for x in ["more", "increment"]):
            ghh.user.increase_metadata_limit(more_form.increment.data)
            ghh.user.get_metadata_df()
            ghh.user.get_metadata_html()
            return render_template(
                "user.html",
                ghh=ghh,
                more_form=more_form,
                search_form=search_form,
            )
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
                    more_form=more_form,
                    search_form=search_form,
                    error=uoe_error,
                )
            except ReadTimeout as timeout_error:
                return render_template(
                    "user.html",
                    ghh=ghh,
                    more_form=more_form,
                    search_form=search_form,
                    error=timeout_error,
                )
            ghh.get_repo_dfs()
            ghh.render_repo_html_tables()
            ghh.get_plots()
            return status(ghh.user.name, ghh)
        if request.method == "POST" and search_form.validate() is False:
            warning = search_form.search_request.errors[0]
            return render_template(
                "user.html",
                ghh=ghh,
                more_form=more_form,
                search_form=search_form,
                warning=warning,
            )
        if all(
            x in request.form.keys() for x in ["login_user", "gat", "hostname", "login"]
        ):
            return render_template(
                "user.html",
                ghh=ghh,
                more_form=more_form,
                search_form=search_form,
            )
        return render_template(
            "user.html",
            ghh=ghh,
            more_form=more_form,
            search_form=search_form,
        )
    return redirect(url_for("home"))


@app.route("/status/<string:username>")
def status(username, ghh):
    """
    Return status of search.
    """
    # there has to be a better way of storing ghh
    # flask.g only remains for 1 request cycle
    # redis and memchache look difficult
    # as does multiprocessing.Manager
    if ghh is not None:
        return render_template(
            "status.html",
            ghh=ghh,
        )
    return redirect(url_for("home"))


@app.route("/repo_status/<string:repo_name>")
def repo_status(repo_name):
    """
    Return status of repo.
    """
    ghh, _ = try_ghh(session)
    if ghh is not None:
        repo_full_name = f"{ghh.user.name}/{repo_name}"
        repo = ghh.get_repo(repo_full_name)
        repo.get_repo_df()
        repo.get_html_table()
        repo.get_plots()
        return render_template(
            "repo_status.html",
            ghh=ghh,
            repo=repo,
        )
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
