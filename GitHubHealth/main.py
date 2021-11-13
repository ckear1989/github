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

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_NOW = datetime.now()
ACCESS_TOKEN_VAR_NAME = "GITHUB_ACCESS_TOKEN"
TIMEOUT = 1

# pylint: disable=redefined-outer-name


def get_connection(hostname=None, user=None, org=None, timeout=TIMEOUT):
    """
    Get connection and login.
    """
    if hostname is None:
        base_url = MainClass.DEFAULT_BASE_URL
    else:
        base_url = f"https://{hostname}/api/v3"
    if user is None:
        if ACCESS_TOKEN_VAR_NAME not in os.environ:
            raise Exception(
                f"ERROR: environment variable {ACCESS_TOKEN_VAR_NAME}"
                " must be set if user is not given."
            )
        github_con = Github(
            base_url=base_url,
            login_or_token=os.getenv(ACCESS_TOKEN_VAR_NAME),
            timeout=timeout,
        )
        this_user = github_con.get_user()
    else:
        assert isinstance(user, str)
        github_con = Github(
            base_url=base_url,
            timeout=timeout,
        )
        this_user = github_con.get_user(user)
        warnings.warn(
            UserWarning(
                f"WARNING: requested user {user} is not validated user.login={this_user.login}"
            )
        )
    this_user_name = this_user.login
    requested_org = None
    if org is not None:
        found_org = False
        for accessable_org in this_user.get_orgs():
            if accessable_org.login == org:
                found_org = True
                requested_org = accessable_org
        if found_org is False:
            warnings.warn(
                UserWarning(
                    f"WARNING: requested org {org} not found for user {this_user_name}."
                )
            )
    return github_con, this_user, requested_org


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
        [get_branch_details(branch) for branch in repo.get_branches()],
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
    repo_df = (
        pd.concat(
            [get_repo_details(repo) for repo in user.get_repos()], ignore_index=True
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
        user (str)          : default None
        org (str)           : default None
        timeout (int)       : default TIMEOUT
        ignore_repos (list) : default None
    If user is None then try to get organisation for repo_table.
    If org is None then fall back on user retrieved from GITHUB_ACCESS_TOKEN.
    """

    def __init__(
        self, hostname=None, user=None, org=None, timeout=TIMEOUT, ignore_repos=None
    ):
        """
        Create connection and get table of repos base don user and org.
        """
        _, self.user, self.org = get_connection(hostname, user, org, timeout)
        self.username = self.user.login
        self.user_url = self.user.html_url
        if ignore_repos is None:
            ignore_repos = []
        self.ignore_repos = ignore_repos
        self.repos = []
        self.repo_df = None
        self.repo_html = None
        self.plots = None

    def get_repos(self):
        """
        Method to get repos as a class object.
        """
        assert isinstance(self.ignore_repos, list)
        repos = [
            repo for repo in self.user.get_repos() if repo.name not in self.ignore_repos
        ]
        setattr(self, "repos", repos)

    def get_repo_df(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        repo_df = (
            pd.concat(
                [get_repo_details(repo) for repo in self.repos], ignore_index=True
            )
            .sort_values(by="repo")
            .reset_index(drop=True)
        )
        setattr(self, "repo_df", repo_df)

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
    github_con, user, org = get_connection()
    print(get_user_gh_df(user))
