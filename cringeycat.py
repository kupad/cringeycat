import click
from users import get_users, get_follows_meta
from feedmanager import get_follows
from rendermanager import render

@click.command()
def main():
    users = get_users()
    users_follows = [(user, get_follows(get_follows_meta(user))) for user in users]
    for (user,follows) in users_follows:
        render(user, follows)


if __name__ == "__main__":
    main()

