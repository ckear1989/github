"""
Helper functions for GitHubHealth class and app.
"""

from copy import deepcopy
from datetime import datetime
import logging

import altair as alt
import numpy as np
import pandas as pd
from requests.exceptions import ReadTimeout

from github.Repository import Repository
from github.NamedUser import NamedUser

BRANCH_DF_COLUMNS = [
    "branch",
    "url",
    "sha",
    "last modified",
    "age (days)",
    "protected",
    "committer",
]
REPOS_DF_COLUMNS = [
    "repo",
    "repo_url",
    "private",
    "branch count",
    "min branch age (days)",
    "max branch age (days)",
    "issues",
    "pull requests",
    "primary language",
    "score",
]
SEARCH_DF_COLUMNS = [
    "resource",
    "owner",
    "name",
    "url",
    "health",
]
BRANCH_TEMPLATE_DF = pd.DataFrame(columns=BRANCH_DF_COLUMNS)
REPOS_TEMPLATE_DF = pd.DataFrame(columns=REPOS_DF_COLUMNS)
SEARCH_TEMPLATE_DF = pd.DataFrame(columns=SEARCH_DF_COLUMNS)
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATE_NOW = datetime.now()
TIMEOUT = 2
MIN_BR_LIMIT = 45
MAX_BR_LIMIT = 90
BC_LIMIT = 3
I_LIMIT = 1
PR_LIMIT = 1


logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def ghh_theme():
    """
    define the theme by returning the dictionary of configurations
    """
    return {
        "config": {
            "view": {
                "height": 500,
                "width": 500,
            },
            "mark": {
                "color": "black",
                "fill": "#1818ab",
                "stroke": "black",
                "strokeWidth": 10,
            },
            "axis": {
                "titleFontSize": "20",
                "labelFontSize": "20",
            },
            "title": {
                "fontSize": "20",
            },
        }
    }


def get_branch_details(branch):
    """
    Get information on branch from PyGitHub API and format in pandas DataFrame.
    """
    commit = branch.commit
    date = commit.commit.author.date
    age = (DATE_NOW - date).days
    committer = "unknown_user"
    if commit.committer is not None:
        committer = commit.committer.login
    branch_dict = {
        "branch": [branch.name],
        "url": [commit.html_url],
        "sha": [commit.sha[:7]],  # short sha should work
        "last modified": [commit.last_modified],
        "age (days)": [age],
        "protected": [branch.protected],
        "committer": [committer],
    }
    branch_df = pd.DataFrame.from_dict(branch_dict)
    return branch_df


def get_branch_df(repo):
    """
    Get information on repo from PyGitHub API and format in pandas DataFrame.
    """
    branch_df = pd.concat(
        [BRANCH_TEMPLATE_DF]
        + [get_branch_details(branch) for branch in repo.get_branches()],
        ignore_index=True,
    )
    return branch_df


def get_repo_details(repo, output="df"):
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
        "branch count": [len(branch_df)],
        "min branch age (days)": [branch_df["age (days)"].min()],
        "max branch age (days)": [branch_df["age (days)"].max()],
        "issues": [issues],
        "pull requests": [pull_requests],
    }
    languages = repo.get_languages()
    primary_language = None
    if len(languages) > 0:
        primary_language = sorted(languages.items(), key=lambda x: x[1], reverse=True)[
            0
        ][0]
    repo_dict["primary language"] = [primary_language]
    repo_dict["score"] = [get_health(repo_dict)]
    repo_df = pd.DataFrame.from_dict(repo_dict)
    if output == "df":
        return_obj = repo_df
    elif output == "dict":
        return_obj = repo_dict
    else:
        raise Exception('Expected output="df" or "dict", got {output}.')
    return return_obj


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
            [REPOS_TEMPLATE_DF]
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
        # this_len = sum([1 for i in pl_obj])
        this_len = pl_obj.totalCount
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
        metadata_df_cpy["owner"] = metadata_df_cpy.apply(
            lambda x: link_repo_name_url(
                x["owner"], "/".join(x["url"].split("/")[:-1])
            ),
            axis=1,
        )
        metadata_df_cpy["name"] = metadata_df_cpy.apply(
            lambda x: link_repo_name_url(x["name"], x["url"]), axis=1
        )
        metadata_df_cpy.drop("url", axis=1, inplace=True)

    repo_html = metadata_df_cpy.style.hide_index()
    if table_id is not None:
        repo_html.set_uuid(table_id)
    repo_html = repo_html.render()
    return repo_html


def render_single_repo_html_table(repo_df, table_id=None):
    """
    format repo_df to html.
    """
    repo_df_cpy = deepcopy(repo_df)
    if len(repo_df_cpy) > 0:
        repo_df_cpy["branch"] = repo_df_cpy.apply(
            lambda x: link_repo_name_url(
                x["branch"], "/".join(x["url"].split("/")[:-2] + ["tree", x["branch"]])
            ),
            axis=1,
        )
        repo_df_cpy["sha"] = repo_df_cpy.apply(
            lambda x: link_repo_name_url(x["sha"], x["url"]), axis=1
        )
        repo_df_cpy["committer"] = repo_df_cpy.apply(
            lambda x: link_repo_name_url(
                x["committer"], "/".join(x["url"].split("/")[:-4] + [x["committer"]])
            ),
            axis=1,
        )
        repo_df_cpy.drop("url", axis=1, inplace=True)
    repo_html = repo_df_cpy.style.hide_index()
    if table_id is not None:
        repo_html.set_uuid(table_id)
    repo_html = repo_html.render()
    return repo_html


def render_repo_html_table(repo_df, table_id=None):
    """
    format repo_df to html.
    """
    repo_df_cpy = deepcopy(repo_df)
    repo_df_cpy["issues"] = repo_df_cpy["issues"].astype(int)
    repo_df_cpy["pull requests"] = repo_df_cpy["pull requests"].astype(int)
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
        .applymap(
            lambda x: format_gt_red(x, MIN_BR_LIMIT), subset=["min branch age (days)"]
        )
        .applymap(
            lambda x: format_gt_red(x, MAX_BR_LIMIT), subset=["max branch age (days)"]
        )
        .applymap(lambda x: format_gt_red(x, BC_LIMIT), subset=["branch count"])
        .applymap(lambda x: format_gt_red(x, I_LIMIT), subset=["issues"])
        .applymap(lambda x: format_gt_red(x, PR_LIMIT), subset=["pull requests"])
    ).format(precision=0, na_rep="missing", formatter={"score": "{:.2f}"})
    if table_id is not None:
        repo_html.set_uuid(table_id)
    repo_html = repo_html.render()
    return repo_html


def get_ghh_plot(plot_df, var):
    """
    Standard formatting of ghh plot.
    """
    # register the custom theme under a chosen name
    alt.themes.register("ghh_theme", ghh_theme)
    # enable the newly registered theme
    alt.themes.enable("ghh_theme")
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


def get_ghh_repo_plot(plot_df, var):
    """
    Standard formatting of ghh plot.
    """
    # register the custom theme under a chosen name
    alt.themes.register("ghh_theme", ghh_theme)
    # enable the newly registered theme
    alt.themes.enable("ghh_theme")
    plot = (
        alt.Chart(plot_df)
        .mark_bar()
        .encode(
            x="branch",
            y=var,
            tooltip=var,
        )
        .interactive()
        .properties(title=f"{var.replace('_', ' ')} by branch")
    )
    return plot


def get_health_ghh_obj(obj):
    """
    get dict with infor for this object.
    """
    if isinstance(obj, Repository):
        this_dict = get_repo_details(obj, "dict")
        score = this_dict["score"]
    elif isinstance(obj, NamedUser):
        repos = list(obj.get_repos())
        repo_df = (
            pd.concat(
                [REPOS_TEMPLATE_DF] + [get_repo_details(repo) for repo in repos],
                ignore_index=True,
            )
            .sort_values(by="repo")
            .reset_index(drop=True)
        )
        this_dict = repo_df.to_dict(orient="list")
        score = np.mean(this_dict["score"])
    return score


def get_health_single(obj):
    """
    get individual scores for 4 repo components.
    """
    branch_count = 0
    branch_age = 0
    issues = 0
    pull_requests = 0
    denom = 1
    if obj["branch count"] >= 3:
        branch_count = 1
    if obj["min branch age (days)"] >= 90:
        branch_age = 1
    if obj["issues"] > 0:
        issues = 1
    if obj["pull requests"] > 0:
        pull_requests = 1
    return denom, branch_count, branch_age, issues, pull_requests


def get_health_multiple(obj):
    """
    get individual scores for 4 repo components.
    """
    branch_count = 0
    branch_age = 0
    issues = 0
    pull_requests = 0
    denom = len(obj["repo"])
    assert all(isinstance(obj[x], list) for x in obj)
    assert all(len(obj[x]) == denom for x in obj)
    for brc in obj["branch count"]:
        if brc >= 3:
            branch_count += 1
    for mba in obj["min branch age (days)"]:
        if mba >= 90:
            branch_age += 1
    for i in obj["issues"]:
        if i > 0:
            issues += 1
    for prq in obj["pull requests"]:
        if prq > 0:
            pull_requests += 1
    return denom, branch_count, branch_age, issues, pull_requests


def get_health(obj):
    """
    calculate health from object depending on type.
    """
    if isinstance(obj, dict):
        assert all(x in REPOS_DF_COLUMNS for x in obj)
        if "score" in obj:
            return obj["score"]
        if isinstance(obj["repo"], str):
            denom, branch_count, branch_age, issues, pull_requests = get_health_single(
                obj
            )
        else:
            (
                denom,
                branch_count,
                branch_age,
                issues,
                pull_requests,
            ) = get_health_multiple(obj)
    elif isinstance(obj, (NamedUser, Repository)):
        denom, branch_count, branch_age, issues, pull_requests = get_health_ghh_obj(obj)
    # formula heavily modified from pylint https://docs.pylint.org/en/1.6.0/faq.html
    logging.debug("branch_count: %s", branch_count)
    logging.debug("branch_age: %s", branch_age)
    logging.debug("issues: %s", issues)
    logging.debug("pull_requests: %s", pull_requests)
    logging.debug("denom: %s", denom)
    if denom > 0:
        neg_score = float(
            2.5 * (branch_count + branch_age + issues + pull_requests) / denom
        )
    else:
        neg_score = np.nan
    logging.debug("neg_score: %s", neg_score)
    health = max(10.0 - neg_score, 0.0)
    return health
