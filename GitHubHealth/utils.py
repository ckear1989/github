"""
Helper functions for GitHubHealth class and app.
"""

from copy import deepcopy
from datetime import datetime

import altair as alt
import pandas as pd
from requests.exceptions import ReadTimeout

BRANCH_DF_COLUMNS = ["branch", "age"]
BRANCH_TEMPLATE_DF = pd.DataFrame(columns=BRANCH_DF_COLUMNS)
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_NOW = datetime.now()
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
TIMEOUT = 2


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
    # will handle these errors later but for now let the value propagate through as None
    issues, _ = get_paginated_list_len(repo.get_issues())
    pull_requests, _ = get_paginated_list_len(repo.get_pulls())
    repo_dict = {
        "repo": [repo.name],
        "repo_url": [repo.html_url],
        "private": [repo.private],
        "branch_count": [len(branch_df)],
        "min_branch_age_days": [branch_df["age"].min()],
        "max_branch_age_days": [branch_df["age"].max()],
        "issues": [issues],
        "pull_requests": [pull_requests],
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
    try:
        this_len = sum([1 for i in pl_obj])
        error_message = None
    except ReadTimeout as to_error:
        this_len = None
        error_message = to_error
    return this_len, error_message


def link_repo_name_url(name, url, target="_blank"):
    """
    concat repo name and url in hyperlink
    """
    return f"<a target='{target}' href='{url}'>{name}</a>"


def render_metadata_html_table(metadata_df, table_id=None):
    """
    format repo_df to html.
    """
    metadata_df_cpy = deepcopy(metadata_df)
    if len(metadata_df_cpy) > 0:
        metadata_df_cpy["name"] = metadata_df_cpy.apply(
            lambda x: link_repo_name_url(x["name"], x["url"]), axis=1
        )
        metadata_df_cpy.drop("url", axis=1, inplace=True)

    repo_html = metadata_df_cpy.style.hide_index()
    if table_id is not None:
        repo_html.set_uuid(table_id)
    repo_html = repo_html.render()
    return repo_html


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


def get_ghh_plot(plot_df, var):
    """
    Standard formatting of ghh plot.
    """
    plot = (
        alt.Chart(plot_df)
        .mark_bar()
        .encode(
            x="repo",
            y=var,
            tooltip=var,
        )
        .interactive()
        .properties(title=f"{var.replace('_', ' ')} by repo")
    )
    return plot
