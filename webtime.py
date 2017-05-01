#!/usr/bin/env python

import sys
import re
from pprint import pformat

class Times:
    def __init__(self, day):
        self.day = day
        self.time = {}
        self.desc = {}

    def __str__(self):
#        print("day={0} time={1}".format(self.day, pformat(self.time)))
        lines = [ "--- {0}".format(self.day) ]
        for project in sorted(self.time.keys()):
            worktime = float(self.time[project]) / 60
            try:
                lines.append("{0}\t{1}: {2}".format(worktime, project, ", ".join(self.desc[project])))
            except:
                lines.append("{0}\t{1}".format(worktime, project))
        return "\n".join(lines)

    def add_time (self, project, minutes):
        try:
            self.time[project] += int(minutes)
        except:
            self.time[project] = int(minutes)

    def add_desc (self, project, desc):
        desc = desc.strip()
        if len(desc) > 0:
            try:
                self.desc[project].append(desc)
            except:
                self.desc[project] = [ desc ]


def byDate (date):
    day,month = date.split('.')[0:2]
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
verbose = len(sys.argv) > 1 and sys.argv[1] == "-v"

for line in sys.stdin:
    m = DAY.match(line)
    if not m:
        if verbose:
            print("NO MATCH: {0}".format(line))
        continue

    proj = m.group('proj')

#    print("DAY: date={date}, hours={hours}, project={proj}, desc={desc}".format(m.groupdict()))
    if day_times is None or (m.group('date') is not None and m.group('date') != curr_day):
        if day_times is not None:
            webtime[curr_day] = day_times
        curr_day = m.group('date')
        day_times = Times(curr_day)
#        print("curr_day={0}".format(curr_day))

    from_minute = get_minute(m.group('from'))
    to_minute = get_minute(m.group('to'))
#    print("Working hours: {0} - {1}".format(from_minute, to_minute))
    if from_minute is not None and to_minute is not None and to_minute > from_minute:
        day_times.add_time(proj, to_minute - from_minute)
    else:
        print("ERROR: invalid time range - {from} - {to}".format(m.groupdict()))

    day_times.add_desc(proj, m.group('desc'))

if curr_day is not None and day_times is not None:
    webtime[curr_day] = day_times

for day in sorted(webtime.keys(), key=byDate):
    print "\n{0}".format(webtime[day])
