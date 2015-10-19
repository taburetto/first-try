from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.schema import Sequence
from User import User

engine = create_engine('postgresql://postgres:Zhenqiguai0808@localhost:5432/Iter')
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
users_table = Table('users', metadata,
                    Column('name', String(80)),
                    Column('email', String(80)),
                    Column('access_token', String(255)),
                    Column('last_type', String(10)),
                    Column('last_city', String(50)),
                    Column('social_id', Integer),
                    Column('id', Integer, Sequence('serial_id', start=2, increment=1), primary_key=True)
                    )
metadata.create_all(engine)

mapper(User, users_table)

test = User('test', 'test@qwe.ru', None, None, 'Moscow', None, 2)

session.add(test)
session.commit()
