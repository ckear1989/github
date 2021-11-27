"""
Helper functions to parse repo details.
Main function handles logic to connect to GitHub and select repos for analysis.
"""
from copy import deepcopy
from datetime import datetime
import os

import altair as alt
import pandas as pd
from github import Github, MainClass
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser
from github.Organization import Organization
from github.GithubException import UnknownObjectException


DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_NOW = datetime.now()
ACCESS_TOKEN_VAR_NAME = "GITHUB_TOKEN"
TIMEOUT = 2
BRANCH_DF_COLUMNS = ["branch", "age"]
BRANCH_TEMPLATE_DF = pd.DataFrame(columns=BRANCH_DF_COLUMNS)
REPOS_DF_COLUMNS = [
    "repo",
    "repo_url",
    "private",
    "branch_count",
    "min_branch_age_days",
    "max_branch_age_days",
    "issues",
    "pull_requests",
]
REPOS_TEMPLATE_DF = pd.DataFrame(columns=REPOS_DF_COLUMNS)

# pylint: disable=redefined-outer-name


def get_connection(hostname=None, user=None, password=None, gat=None, timeout=TIMEOUT):
    """
    Get connection and login.
    """
    if hostname is None:
        base_url = MainClass.DEFAULT_BASE_URL
    elif hostname == "github.com":
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
    _ = this_user.login
    this_user = RequestedObject(this_user, this_user.html_url)
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
    # print(dir(repo))
    repo_dict = {
        "repo": [repo.name],
        "repo_url": [repo.html_url],
        "private": [repo.private],
        "branch_count": [len(branch_df)],
        "min_branch_age_days": [branch_df["age"].min()],
        "max_branch_age_days": [branch_df["age"].max()],
        "issues": get_paginated_list_len(repo.get_issues()),
        "pull_requests": get_paginated_list_len(repo.get_pulls()),
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


def get_paginated_list_len(pl_obj):
    """
    No inbuilt method to get length so iterate through?
    """
    return sum([1 for i in pl_obj])


def link_repo_name_url(name, url):
    """
    concat repo name and url in hyperlink
    """
    return f"<a href='{url}'>{name}</a>"


def render_repo_html_table(repo_df):
    """
    format repo_df to html.
    """
    repo_df_cpy = deepcopy(repo_df)
    repo_df_cpy["issues"] = repo_df_cpy["issues"].astype(int)
    repo_df_cpy["pull_requests"] = repo_df_cpy["pull_requests"].astype(int)
    if len(repo_df_cpy) > 0:
        repo_df_cpy["repo"] = repo_df_cpy.apply(
            lambda x: link_repo_name_url(x["repo"], x["repo_url"]), axis=1
        )
        repo_df_cpy.drop("repo_url", axis=1, inplace=True)

    repo_html = (
        repo_df_cpy.style.hide_index()
        .applymap(
            lambda x: "font-weight: bold" if x is False else None,
            subset=["private"],
        )
        .applymap(lambda x: format_gt_red(x, 45), subset=["min_branch_age_days"])
        .applymap(lambda x: format_gt_red(x, 90), subset=["max_branch_age_days"])
        .applymap(lambda x: format_gt_red(x, 3), subset=["branch_count"])
        .render(precision=0)
    )
    return repo_html


# pylint: disable=too-many-instance-attributes
class RequestedObject:
    """
    Container for requested objects.
    """

    def __init__(self, obj, url):
        self.obj = obj
        self.name = None
        self.avatar_url = None
        if isinstance(obj, AuthenticatedUser):
            self.name = self.obj.login
            self.avatar_url = obj.avatar_url
        if isinstance(obj, NamedUser):
            self.name = self.obj.login
            self.avatar_url = obj.avatar_url
        elif isinstance(obj, Organization):
            self.name = self.obj.login
            self.avatar_url = obj.avatar_url
        self.url = url
        self.metadata_df = None
        self.metadata_html = None
        self.repos = []
        self.repo_df = None
        self.plots = []

    def get_repos(self, ignore_repos=None):
        """
        Get repos of requested object.
        """
        if ignore_repos is None:
            ignore_repos = []
        repos = [x for x in self.obj.get_repos() if x.name not in ignore_repos]
        setattr(self, "repos", repos)

    def return_repos(self, ignore_repos=None):
        """
        Get repos of requested object.
        """
        if ignore_repos is None:
            ignore_repos = []
        if self.repos == []:
            self.get_repos(ignore_repos=ignore_repos)
        return self.repos

    def get_metadata_df(self):
        """
        Main method to parse object metadata into pandas DataFrame.
        """
        metadata_dict = {
            "repos": [get_paginated_list_len(self.obj.get_repos())],
            "orgs": [get_paginated_list_len(self.obj.get_orgs())],
            "teams": [get_paginated_list_len(self.obj.get_teams())],
        }
        metadata_df = pd.DataFrame.from_dict(metadata_dict).reset_index(drop=True)
        setattr(self, "metadata_df", metadata_df)

    def get_metadata_html(self):
        """
        Main method to parse object metadata into pandas DataFrame.
        """
        if self.metadata_df is None:
            self.get_metadata_df()
        metadata_html = self.metadata_df.to_html(
            classes="dataframe",
            table_id="table-metadata",
            index=False,
        )
        setattr(self, "metadata_html", metadata_html)

    def get_repo_df(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        repo_df = (
            pd.concat(
                [REPOS_TEMPLATE_DF] + [get_repo_details(repo) for repo in self.repos],
                ignore_index=True,
            )
            .sort_values(by="repo")
            .reset_index(drop=True)
        )
        setattr(self, "repo_df", repo_df)

    def get_plots(self):
        """
        Get plots from repo df.
        """
        branch_count_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y="branch_count",
            )
            .interactive()
            .properties(title="branch count by repo")
        )
        # debug by saving plots to see raw html
        # branch_count_plot_noni = (
        #     alt.Chart(self.repo_df)
        #     .mark_bar()
        #     .encode(
        #         x="repo",
        #         y="branch_count",
        #     )
        #     .properties(title="branch count by repo")
        # )
        # if self.name == "ckear1989":
        #     branch_count_plot.save("branch_count_plot.html")
        #     branch_count_plot_noni.save("branch_count_plot_noni.html")
        branch_age_max_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y=alt.Y(
                    "max_branch_age_days",
                    sort=alt.EncodingSortField(
                        field="max_branch_age_days", op="sum", order="descending"
                    ),
                ),
            )
            .interactive()
            .properties(title="max branch age by repo")
        )
        branch_age_min_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y=alt.Y(
                    "min_branch_age_days",
                    sort=alt.EncodingSortField(
                        field="min_branch_age_days", op="sum", order="descending"
                    ),
                ),
            )
            .interactive()
            .properties(title="min branch age by repo")
        )
        issues_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y=alt.Y(
                    "issues",
                    sort=alt.EncodingSortField(
                        field="issues", op="sum", order="descending"
                    ),
                ),
            )
            .interactive()
            .properties(title="issues by repo")
        )
        pr_plot = (
            alt.Chart(self.repo_df)
            .mark_bar()
            .encode(
                x="repo",
                y=alt.Y(
                    "pull_requests",
                    sort=alt.EncodingSortField(
                        field="pull_requests", op="sum", order="descending"
                    ),
                ),
            )
            .interactive()
            .properties(title="pull requests by repo")
        )
        plots = [
            branch_count_plot,
            branch_age_max_plot,
            branch_age_min_plot,
            issues_plot,
            pr_plot,
        ]
        plots = [x.configure_view(discreteWidth=300).to_json() for x in plots]
        setattr(self, "plots", plots)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
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
        if hostname is None:
            self.base_url = MainClass.DEFAULT_BASE_URL
        elif hostname == "github.com":
            self.base_url = MainClass.DEFAULT_BASE_URL
        else:
            self.base_url = f"https://{hostname}/api/v3"
        self.public_url = f"https://{hostname}/"

        self.con, self.user = get_connection(hostname, login, password, gat, timeout)
        self.username = self.user.name
        self.user_url = self.user.url
        self.repos = []
        self.repo_dfs = {}
        self.repo_html = {}
        self.plots = None
        self.requested_user = None
        self.requested_org = None

    def get_repos(self, search_request, users=False, orgs=False, ignore_repos=None):
        """
        Method to get repos as a class object.
        """
        if ignore_repos is None:
            ignore_repos = ""
        search_request = search_request.strip("")
        assert isinstance(search_request, str)
        assert isinstance(users, bool)
        assert isinstance(orgs, bool)
        assert isinstance(ignore_repos, str)
        ignore_repos = ignore_repos.split(",")
        assert isinstance(ignore_repos, list)
        repos = {
            "users": [],
            "orgs": [],
        }
        if users is True:
            try:
                this_user = self.con.get_user(search_request)
                requested_user = RequestedObject(this_user, this_user.html_url)
                requested_user.get_repos(ignore_repos)
                repos["users"] = requested_user.return_repos()
            except UnknownObjectException:
                requested_user = RequestedObject(
                    None, f"{self.public_url}/{search_request}"
                )
        else:
            requested_user = RequestedObject(
                None, f"{self.public_url}/{search_request}"
            )
        if orgs is True:
            try:
                this_org = self.con.get_organization(search_request)
                requested_org = RequestedObject(this_org, this_org.html_url)
                requested_org.get_repos(ignore_repos)
                repos["orgs"] = requested_org.return_repos()
            except UnknownObjectException:
                requested_org = RequestedObject(
                    None, f"{self.public_url}/{search_request}"
                )
        else:
            requested_org = RequestedObject(None, f"{self.public_url}/{search_request}")
        setattr(self, "repos", repos)
        setattr(self, "requested_user", requested_user)
        setattr(self, "requested_org", requested_org)

    def get_repo_dfs(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        self.requested_user.get_repo_df()
        self.requested_org.get_repo_df()
        repo_dfs = {
            "users": self.requested_user.repo_df,
            "orgs": self.requested_org.repo_df,
        }
        setattr(self, "repo_dfs", repo_dfs)

    def render_repo_html_tables(self):
        """
        Render pandas df to html with formatting of cells etc.
        """
        user_repo_html = render_repo_html_table(self.repo_dfs["users"])
        org_repo_html = render_repo_html_table(self.repo_dfs["orgs"])
        repo_html = {
            "users": user_repo_html,
            "orgs": org_repo_html,
        }
        setattr(self, "repo_html", repo_html)

    def get_plots(self):
        """
        get altair plot objects as html.
        """
        self.requested_user.get_plots()
        self.requested_org.get_plots()
        plots = {
            "users": self.requested_user.plots,
            "orgs": self.requested_org.plots,
        }
        setattr(self, "plots", plots)


if __name__ == "__main__":
    github_con, user = get_connection(
        user="ckear1989", gat=os.environ[ACCESS_TOKEN_VAR_NAME]
    )
    print(get_user_gh_df(user))
