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
    SEARCH_DF_COLUMNS,
    TIMEOUT,
    get_ghh_plot,
    get_ghh_repo_plot,
    get_repo_details,
    get_branch_df,
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


class Metadata:
    """
    Class for holding metadata from a requested object.
    """

    def __init__(self, requested_object, input_from=1, input_to=10):
        """
        Set self up like search results.
        """
        self.requested_object = requested_object
        if (input_to < 1) or (input_from < 1):
            raise ValueError
        if input_to < input_from:
            raise ValueError
        if (input_to - input_from) > 50:
            warnings.warn(UserWarning("max number of requested results is 50"))
            input_to = max((input_to - 50), (input_from + 1))
        self.input_from = input_from
        self.input_to = input_to
        self.retrieved = -1
        self.total = -1
        self.metadata_df = pd.DataFrame()
        self.metadata_html = None

    def set_input_limits(self, input_from, input_to):
        """
        Increase or decrease input limits.
        """
        if input_to < input_from:
            raise ValueError("input_to must be greater than input_from")
        if (input_to - input_from) > 50:
            warnings.warn(UserWarning("max number of requested results is 50"))
            input_to = max((input_to - 50), (input_from + 1))
        setattr(self, "input_from", input_from)
        setattr(self, "input_to", input_to)

    def get_metadata(self):
        """
        resource_type, resource_name
        url is external link to github
        health is internal link dynamically created by javascript in user.html
        """
        metadata_dict = {akey: [] for akey in SEARCH_DF_COLUMNS}
        i = 0
        self.requested_object.get_repos()
        self.requested_object.get_orgs()
        self.requested_object.get_teams()
        for repo in self.requested_object.repos:
            i += 1
            if self.input_from <= i <= self.input_to:
                metadata_dict["resource"].append("repo")
                metadata_dict["owner"].append(repo.owner.login)
                metadata_dict["name"].append(repo.name)
                metadata_dict["url"].append(repo.html_url)
                metadata_dict["health"].append("health")
        for org in self.requested_object.orgs:
            i += 1
            if self.input_from <= i <= self.input_to:
                metadata_dict["resource"].append("org")
                metadata_dict["owner"].append(org.owner.login)
                metadata_dict["name"].append(org.name)
                metadata_dict["url"].append(org.html_url)
                metadata_dict["health"].append("health")
        for team in self.requested_object.teams:
            i += 1
            if self.input_from <= i <= self.input_to:
                metadata_dict["resource"].append("team")
                metadata_dict["owner"].append(team.owner.login)
                metadata_dict["name"].append(team.name)
                metadata_dict["url"].append(team.members_url)
                metadata_dict["health"].append("health")
        metadata_df = pd.DataFrame.from_dict(metadata_dict).reset_index(drop=True)
        retrieved = self.input_to - self.input_from
        total = (
            len(self.requested_object.repos)
            + len(self.requested_object.orgs)
            + len(self.requested_object.teams)
        )
        if total < self.input_to:
            warnings.warn(UserWarning("more results requested than available"))
            setattr(self, "input_to", total)
        if self.input_from > self.input_to:
            warnings.warn(UserWarning("results start greater than results end"))
            setattr(self, "input_from", self.input_to)
        setattr(self, "metadata_df", metadata_df)
        setattr(self, "retrieved", retrieved)
        setattr(self, "total", total)

    def get_metadata_html(self):
        """
        Main method to parse object metadata into pandas DataFrame.
        """
        if self.metadata_df is None:
            self.get_metadata()
        metadata_html = render_metadata_html_table(
            self.metadata_df, table_id="user-metadata"
        )
        setattr(self, "metadata_html", metadata_html)


# pylint: disable=too-few-public-methods
class DummyResults:
    """
    Probably a better way of doing this.
    """

    totalCount = 0


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
        repos=False,
        ignore=None,
        input_from=1,
        input_to=10,
    ):
        """
        Filter and repos bool will be added.  Avoid the dodo word.
        """
        if ignore is None:
            ignore = ""
        search_request = search_request.strip("")
        assert isinstance(search_request, str)
        assert isinstance(users, bool)
        assert isinstance(orgs, bool)
        assert isinstance(repos, bool)
        assert isinstance(ignore, str)
        self.ghh = ghh
        self.search_request = search_request
        self.users = users
        self.orgs = orgs
        self.repos = repos
        self.ignore = []
        if (input_to < 1) or (input_from < 1):
            raise ValueError
        if input_to < input_from:
            raise ValueError
        if (input_to - input_from) > 50:
            warnings.warn(UserWarning("max number of requested results is 50"))
            input_to = max((input_to - 50), (input_from + 1))
        self.input_from = input_from
        self.input_to = input_to
        self.get_ignore(ignore)
        self.total = -1
        self.retrieved = -1
        self.table_df = None
        self.html = None
        self.user_results = None
        self.repo_results = None

    def set_input_limits(self, input_from, input_to):
        """
        Increase or decrease input limits.
        """
        if input_to < input_from:
            raise ValueError("input_to must be greater than input_from")
        if (input_to - input_from) > 50:
            warnings.warn(UserWarning("max number of requested results is 50"))
            input_to = max((input_to - 50), (input_from + 1))
        setattr(self, "input_from", input_from)
        setattr(self, "input_to", input_to)

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
        if self.users is True:
            user_results = self.ghh.con.search_users(self.search_request)
        else:
            user_results = DummyResults()
        if self.repos is True:
            repo_results = self.ghh.con.search_repositories(self.search_request)
        else:
            repo_results = DummyResults()
        total = user_results.totalCount + repo_results.totalCount
        requested = self.input_to - self.input_from + 1
        if total < self.input_to:
            warnings.warn(UserWarning("more results requested than available"))
            setattr(self, "input_to", total)
        if self.input_from > self.input_to:
            warnings.warn(UserWarning("results start greater than results end"))
            setattr(self, "input_from", max((self.input_to - requested), 1))
        setattr(self, "user_results", user_results)
        setattr(self, "repo_results", repo_results)
        setattr(self, "total", total)
        logger.info("search user_results count: %s", self.user_results.totalCount)
        logger.info("search repo_results count: %s", self.repo_results.totalCount)
        logger.info("search total: %s", total)

    def get_slices(self):
        """
        Check requested results from and to against retrieved results and return indices.
        """
        assert self.input_to >= self.input_from
        requested_total = self.input_to - self.input_from + 1
        user_total = self.user_results.totalCount
        repo_total = self.repo_results.totalCount
        results_total = user_total + repo_total
        if self.input_from > results_total:
            # more requested than exist
            # shift input_from and input_to by requested_total
            warnings.warn(
                UserWarning(
                    "requested results start out of range.  setting to total - range"
                )
            )
            input_from = max((results_total - requested_total), 1)
            input_to = self.input_to + requested_total
            setattr(self, "input_from", input_from)
            setattr(self, "input_to", input_to)
        # some of user none of repo
        if (self.input_from <= user_total) and (self.input_to <= user_total):
            user_start = self.input_from - 1
            user_end = self.input_to
            repo_start = None
            repo_end = None
        # some of user some of repo
        elif self.input_from <= user_total < self.input_to:
            user_start = self.input_from - 1
            user_end = user_total
            user_retrieved = user_end - user_start
            remaining = requested_total - user_retrieved
            repo_start = 0
            repo_end = remaining
            if remaining > repo_total:
                repo_end = repo_total
        # none of user some of repo
        elif (self.input_from > user_total) and (self.input_to >= user_total):
            user_start = None
            user_end = None
            repo_start = self.input_from - user_total - 1
            remaining = requested_total
            repo_end = repo_start + remaining
        else:
            raise Exception("this should not occur")
        return user_start, user_end, repo_start, repo_end

    def get_output_results(self):
        """
        Retrieve slices and use them for temporary results. Use these to get table.
        """
        user_start, user_end, repo_start, repo_end = self.get_slices()
        # pylint: disable=unsubscriptable-object
        logger.info("user_start: %s, user_end: %s", user_start, user_end)
        logger.info("repo_start: %s, repo_end: %s", user_start, user_end)
        # slicing returns Slice object and not PaginatedList
        if user_start is None and user_end is None:
            user_results = []
        else:
            user_results = self.user_results[user_start:user_end]
        if repo_start is None and repo_end is None:
            repo_results = []
        else:
            repo_results = self.repo_results[repo_start:repo_end]
        metadata_dict = {akey: [] for akey in SEARCH_DF_COLUMNS}
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
        table_df = pd.DataFrame.from_dict(metadata_dict).reset_index(drop=True)
        html = render_metadata_html_table(table_df, table_id="search-metadata")
        setattr(self, "retrieved", len(table_df))
        setattr(self, "table_df", table_df)
        setattr(self, "html", html)


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
        self.metadata = None
        self.metadata_html = None
        self.repos = []
        self.repo_dict = None
        self.repo_df = None
        self.plots = []

    def get_repo(self, repo_name):
        """
        Get a specific repo for this object.
        """
        return self.obj.get_repo(repo_name)

    def get_repos(self, ignore=None):
        """
        Get repos of requested object.
        """
        if ignore is None:
            ignore = []
        repos = [x for x in self.obj.get_repos() if x.name not in ignore]
        setattr(self, "repos", repos)

    def get_orgs(self, ignore=None):
        """
        Get repos of requested object.
        """
        if ignore is None:
            ignore = []
        orgs = [x for x in self.obj.get_orgs() if x.name not in ignore]
        setattr(self, "orgs", orgs)

    def get_teams(self, ignore=None):
        """
        Get repos of requested object.
        """
        if ignore is None:
            ignore = []
        teams = [x for x in self.obj.get_teams() if x.name not in ignore]
        setattr(self, "teams", teams)

    def return_repos(self, ignore=None):
        """
        Get repos of requested object.
        """
        if ignore is None:
            ignore = []
        if self.repos == []:
            self.get_repos(ignore=ignore)
        return self.repos

    def get_metadata(self):
        """
        Main method to parse object metadata into pandas DataFrame.
        """
        metadata = Metadata(self)
        metadata.get_metadata()
        setattr(self, "metadata", metadata)

    def get_metadata_html(self):
        """
        Main method to parse object metadata into pandas DataFrame.
        """
        if self.metadata is None:
            self.get_metadata()
        self.metadata.get_metadata_html()
        setattr(self, "metadata_html", self.metadata.metadata_html)

    def get_repo_df(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        if self.repos == []:
            self.get_repos()
        repo_df = (
            pd.concat(
                [REPOS_TEMPLATE_DF] + [get_repo_details(repo) for repo in self.repos],
                ignore_index=True,
            )
            .sort_values(by="repo")
            .reset_index(drop=True)
        )
        repo_dict = repo_df.to_dict(orient="list")
        setattr(self, "repo_dict", repo_dict)
        setattr(self, "repo_df", repo_df)

    def get_plots(self):
        """
        Get plots from repo df.
        """
        branch_count_plot = get_ghh_plot(self.repo_df, "branch count")
        branch_age_max_plot = get_ghh_plot(self.repo_df, "max branch age (days)")
        branch_age_min_plot = get_ghh_plot(self.repo_df, "min branch age (days)")
        issues_plot = get_ghh_plot(self.repo_df, "issues")
        pr_plot = get_ghh_plot(self.repo_df, "pull requests")
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
        repo_df = get_branch_df(self.obj)
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
