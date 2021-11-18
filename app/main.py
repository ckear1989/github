"""
Module for flask app.
"""
import os

from GitHubHealth import app

import GitHubHealth

TEMPLATE_DIR = os.path.abspath(f"{GitHubHealth.__path__[0]}/templates/")

if __name__ == "__main__":
    app.config["template_dir"] = TEMPLATE_DIR
    app.run(debug=True)
