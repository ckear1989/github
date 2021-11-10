# GitHubHealth

GitHubHealth is a Python library for monitoring code health in GitHub..

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install GitHubHealth
```

## Usage
Get repo health as pandas DataFrame.
```python
from GitHubHealth.main import GitHubHealth

my_repo_health = GitHubHealth()
my_repo_health.repo_df
```

Launch Flask app to view repo health tables and plots.
```python
from GitHubHealth.app import app

app.run()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
