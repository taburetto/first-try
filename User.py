from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.engine.url import URL
import settings


Base = declarative_base()
engine = create_engine(URL(**settings.DATABASE))
Session = sessionmaker(bind=engine)
metadata = Base.metadata


class User(Base):
    __tablename__ = 'users'
    name = Column(String(80))
    email = Column(String(80))
    access_token = Column(String(255))
    last_type = Column(String(10))
    last_city = Column(String(50))
    social_id = Column(Integer)
    id = Column(Integer, primary_key=True)

    def __init__(self, name, email, access_token, last_type, last_city, social_id):
        self.name = name
        self.email = email
        self.access_token = access_token
        self.last_type = last_type
        self.last_city = last_city
        self.social_id = social_id


def add(**kwargs):
    session = Session()
    user = User(None, None, None, None, None, None)
    for key, value in kwargs.iteritems():
        if key in ['email', 'social_id']:
            setattr(user, key, value)
    session.add(user)
    session.commit()
    session.close()


def check(email):
    session = Session()
    #Checks if a user in the database.
    #If list of emails, filtered by the email given, is not empty, 'True' is returned.
    #Otherwise, 'False' is returned.
    if session.query(User.email).filter_by(email=email).all():
        session.close()
        return True
    else:
        session.close()
        return False
