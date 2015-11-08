import jwt
import os
import json
import requests
from GuideRoutes import GuideRoute, find_by_id as find_route_by_id
from User import User, find_by_email, find_by_id as find_user_by_id, AlreadyExists
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
    user = find_user_by_id(id=g.user_id)
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


@app.route('/route/download', methods=['POST'])
@login_required
def route_download():
    if not request.json or not 'id' in request.json:
        response = jsonify(message='Have to an id of the route')
        response.status_code = 400
        return response
    else:
        route = find_route_by_id(request.json['id'])
        if route:
            return jsonify(route.json_to_download())
        else:
            return jsonify(message="No such a route")

if __name__ == '__main__':
    app.run()