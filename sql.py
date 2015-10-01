from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime, Text, Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///se390.db'
db = SQLAlchemy(app)

session_status = db.Table('session_status',
    db.Column('session_id', Integer, ForeignKey('session.id')),
    db.Column('status_id', Integer, ForeignKey('status.id'))
)

session_level = db.Table('session_level',
    db.Column('session_id', Integer, ForeignKey('session.id')),
    db.Column('level_id', Integer, ForeignKey('level.id'))
)

session_faculty = db.Table('session_faculty',
    db.Column('session_id', Integer, ForeignKey('session.id')),
    db.Column('faculty_id', Integer, ForeignKey('faculty.id'))
)

class status(db.Model):
     # one of ("Co-op", "Graduating")
    __tablename__ = 'status'
    id = db.Column(Integer, primary_key=True)
    status = db.Column(String(20))

class Level(db.Model):
    # one of ("Junior", "Intermediate", "Senior", "Bachelor", "Masters", "PhD")
    __tablename__ = 'level'
    id = db.Column(Integer, primary_key=True)
    level = db.Column(String(20))

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(Integer, primary_key=True)
    ceca_name = db.Column(String(250))
    nice_name = db.Column(String(250))

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(Integer, primary_key=True)
    employer = db.Column(String(250))
    start = db.Column(DateTime())
    end = db.Column(DateTime())
    location = db.Column(String(250))
    website = db.Column(String(250))
    description = db.Column(Text())
    status = db.relationship("status", secondary=session_status)
    level = db.relationship("level", secondary=session_level)
    faculty = db.relationship("faculty", secondary=session_faculty)

db.create_all()
