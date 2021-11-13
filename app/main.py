"""
Module for flask app.
"""

from flask import Flask, request, render_template

from GitHubHealth import GitHubHealth

app = Flask(__name__)


@app.route("/")
def my_form():
    """
    Get home page with form.
    """
    return render_template("index.html")


@app.route("/", methods=["POST"])
def my_form_post():
    """
    Control routing of app.
    """
    # ghh = GitHubHealth(user="ckear1989")
    # ghh.get_repos()
    # ghh.get_repo_df()
    # ghh.render_repo_html_table()
    # ghh.get_plots()
    # plots = ghh.plots
    user = request.form["text"]
    ghh = GitHubHealth(user=user)
    ghh.get_repos()
    ghh.get_repo_df()
    ghh.render_repo_html_table()
    ghh.get_plots()
    plots = ghh.plots
    return render_template(
        "status.html",
        url=ghh.user_url,
        user=ghh.username,
        table=ghh.repo_html,
        plots=plots,
    )


if __name__ == "__main__":
    app.run(debug=True)
