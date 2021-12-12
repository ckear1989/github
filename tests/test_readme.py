"""
Get python sections of README and attempt to run.
"""

import os

import subx


def test_readme_rst_valid():
    """
    check setup.py file is formatted correctly.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    subx.call(
        cmd=[
            "python",
            os.path.join(base_dir, "setup.py"),
            "check",
            "--metadata",
            "--restructuredtext",
            "--strict",
        ]
    )
