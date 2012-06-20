# Copyright 2012 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Scevenger interface: gathers any type of personal data around an email address
# from different services.

BEANSTALKD = "localhost:11300"
MONGODB = "localhost:27017"
LOG_FILE = "usemails.log"

import logging
from pytz import utc, timezone
from datetime import datetime

def logging_time_converter(*args):
  """All arguments are ignored"""
  utc_time = utc.localize(datetime.utcnow())
  log_tz = timezone('Canada/Pacific')
  log_dt = log_tz.normalize(utc_time.astimezone(log_tz))
  return log_dt.timetuple()

LOG_FORMAT = "%(asctime)s:%(module)s:%(filename)s:%(lineno)s: [%(levelname)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, datefmt=DATE_FORMAT, level=logging.INFO)
logging.Formatter.converter = logging_time_converter
