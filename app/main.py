"""
Module for flask app.
"""

from flask import Flask, render_template

from GitHubHealth import GitHubHealth

app = Flask(__name__)


@app.route("/")
def index():
    """
    Control routing of app.
    """
    ghh = GitHubHealth(user="ckear")
    ghh.get_repos()
    ghh.get_repo_df()
    ghh.render_repo_html_table()
    ghh.get_plots()
    plots = ghh.plots
    return render_template(
        "index.html",
        url=ghh.user_url,
        user=ghh.username,
        table=ghh.repo_html,
        plots=plots,
    )


if __name__ == "__main__":
    app.run(debug=True)
