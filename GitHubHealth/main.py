"""
Helper functions to parse repo details.
Main function handles logic to connect to GitHub and select repos for analysis.
"""

from github import MainClass
from github.GithubException import UnknownObjectException

from .requested_object import (
    RequestedObject,
    get_connection,
)
from .utils import (
    TIMEOUT,
    render_repo_html_table,
)

ACCESS_TOKEN_VAR_NAME = "GITHUB_TOKEN"


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
