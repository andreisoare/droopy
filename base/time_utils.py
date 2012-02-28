import time
import datetime
import pytz

def time_to_unix_utc(t):
  return int(time.mktime(t) - time.timezone)

def current_unix_time_utc():
  return time_to_unix_utc(time.gmtime())

def datetime_utc_to_timezone(dt, tz):
  utc = pytz.utc
  utc_dt = utc.localize(dt)
  tz_dt = tz.normalize(utc_dt)
  return tz_dt
