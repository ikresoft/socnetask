import requests
import json
import sys
import argparse
import random

API_URL = 'http://localhost:8000/api/v1'


def get_headers(token=None):
    """ Create headers based on function arguments """
    headers = {
        'Accept': 'application/json'
    }
    if token:
        headers.update({
            'Authorization': 'JWT %s' % token
        })
    return headers


def enter_user():
    """ This is used only if user wants to enter information in std input """
    username = raw_input("Username: ")
    password = raw_input("Password: ")
    email = raw_input("Email: ")
    return username, password, email


def signup_user(username, password, email):
    """ Make request for signup single user """
    url = '/'.join([API_URL, 'account', 'signup/'])
    response = requests.post(url, data={
        'username': username,
        'password': password,
        'email': email
    }, headers=get_headers(), json=True)
    return response.json(), response.status_code


def signup_users(users):
    """ Signup users using single signup user """
    _users = []
    for user in users:
        user_object, status = signup_user(
            user['username'],
            user['password'],
            user['email']
        )
        user_object["password"] = user["password"]
        if status == 201:
            _users.append(user_object)
    return _users


def login_user(username, password):
    """ Login user and get attributes with JWT token """
    url = '/'.join([API_URL, 'account', 'login/'])
    response = requests.post(url, data={
        'username': username,
        'password': password
    }, json=True)
    return response.json(), response.status_code


def create_post(user_id, token, title, content):
    """ Create post using api call """
    url = '/'.join([API_URL, 'blog', 'post', 'create/'])
    response = requests.post(url, data={
        'user': user_id,
        'title': title,
        'body': content
    }, headers=get_headers(token), json=True)
    return response.json(), response.status_code


def get_user_with_max_posts(maxlikes, token):
    """ user who has most posts and has not reached max likes """
    url = '/'.join([API_URL, 'blog', 'post', 'topuser', '?maxlikes=%d' % maxlikes])
    response = requests.get(url, json=True, headers=get_headers(token))
    return response.json(), response.status_code


def like_or_unlike_post(user_id, token, post_id, url_sufix='like/'):
    """ This function is used for both process like and unlike """
    url = '/'.join([API_URL, 'blog', 'post', '%d', url_sufix])
    response = requests.put(url % post_id, headers=get_headers(token), data={
        'user_id': user_id
    }, json=True)
    return response.json(), response.status_code


def random_post_with_zero_likes(user_id, token):
    """ User can only like random posts from users who have at least one post with 0 likes """
    url = '/'.join([API_URL, 'blog', 'post', 'random/'])
    response = requests.get(url, headers=get_headers(token), data={
        'user_id': user_id
    }, json=True)
    return response.json(), response.status_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", help="raw input for users just write shell, default is file", default="file")
    parser.add_argument(
        "-c", help="config file (config.json)", default="./config.json")
    args = parser.parse_args()

    with open(args.c) as config_file:
        config = json.load(config_file)
        users = config["users"]
        if args.i == "shell":
            users = []
            for i in range(config['rules']['number_of_users']):
                username, password, email = enter_user()
                users.append({
                    "username": username,
                    "password": password,
                    "email": email
                })
        users_auth = signup_users(users)
        posts = []
        last_loggedin_user = None
        for user in users_auth:
            user_obj, status = login_user(user['username'], user['password'])
            if status == 200:
                for i in range(random.randint(1, config['rules']['max_posts_per_user'])):
                    post = create_post(
                        user_obj['id'],
                        user_obj['token'],
                        config['blog']['post']['title'],
                        config['blog']['post']['content']
                    )
                    posts.append(post)
            last_loggedin_user = user_obj

        max_likes_per_user = config['rules']['max_likes_per_user']
        while True:
            # get user with most posts and not reached max likes
            user_max_posts, status = get_user_with_max_posts(
                max_likes_per_user, last_loggedin_user['token']
            )
            if status == 200:
                likes = user_max_posts['likes']
                user = next(
                    user for user in users_auth if user['username'] == user_max_posts['username']
                )
                user_obj, status = login_user(user['username'], user['password'])

                while likes < max_likes_per_user:
                    post, status = random_post_with_zero_likes(user_obj['id'], user_obj['token'])

                    if status == 404:
                        sys.exit(0)

                    if post['user'] == user_obj['id']:
                        continue

                    like_object, status = like_or_unlike_post(
                        user_obj['id'], user_obj['token'], post['id']
                    )

                    if status == 200:
                        likes += 1
