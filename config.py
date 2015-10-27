import os

DEBUG = True

TOKEN_SECRET = os.environ.get('SECRET_KEY') or 'JWT Token Secret String'
GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET') or 'Google Client Secret'
FACEBOOK_SECRET = os.environ.get('FACEBOOK_SECRET') or 'Facebook Client Secret'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///app.db'
