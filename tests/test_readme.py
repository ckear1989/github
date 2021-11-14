"""
Get python sections of README and attempt to run.
"""

from __future__ import absolute_import, division, unicode_literals, print_function

import os
import tempfile
import subprocess

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


def test_readme_examples():
    """
    Parse README and get sections.
    """
    readme_path = f"{os.path.dirname(os.path.dirname(__file__))}/README.md"
    with open(readme_path, "r", encoding="ascii") as infile:
        readme_contents = infile.readlines()
    examples = []
    example = ""
    example_flag = 0
    for line in readme_contents:
        if (
            line.startswith("```")
            and line.startswith("```python") is False
            and example_flag == 1
        ):
            # skip run app
            if example == "app.run()":
                example = f"# {example}"
            examples.append(example)
            example_flag = 0
            example = ""
        if example_flag == 1:
            example += line
        if line.startswith("```python"):
            example_flag = 1
    for example in examples:
        with tempfile.NamedTemporaryFile("w") as out_file:
            out_file.write(example)
            subprocess.run(
                [f"python {out_file.name}"], shell=True, check=True, capture_output=True
            )
