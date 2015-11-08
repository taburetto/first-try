from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.types import Float, Text, Boolean
from sqlalchemy.schema import ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship

# for local database on Windows
#import settings
#for Heroku
import settings_heroku as settings

Base = declarative_base()
engine = create_engine(URL(**settings.DATABASE))
Session = sessionmaker(bind=engine)
metadata = Base.metadata

association_table = Table('places_in_routes', Base.metadata,
                          Column('place_id', Integer, ForeignKey('places.id')),
                          Column('route_id', Integer, ForeignKey('guide_routes.id')),
                          Column('number', Integer),
                          Column('id', Integer))


class Place(Base):
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    description = Column(Text)
    longitude = Column(Float)
    latitude = Column(Float)
    pictures = relationship("Picture")

    def __init__(self, name=None, description=None, longitude=None, latitude=None):
        self.name = name
        self.description = description
        self.longitude = longitude
        self.latitude = latitude

    def to_json(self):
        pictures = []
        for picture in self.pictures:
            pictures.append(picture.to_json())
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            longitude=self.longitude,
            latitude=self.latitude,
            pictures=pictures
        )


class Picture(Base):
    __tablename__ = 'pictures'
    id = Column(Integer, primary_key=True)
    url = Column(Text)
    place_id = Column(Integer, ForeignKey('places.id'))
    is_default = Column(Boolean)

    def __init__(self, url=None, place_id=None):
        self.url = url
        self.place_id = place_id

    def to_json(self):
        return dict(id=self.id, url=self.url, default=self.is_default)


class GuideRoute(Base):
    __tablename__ = 'guide_routes'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    user_id = Column(Integer, ForeignKey('user.id'))
    rating = Column(Float)
    price = Column(Integer)
    description = Column(Text)
    places = relationship("Place",
                          secondary=association_table)

    def __init__(self, name=None, rating=None, price=None, description=None, user_id=None):
        self.name = name
        self.rating = rating
        self.price = price
        self.description = description
        self.user_id = user_id

    def json_to_download(self):
        for place in self.places:
            places.append(place.to_json())
        return dict(
            id=self.id,
            name=self.name,
            user_id=self.user_id,
            rating=self.rating,
            price=self.price,
            description=self.description,
            places=places
        )


metadata.create_all(engine)


def find_by_id(id):
    session = Session()
    route = session.query(GuideRoute).filter_by(id=id).first()
    return route