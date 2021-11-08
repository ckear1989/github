"""
Setup for pip package installation.
"""

import setuptools

setuptools.setup(
    name="github",
    extras_require={
        "dev": [
            "pre-commit>=2.15.0",
            "pre-commit-hooks>=4.0.1",
            "PyGitHub>=1.55",
            "pylint>=2.11.1",
            "pandas>=1.3.4",
            "flask>-2.0.2",
        ],
        "test": [
            "pytest>=6.2.5",
        ],
    },
)
