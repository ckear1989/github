"""
Helper functions to parse repo details.
Main function handles logic to connect to GitHub and select repos for analysis.
"""
from datetime import datetime
import os

import pandas as pd
from github import Github

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_NOW = datetime.now()


def get_connection():
    """
    Get connection and login.
    """
    github_con = Github(login_or_token=os.getenv("GITHUB_ACCESS_TOKEN"))
    user = github_con.get_user()
    _ = user.login
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


def main():
    """
    Main method to parse repo details into pandas DataFrame.
    """
    github_con = get_connection()
    user = github_con.get_user()
    repo_df = pd.concat(
        [get_repo_details(repo) for repo in user.get_repos()], ignore_index=True
    )
    # orgs = user.get_orgs():
    return repo_df


if __name__ == "__main__":
    main()
