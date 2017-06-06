from wand.image import Image
from wand.display import display

from datetime import datetime
import time
import os

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


def make_thumbnail(directory, system_uid, size=100, overwrite=False):
    src_filename = "%s.jpg" % system_uid
    src_path = os.path.join(directory, src_filename)
    suffix = 'jpg'
    if not os.path.exists(src_path):
        src_filename = "%s.png" % system_uid
        src_path = os.path.join(directory, src_filename)
        suffix = 'png'

    with Image(filename=src_path) as img:
        w, h = img.size
        offset_x = 0
        offset_y = 0
        if w > h:
            factor = h / float(size)
            new_h = size
            new_w = int(w / factor)
            offset_x = int((new_w - size) / 2)
        else:
            factor = w / size
            new_w = size
            new_h = int(h / factor)
            offset_y = int((new_h - size) / 2)

        img.resize(int(new_w), int(new_h))
        img.crop(left=offset_x, top=offset_y, width=size, height=size)
        thumb_filename = system_uid + '_thumb.' + suffix
        thumb_path = os.path.join(directory, thumb_filename)
        if overwrite or not os.path.exists(thumb_path):
            img.save(filename=thumb_path)
        elif os.path.exists(thumb_path):
            print "can't overwrite existing file"


def get_measurement_table_name(measurement_name, system_uid):
    """Generate the measurement table name in the database given the
    system UID and measurment name"""
    table_name = "aqxs_" + measurement_name + "_" + system_uid
    return table_name
