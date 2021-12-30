"""
create html with plots.  useful for testing formatting etc.
"""

import os

from jinja2 import Environment, FileSystemLoader

DUMMY_PLOTS_HTML = "plots.html"


def test_dummy_plots(ghh):
    """
    dummy repo status
    """
    repo = ghh.get_repo("ckear1989", "github")
    repo.get_repo_df()
    repo.get_html_table()
    repo.get_plots()
    env = Environment(loader=FileSystemLoader("GitHubHealth/app/templates"))
    template = env.get_template("test_repo_status.html")
    output_from_parsed_template = template.render(ghh=ghh, repo=repo)
    with open(DUMMY_PLOTS_HTML, "w", encoding="utf-8") as html_out:
        html_out.write(output_from_parsed_template)
    assert os.path.exists(DUMMY_PLOTS_HTML)
