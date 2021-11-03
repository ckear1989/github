"""
Empty module docstring.
"""
import os

from github import Github


def main():
    """
    Empty docstring.
    """
    github_con = Github(login_or_token=os.getenv("GITHUB_ACCESS_TOKEN"))
    user = github_con.get_user()
    _ = user.login
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
