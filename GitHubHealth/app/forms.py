"""
Store classes for forms for app.
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
    validators,
)


class LoginForm(FlaskForm):
    """
    Form for github user class.
    """

    login_user = StringField("user login", [validators.DataRequired()])
    gat = PasswordField("github token", [validators.DataRequired()])
    hostname = StringField(
        "hostname", [validators.DataRequired()], default="github.com"
    )
    results_limit = IntegerField(
        "results limit", [validators.DataRequired()], default=10
    )
    timeout = IntegerField("timeout", [validators.DataRequired()], default=2)
    login = SubmitField(render_kw={"onclick": "loading_login()"})

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
        if not self.login_user.data or not self.gat.data:
            msg = "Log in using GitHub username and access token"
            self.login_user.errors.append(msg)
            self.gat.errors.append(msg)
            return False
        if self.timeout.data < 1 or self.timeout.data > 10:
            msg = "timeout must be a value between 1 and 10"
            self.timeout.errors.append(msg)
            return False
        if self.results_limit.data < 1 or self.results_limit.data > 50:
            msg = "timeout must be a value between 1 and 50"
            self.timeout.errors.append(msg)
            return False
        return True


class SearchForm(FlaskForm):
    """
    Form for github user class.
    """

    search_request = StringField()
    search_users = BooleanField("users")
    search_orgs = BooleanField("orgs")
    search_ignore_repos = StringField("ignore repos", id="ignore-repos")
    search = SubmitField(render_kw={"onclick": "loading_search()"})

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            msg = "super() validate false"
            self.search_request.errors.append(msg)
            return False
        if not self.search_request.data:
            msg = "Please enter search term."
            self.search_request.errors.append(msg)
            return False
        if len(self.search_request.data) < 4:
            msg = "Please enter longer search term."
            self.search_request.errors.append(msg)
            return False
        if self.search_users.data is False and self.search_orgs.data is False:
            msg = "Please choose users, orgs or both"
            self.search_request.errors.append(msg)
            return False
        return True


class MoreForm(FlaskForm):
    """
    Form for github user class.
    """

    more = SubmitField()
    increment = IntegerField("increment", [validators.DataRequired()], default=2)
