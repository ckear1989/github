"""
Module for flask app.
"""

from flask import (
    Flask,
    render_template,
)
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import (
    StringField,
    SubmitField,
)

from .main import GitHubHealth

app = Flask(__name__)
app.config["SECRET_KEY"] = "AiDmvqGvOsYlu81HBM53Ng4b0lBc0DAn"
Bootstrap(app)


class GitHubAccessTokenForm(FlaskForm):
    """
    Form for github access token class.
    """

    name = StringField("Github Access Token")
    submit = SubmitField()


class UserForm(FlaskForm):
    """
    Form for github user class.
    """

    name = StringField("User")
    submit_user = SubmitField()


@app.route("/")
def my_form():
    """
    Get home page with form.
    """
    gat_form = GitHubAccessTokenForm()
    user_form = UserForm()
    return render_template(
        "index.html",
        gat_form=gat_form,
        user_form=user_form,
    )


@app.route("/", methods=["POST"])
def my_form_post():
    """
    Control routing of app.
    """
    user_form = UserForm()
    user = user_form.name.data
    ghh = GitHubHealth(user=user)
    ghh.get_repos()
    ghh.get_repo_df()
    ghh.render_repo_html_table()
    ghh.get_plots()
    plots = ghh.plots
    return render_template(
        "status.html",
        url=ghh.user_url,
        user=ghh.username,
        table=ghh.repo_html,
        plots=plots,
    )


if __name__ == "__main__":
    app.run(debug=True)
