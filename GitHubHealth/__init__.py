"""
GitHubHealth module.
"""
# pylint: disable=invalid-name

__all__ = ["TIMEOUT", "main", "app"]

from .main import (  # noqa
    GitHubHealth,  # noqa
    ACCESS_TOKEN_VAR_NAME,  # noqa
)  # noqa
from .app.main import app  # noqa

TIMEOUT = 2
