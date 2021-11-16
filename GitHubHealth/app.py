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
    redirect,
    url_for,
)
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import (
    BooleanField,
    StringField,
    SubmitField,
    PasswordField,
    validators,
)
from github.GithubException import (
    UnknownObjectException,
    BadCredentialsException,
    RateLimitExceededException,
)

from .main import (
    ACCESS_TOKEN_VAR_NAME,
    GitHubHealth,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
Bootstrap(app)


class LoginForm(FlaskForm):
    """
    Form for github user class.
    """
    login_user = StringField("login_user", [validators.DataRequired()])
    password = PasswordField("password")
    gat = PasswordField("GitHub Access Token")
    # remember_me = BooleanField('Remember Me')
    login_submit = SubmitField()


class SearchForm(FlaskForm):
    """
    Form for github user class.
    """
    search_user = StringField("search_user", [validators.DataRequired()])
    org = StringField("search org")
    search_submit = SubmitField()


@app.route("/", methods=["POST", "GET"])
def login():
    """
    Get login page with form.
    """
    login_form = LoginForm()
    search_form = SearchForm()
    app.logger.debug('debug1')
    app.logger.debug(login_form.login_user.data)
    app.logger.debug(search_form.search_user.data)
    app.logger.debug('debug2')
    if request.method == "POST" and search_form.validate():
        app.logger.debug(login_form.login_user.data)
        app.logger.debug(search_form.search_user.data)
        app.logger.debug('debug2.1')
        ghh.get_repos(search_user, search_org)
        ghh.get_repo_dfs()
        ghh.render_repo_html_tables()
        ghh.get_plots()
        plots = ghh.plots
        return status(ghh)
    else:
        return render_template(
            "search.html",
            search_form=search_form,
        )
    if request.method == "POST" and login_form.validate():
        app.logger.debug('debug3')
        user = login_form.login_user.data
        gat = login_form.gat.data
        password = login_form.password.data
        try:
            ghh = GitHubHealth(login=user, password=password, gat=gat)
            app.logger.debug('debug4')
            search_user = search_form.search_user.data
            search_org = search_form.org.data
            app.logger.debug(search_user)
            app.logger.debug('debug5')
            if request.method == "POST" and search_form.validate():
                app.logger.debug('debug6')
                ghh.get_repos(search_user, search_org)
                ghh.get_repo_dfs()
                ghh.render_repo_html_tables()
                ghh.get_plots()
                plots = ghh.plots
                return status(ghh)
            else:
                app.logger.debug('debug7')
                return render_template(
                    "search.html",
                    search_form=search_form,
                )
        except BadCredentialsException as e:
            return render_template(
                "login.html",
                login_form=login_form,
                error=e,
              )
            app.logger.debug('debug8')
            search_form = SearchForm()
            search_user = search_form.search_user.data
            app.logger.debug(search_user)
            search_org = search_form.org.data
            app.logger.debug('debug9')
            if request.method == "POST" and search_form.validate():
                ghh.get_repos(search_user, search_org)
                ghh.get_repo_dfs()
                ghh.render_repo_html_tables()
                ghh.get_plots()
                plots = ghh.plots
                return status(ghh)
            else:
                return render_template(
                    "search.html",
                    search_form=search_form,
                )
    else:
        app.logger.debug('debug10')
        return render_template(
            "login.html",
            login_form=login_form,
            error="redirected",
        )


# @app.route("/search", methods=["POST", "GET"])
# def search():
#     """
#     Search for a user and org.
#     """
#     # ghh = request.args.get("ghh")
#     print(ghh)
#     # ghh = session["ghh"]
#     search_form = SearchForm()
#     search_user = search_form.search_user.data
#     search_org = search_form.org.data
#     app.logger.debug('debug3')
#     print("debug3")
#     print(search_user)
#     print(search_org)
#     print(request.method)
#     print(search_form.validate())
#     if request.method == "POST" and search_form.validate():
#         print("debug4")
#         print(search_user)
#         print(search_org)
#         ghh.get_repos(search_user, search_org)
#         ghh.get_repo_dfs()
#         ghh.render_repo_html_tables()
#         ghh.get_plots()
#         plots = ghh.plots
#         return status(ghh)
#     else:
#         print("debug5")
#         print(request.method)
#         print(search_form.validate())
#         print(search_user)
#         print(search_org)
#         print(search_form)
#         # print(render_template(
#         #     "search.html",
#         #     search_form=search_form,
#         # ))
#         return render_template(
#             "search.html",
#             search_form=search_form,
#         )
# 
#        
# 
# @app.route("/status")
# def status(ghh):
#     """
#     Print status of app.
#     """
#     print("debug6")
#     print(ghh)
#     return render_template(
#         "status.html",
#         url=ghh.user_url,
#         user=ghh.username,
#         table=ghh.repo_html,
#         plots=plots,
#     )
# 
# 
# @app.route("/error")
# def error(error_type):
#     """
#     Report error.
#     """
#     print("debug7")
#     print(error_type)
#     return render_template(
#         "error.html",
#         error_type=error_type,
#     )


if __name__ == "__main__":
    app.run(debug=True)
