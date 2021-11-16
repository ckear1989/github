"""
Helper functions to parse repo details.
Main function handles logic to connect to GitHub and select repos for analysis.
"""
from datetime import datetime
import os
import warnings

import altair as alt
import pandas as pd
from github import Github, MainClass
from github.GithubException import (
    UnknownObjectException,
    BadCredentialsException,
)

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_NOW = datetime.now()
ACCESS_TOKEN_VAR_NAME = "GITHUB_TOKEN"
TIMEOUT = 1
BRANCH_DF_COLUMNS = ["branch", "age"]
BRANCH_TEMPLATE_DF = pd.DataFrame(columns=BRANCH_DF_COLUMNS)
REPOS_DF_COLUMNS = [
    "repo",
    "private",
    "branch_count",
    "min_branch_age_days",
    "max_branch_age_days",
]
REPOS_TEMPLATE_DF = pd.DataFrame(columns=REPOS_DF_COLUMNS)

# pylint: disable=redefined-outer-name


def get_connection(hostname=None, user=None, password=None, gat=None, timeout=TIMEOUT):
    """
    Get connection and login.
    """
    if hostname is None:
        base_url = MainClass.DEFAULT_BASE_URL
    else:
        base_url = f"https://{hostname}/api/v3"
    if gat is not None:
        github_con = Github(
            base_url=base_url,
            login_or_token=gat,
            timeout=timeout,
        )
    elif user is not None:
        if password is not None:
            github_con = Github(
                base_url=base_url,
                login_or_token=user,
                password=password,
                timeout=timeout,
            )
        else:
            raise Exception("provide either user+password or gat")
    else:
        raise Exception("provide either user+password or gat")
    this_user = github_con.get_user()
    this_user.login
    return github_con, this_user


def get_branch_details(branch):
    """
    Get information on branch from PyGitHub API and format in pandas DataFrame.
    """
    commit = branch.commit
    date = commit.raw_data["commit"]["author"]["date"]
    date = datetime.strptime(date, DATE_FORMAT)
    age = (DATE_NOW - date).days
    branch_dict = {"branch": [branch.name], "age": [age]}
    branch_df = pd.DataFrame.from_dict(branch_dict)
    return branch_df


def get_repo_details(repo):
    """
    Get information on repo from PyGitHub API and format in pandas DataFrame.
    """
    branch_df = pd.concat(
        [BRANCH_TEMPLATE_DF]
        + [get_branch_details(branch) for branch in repo.get_branches()],
        ignore_index=True,
    )
    repo_dict = {
        "repo": [repo.name],
        "private": [repo.private],
        "branch_count": [len(branch_df)],
        "min_branch_age_days": [branch_df["age"].min()],
        "max_branch_age_days": [branch_df["age"].max()],
    }
    languages = repo.get_languages()
    primary_language = None
    if len(languages) > 0:
        primary_language = sorted(languages.items(), key=lambda x: x[1], reverse=True)[
            0
        ][0]
    repo_dict["primary_language"] = primary_language
    repo_df = pd.DataFrame.from_dict(repo_dict)
    return repo_df


def format_gt_red(val, red_length):
    """
    Helper function to get css style of color for cell value.
    """
    return "color: red" if val > red_length else None


def get_user_gh_df(user):
    """
    Main method to parse repo details into pandas DataFrame.
    """
    template_df = pd.DataFrame(columns=REPOS_DF_COLUMNS)
    repo_df = (
        pd.concat(
            [template_df]
            + [get_repo_details(repo) for repo in user.get_repos() if user is not None],
            ignore_index=True,
        )
        .sort_values(by="repo")
        .reset_index(drop=True)
    )
    return repo_df


# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=fixme
# TODO:
# break this into two classes
class GitHubHealth:
    """
    Class object for GitHubHeath.
    Args:
        hostname (str)      : default None
        login (str)         : default None
        password (str)      : default None
        gat (str)           : default None
        org (str)           : default None
        timeout (int)       : default TIMEOUT
    If user is None then try to get organisation for repo_table.
    If org is None then fall back on user retrieved from GITHUB_TOKEN.
    """

    def __init__(
        self, hostname=None, login=None, password=None, gat=None, timeout=TIMEOUT
    ):
        """
        Create connection based on (login+password) or (gat).
        """
        self.con, self.user = get_connection(hostname, login, password, gat, timeout)
        self.username = self.user.login
        self.user_url = self.user.html_url
        self.repos = []
        self.repo_df = None
        self.repo_html = None
        self.plots = None

    def get_repos(self, user, org=None, ignore_repos=None):
        """
        Method to get repos as a class object.
        """
        if ignore_repos is None:
            ignore_repos = []
        assert isinstance(ignore_repos, list)
        repos = {"user":[], "org":[]}
        repos["user"] = [
            repo
            for repo in self.user.get_repos(user)
            if repo.name not in ignore_repos
        ]
        if org is not None:
            repos["org"] = [
                repo
                for repo in self.user.get_repos(org)
                if repo.name not in ignore_repos
            ]
        setattr(self, "repos", repos)

    def get_repo_dfs(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        repo_dfs = {
            "user": REPOS_TEMPLATE_DF,
            "org": REPOS_TEMPLATE_DF,
        }
        repo_dfs["user"] = (
            pd.concat(
                [get_repo_details(repo) for repo in self.repos["user"]], ignore_index=True
            )
            .sort_values(by="repo")
            .reset_index(drop=True)
        )
        repo_dfs["org"] = (
            pd.concat(
                [get_repo_details(repo) for repo in self.repos["org"]], ignore_index=True
            )
            .sort_values(by="repo")
            .reset_index(drop=True)
        )
        setattr(self, "repo_dfs", repo_dfs)

    def render_repo_html_table(self):
        """
        Render pandas df to html with formatting of cells etc.
        """
        repo_html = (
            self.repo_df.style.hide_index()
            .applymap(
                lambda x: "color: red" if x is False else None, subset=["private"]
            )
            .applymap(lambda x: format_gt_red(x, 45), subset=["min_branch_age_days"])
            .applymap(lambda x: format_gt_red(x, 90), subset=["max_branch_age_days"])
            .applymap(lambda x: format_gt_red(x, 3), subset=["branch_count"])
            .render()
        )
        self.repo_html = repo_html

    def get_plots(self):
        """
        get altair plot objects as html.
        """
        branch_count_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y="branch_count",
            )
        ).properties(title="branch count by repo")
        branch_age_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y="max_branch_age_days",
            )
        ).properties(title="max branch age by repo")
        plots = [branch_count_plot, branch_age_plot]
        plots = [x.configure_view(discreteWidth=300).to_json() for x in plots]
        self.plots = plots


if __name__ == "__main__":
    github_con, user = get_connection()
    print(get_user_gh_df(user))
