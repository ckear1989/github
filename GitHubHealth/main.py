"""
Helper functions to parse repo details.
Main function handles logic to connect to GitHub and select repos for analysis.
"""

from github import MainClass
from github.GithubException import UnknownObjectException

from .requested_object import (
    RequestedObject,
    RequestedRepo,
    SearchResults,
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
        timeout (int)       : default TIMEOUT
    """

    def __init__(
        self,
        hostname=None,
        login=None,
        password=None,
        gat=None,
        timeout=TIMEOUT,
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
        self.con, self.user = get_connection(
            hostname,
            login,
            password,
            gat,
            timeout,
        )
        self.username = self.user.name
        self.user_url = self.user.url
        self.repos = []
        self.repo_dfs = {}
        self.repo_html = {}
        self.plots = None
        self.requested_df = None
        self.requested_object = None
        self.requested_user = None
        self.requested_org = None
        self.search_results = None

    def get_repo(self, repo_owner, repo_name):
        """
        Method to get repos as a class object.
        """
        this_repo = self.con.get_repo(f"{repo_owner}/{repo_name}")
        requested_repo = RequestedRepo(
            this_repo,
            this_repo.html_url,
        )
        return requested_repo

    def search(
        self,
        search_request,
        **kwargs,
    ):
        """
        Search for users and/or orgs and get results table.
        """
        search_results = SearchResults(self, search_request, **kwargs)
        search_results.search()
        search_results.get_output_results()
        setattr(self, "search_results", search_results)

    def get_requested_object(self, resource_name):
        """
        Method to get repos as a class object.
        """
        try:
            this_user = self.con.get_user(resource_name)
            requested_user = RequestedObject(
                this_user,
                this_user.html_url,
            )
        except UnknownObjectException:
            requested_user = RequestedObject(
                None,
                f"{self.public_url}/{resource_name}",
            )
        setattr(self, "requested_object", requested_user)

    def get_requested_repos(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        self.requested_object.get_repos()
        setattr(self, "requested_repos", self.requested_object.repos)

    def get_requested_df(self):
        """
        Main method to parse repo details into pandas DataFrame.
        """
        self.requested_object.get_repo_df()
        setattr(self, "requested_df", self.requested_object.repo_df)

    def render_requested_html_table(self):
        """
        Render pandas df to html with formatting of cells etc.
        """
        requested_html = render_repo_html_table(
            self.requested_df, table_id="requested-obj-metadata"
        )
        setattr(self, "repo_html", requested_html)

    def get_plots(self):
        """
        get altair plot objects as html.
        """
        self.requested_object.get_plots()
        setattr(self, "plots", self.requested_object.plots)
