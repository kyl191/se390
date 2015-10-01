from flask import Flask, render_template, jsonify, request
from filtering import events_for_request
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
        return "ics will go here with %d events" % len(events)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
