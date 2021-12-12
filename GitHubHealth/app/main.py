"""
Module for flask app.
"""

from logging.config import dictConfig
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
from flask_wtf.csrf import CSRFError
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

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


def get_csrf_token():
    """
    format csrf token for meta tag in header.
    """
    return_tag = f"<meta name=\"csrf-token\" content=\"{session['csrf_token']}\">"
    return return_tag


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


@app.errorhandler(CSRFError)
def handle_csrf_error(error_message):
    """
    Handle a CSRF error.
    """
    LOG.debug("debugCSRF: %s", error_message)
    login_form = LoginForm()
    return (
        render_template(
            "index.html",
            login_form=login_form,
            error=error_message,
        ),
        400,
    )


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
        raise Exception("search should never happen in index")
    # if already logged in return user page
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
        raise Exception("search should never happen from login")
    if request.method == "GET":
        ghh, _ = try_ghh(session)
        if ghh is not None:
            return redirect(url_for("user", username=ghh.user.name))
    login_form = LoginForm()
    if request.method == "POST" and login_form.validate():
        session["login_user"] = login_form.login_user.data
        session["gat"] = login_form.gat.data
        session["hostname"] = login_form.hostname.data
        session["results_limit"] = login_form.results_limit.data
        session["timeout"] = login_form.timeout.data
        ghh, _ = try_ghh(session)
        if ghh is not None:
            return redirect(url_for("user", username=ghh.user.name))
        return redirect(url_for("home"))
    return redirect(url_for("home"))


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


@app.route("/user/<username>", methods=["POST", "GET"])
def user(username):
    """
    Get user page.
    """
    ghh, _ = try_ghh(session)
    if ghh is not None:
        search_form = SearchForm()
        more_form = MoreForm()
        ghh.user.get_metadata_html()
        # this is needed.  how else whould I do it?
        # pylint: disable=no-else-return
        if request.method == "POST":
            if search_form.validate():
                return redirect(url_for("search"))
            elif more_form.validate():
                ghh.user.metadata.set_input_limits(
                    input_from=more_form.results_from.data,
                    input_to=more_form.results_to.data,
                )
                return redirect(url_for("user", username=username))
        return render_template(
            "user.html",
            ghh=ghh,
            search_form=search_form,
            more_form=more_form,
        )
    return redirect(url_for("home"))


@app.route("/search/")
def search_results(ghh, search_request, search_users, search_orgs, ignore):
    """
    Search results from given search paramaters.
    """
    search_form = SearchForm()
    more_form = MoreForm()
    try:
        ghh.search(
            search_request=search_request,
            users=search_users,
            orgs=search_orgs,
            ignore=ignore,
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
    if request.method == "POST" and more_form.validate():
        print(more_form)
        print(more_form.results_from)
        print(more_form.results_to)
        ghh.search(
            search_request=search_request,
            users=search_users,
            orgs=search_orgs,
            ignore=ignore,
            results_from=more_form.results_from.data,
            results_to=more_form.results_to.data,
        )
    return render_template(
        "search_results.html",
        ghh=ghh,
        more_form=more_form,
    )


@app.route("/status/<string:resource_name>")
def status(resource_name):
    """
    Return status of search.
    """
    search_form = SearchForm()
    more_form = MoreForm()
    ghh, _ = try_ghh(session)
    if ghh is not None:
        try:
            ghh.get_requested_object(resource_name)
            ghh.get_requested_repos()
            ghh.get_requested_df()
            ghh.render_requested_html_table()
            ghh.get_plots()
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
        return render_template(
            "status.html",
            ghh=ghh,
        )
    return redirect(url_for("home"))


@app.route("/repo_status/<string:repo_owner>/<string:repo_name>")
def repo_status(repo_owner, repo_name):
    """
    Return status of repo.
    """
    ghh, _ = try_ghh(session)
    if ghh is not None:
        repo = ghh.get_repo(repo_owner, repo_name)
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
