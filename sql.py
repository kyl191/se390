from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime, Text, Enum

db = SQLAlchemy()

# sqlite://<nohostname>/<path>
# where <path> is relative:
engine = create_engine('sqlite:///se390.db')

Base = declarative_base()

session_status = Table('session_status', Base.metadata,
    Column('session_id', Integer, ForeignKey('session.id')),
    Column('status_id', Integer, ForeignKey('status.id'))
)

session_level = Table('session_level', Base.metadata,
    Column('session_id', Integer, ForeignKey('session.id')),
    Column('level_id', Integer, ForeignKey('level.id'))
)

session_faculty = Table('session_faculty', Base.metadata,
    Column('session_id', Integer, ForeignKey('session.id')),
    Column('faculty_id', Integer, ForeignKey('faculty.id'))
)

class Session(db.Model):
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True)
    employer = Column(String(250))
    start = Column(DateTime())
    end = Column(DateTime())
    location = Column(String(250))
    website = Column(String(250))
    description = Column(Text())
    status = relationship("status", secondary=session_status)
    level = relationship("level", secondary=session_level)
    faculty = relationship("faculty", secondary=session_faculty)

class status(db.Model):
     # one of ("Co-op", "Graduating")
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True)
    status = Column(String(20))

class Level(db.Model):
    # one of ("Junior", "Intermediate", "Senior", "Bachelor", "Masters", "PhD")
    __tablename__ = 'level'
    id = Column(Integer, primary_key=True)
    level = Column(String(20))

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = Column(Integer, primary_key=True)
    ceca_name = Column(String(250))
    nice_name = Column(String(250))

Base.metadata.create_all(engine)
