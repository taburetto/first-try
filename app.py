import jwt
import os
import json
import requests
from User import User, find_by_email, find_by_id, AlreadyExists
from datetime import datetime, timedelta
from flask import g, send_file, request, redirect, url_for, jsonify, abort
from jwt import DecodeError, ExpiredSignature, decode, encode
from flask import Flask
from requests_oauthlib import OAuth1
from functools import wraps


current_path = os.path.dirname(__file__)
client_path = os.path.abspath(os.path.join(current_path, '..', '..', 'client'))


app = Flask(__name__, static_url_path='', static_folder=client_path)
app.config.from_object('config')


def create_token(user):
    payload = {
        'sub': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    token = jwt.encode(payload, app.config['TOKEN_SECRET'])
    return token.decode('unicode_escape')


def parse_token(req):
    token = str(req.headers.get('Authorization'))
    return jwt.decode(token, app.config['TOKEN_SECRET'])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response
        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.user_id = payload['sub']

        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/me')
@login_required
def me():
    user = find_by_id(id=g.user_id)
    return jsonify(user.to_json())


@app.route('/auth/login', methods=['POST'])
def login():
    if not request.json or not ('email' and 'password' in request.json):
        response = jsonify(message='Have to send both email and password')
        response.status_code = 400
        return response
    user = find_by_email(request.json['email'])
    if not user or not user.check_password(request.json['password']):
        response = jsonify(message='Wrong Email or Password')
        response.status_code = 401
        return response
    token = create_token(user)
    id = find_by_email(email=request.json['email']).id
    return jsonify(id=id, email=request.json['email'], token=token)


@app.route('/auth/signup', methods=['POST'])
def signup():
    if not request.json or not ('email' and 'password' in request.json):
        response = jsonify(message='Have to send both email and password')
        response.status_code = 400
        return response
    else:
        user = User(email=request.json['email'], password=request.json['password'])
        try:
            user.add()
            token = create_token(user)
            id = find_by_email(email=request.json['email']).id
            return jsonify(id=id, email=request.json['email'], token=token)
        except AlreadyExists:
            response = jsonify(message='User already exists')
            response.status_code = 400
            return response


@app.route('/auth/google', methods=['POST'])
def google():
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    people_api_url = 'https://www.googleapis.com/plus/v1/people/me/openIdConnect'

    payload = dict(client_id=request.json['clientId'],
                   redirect_uri=request.json['redirectUri'],
                   client_secret=app.config['GOOGLE_SECRET'],
                   code=request.json['code'],
                   grant_type='authorization_code')

    # Step 1. Exchange authorization code for access token.
    r = requests.post(access_token_url, data=payload)
    token = json.loads(r.text)
    headers = {'Authorization': 'Bearer {0}'.format(token['access_token'])}

    # Step 2. Retrieve information about the current user.
    r = requests.get(people_api_url, headers=headers)
    profile = json.loads(r.text)

    user = User.query.filter_by(google=profile['sub']).first()
    if user:
        token = create_token(user)
        return jsonify(token=token)
    u = User(google=profile['sub'],
             display_name=profile['name'])
    u.add()
    token = create_token(u)
    return jsonify(token=token)


@app.route('/auth/facebook', methods=['POST'])
def facebook():
    access_token_url = 'https://graph.facebook.com/v2.3/oauth/access_token'
    graph_api_url = 'https://graph.facebook.com/v2.3/me'

    params = {
        'client_id': request.json['clientId'],
        'redirect_uri': request.json['redirectUri'],
        'client_secret': app.config['FACEBOOK_SECRET'],
        'code': request.json['code']
    }

    # Step 1. Exchange authorization code for access token.
    r = requests.get(access_token_url, params=params)
    access_token = dict(parse_qsl(r.text))

    # Step 2. Retrieve information about the current user.
    r = requests.get(graph_api_url, params=access_token)
    profile = json.loads(r.text)

    # Step 3. (optional) Link accounts.
    if request.headers.get('Authorization'):
        user = User.query.filter_by(facebook=profile['id']).first()
        if user:
            response = jsonify(message='There is already a Facebook account that belongs to you')
            response.status_code = 409
            return response

        payload = parse_token(request)

        user = User.query.filter_by(id=payload['sub']).first()
        if not user:
            response = jsonify(message='User not found')
            response.status_code = 400
            return response

        u = User(facebook=profile['id'], display_name=profile['name'])
        u.add()
        token = create_token(u)
        return jsonify(token=token)

    # Step 4. Create a new account or return an existing one.
    user = User.query.filter_by(facebook=profile['id']).first()
    if user:
        token = create_token(user)
        return jsonify(token=token)

    u = User(facebook=profile['id'], display_name=profile['name'])
    u.add()
    token = create_token(u)
    return jsonify(token=token)

if __name__ == '__main__':
    app.run()