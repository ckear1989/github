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
from requests.exceptions import ReadTimeout

from github.GithubException import (
    UnknownObjectException,
    BadCredentialsException,
)

from GitHubHealth import GitHubHealth

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
    gat = PasswordField("github token", [validators.DataRequired()])
    # remember_me = BooleanField('Remember Me')
    login = SubmitField(render_kw={"onclick": "loading()"})

    # will fix this at some stage
    # pylint: disable=bad-super-call
    # pylint: disable=arguments-differ
    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        if not self.login_user.data or not self.gat.data:
            msg = "Log in using GitHub username and access token"
            self.errors.append(msg)
            self.errors.append(msg)
            return False
        return True


class SearchForm(FlaskForm):
    """
    Form for github user class.
    """

    search_user = StringField("user")
    search_org = StringField("org")
    search_ignore_repos = StringField("ignore repos")
    search = SubmitField(render_kw={"onclick": "loading()"})

    # will fix this at some stage
    # pylint: disable=bad-super-call
    # pylint: disable=arguments-differ
    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        if not self.search_user.data and not self.search_org.data:
            msg = "At least one of user or org must be set"
            self.search_user.errors.append(msg)
            self.search_org.errors.append(msg)
            return False
        return True


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


@app.route("/", methods=["POST", "GET"])
def home():
    """
    Get home page.
    """
    print(request.method)
    if "login_user" not in session:
        login()
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    Get login page with form.
    """
    login_form = LoginForm()
    if "login_user" in session:
        if "gat" in session:
            try:
                ghh = GitHubHealth(
                    login=session["login_user"],
                    gat=session["gat"],
                )
            except BadCredentialsException:
                del session["gat"]
                return render_template(
                    "login.html",
                    login_form=login_form,
                )
            return search(ghh)
    if request.method == "POST" and login_form.validate():
        login_user = login_form.login_user.data
        gat = login_form.gat.data
        try:
            ghh = GitHubHealth(login=login_user, gat=gat)
        except BadCredentialsException as bce_error:
            return render_template(
                "login.html",
                login_form=login_form,
                error=bce_error,
            )
        session["login_user"] = login_user
        session["gat"] = gat
        return search(ghh)
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
    return login()


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
        except ReadTimeout as timeout_error:
            return render_template(
                "search.html",
                search_form=search_form,
                error=timeout_error,
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
