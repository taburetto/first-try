from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.schema import Sequence


Base = declarative_base()
engine = create_engine('postgresql://postgres:Zhenqiguai0808@localhost:5432/Iter')
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
        if key in dir(User):
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

test_email = 'taburetto@yandex.ru'
check(test_email)
if not check(test_email):
    print('not there')
    add(email=test_email)