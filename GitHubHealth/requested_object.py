"""
RequesteObject class define attributes for easily retrieval.
"""

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
        elif isinstance(obj, Repository):
            self.name = self.obj.name
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
        # resource_type, resource_name
        # url is external link to github
        # health is internal link dynamically created by javascript in user.html
        metadata_dict = {"resource": [], "name": [], "url": [], "health": []}
        for repo in self.obj.get_repos():
            metadata_dict["resource"].append("repo")
            metadata_dict["name"].append(repo.name)
            metadata_dict["url"].append(repo.html_url)
            metadata_dict["health"].append("health")
        for resource in self.obj.get_orgs():
            metadata_dict["resource"].append("org")
            metadata_dict["name"].append(resource.name)
            metadata_dict["url"].append(resource.html_url)
            metadata_dict["health"].append("health")
        for resource in self.obj.get_teams():
            metadata_dict["resource"].append("team")
            metadata_dict["name"].append(resource.name)
            metadata_dict["url"].append(resource.html_url)
            metadata_dict["health"].append("health")
        metadata_df = pd.DataFrame.from_dict(metadata_dict).reset_index(drop=True)
        setattr(self, "metadata_df", metadata_df)

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
        branch_age_plot = get_ghh_repo_plot(self.repo_df, "age")
        plots = [
            branch_age_plot,
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
            self.repo_df,
        )
        setattr(self, "html_table", html_table)
