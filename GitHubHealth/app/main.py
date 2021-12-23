"""
Module for flask app.
"""

import logging
from logging.config import dictConfig
from logging.handlers import SMTPHandler
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
from requests.exceptions import (
    ReadTimeout,
    ConnectionError as RequestsConnectionError,
)

from github.GithubException import (
    UnknownObjectException,
    BadCredentialsException,
    GithubException,
    RateLimitExceededException,
)

from GitHubHealth import GitHubHealth
from GitHubHealth.app.forms import (
    LoginForm,
    MoreForm,
    SearchForm,
)

# pylint: disable=invalid-name
REQUIREMENTS = str(
    pkg_resources.resource_stream("GitHubHealth", "app/requirements.txt").read()
)
version_requirements = [
    x.strip().split("GitHubHealth==")[1]
    for x in REQUIREMENTS.split("\\n")
    if "GitHubHealth" in x
][0]
VERSION = version_requirements

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

mail_handler = SMTPHandler(
    mailhost="127.0.0.1",
    fromaddr="server-error@githubhealth.com",
    toaddrs=["support@GitHubHealth.com"],
    subject="Application Error",
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
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
    ghh = GitHubHealth(
        login=login_user,
        gat=gat,
        hostname=hostname,
        timeout=timeout,
    )
    return ghh


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
csrf = CSRFProtect()
csrf.init_app(app)
LOG = create_logger(app)
Bootstrap(app)


@app.errorhandler(RateLimitExceededException)
def handle_rate_limit_error(error_message):
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


@app.errorhandler(KeyError)
def internal_key_error(error_message):
    """
    Handle a key error.
    """
    LOG.debug("debug key error: %s", error_message)
    session["error"] = "KeyError"
    return redirect(url_for("home"))


# who knows how this works?
# pylint: disable=assigning-non-slot
@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def home():
    """
    Get home page.
    """
    if "error" not in session:
        session["error"] = ""
    login_form = LoginForm()
    if "login_user" in request.form.keys():
        if request.method == "POST" and login_form.validate():
            session["login_user"] = login_form.login_user.data
            session["gat"] = login_form.gat.data
            session["hostname"] = login_form.hostname.data
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
        error=session["error"],
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


@app.route("/user/<string:username>", methods=["POST", "GET"])
def user(username):
    """
    Get user page.
    """
    if username != session["login_user"]:
        return redirect(url_for("home"))
    ghh, _ = try_ghh(session)
    if ghh is not None:
        search_form = SearchForm()
        more_form = MoreForm()
        ghh.user.get_metadata()
        ghh.user.get_metadata_html()
        # this is needed. how else whould I do it?
        # pylint: disable=no-else-return
        if request.method == "POST":
            if search_form.validate():
                session["search_users"] = search_form.search_users.data
                session["search_orgs"] = search_form.search_orgs.data
                session["search_repos"] = search_form.search_repos.data
                session["ignore"] = search_form.ignore.data
                return redirect(
                    url_for(
                        "search_results",
                        search_request=search_form.search_request.data,
                    )
                )
            elif more_form.validate():
                ghh.user.metadata.set_input_limits(
                    input_from=more_form.input_from.data,
                    input_to=more_form.input_to.data,
                )
                ghh.user.metadata.get_metadata()
                ghh.user.metadata.get_metadata_html()
                setattr(ghh.user, "metadata_html", ghh.user.metadata.metadata_html)
                return render_template(
                    "user.html",
                    ghh=ghh,
                    search_form=search_form,
                    more_form=more_form,
                )
        return render_template(
            "user.html",
            ghh=ghh,
            search_form=search_form,
            more_form=more_form,
        )
    return redirect(url_for("home"))


@app.route("/search/<string:search_request>", methods=["POST", "GET"])
def search_results(search_request):
    """
    Search results from given search paramaters.
    """
    ghh, _ = try_ghh(session)
    search_users = session["search_users"]
    search_orgs = session["search_orgs"]
    search_repos = session["search_repos"]
    ignore = session["ignore"]
    if ghh is not None:
        more_form = MoreForm()
        try:
            ghh.search(
                search_request=search_request,
                users=search_users,
                orgs=search_orgs,
                repos=search_repos,
                ignore=ignore,
            )
        except UnknownObjectException:
            return redirect(url_for("user", username=session["login_user"]))
        except ReadTimeout:
            return redirect(url_for("user", username=session["login_user"]))
        if request.method == "POST" and more_form.validate():
            ghh.search_results.set_input_limits(
                input_from=more_form.input_from.data,
                input_to=more_form.input_to.data,
            )
            ghh.search_results.get_output_results()
        return render_template(
            "search_results.html",
            ghh=ghh,
            more_form=more_form,
        )
    return redirect(url_for("user", username=session["login_user"]))


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
    if not app.debug:
        app.logger.addHandler(mail_handler)
    app.run(debug=True)
