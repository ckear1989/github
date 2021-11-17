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
from flask_wtf import (
    FlaskForm,
    CSRFProtect,
)
from flask_bootstrap import Bootstrap
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    validators,
)

from github.GithubException import (
    UnknownObjectException,
    BadCredentialsException,
)

from .main import GitHubHealth

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
csrf = CSRFProtect()
csrf.init_app(app)
LOG = create_logger(app)
Bootstrap(app)


class LoginForm(FlaskForm):
    """
    Form for github user class.
    """

    login_user = StringField("user login", [validators.DataRequired()])
    # password = PasswordField("password")
    gat = PasswordField("github token")
    # remember_me = BooleanField('Remember Me')
    login_submit = SubmitField()


class SearchForm(FlaskForm):
    """
    Form for github user class.
    """

    search_user = StringField("user", [validators.DataRequired()])
    search_org = StringField("org")
    search_ignore_repos = StringField("ignore repos")
    search = SubmitField()


@app.errorhandler(400)
def page_not_found(error_message):
    """
    Handle a 400 error.
    """
    login_form = LoginForm()
    return (
        render_template(
            "login.html",
            login_form=login_form,
            error=error_message,
        ),
        400,
    )


@app.route("/", methods=["POST", "GET"])
def login():
    """
    Get login page with form.
    """
    login_form = LoginForm()
    if "login_user" in session:
        if "gat" in session:
            # if "password" in session:
            ghh = GitHubHealth(
                login=session["login_user"],
                # password=session["password"],
                gat=session["gat"],
            )
            return search(ghh)
    if request.method == "POST" and login_form.validate():
        login_user = login_form.login_user.data
        gat = login_form.gat.data
        # password = login_form.password.data
        try:
            ghh = GitHubHealth(login=login_user, gat=gat)  # password=password, gat=gat)
        except BadCredentialsException as bce_error:
            LOG.debug("bad_credentials")
            return render_template(
                "login.html",
                login_form=login_form,
                error=bce_error,
            )
        session["login_user"] = login_user
        session["gat"] = gat
        # session["password"] = password
        return search(ghh)
    return render_template(
        "login.html",
        login_form=login_form,
    )


@app.route("/search", methods=["POST", "GET"])
def search(ghh):
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
    LOG.debug(search_ignore_repos)
    if request.method == "POST" and search_form.validate():
        try:
            ghh.get_repos(
                user=search_user, org=search_org, ignore_repos=search_ignore_repos
            )
        except UnknownObjectException as uoe_error:
            return render_template(
                "search.html",
                search_form=search_form,
                error=uoe_error,
            )
        ghh.get_repo_dfs()
        ghh.render_repo_html_tables()
        ghh.get_plots()
        LOG.debug(search_user)
        search_user_url = ghh.requested_user.url
        search_org_url = ghh.requested_org.url
        LOG.debug(search_user_url)
        LOG.debug(search_org_url)
        return status(ghh)
    return render_template(
        "search.html",
        search_form=search_form,
        ignore_repos_forms=search_ignore_repos,
    )


@app.route("/status")
def status(ghh):
    """
    Print status of app.
    """
    return render_template(
        "status.html",
        user=ghh.requested_user,
        org=ghh.requested_org,
        user_table=ghh.repo_html["user"],
        org_table=ghh.repo_html["org"],
        user_plots=ghh.plots["user"],
        org_plots=ghh.plots["org"],
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
