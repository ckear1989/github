"""
Modulle for flask app.
"""
from flask import Flask, render_template

from ckear.main import main

app = Flask(__name__)


@app.route("/")
def index():
    """
    Control routing of app.
    """
    gh_df = main()
    return render_template("index.html", table=gh_df.to_html(classes="data"))


if __name__ == "__main__":
    app.run(debug=True)
