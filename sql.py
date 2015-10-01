from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime, Text, Enum
import re

def slug_generator(field_name):
    def generate_slug(ctx):
        return re.sub("[^a-z-]", "", ctx.current_parameters[field_name].lower())
    return generate_slug

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///se390.db'
db = SQLAlchemy(app)

session_status = db.Table('session_status',
    db.Column('session_id', Integer, db.ForeignKey('session.id')),
    db.Column('status_id', Integer, db.ForeignKey('status.id'))
)

session_level = db.Table('session_level',
    db.Column('session_id', Integer, db.ForeignKey('session.id')),
    db.Column('level_id', Integer, db.ForeignKey('level.id'))
)

session_faculty = db.Table('session_faculty',
    db.Column('session_id', Integer, db.ForeignKey('session.id')),
    db.Column('faculty_id', Integer, db.ForeignKey('faculty.id'))
)

class Status(db.Model):
     # one of ("Co-op", "Graduating")
    __tablename__ = 'status'
    id = db.Column(Integer, primary_key=True)
    slug = db.Column(String(20), default=slug_generator("status"))
    status = db.Column(String(20))
    def serialize(self):
        return {"slug": self.slug, "status": self.status}

class Level(db.Model):
    # one of ("Junior", "Intermediate", "Senior", "Bachelor", "Masters", "PhD")
    __tablename__ = 'level'
    id = db.Column(Integer, primary_key=True)
    slug = db.Column(String(20), default=slug_generator("level"))
    level = db.Column(String(20))

    def serialize(self):
       return {"slug": self.slug, "level": self.level}

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(Integer, primary_key=True)
    slug = db.Column(String(20), default=slug_generator("ceca_name"))
    ceca_name = db.Column(String(250))
    nice_name = db.Column(String(250))
    def serialize(self):
        return {"slug": self.slug, "name": self.nice_name}

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(Integer, primary_key=True)
    employer = db.Column(String(250))
    start = db.Column(DateTime())
    end = db.Column(DateTime())
    location = db.Column(String(250))
    website = db.Column(String(250))
    description = db.Column(Text())
    status = db.relationship("Status", secondary=session_status)
    level = db.relationship("Level", secondary=session_level)
    faculty = db.relationship("Faculty", secondary=session_faculty)

    def serialize(self):
        # Not really worth setting up something more complicated for this 1 case
        return {
            "employer" : self.employer,
            "location" : self.location,
            "website" : self.website,
            "description" : self.description,
            "start" : self.start.isoformat(),
            "end" : self.end.isoformat(),
            "status": [x.serialize() for x in self.status],
            "level": [x.serialize() for x in self.level],
            "faculty": [x.serialize() for x in self.faculty]
        }

db.create_all()
