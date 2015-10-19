from icalendar import Calendar, Event
from pytz import timezone

def format_to_ical(info_sessions):
    cal = Calendar()
    cal.add('X-WR-CALNAME', 'Info Sessions') # Calendar name
    eastern = timezone('Canada/Eastern') # Embed timezone info into events

    for session in info_sessions:
        # If the session is longer than 4 hours it's probably a holiday entry
        # Also filter out closed/cancelled info sessions
        # This should probably be done in filtering.py
        if ((session.end - session.start).total_seconds() > 14400) or \
           ("closed info" in session.employer.lower()) or \
           ("cancelled" in session.employer.lower()):
            continue
        event = Event()
        event.add('summary', session.employer) # Event title
        event.add('description', session.description)
        event.add('location', session.location)
        event.add('dtstart', eastern.localize(session.start))
        event.add('dtend', eastern.localize(session.end))
        event.add('url', session.website)
        cal.add_component(event)

    return cal.to_ical()