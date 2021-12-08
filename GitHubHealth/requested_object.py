"""
RequesteObject class define attributes for easily retrieval.
"""

import logging
import warnings

import pandas as pd

from github import (
    Github,
    MainClass,
)
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser
from github.Organization import Organization
from github.Repository import Repository

from .utils import (
    REPOS_TEMPLATE_DF,
    TIMEOUT,
    get_ghh_plot,
    get_ghh_repo_plot,
    get_repo_details,
    get_single_repo_details,
    render_metadata_html_table,
    render_single_repo_html_table,
)

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


# pylint: disable=too-many-arguments
def get_connection(
    hostname=None,
    user=None,
    password=None,
    gat=None,
    timeout=TIMEOUT,
    results_limit=None,
):
    """
    Get connection and login.
    """
    if hostname is None:
        base_url = MainClass.DEFAULT_BASE_URL
    elif hostname == "github.com":
        base_url = MainClass.DEFAULT_BASE_URL
    else:
        base_url = f"https://{hostname}/api/v3"
    if results_limit is None:
        results_limit = 10
    assert isinstance(results_limit, int)
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
    this_user = RequestedObject(this_user, this_user.html_url, results_limit)
    return github_con, this_user


# pylint: disable=too-many-instance-attributes
class SearchResults:
    """
    Use ghh object to search for users and/or orgs.
    """

    def __init__(
        self,
        ghh,
        search_request,
        users=False,
        orgs=False,
        ignore=None,
        results_limit=10,
    ):
        self.ghh = ghh
        self.search_request = search_request
        self.users = users
        self.orgs = orgs
        self.ignore = []
        self.get_ignore(ignore)
        self.results_limit = results_limit
        self.table_df = None
        self.table = None

    def get_ignore(self, ignore):
        """
        format ignore string to list.
        """
        if ignore is None:
            ignore = ""
        ignore = ignore.strip()
        ignore = ignore.split(",")
        setattr(self, "ignore", ignore)

    def search(self):
        """
        Let's search for some shit.
        """
        user_results = self.ghh.con.search_users(self.search_request)
        repo_results = self.ghh.con.search_repositories(self.search_request)
        logger.info("search user_results count: %s", user_results.totalCount)
        logger.info("search repo_results count: %s", repo_results.totalCount)
        if user_results.totalCount > self.results_limit:
            user_results = user_results[: self.results_limit]
        if repo_results.totalCount > self.results_limit:
            repo_results = repo_results[: self.results_limit]
        metadata_dict = {
            "resource": [],
            "owner": [],
            "name": [],
            "url": [],
            "health": [],
        }
        for user in user_results:
            if isinstance(user, NamedUser):
                if user.login not in self.ignore:
                    metadata_dict["resource"].append("user")
                    metadata_dict["owner"].append(user.login)
                    metadata_dict["name"].append(user.login)
                    metadata_dict["url"].append(user.html_url)
                    metadata_dict["health"].append("health")
            else:
                warnings.warn(
                    f"unexpected search result found: {type(user)} {user.login}"
                )
        for repo in repo_results:
            if isinstance(repo, Repository):
                if repo.name not in self.ignore:
                    metadata_dict["resource"].append("repo")
                    metadata_dict["owner"].append(repo.owner.login)
                    metadata_dict["name"].append(repo.name)
                    metadata_dict["url"].append(repo.html_url)
                    metadata_dict["health"].append("health")
            else:
                warnings.warn(
                    f"unexpected search result found: {type(repo)} {repo.name}"
                )
        table = pd.DataFrame.from_dict(metadata_dict).reset_index(drop=True)
        html_table = render_metadata_html_table(table, table_id="search-metadata")
        setattr(self, "table_df", table)
        setattr(self, "table", html_table)


# pylint: disable=too-many-instance-attributes
class RequestedObject:
    """
    Container for requested objects.
    """

    def __init__(self, obj, url, results_limit):
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
        elif isinstance(obj, Repository):
            self.name = self.obj.name
        self.url = url
        self.metadata_df = None
        self.metadata_limit = results_limit
        self.metadata_limit_reached = False
        self.metadata_html = None
        self.repos = []
        self.repo_df = None
        self.plots = []

    def increase_metadata_limit(self, increment=2):
        """
        Add more to metadata limit.
        """
        increment = max(0, increment)
        self.metadata_limit += increment

    def get_repos(self, ignore=None):
        """
        Get repos of requested object.
        """
        if ignore is None:
            ignore = []
        repos = [x for x in self.obj.get_repos() if x.name not in ignore]
        setattr(self, "repos", repos)

    def return_repos(self, ignore=None):
        """
        Get repos of requested object.
        """
        if ignore is None:
            ignore = []
        if self.repos == []:
            self.get_repos(ignore=ignore)
        return self.repos

    def get_metadata_df(self):
        """
        Main method to parse object metadata into pandas DataFrame.
        """
        limit = self.metadata_limit
        # resource_type, resource_name
        # url is external link to github
        # health is internal link dynamically created by javascript in user.html
        metadata_dict = {
            "resource": [],
            "owner": [],
            "name": [],
            "url": [],
            "health": [],
        }
        metadata_limit_reached = False
        repos = self.obj.get_repos()
        if repos.totalCount > limit:
            metadata_limit_reached = True
            repos = repos[:limit]
        orgs = self.obj.get_orgs()
        if orgs.totalCount > limit:
            metadata_limit_reached = True
            orgs = orgs[:limit]
        teams = self.obj.get_teams()
        if teams.totalCount > limit:
            metadata_limit_reached = True
            teams = teams[:limit]
        for repo in repos:
            metadata_dict["resource"].append("repo")
            metadata_dict["owner"].append(repo.owner.login)
            metadata_dict["name"].append(repo.name)
            metadata_dict["url"].append(repo.html_url)
            metadata_dict["health"].append("health")
        for org in orgs:
            metadata_dict["resource"].append("org")
            metadata_dict["owner"].append(org.owner.login)
            metadata_dict["name"].append(org.name)
            metadata_dict["url"].append(org.html_url)
            metadata_dict["health"].append("health")
        for team in teams:
            metadata_dict["resource"].append("team")
            metadata_dict["owner"].append(team.owner.login)
            metadata_dict["name"].append(team.name)
            metadata_dict["url"].append(team.members_url)
            metadata_dict["health"].append("health")
        metadata_df = pd.DataFrame.from_dict(metadata_dict).reset_index(drop=True)
        setattr(self, "metadata_df", metadata_df)
        setattr(self, "metadata_limit_reached", metadata_limit_reached)

    def get_metadata_html(self):
        """
        Main method to parse object metadata into pandas DataFrame.
        """
        if self.metadata_df is None:
            self.get_metadata_df()
        metadata_html = render_metadata_html_table(
            self.metadata_df, table_id="table-metadata"
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
        branch_count_plot = get_ghh_plot(self.repo_df, "branch_count")
        branch_age_max_plot = get_ghh_plot(self.repo_df, "max_branch_age_days")
        branch_age_min_plot = get_ghh_plot(self.repo_df, "min_branch_age_days")
        issues_plot = get_ghh_plot(self.repo_df, "issues")
        pr_plot = get_ghh_plot(self.repo_df, "pull_requests")
        plots = [
            branch_count_plot,
            branch_age_max_plot,
            branch_age_min_plot,
            issues_plot,
            pr_plot,
        ]
        plots = [x.configure_view(discreteWidth=300).to_json() for x in plots]
        setattr(self, "plots", plots)


class RequestedRepo(RequestedObject):
    """
    Container for requested objects.
    """

    def get_repo_df(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        repo_df = get_single_repo_details(self.obj)
        setattr(self, "repo_df", repo_df)

    def get_plots(self):
        """
        Get plots from repo df.
        """
        branch_age_plot = get_ghh_repo_plot(self.repo_df, "age (days)")
        protected_plot = get_ghh_repo_plot(self.repo_df, "protected")
        plots = [
            branch_age_plot,
            protected_plot,
        ]
        plots = [x.configure_view(discreteWidth=300).to_json() for x in plots]
        setattr(self, "plots", plots)

    def get_html_table(self):
        """
        Get html table.
        """
        if self.repo_df is None:
            self.get_repo_df()
        html_table = render_single_repo_html_table(
            self.repo_df, table_id="repo-metadata"
        )
        setattr(self, "html_table", html_table)
