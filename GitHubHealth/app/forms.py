"""
Store classes for forms for app.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    validators,
)


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
