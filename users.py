import json
from pathlib import Path

def get_users():
    users = [d.name for d in Path('./db/users').iterdir() if d.is_dir()]
    return users

def get_follows_meta(user):
    "Get subscription data - what feeds are we following"
    with open(f"db/users/{user}/follows.json", 'r') as file:
        follows_meta = json.load(file)
    #print(json.dumps(follows_meta, indent=4))
    return follows_meta

def test():
    users = get_users()
    for user in users:
        follows_meta = get_follows_meta(user)
        print(user, follows_meta)


if __name__ == "__main__":
    test()
