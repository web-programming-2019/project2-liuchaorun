from sqlalchemy import Column, String, create_engine, TIMESTAMP, INTEGER, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

base = declarative_base()


class User(base):
    __tablename__ = 'User'

    username = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    imageUrl = Column(String, nullable=False)
    createdTime = Column(TIMESTAMP, nullable=False)


class Message(base):
    __tablename__ = 'Message'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    content = Column(JSON, nullable=False)
    createdTime = Column(TIMESTAMP, nullable=False)
    channel = Column(String, nullable=False)


def create(postgresUrl):
    engine = create_engine(postgresUrl)
    base.metadata.create_all(engine)
    db = scoped_session(sessionmaker(bind=engine))
    return db
