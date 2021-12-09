# GitHubHealth

[![PyPI version](https://badge.fury.io/py/GitHubHealth.svg)](https://badge.fury.io/py/GitHubHealth)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pylint](https://github.com/ckear1989/github/blob/dev/data/pylint.svg)](https://github.com/jongracecox/anybadge)
[![Buy me a coffee](https://github.com/ckear1989/github/blob/dev/data/buy_me_a_coffee.png)](https://www.buymeacoffee.com/ckear1988)

GitHubHealth is a Python library for monitoring code health in GitHub.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install GitHubHealth.

```bash
# shell
pip install GitHubHealth
```

## Usage
Set access token environment variable.
```bash
# shell
export GITHUB_TOKEN=<your github pat>
```

Get repo health as pandas DataFrame.
```python
# python
import os
from GitHubHealth.main import ACCESS_TOKEN_VAR_NAME
from GitHubHealth import GitHubHealth
my_repo_health = GitHubHealth(gat=os.environ[ACCESS_TOKEN_VAR_NAME])
my_repo_health.user.get_repo_df()
my_repo_health.user.repo_df
```

Launch Flask app to view repo health tables and plots.

```python
# python
from GitHubHealth import app
app.run()
```

## Contributing
>Collaborators can be added on a case by case basis so please reach out if you would like to \
>contribute. As this is a personal hobby I will review any PRs and manage access and deployment \
>myself. I welcome any issues and feature requests to be submitted and will try to reply in a \
>timely manner. Please make sure to update tests as appropriate. I advise using use pre-commit to \
>help with automated testing and adhering to pylint and black formatting standards.

## License
[MIT](https://choosealicense.com/licenses/mit/)
