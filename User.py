from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.engine.url import URL
from werkzeug.security import generate_password_hash, check_password_hash


#for local database on Windows
#import settings
#for Heroku
import settings_heroku as settings

Base = declarative_base()
engine = create_engine(URL(**settings.DATABASE))
Session = sessionmaker(bind=engine)
metadata = Base.metadata


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    google = Column(String(120))
    password = Column(String(120))
    name = Column(String(120))
    social_id = Column(String(120))
    last_city = Column(String(50))

    def __init__(self, email=None, password=None, name=None, google=None, social_id=None, last_city=None):
        if email:
            self.email = email.lower()
        if password:
            self.set_password(password)
        self.name = name
        self.last_city = last_city
        self.social_id = social_id
        self.google = google

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_json(self):
        return dict(id=self.id, email=self.email, google=self.google)

    def add(self):
            session = Session()
            if not find_by_email(self.email):
                session.add(self)
                session.commit()
            else:
                raise AlreadyExists


def find_by_email(email):
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    return user


def find_by_id(id):
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    return user

class AlreadyExists(Exception):
    pass

metadata.create_all(engine)