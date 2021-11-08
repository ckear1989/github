"""
Helper functions to parse repo details.
Main function handles logic to connect to GitHub and select repos for analysis.
"""
from datetime import datetime
import os

import altair as alt
import pandas as pd
from github import Github, MainClass

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_NOW = datetime.now()

# pylint: disable=redefined-outer-name


def get_connection(hostname=None, user=None, org=None):
    """
    Get connection and login.
    """
    if hostname is None:
        base_url = MainClass.DEFAULT_BASE_URL
    else:
        base_url = f"https://{hostname}/api/v3"
    github_con = Github(
        base_url=base_url, login_or_token=os.getenv("GITHUB_ACCESS_TOKEN")
    )
    this_user = github_con.get_user()
    this_user_name = this_user.login
    if user is not None:
        assert user == this_user_name
    if org is not None:
        assert org in this_user.get_orgs()
    return github_con


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
        "max_branch_age": [branch_df["age"].max()],
    }
    repo_df = pd.DataFrame.from_dict(repo_dict)
    return repo_df


def format_gt_red(val, red_length):
    """
    Helper function to get css style of color for cell value.
    """
    # pylint: disable=consider-using-f-string
    return "color: {}".format("red" if val > red_length else "black")


def get_user_gh_df(user):
    """
    Main method to parse repo details into pandas DataFrame.
    """
    repo_df = pd.concat(
        [get_repo_details(repo) for repo in user.get_repos()], ignore_index=True
    ).sort_values(by="repo")
    return repo_df


class GitHubHealth:
    """
    Class object for GitHubHeath.
    Args:
        hostname (str): default None
        user (str):     default None
        org (str):      default None
    If user is None then try to get organisation for repo_table.
    If org is None then fall back on user retrieved from GITHUB_ACCESS_TOKEN.
    """

    def __init__(self, hostname=None, user=None, org=None):
        """
        Create connection and get table of repos base don user and org.
        """
        github_con = get_connection(hostname, user, org)
        self.user = github_con.get_user()
        self.username = self.user.login
        self.user_url = self.user.html_url
        self.repo_df = get_user_gh_df(self.user)
        self.repo_html = None
        self.plots = None

    def render_repo_html_table(self):
        """
        Render pandas df to html with formatting of cells etc.
        """
        repo_html = (
            self.repo_df.style.hide_index()
            .applymap(lambda x: format_gt_red(x, 90), subset=["max_branch_age"])
            .applymap(lambda x: format_gt_red(x, 3), subset=["branch_count"])
            .render()
        )
        self.repo_html = repo_html

    def get_plots(self):
        """
        get altair plot objects as html.
        """
        plots = []
        branch_count_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y="branch_count",
                # color="year:N",
                # column="site:N"
            )
        )
        bcp_json = branch_count_plot.to_json()
        plots.append(bcp_json)
        self.plots = plots


if __name__ == "__main__":
    github_con = get_connection()
    user = github_con.get_user()
    print(get_user_gh_df(user))
