#!/usr/bin/env python

import sys
import re
from pprint import pformat


class Times:
    def __init__(self):
        self.time = {}
        self.desc = {}

    def __str__(self):
        for project in sorted(self.time.keys()):
            worktime = float(self.time[project]) / 60
            try:
                return "{0:20s}  {1}  {2}".format(project, worktime, ",".join(self.desc[project]))
            except:
                return "{0:20s}  {1}  ---".format(project, worktime)

    def add_time (self, project, minutes):
        try:
            self.time[project] += int(minutes)
        except:
            self.time[project] = int(minutes)

    def add_desc (self, project, desc):
        try:
            self.desc[project].append(desc)
        except:
            self.desc[project] = [ desc ]


def byDate (date):
    day,month = date[:-1].split('.')
    return 100 * int(month) + int(day)

def get_minute (hhmm):
    try:
        m = HHMM.match(hhmm)
        return 60 * int(m.group('hours')) + int(m.group('minutes'))
    except:
        return None

DAY = re.compile(r"""^(?P<date>\d+\.\d+\.)?\s+(?P<from>\d+:\d+)-(?P<to>\d+:\d+)\s+(?P<proj>\S+)(?P<desc>.*)""")
HHMM = re.compile(r"""(?P<hours>\d+):(?P<minutes>\d+)""")

webtime = {}
curr_day = None
day_times = None


for line in sys.stdin:
    m = DAY.match(line)
    if not m:
        #print("NO MATCH: {0}".format(line))
        continue

    proj = m.group('proj')

    print("DAY: date={date}, hours={hours}, project={proj}, desc={desc}".format(m.groupdict()))
    if day_times is None or (m.group('date') is not None and m.group('date') != curr_day):
        if day_times is not None:
            webtime[curr_day] = day_times
        day_times = Times()
        curr_day = m.group('date')

    from_minute = get_minute(m.group('from'))
    to_minute = get_minute(m.group('to'))
    #print("Working hours: {0} - {1}".format(from_minute, to_minute))
    if from_minute is not None and to_minute is not None and to_minute > from_minute:
        day_times.add_time(proj, to_minute - from_minute)
    else:
        print("ERROR: invalid time range - {from} - {to}".format(m.groupdict()))

    if len(m.group('desc')) > 0:
        day_times.add_desc(proj, m.group('desc'))

if curr_day is not None and day_times is not None:
    webtime[curr_day] = day_times

for day in sorted(webtime.keys(), key=byDate):
    print("{0:6s} {1}".format(day, webtime[day]))
