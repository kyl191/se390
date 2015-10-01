from datetime import datetime
import logging as log
import re

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
import requests
from sql import db, Level, Status, Faculty, Session

class InfoSession(object):

  def __init__(self, rows):
    # parse_row will try to print the employer if something goes wrong
    # Make sure something is present so we don't die completely
    self.employer = self.parse_row(rows[0], "Employer")
    self.location = self.parse_row(rows[3], "Location")
    self.website = self.parse_row(rows[4], "Web Site")
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
    if self.website.name == "a":
      self.website = self.website.contents[0]
    if self.website.startswith("http") and len(self.website) <= 8:
      self.website = None

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
    return set((item.strip() for item in text.split(",")))

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

def basic_program_name(ceca_name):
  # All sorts of special cases in here
  ceca_name = ceca_name.strip()
  if ceca_name.endswith(")") and "(" not in ceca_name:
    ceca_name = ceca_name[:-1]
  if "GBDA" in ceca_name:
    return "GBDA"
  if "CPA" in ceca_name and "Arts/AFM" in ceca_name:
    return "Arts/AFM (CPA)"
  if ceca_name.startswith("ENG"):
    return ceca_name.split('-')[1].strip() + " Engineering"
  if re.match("[A-Z]{3,4}", ceca_name):
    return ceca_name.split(' - ')[1].strip()
  return ceca_name

def apply_nice_faculty_names(faculty_map):
  basic_name_pool = set()
  dupe_basic_names = set()
  for ceca_name, facultyobj in faculty_map.items():
    nice_name = basic_program_name(ceca_name)
    facultyobj.nice_name = nice_name
    if nice_name in basic_name_pool:
      dupe_basic_names.add(nice_name)
    basic_name_pool.add(nice_name)

  # Some names are duplicates as we stripped the actual faculty info
  for ceca_name, facultyobj in faculty_map.items():
    if facultyobj.nice_name in dupe_basic_names:
      facultyobj.nice_name += " (%s)" % ceca_name.split('-')[0].strip().title()

def load_from_URL(url):
  p = requests.get(url)
  table_rows = BeautifulSoup(p.content, "html.parser").find(id="tableform").find_all("tr")
  sessions = []
  for row in range(len(table_rows)):
    if table_rows[row].td.contents[0] != "Employer: " or "No info sessions" in table_rows[row]:
      continue
    sessions.append(InfoSession(table_rows[row:row+9]))
  return sessions

def get_sessions(months=4):
  sessions = []
  for i in range(months):
    get_date =  datetime.now() + relativedelta(months=i)
    url_fmt = "http://www.ceca.uwaterloo.ca/students/sessions_details.php?id=%Y%b"
    url = get_date.strftime(url_fmt)
    sessions.extend(load_from_URL(url))
  return sessions

def import_sessions():
  sessions = get_sessions()

  # We trash everything and recreate the db from scratch, for convenience
  # (this will leave the database empty for some time... oh well. DROP TABLE can't be rolled back in a transaction.)
  for table in db.metadata.sorted_tables:
    db.session.execute("DROP TABLE %s" % table.name)
  db.create_all()

  def get_enum_set(attrs):
    return set([item for sublist in [getattr(session, attrs) for session in sessions if getattr(session, attrs)] for item in sublist])

  def instantiate_enums(enum_set, db_type, db_field, postproc=None):
    enum_map = {}
    for enum_value in enum_set:
      db_obj = db_type()
      setattr(db_obj, db_field, enum_value)
      if postproc:
        for k,v in postproc(db_obj).items():
          setattr(db_obj, k, v)
      db.session.add(db_obj)
      enum_map[enum_value] = db_obj
    return enum_map

  level_map = instantiate_enums(get_enum_set("levels"), Level, "level")
  status_map = instantiate_enums(get_enum_set("status"), Status, "status")
  faculty_map = instantiate_enums(get_enum_set("faculty"), Faculty, "ceca_name")

  # It's a somewhat involved process
  apply_nice_faculty_names(faculty_map)

  for parsed_session in sessions:
    session = Session()
    session.employer = parsed_session.employer
    session.location = parsed_session.location
    session.start = parsed_session.start
    session.end = parsed_session.end
    session.website = parsed_session.website
    session.description = parsed_session.description
    if parsed_session.levels:
      session.level = [level_map[level] for level in parsed_session.levels]
    if parsed_session.faculty:
      session.faculty = [faculty_map[faculty] for faculty in parsed_session.faculty]
    if parsed_session.status:
      session.status = [status_map[status] for status in parsed_session.status]
    db.session.add(session)

  db.session.commit()

if __name__ == "__main__":
  import_sessions()
