from datetime import datetime
import logging as log
import re

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import requests

class InfoSession(object):

  def __init__(self, rows):
    # parse_row will try to print the employer if something goes wrong
    # Make sure something is present so we don't die completely
    self.employer = "pre-init"
    self.employer = self.parse_row(rows[0], "Employer")
    self.loc = self.parse_row(rows[3], "Location")
    self.site = self.parse_row(rows[4], "Web Site")
    self.parse_description(rows[6])
    
    self.parse_text_block(rows[5])
    date = self.parse_row(rows[1], "Date")
    time = self.parse_row(rows[2], "Time")
    self.build_datetime(date, time)
    self.strip_site()
    # Sometimes there's an "ATTENDANCE: " table row, so use the correct line if it's present
    if rows[7].find(style=re.compile("red")) is None:
      self.set_id(rows[7])
    else:
      self.set_id(rows[8])

  def parse_text_block(self, row):
    text = row.td.i.contents
    if text is None:
      log.error("Couldn't extract info block: %s" % row)
      return
    if len(text) is not 5:
      log.error("Expected 5 entries in info block, got %i: %s" % (len(text), row))

    self.levels = self.parse_levels(text[0]) if len(text) >=1 else None
    self.status = self.parse_student_status(text[2]) if len(text) >= 3 else None
    self.faculty = self.parse_faculty(text[4]) if len(text) >= 5 else None

  def build_datetime(self, date_text, time_text):
    date_fmt = "%B %d, %Y"
    time_fmt = "%I:%M %p"
    (start_text, end_text) = time_text.split(" - ")
    date = datetime.strptime(date_text, date_fmt)
    start_time = datetime.strptime(start_text, time_fmt).time()
    end_time = datetime.strptime(end_text, time_fmt).time()
    self.start = datetime.combine(date, start_time)
    self.end = datetime.combine(date, end_time)

  def strip_site(self):
    if self.site.name == "a":
      self.site = self.site.contents[0]
    if self.site.startswith("http") and len(self.site) <= 8:
      self.site = None

  def parse_row(self, row, name, elems=2):
    r = []
    for d in row.find_all("td"):
      if len(d.contents) is not 1:
        log.warn("length of element >1 in %s from %s (%s)" % (name, self.employer, row))
        return None
      # The url is a Tag, coerce it to a string for checking
      if d.contents[0] is not None and len(d.contents[0].string.strip()) is not 0:
        r.append(d.contents[0])
    if not len(r) == elems:
      log.warn("%s: %s doesn't contain exactly %i data elements" % (name, row, elems))
    if not r[0].split(":")[0] == name:
      log.warn("%s doesn't start with %s" % (row, name))
    return r[1]

  def parse_levels(self, text):
    reference = {"Junior","Intermediate","Senior","Bachelor","Masters","PhD"}
    if not text.startswith("For "):
      log.warn("%s doesn't start with 'For ', assuming all levels for %s" % (text, self.employer))
      return reference
    levels = {l.strip() for l in text[4:].split(",") if len(l) is not 0}
    if len(levels) > 0:
      log.info("Extracted %s from %s" % (levels, text))
    else:
      level = reference
      log.warn("No levels provided, assuming all levels for %s" % self.employer)
    if not reference.issuperset(levels):
      log.warn("Found unknown student levels in set: %s" % levels)
    return levels.intersection(reference)

  def parse_student_status(self, text):
    reference = {"Co-op", "Graduating"}
    words = re.findall("[\w-]+", text)
    try:
      words.remove("Students")
      words.remove("and")
    except ValueError:
      pass
    status = set(words)
    if not reference.issuperset(status):
      log.warn("Found unknown student status in set: %s in %s" % (status, self.employer))
    return status.intersection(reference)

  def parse_faculty(self, text):
    return set(text.split(","))

  def parse_description(self, text):
    desc = text.find("i").string
    self.description = desc if desc is not None and len(desc) is not 0 else None
  
  def set_id(self, text):
    url = text.find("a").attrs['href']
    ids = re.findall("id=([0-9]+)", url)
    self.id = int(ids[0]) if len(ids) > 0 else None

  def __str__(self):
    # This doesn't work
    return "%s on %s (%i)" % (self.employer, self.start, self.id if not None else 0)

def load_from_URL(url):
  p = requests.get(url)
  table_rows = BeautifulSoup(p.content, "html.parser").find(id="tableform").find_all("tr")
  sessions = []
  for row in range(len(table_rows)):
    if table_rows[row].td.contents[0] != "Employer: ":
      continue
    sessions.append(InfoSession(table_rows[row:row+9]))
  return sessions

def get_sessions(months=4):
  sessions = []
  for i in range(months):
    get_date =  datetime.now() + relativedelta(months=i)
    url_fmt = "http://www.ceca.uwaterloo.ca/students/sessions_details.php?id=%Y%b"
    url = get_date.strftime(url_fmt)
    log.warn(url)
    sessions.extend(load_from_URL(url))
  return sessions

if __name__ == "__main__":
  sess = get_sessions()