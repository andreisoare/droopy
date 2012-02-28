# Copyright 2011 Sunnytrail Insight Labs Inc. All rights reserved.
# Author: andrei@thesunnytrail.com (Andrei Soare)
#
# Useful functions for working with Beanstalk.

import global_settings
import logging
import time

from beanstalkc import Connection, SocketError

def watch_only(connection, tube):
  for t in connection.watching():
    if t != tube: connection.ignore(t)
  connection.watch(tube)

def use_only(connection, tube):
  connection.use(tube)

def connect_beanstalk(host, port, watch_tube='default', use_tube='default', attempts=-1):
  step = 0
  while step < attempts or attempts == -1:
    step += 1
    try:
      logging.info('connecting to beanstalk at %s:%s watching tube '
          '"%s" and using tube "%s".'
          % (host, unicode(port), watch_tube, use_tube))
      connection = Connection(host, int(port))
      watch_only(connection, watch_tube)
      use_only(connection, use_tube)
      return connection
    except SocketError:
      logging.getLogger().error('Cannot connect to beanstalk.')
      time.sleep(10)

def clean_beanstalk(timeout=3):
  """Deletes all jobs from beanstalk."""
  logging.info('Cleaning all beanstalk tubes...')
  host, port = global_settings.BEANSTALKD.split(':')
  queue = connect_beanstalk(host, port)
  for tube in queue.tubes():
    queue.watch(tube)
    while True:
      job = queue.reserve(timeout=timeout)
      if job is None: break
      job.delete()
  queue.close()
