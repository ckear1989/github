"""
Setup for pip package installation.
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GitHubHealth",
    url="https://github.com/ckear1989/github/",
    license="MIT",
    author="Conor Kearney",
    author_email="ckear1989@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "PyGitHub==1.55",
        "pandas==1.3.4",
        "flask==2.0.2",
        "altair==4.1.0",
    ],
    extras_require={
        "dev": [
            "pre-commit>=2.15.0",
            "PyGitHub>=1.55",
            "pylint>=2.11.1",
            "pandas>=1.3.4",
            "flask>=2.0.2",
            "altair>=4.1.0",
            "gunicorn>=20.1.0",
            "anybadge>=1.8.0",
        ],
        "test": [
            "pytest>=6.2.5",
        ],
    },
    packages=setuptools.find_packages(),
    package_data={"": ["../data/pylint.svg"]},
    include_package_data=True,
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)
