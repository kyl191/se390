from flask import Flask, render_template, jsonify, request
from filtering import events_for_request
from sql import db, Level, Status, Faculty
from calendar import format_to_ical
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedule')
def schedule():
    content_type = request.args.get("format", "json" if request.headers.get("accept", "text/calendar") == "application/json" else "ics")
    events = events_for_request()
    if content_type == "json":
        return jsonify(count=len(events), sessions=[x.serialize() for x in events])
    else:
        return format_to_ical(events)

@app.route('/api/filters')
def available_filters():
    filter_options_dict = {}
    for filter_type in (Level, Status, Faculty):
        filter_options_dict[filter_type.__name__.lower()] = [x.serialize() for x in db.session.query(filter_type).all()]
    return jsonify(**filter_options_dict)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
