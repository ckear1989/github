# GitHubHealth

[![PyPI version](https://badge.fury.io/py/GitHubHealth.svg)](https://badge.fury.io/py/GitHubHealth)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pylint](https://github.com/ckear1989/github/blob/dev/data/pylint.svg)](https://github.com/jongracecox/anybadge)

GitHubHealth is a Python library for monitoring code health in GitHub.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install GitHubHealth.

```bash
pip install GitHubHealth
```

## Usage
Set access token environment variable.
```bash
export GITHUB_TOKEN=<your github pat>
```


Get repo health as pandas DataFrame.
```python
from GitHubHealth import GitHubHealth

my_repo_health = GitHubHealth()
my_repo_health.get_repos()
my_repo_health.get_repo_df()
my_repo_health.repo_df
```

Launch Flask app to view repo health tables and plots.
```python
from GitHubHealth import app

app.run()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
