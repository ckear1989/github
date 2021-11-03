import setuptools

setuptools.setup(
    name="github",
    extras_require={
        "dev": [
            "pre-commit",
            "pre-commit-hooks",
            "PyGitHub",
        ],
        "test": [],
    },
)
