from datetime import datetime
import time

"""Time related utility functions for PF1010 web application
Time and date functionality is centralized here
"""

API_DATE_FORMAT = '%Y-%m-%d'
API_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
FALLBACK_TIME_FORMAT = '%Y-%m-%dT%H:%MZ'


def make_time24(timestr):
    if timestr.endswith('AM') or timestr.endswith('PM'):
        comps = timestr.split()
        ampm = comps[1]
        timecomps = map(int, comps[0].split(':'))
        hours = timecomps[0]
        minutes = timecomps[1]
        if hours == 12:
            hours = 0 if ampm == 'AM' else hours
        elif ampm == 'PM':
            hours += 12
        return "%02d:%02d" % (hours, minutes)
    else:
        return timestr


def get_form_time(datestr, timestr):
    if timestr:
        timestr = make_time24(timestr)
        s = "%sT%sZ" % (datestr, timestr)
    else:
        s = "%sT00:00:00Z" % datestr
    return get_timestamp(s)

def get_timestamp(s):
    try:
        return datetime.fromtimestamp(time.mktime(time.strptime(s, API_TIME_FORMAT)))
    except:
        return datetime.fromtimestamp(time.mktime(time.strptime(s, FALLBACK_TIME_FORMAT)))
