"""
Setup for pip package installation.
"""

import setuptools
import setuptools_scm

# parse README for long_description and summary
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    description = next(
        x for x in long_description.split("\n") if x and x[0] not in ["#", "["]
    )

setuptools.setup(
    name="GitHubHealth",
    version=setuptools_scm.get_version(),
    url="https://github.com/ckear1989/github/",
    license="MIT",
    author="Conor Kearney",
    author_email="ckear1989@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "PyGitHub==1.55",
        "pandas==1.3.4",
        "flask==2.0.2",
        "flask-wtf==1.0.0",
        "Flask-Bootstrap4==4.0.2",
        "altair==4.1.0",
        "setuptools_scm>=6.3.2",
    ],
    extras_require={
        "deploy": [
            "PyGitHub==1.55",
            "pandas==1.3.4",
            "flask==2.0.2",
            "flask-wtf==1.0.0",
            "Flask-Bootstrap4==4.0.2",
            "altair==4.1.0",
            "gunicorn==20.1.0",
        ],
        "dev": [
            "pre-commit>=2.15.0",
            "PyGitHub>=1.55",
            "pylint>=2.11.1",
            "pandas>=1.3.4",
            "flask>=2.0.2",
            "flask-wtf>=1.0.0",
            "Flask-Bootstrap4>=4.0.2",
            "altair>=4.1.0",
            "gunicorn>=20.1.0",
            "anybadge>=1.8.0",
        ],
        "test": [
            "pytest>=6.2.5",
            "subx>=2020.42.0",
            "docutils>=0.18",
            "pytest_codeblocks>=0.12.0",
        ],
    },
    packages=setuptools.find_packages(),
    package_data={"": ["../data/pylint.svg", "templates/*", "static/css/*"]},
    include_package_data=True,
)
