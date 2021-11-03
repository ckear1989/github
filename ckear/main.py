"""
Empty module docstring.
"""
import os

from github import Github


def get_connection():
    """
    Get connection and login.
    """
    github_con = Github(login_or_token=os.getenv("GITHUB_ACCESS_TOKEN"))
    user = github_con.get_user()
    _ = user.login
    return github_con


def main():
    """
    Empty docstring.
    """
    github_con = get_connection()
    user = github_con.get_user()
    print(dir(user))
    # Then play with your Github objects:
    for repo in github_con.get_user().get_repos():
        print(repo.name)
        # print(dir(repo))
    for org in github_con.get_user().get_orgs():
        print(org.name)
        print(dir(org))


if __name__ == "__main__":
    main()
