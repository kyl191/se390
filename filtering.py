from flask import request
from sql import db, Session, Level, Faculty, Status
from sqlalchemy.orm import contains_eager

def events_for_request():
    return _filter_with_parameters(request.args)

def _filter_with_parameters(parameters):
    # By default, return everything (including stuff w/ missing filterable metadata)
    event_query = db.session.query(Session)\
        .outerjoin(Session.level, Session.faculty, Session.status)\
        .options(contains_eager(Session.level), contains_eager(Session.status), contains_eager(Session.faculty))

    def multi_valued(value):
        return value.split(",")

    if "level" in parameters:
        event_query = event_query.filter(Level.slug.in_(multi_valued(parameters["level"])))

    if "faculty" in parameters:
        event_query = event_query.filter(Faculty.slug.in_(multi_valued(parameters["faculty"])))

    if "status" in parameters:
        event_query = event_query.filter(Status.slug.in_(multi_valued(parameters["status"])))

    return event_query.all()
